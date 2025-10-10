#!/usr/bin/env python3
"""
Sort HSK Deck by Radical Dependencies
======================================
Organizes the HSK 1-3 deck into levels where:
- Level 1-47: Radicals (5 radicals per level, 233 total)
- Hanzi levels: Each hanzi only uses radicals from previous levels
- Vocabulary levels: Each word only uses hanzi from previous levels

This creates a natural learning progression where all components
are learned before the characters that use them.

Adapted for HSK 1-3 data structure.
"""

import pandas as pd
import sys
import io

# Windows console UTF-8 setup
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Constants
RADICALS_PER_LEVEL = 5


def load_data():
    """Load all three parquet files"""
    print("📂 Loading HSK data from parquet files...")
    radicals_df = pd.read_parquet('data/radicals.parquet')
    hanzi_df = pd.read_parquet('data/hanzi.parquet')
    vocab_df = pd.read_parquet('data/vocabulary.parquet')
    
    print(f"   ✓ Loaded {len(radicals_df)} radicals")
    print(f"   ✓ Loaded {len(hanzi_df)} hanzi")
    print(f"   ✓ Loaded {len(vocab_df)} vocabulary")
    
    return radicals_df, hanzi_df, vocab_df


def assign_radical_levels(radicals_df):
    """
    Assign level numbers to radicals.
    5 radicals per level (already sorted by productivity)
    """
    print("\n📊 Assigning radical levels...")
    
    # Add level column (1-indexed)
    radicals_df['level'] = [(i // RADICALS_PER_LEVEL) + 1 for i in range(len(radicals_df))]
    
    # Create a mapping of radical -> level
    radical_to_level = dict(zip(radicals_df['radical'], radicals_df['level']))
    
    num_levels = radicals_df['level'].max()
    print(f"   ✓ Created {num_levels} radical levels ({RADICALS_PER_LEVEL} radicals each)")
    
    return radicals_df, radical_to_level, num_levels


def parse_radicals_from_hanzi(radicals_str):
    """
    Parse the radicals string from hanzi data.
    Format: "radical1|radical2|radical3" (pipe-separated)
    """
    if pd.isna(radicals_str) or not radicals_str:
        return []
    
    # Split by "|" and clean up
    parts = radicals_str.split('|')
    return [r.strip() for r in parts if r.strip()]


def calculate_hanzi_level(radicals_list, radical_to_level, radical_levels):
    """
    Calculate the level for a hanzi based on its component radicals.
    The hanzi level is one after the maximum level of any of its radicals.
    If a radical is unknown, we consider it level 1.
    """
    if not radicals_list:
        return radical_levels + 1  # Unknown components go after radicals
    
    max_radical_level = 0
    for radical in radicals_list:
        radical_level = radical_to_level.get(radical, 1)  # Default to level 1 if unknown
        max_radical_level = max(max_radical_level, radical_level)
    
    # Hanzi comes after its highest-level radical
    return max_radical_level + 1


def assign_hanzi_levels(hanzi_df, radical_to_level, radical_levels):
    """
    Assign level numbers to hanzi based on their component radicals.
    Each hanzi's level is one after the highest-level radical it contains.
    """
    print("\n🔤 Assigning hanzi levels based on radical dependencies...")
    
    hanzi_levels = []
    hanzi_to_level = {}
    
    for idx, row in hanzi_df.iterrows():
        # Use 'components' column (not 'radicals')
        components_str = row.get('components', row.get('radicals', ''))
        radicals_list = parse_radicals_from_hanzi(components_str)
        level = calculate_hanzi_level(radicals_list, radical_to_level, radical_levels)
        hanzi_levels.append(level)
        hanzi_to_level[row.get('hanzi', row.get('character', ''))] = level
    
    hanzi_df['level'] = hanzi_levels
    
    # Sort by: 1) level (ascending), 2) hsk_level (ascending), 3) component_count (ascending - simpler first)
    sort_columns = ['level', 'hsk_level']
    sort_ascending = [True, True]
    
    # Add component_count as a tiebreaker if available (simpler characters first)
    if 'component_count' in hanzi_df.columns:
        sort_columns.append('component_count')
        sort_ascending.append(True)
    
    hanzi_df = hanzi_df.sort_values(sort_columns, ascending=sort_ascending)
    
    # Reset index after sorting
    hanzi_df = hanzi_df.reset_index(drop=True)
    
    # Print statistics
    level_counts = hanzi_df['level'].value_counts().sort_index()
    print(f"   ✓ Assigned hanzi to {len(level_counts)} levels")
    print(f"   ✓ Level range: {hanzi_df['level'].min()} to {hanzi_df['level'].max()}")
    print(f"   ✓ Average hanzi per level: {len(hanzi_df) / len(level_counts):.1f}")
    
    return hanzi_df, hanzi_to_level


def parse_characters_from_vocab(characters_str):
    """
    Parse the characters string from vocabulary data.
    Format: "char1 (meaning1) + char2 (meaning2)"
    """
    if pd.isna(characters_str) or not characters_str:
        return []
    
    # Split by " + " and extract just the character (before the parenthesis)
    parts = characters_str.split(' + ')
    characters = []
    for part in parts:
        # Extract character before "("
        char = part.split('(')[0].strip()
        if char:
            characters.append(char)
    
    return characters


def calculate_vocab_level(word, characters_list, hanzi_to_level, max_hanzi_level):
    """
    Calculate the level for a vocabulary word based on its component hanzi.
    The vocab level is one after the maximum level of any of its characters.
    """
    if not characters_list:
        # Try to get characters from the word itself
        characters_list = list(word)
    
    if not characters_list:
        return max_hanzi_level + 1  # Unknown goes after hanzi
    
    max_char_level = 0
    for char in characters_list:
        char_level = hanzi_to_level.get(char, max_hanzi_level + 1)
        max_char_level = max(max_char_level, char_level)
    
    # Vocab comes after its highest-level character
    return max_char_level + 1


def assign_vocab_levels(vocab_df, hanzi_to_level, max_hanzi_level):
    """
    Assign level numbers to vocabulary based on their component hanzi.
    Each word's level is one after the highest-level hanzi it contains.
    """
    print("\n📚 Assigning vocabulary levels based on hanzi dependencies...")
    
    vocab_levels = []
    
    for idx, row in vocab_df.iterrows():
        # Vocabulary doesn't have 'characters' column in HSK data
        # Just use the word itself to extract characters
        word = row.get('word', '')
        characters_list = list(word) if word else []
        
        level = calculate_vocab_level(word, characters_list, hanzi_to_level, max_hanzi_level)
        vocab_levels.append(level)
    
    vocab_df['level'] = vocab_levels
    
    # Sort by: 1) level (ascending), 2) hsk_level (ascending), 3) frequency_position (ascending - more frequent first)
    sort_columns = ['level', 'hsk_level']
    sort_ascending = [True, True]
    
    # Add frequency_position as final tiebreaker if available (lower position = more frequent)
    if 'frequency_position' in vocab_df.columns:
        sort_columns.append('frequency_position')
        sort_ascending.append(True)
    
    vocab_df = vocab_df.sort_values(sort_columns, ascending=sort_ascending)
    
    vocab_df = vocab_df.reset_index(drop=True)
    
    # Print statistics
    level_counts = vocab_df['level'].value_counts().sort_index()
    print(f"   ✓ Assigned vocabulary to {len(level_counts)} levels")
    print(f"   ✓ Level range: {vocab_df['level'].min()} to {vocab_df['level'].max()}")
    print(f"   ✓ Average words per level: {len(vocab_df) / len(level_counts):.1f}")
    
    return vocab_df


def save_sorted_data(radicals_df, hanzi_df, vocab_df):
    """Save the sorted data back to parquet files"""
    print("\n💾 Saving sorted data with levels...")
    
    radicals_df.to_parquet('data/radicals.parquet', index=False)
    print(f"   ✓ Saved {len(radicals_df)} radicals to data/radicals.parquet")
    
    hanzi_df.to_parquet('data/hanzi.parquet', index=False)
    print(f"   ✓ Saved {len(hanzi_df)} hanzi to data/hanzi.parquet")
    
    vocab_df.to_parquet('data/vocabulary.parquet', index=False)
    print(f"   ✓ Saved {len(vocab_df)} vocabulary to data/vocabulary.parquet")
    
    # Also save CSV versions
    radicals_df.to_csv('data/radicals.csv', index=False, encoding='utf-8-sig')
    hanzi_df.to_csv('data/hanzi.csv', index=False, encoding='utf-8-sig')
    vocab_df.to_csv('data/vocabulary.csv', index=False, encoding='utf-8-sig')
    print(f"   ✓ Saved CSV versions to data/ folder")


def print_level_summary(radicals_df, hanzi_df, vocab_df):
    """Print a summary of the level distribution"""
    print("\n" + "="*60)
    print("📊 LEVEL DISTRIBUTION SUMMARY (HSK 1-3)")
    print("="*60)
    
    print("\n🔷 RADICALS (5 per level):")
    radical_levels = radicals_df['level'].value_counts().sort_index()
    for level in sorted(radical_levels.index[:10]):  # Show first 10 levels
        count = radical_levels[level]
        sample_rads = radicals_df[radicals_df['level'] == level]['radical'].head(5).tolist()
        print(f"   Level {level:2d}: {count} radicals - {', '.join(sample_rads)}")
    if len(radical_levels) > 10:
        print(f"   ... ({len(radical_levels) - 10} more levels)")
    
    print("\n🔤 HANZI (sorted by radical dependencies):")
    hanzi_levels = hanzi_df['level'].value_counts().sort_index()
    for level in sorted(hanzi_levels.index[:10]):  # Show first 10 levels
        count = hanzi_levels[level]
        # Use 'hanzi' column name
        char_col = 'hanzi' if 'hanzi' in hanzi_df.columns else 'character'
        sample_chars = hanzi_df[hanzi_df['level'] == level][char_col].head(5).tolist()
        print(f"   Level {level:2d}: {count:3d} hanzi - {', '.join(sample_chars)}")
    if len(hanzi_levels) > 10:
        print(f"   ... ({len(hanzi_levels) - 10} more levels)")
    
    print("\n📚 VOCABULARY (sorted by hanzi dependencies):")
    vocab_levels = vocab_df['level'].value_counts().sort_index()
    for level in sorted(vocab_levels.index[:10]):  # Show first 10 levels
        count = vocab_levels[level]
        sample_words = vocab_df[vocab_df['level'] == level]['word'].head(5).tolist()
        print(f"   Level {level:2d}: {count:3d} words - {', '.join(sample_words)}")
    if len(vocab_levels) > 10:
        print(f"   ... ({len(vocab_levels) - 10} more levels)")
    
    print("\n" + "="*60)
    print(f"Total Levels: {max(radicals_df['level'].max(), hanzi_df['level'].max(), vocab_df['level'].max())}")
    print("="*60)


def main():
    print("="*60)
    print("🎴 HSK 1-3 DECK - DEPENDENCY-BASED SORTING")
    print("="*60)
    print("\nThis script organizes the HSK deck so that:")
    print("  1. Radicals are learned first (5 per level)")
    print("  2. Hanzi are introduced only after their radicals")
    print("  3. Vocabulary uses only previously learned hanzi")
    print()
    
    try:
        # Load data
        radicals_df, hanzi_df, vocab_df = load_data()
        
        # Assign levels to radicals
        radicals_df, radical_to_level, radical_levels = assign_radical_levels(radicals_df)
        
        # Assign levels to hanzi based on radicals
        hanzi_df, hanzi_to_level = assign_hanzi_levels(hanzi_df, radical_to_level, radical_levels)
        
        # Assign levels to vocabulary based on hanzi
        max_hanzi_level = hanzi_df['level'].max()
        vocab_df = assign_vocab_levels(vocab_df, hanzi_to_level, max_hanzi_level)
        
        # Save sorted data
        save_sorted_data(radicals_df, hanzi_df, vocab_df)
        
        # Print summary
        print_level_summary(radicals_df, hanzi_df, vocab_df)
        
        print("\n✅ Sorting complete! HSK data is now organized by dependency levels.")
        print("\n🎯 Next step: python create_hsk_deck.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
