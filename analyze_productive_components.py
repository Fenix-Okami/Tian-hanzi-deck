#!/usr/bin/env python3
"""
Analyze Productive Components
Ranks character components by their "productivity score" based on:
1. How many characters contain the component
2. Weighted by the frequency rank of those characters

Formula: score = sum(1/frequency_rank) for each character containing the component
Characters that appear more frequently contribute more to the component's score.

Based on methodology from: https://hanzicraft.com/lists/productive-components
"""

import sys
from collections import defaultdict

try:
    from hanzipy.decomposer import HanziDecomposer
    from hanzipy.dictionary import HanziDictionary
except ImportError:
    print("❌ Error: hanzipy is not installed")
    print("\nTo install hanzipy, run:")
    print("  pip install hanzipy")
    sys.exit(1)

# =============================================================================
# CONFIGURATION
# =============================================================================
# Set this to limit the analysis to the top N most frequent characters
# Use None for full dataset (9933 characters), or set a specific number like 1500
HANZI_FREQUENCY_LIMIT = 1500  # Analyze only top 1500 most frequent characters

# Full Jun Da frequency list size
FREQUENCY_LIST_SIZE = 9933


def calculate_productive_components():
    """
    Calculate productive component scores
    
    Returns:
        Dictionary mapping component -> {
            'score': float,
            'count': int,
            'characters': list of tuples (char, frequency_rank)
        }
    """
    # Determine how many characters to analyze
    max_chars = HANZI_FREQUENCY_LIMIT if HANZI_FREQUENCY_LIMIT else FREQUENCY_LIST_SIZE
    
    print("=" * 60)
    print("🔍 Analyzing Productive Components")
    print("=" * 60)
    if HANZI_FREQUENCY_LIMIT:
        print(f"📊 Analyzing TOP {max_chars} most frequent characters")
        print(f"   (Limited by HANZI_FREQUENCY_LIMIT setting)\n")
    else:
        print(f"📊 Analyzing ALL {FREQUENCY_LIST_SIZE} characters in Jun Da frequency list\n")
    
    # Initialize Hanzipy
    print("🔧 Initializing Hanzipy (this may take a moment)...")
    decomposer = HanziDecomposer()
    dictionary = HanziDictionary()
    print("✓ Hanzipy initialized\n")
    
    # Build component data
    component_data = defaultdict(lambda: {
        'score': 0.0,
        'count': 0,
        'characters': []
    })
    
    # Collect all characters and their components
    print("📝 Step 1: Extracting components from characters...")
    if max_chars < 3000:
        print("   (This should be quick...)\n")
    else:
        print("   (This will take a few minutes...)\n")
    
    processed = 0
    for position in range(1, max_chars + 1):
        try:
            char_data = dictionary.get_character_in_frequency_list_by_position(position)
            if not char_data or 'character' not in char_data:
                continue
            
            char = char_data['character']
            
            # Get radical decomposition
            decomposition = decomposer.decompose(char, 2)
            if not decomposition or 'components' not in decomposition:
                continue
            
            components = decomposition['components']
            
            # Each character contributes 1/frequency_rank to its components
            contribution = 1.0 / position
            
            for component in components:
                if component and component != char:  # Don't count the character itself
                    component_data[component]['score'] += contribution
                    component_data[component]['count'] += 1
                    component_data[component]['characters'].append((char, position))
            
            processed += 1
            # Show progress updates based on dataset size
            update_interval = 100 if max_chars <= 2000 else 500
            if position % update_interval == 0:
                print(f"   Processed: {position}/{max_chars} characters, found {len(component_data)} components")
        
        except Exception:
            continue
    
    print(f"\n✓ Successfully processed {processed} characters")
    
    # Filter out components that only appear once
    filtered_components = {
        comp: data for comp, data in component_data.items()
        if data['count'] > 1
    }
    
    print(f"\n✓ Found {len(filtered_components)} productive components (appearing in 2+ characters)")
    print(f"✓ Total components before filtering: {len(component_data)}")
    
    return filtered_components


def rank_components(component_data):
    """Sort components by productivity score"""
    ranked = sorted(
        component_data.items(),
        key=lambda x: x[1]['score'],
        reverse=True
    )
    return ranked


def display_results(ranked_components, top_n=50):
    """Display the top N productive components"""
    print("\n" + "=" * 60)
    print(f"🏆 Top {top_n} Most Productive Components")
    print("=" * 60)
    print("\nRank | Component | Score    | Count | Top 3 Characters (Frequency Rank)")
    print("-" * 75)
    
    for rank, (component, data) in enumerate(ranked_components[:top_n], start=1):
        score = data['score']
        count = data['count']
        
        # Get top 3 most frequent characters containing this component
        top_chars = sorted(data['characters'], key=lambda x: x[1])[:3]
        char_display = ", ".join([f"{char}({pos})" for char, pos in top_chars])
        
        print(f"{rank:4} | {component:9} | {score:8.2f} | {count:5} | {char_display}")
    
    print("=" * 60)


def save_results(ranked_components, filename='data/productive_components.csv'):
    """Save results to CSV file"""
    import os
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("rank,component,productivity_score,character_count,sample_characters\n")
        
        for rank, (component, data) in enumerate(ranked_components, start=1):
            score = data['score']
            count = data['count']
            
            # Get top 5 most frequent characters
            top_chars = sorted(data['characters'], key=lambda x: x[1])[:5]
            char_list = ";".join([f"{char}({pos})" for char, pos in top_chars])
            
            f.write(f"{rank},{component},{score:.4f},{count},{char_list}\n")
    
    print(f"\n💾 Results saved to: {filename}")


def compare_with_hanzicraft():
    """Compare results with HanziCraft's known top components"""
    print("\n" + "=" * 60)
    print("📊 Comparison with HanziCraft Top 10")
    print("=" * 60)
    
    hanzicraft_top10 = [
        ('人', 1, 942),
        ('口', 2, 1503),
        ('白', 3, 120),
        ('勺', 4, 17),
        ('日', 5, 664),
        ('一', 6, 68),
        ('小', 7, 343),
        ('大', 8, 374),
        ('土', 9, 346),
        ('十', 10, 560),
    ]
    
    print("\nHanziCraft Expected (full character database):")
    for comp, rank, count in hanzicraft_top10:
        print(f"  {rank:2}. {comp} (appears in {count} characters)")
    
    max_chars = HANZI_FREQUENCY_LIMIT if HANZI_FREQUENCY_LIMIT else FREQUENCY_LIST_SIZE
    
    print("\nNote: Results will differ based on settings:")
    if HANZI_FREQUENCY_LIMIT:
        print(f"  - Current setting: Top {max_chars} most frequent characters")
        print("  - HanziCraft uses full character database (~20,000+ characters)")
    else:
        print(f"  - We're using Jun Da frequency list ({FREQUENCY_LIST_SIZE} characters)")
        print("  - HanziCraft may use a different/larger character database")
    print("  - Component extraction methods may differ slightly")
    print("  - We weight by frequency, HanziCraft also uses frequency weighting")


def main():
    """Main function"""
    import time
    start_time = time.time()
    
    # Calculate productive components
    component_data = calculate_productive_components()
    
    # Rank by productivity score
    ranked_components = rank_components(component_data)
    
    # Display results
    display_results(ranked_components, top_n=50)
    
    # Save to file
    save_results(ranked_components)
    
    # Compare with HanziCraft
    compare_with_hanzicraft()
    
    # Summary
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    max_chars = HANZI_FREQUENCY_LIMIT if HANZI_FREQUENCY_LIMIT else FREQUENCY_LIST_SIZE
    
    print("\n" + "=" * 60)
    print("✨ Analysis Complete!")
    print("=" * 60)
    print(f"⏱️  Time: {minutes}m {seconds}s")
    if HANZI_FREQUENCY_LIMIT:
        print(f"📊 Analyzed: Top {max_chars} most frequent characters")
    else:
        print(f"📊 Analyzed: All {FREQUENCY_LIST_SIZE} characters from Jun Da frequency list")
    print(f"🔍 Found: {len(ranked_components)} productive components")
    print("\n💡 Use this data to order radicals by pedagogical value!")
    print(f"📝 Edit HANZI_FREQUENCY_LIMIT in the script to analyze different amounts")
    print("=" * 60)


if __name__ == '__main__':
    main()
