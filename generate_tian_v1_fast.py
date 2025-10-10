#!/usr/bin/env python3
"""
Generate Tian Hanzi Deck v1 - OPTIMIZED with Multiprocessing
Creates decks for top 1500 Hanzi by frequency using Hanzipy

This script uses multiprocessing to speed up data generation significantly.
Expected speedup: 2-4x faster depending on CPU cores.

This script generates three decks:
1. Radicals - Unique radicals from the top 1500 characters
2. Hanzi - Top 1500 characters with meanings and readings
3. Vocabulary - High-frequency words using these characters
"""

import sys
from collections import OrderedDict
from multiprocessing import Pool, cpu_count
from parquet_utils import ParquetDataManager

try:
    from hanzipy.decomposer import HanziDecomposer
    from hanzipy.dictionary import HanziDictionary
except ImportError:
    print("❌ Error: hanzipy is not installed")
    print("\nTo install hanzipy, run:")
    print("  pip install hanzipy")
    sys.exit(1)

# Constants
TOP_N_HANZI = 1500
VOCAB_PER_HANZI = 2  # Number of vocabulary words per character
NUM_PROCESSES = max(1, cpu_count() - 1)  # Use all cores minus 1


def init_worker():
    """Initialize Hanzipy in each worker process"""
    global decomposer, dictionary
    decomposer = HanziDecomposer()
    dictionary = HanziDictionary()


def fetch_character_batch(positions):
    """Fetch a batch of characters by their frequency positions"""
    characters = []
    for position in positions:
        try:
            char_data = dictionary.get_character_in_frequency_list_by_position(position)
            if char_data and 'character' in char_data:
                characters.append(char_data)
        except Exception:
            continue
    return characters


def process_character_for_radicals(char_data):
    """Extract radicals from a single character"""
    char = char_data['character']
    radicals_found = {}
    
    try:
        decomposition = decomposer.decompose(char, 2)
        
        if decomposition and 'components' in decomposition:
            components = decomposition['components']
            
            for component in components:
                if component:
                    try:
                        meaning = decomposer.get_radical_meaning(component)
                        if meaning and meaning != component:
                            radicals_found[component] = meaning
                        else:
                            radicals_found[component] = f"Component {component}"
                    except Exception:
                        radicals_found[component] = f"Component {component}"
    except Exception:
        pass
    
    return radicals_found


def process_character_for_hanzi(char_data):
    """Process a single character to create hanzi card data"""
    char = char_data['character']
    
    try:
        # Get definitions
        definitions = dictionary.definition_lookup(char)
        if not definitions:
            return None
        
        # Use the first definition
        first_def = definitions[0]
        meaning = first_def['definition']
        reading = first_def['pinyin']
        
        # Get radical composition
        decomposition = decomposer.decompose(char, 2)
        radicals = ""
        if decomposition and 'components' in decomposition:
            components = decomposition['components']
            radicals = " + ".join(components)
        
        # Create basic mnemonics
        meaning_mnemonic = f'The character {char} means "{meaning}". '
        if radicals:
            meaning_mnemonic += f'It is composed of: {radicals}.'
        
        reading_mnemonic = f'Pronounced as "{reading}". Remember the sound by associating it with the meaning "{meaning}".'
        
        return {
            'character': char,
            'meaning': meaning,
            'reading': reading,
            'radicals': radicals if radicals else char,
            'meaning_mnemonic': meaning_mnemonic,
            'reading_mnemonic': reading_mnemonic,
            'frequency_rank': char_data.get('number', 0)
        }
    except Exception:
        return None


def process_character_for_vocab(hanzi_data):
    """Generate vocabulary for a single character"""
    char = hanzi_data['character']
    vocab_list = []
    
    try:
        # Get example words sorted by frequency
        examples = dictionary.get_examples(char)
        
        # Collect high-frequency examples first, then mid-frequency
        candidate_words = []
        if 'high_frequency' in examples:
            candidate_words.extend(examples['high_frequency'][:2])
        if 'mid_frequency' in examples and len(candidate_words) < VOCAB_PER_HANZI:
            candidate_words.extend(examples['mid_frequency'][:VOCAB_PER_HANZI - len(candidate_words)])
        
        # Add vocabulary cards
        for word_data in candidate_words[:VOCAB_PER_HANZI]:
            word = word_data['simplified']
            
            # Skip single characters
            if len(word) < 2:
                continue
            
            # Break down the word into characters
            characters_breakdown = []
            for w_char in word:
                try:
                    char_def = dictionary.definition_lookup(w_char)
                    if char_def:
                        char_meaning = char_def[0]['definition'].split('/')[0]
                        characters_breakdown.append(f'{w_char} ({char_meaning})')
                except Exception:
                    characters_breakdown.append(w_char)
            
            characters_str = " + ".join(characters_breakdown) if characters_breakdown else word
            
            # Create a simple mnemonic
            mnemonic = f'Remember: {word} means "{word_data["definition"]}". '
            if len(characters_breakdown) > 1:
                mnemonic += f'Think of the individual meanings combining: {characters_str}'
            
            vocab_list.append({
                'word': word,
                'meaning': word_data['definition'],
                'reading': word_data['pinyin'],
                'characters': characters_str,
                'example': '',
                'mnemonic': mnemonic
            })
    except Exception:
        pass
    
    return vocab_list


def get_top_hanzi(n=1500):
    """Get the top N characters by frequency using multiprocessing"""
    print(f"\n📊 Fetching top {n} characters by frequency...")
    print(f"   Using {NUM_PROCESSES} worker processes")
    
    # Initialize Hanzipy in main process for batch splitting
    init_worker()
    
    # Split positions into batches for parallel processing
    batch_size = 50
    position_batches = []
    for i in range(1, n + 1, batch_size):
        batch = list(range(i, min(i + batch_size, n + 1)))
        position_batches.append(batch)
    
    # Process batches in parallel
    characters = []
    with Pool(processes=NUM_PROCESSES, initializer=init_worker) as pool:
        results = pool.map(fetch_character_batch, position_batches)
        for batch_result in results:
            characters.extend(batch_result)
            if len(characters) % 100 < batch_size:
                print(f"   Progress: {len(characters)}/{n} characters")
    
    print(f"✓ Retrieved {len(characters)} characters")
    return characters


def extract_unique_radicals(characters):
    """Extract unique radicals from a list of characters using multiprocessing"""
    print("\n🔍 Extracting unique radicals...")
    print(f"   Using {NUM_PROCESSES} worker processes")
    
    radicals_dict = OrderedDict()
    
    # Process characters in parallel
    with Pool(processes=NUM_PROCESSES, initializer=init_worker) as pool:
        results = pool.map(process_character_for_radicals, characters)
        
        # Merge results
        for i, char_radicals in enumerate(results):
            for radical, meaning in char_radicals.items():
                if radical not in radicals_dict:
                    radicals_dict[radical] = meaning
            
            if (i + 1) % 200 == 0:
                print(f"   Processed: {i + 1}/{len(characters)} characters, found {len(radicals_dict)} unique radicals")
    
    print(f"✓ Found {len(radicals_dict)} unique radicals")
    return radicals_dict


def generate_radical_mnemonic(radical, meaning):
    """Generate a simple mnemonic for a radical"""
    mnemonics = {
        '氵': 'Three drops of water falling down. Found in water-related characters.',
        '亻': 'A person standing upright, the left form of 人 (person).',
        '讠': 'Speech radical - like words coming out of a mouth.',
        '扌': 'Hand radical - the left form of 手 (hand).',
        '钅': 'Metal radical - related to gold and metal.',
        '木': 'A tree with branches and roots.',
        '口': 'An open mouth or enclosure.',
        '心': 'A heart with its chambers.',
        '女': 'A woman, often representing feminine concepts.',
        '日': 'The sun, or represents day and time.',
        '月': 'The moon, or represents month.',
        '火': 'Flames of fire burning.',
        '土': 'Earth or soil.',
        '⻊': 'Walking or movement, the simplified form of 走.',
        '艹': 'Grass growing from the ground.',
        '宀': 'A house with a roof.',
        '纟': 'Silk thread, related to fabric and thread.',
    }
    
    if radical in mnemonics:
        return mnemonics[radical]
    else:
        return f'The {radical} radical represents "{meaning}". Look for this component in related characters.'


def generate_hanzi_data(characters):
    """Generate hanzi card data with meanings, readings, and mnemonics using multiprocessing"""
    print("\n📝 Generating Hanzi data...")
    print(f"   Using {NUM_PROCESSES} worker processes")
    
    # Process characters in parallel
    with Pool(processes=NUM_PROCESSES, initializer=init_worker) as pool:
        results = pool.map(process_character_for_hanzi, characters)
        
        # Filter out None results and track progress
        hanzi_data = []
        for i, result in enumerate(results):
            if result is not None:
                hanzi_data.append(result)
            
            if (i + 1) % 200 == 0:
                print(f"   Progress: {i + 1}/{len(characters)} characters")
    
    print(f"✓ Generated {len(hanzi_data)} hanzi cards")
    return hanzi_data


def generate_vocab_data(hanzi_data):
    """Generate vocabulary data using high-frequency words with multiprocessing"""
    print("\n📚 Generating Vocabulary data...")
    print(f"   Using {NUM_PROCESSES} worker processes")
    
    # Process characters in parallel
    with Pool(processes=NUM_PROCESSES, initializer=init_worker) as pool:
        results = pool.map(process_character_for_vocab, hanzi_data)
        
        # Flatten results and remove duplicates
        vocab_set = set()
        vocab_data = []
        
        for i, vocab_list in enumerate(results):
            for vocab in vocab_list:
                if vocab['word'] not in vocab_set:
                    vocab_set.add(vocab['word'])
                    vocab_data.append(vocab)
            
            if (i + 1) % 200 == 0:
                print(f"   Progress: {i + 1}/{len(hanzi_data)} characters, {len(vocab_data)} vocab words")
    
    print(f"✓ Generated {len(vocab_data)} vocabulary cards")
    return vocab_data


def save_data_to_parquet(radicals_dict, hanzi_data, vocab_data, output_dir='data'):
    """Save generated data to Parquet files"""
    print(f"\n💾 Saving data to Parquet format in {output_dir}/...")
    
    # Convert radicals dict to list of dicts
    radicals_list = []
    for radical, meaning in radicals_dict.items():
        mnemonic = generate_radical_mnemonic(radical, meaning)
        radicals_list.append({
            'radical': radical,
            'meaning': meaning,
            'mnemonic': mnemonic
        })
    
    # Save using ParquetDataManager
    manager = ParquetDataManager(output_dir)
    manager.save_all(radicals_list, hanzi_data, vocab_data)
    
    print(f"✓ Data saved to Parquet files in {output_dir}/")


def main():
    """Main function to generate the Tian v1 deck data"""
    import time
    start_time = time.time()
    
    print("=" * 60)
    print("🎴 Tian Hanzi Deck v1 Generator (MULTIPROCESSING)")
    print("=" * 60)
    print(f"⚡ Using {NUM_PROCESSES} CPU cores for parallel processing")
    
    # Step 1: Get top N characters
    characters = get_top_hanzi(TOP_N_HANZI)
    
    # Step 2: Extract unique radicals
    radicals_dict = extract_unique_radicals(characters)
    
    # Step 3: Generate hanzi data
    hanzi_data = generate_hanzi_data(characters)
    
    # Step 4: Generate vocabulary data
    vocab_data = generate_vocab_data(hanzi_data)
    
    # Step 5: Save to Parquet
    save_data_to_parquet(radicals_dict, hanzi_data, vocab_data)
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    # Summary
    print("\n" + "=" * 60)
    print("✨ Generation Complete!")
    print("=" * 60)
    print("📊 Summary:")
    print(f"   - Radicals: {len(radicals_dict)} unique components")
    print(f"   - Hanzi: {len(hanzi_data)} characters")
    print(f"   - Vocabulary: {len(vocab_data)} words")
    print(f"   - Total Cards: {len(radicals_dict) + len(hanzi_data) + len(vocab_data)}")
    print("\n⚡ Performance:")
    print(f"   - CPU Cores Used: {NUM_PROCESSES}")
    print(f"   - Total Time: {minutes}m {seconds}s")
    print(f"   - Avg Speed: {len(hanzi_data) / elapsed_time:.1f} characters/second")
    print("\n📁 Data saved to: data/ (Parquet format)")
    print("\n🎯 Next steps:")
    print("   1. Review the generated data: python parquet_utils.py load")
    print("   2. Create the Anki deck: python create_deck_from_parquet.py")
    print("   3. Import the .apkg file into Anki")
    print("=" * 60)


if __name__ == '__main__':
    main()
