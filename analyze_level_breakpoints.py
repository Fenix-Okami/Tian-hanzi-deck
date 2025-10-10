#!/usr/bin/env python3
"""
Analyze Level Breakpoints
==========================
This script analyzes the optimal radical grouping to unlock at least 20 hanzi per level.

Instead of fixed radicals per level (e.g., 5 radicals), this finds natural breakpoints
where adding radicals unlocks a meaningful number of new characters.

Strategy:
1. Start with most productive radicals
2. Add radicals one by one
3. When >= 20 new hanzi become available (all their components learned), create a level
4. Repeat until all radicals assigned
"""

import pandas as pd
import sys
import io
from pathlib import Path

# Windows console UTF-8 setup
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def load_data():
    """Load radicals and hanzi data"""
    print("📂 Loading data...")
    
    radicals_df = pd.read_parquet('data/radicals.parquet')
    hanzi_df = pd.read_parquet('data/hanzi.parquet')
    
    print(f"   ✓ Loaded {len(radicals_df)} radicals")
    print(f"   ✓ Loaded {len(hanzi_df)} hanzi")
    print()
    
    return radicals_df, hanzi_df


def parse_components(components_str):
    """Parse pipe-separated components string"""
    if pd.isna(components_str) or not components_str:
        return []
    return [c.strip() for c in str(components_str).split('|') if c.strip()]


def can_learn_hanzi(hanzi_components, learned_radicals):
    """Check if all components of a hanzi are in learned radicals"""
    if not hanzi_components:
        return False
    return all(comp in learned_radicals for comp in hanzi_components)


def find_breakpoints(radicals_df, hanzi_df, min_hanzi_per_level=20):
    """
    Find optimal radical grouping to unlock at least min_hanzi_per_level hanzi per level.
    
    Returns:
        List of tuples: (level_num, radical_indices, num_radicals, newly_unlocked_hanzi)
    """
    print(f"🔍 Finding breakpoints (target: ≥{min_hanzi_per_level} hanzi per level)...")
    print("=" * 70)
    
    # Sort radicals by productivity (already done in data, but ensure it)
    radicals_sorted = radicals_df.sort_values('usage_count', ascending=False).reset_index(drop=True)
    
    # Parse all hanzi components once
    hanzi_components_list = []
    for idx, row in hanzi_df.iterrows():
        components = parse_components(row.get('components', ''))
        hanzi_components_list.append({
            'hanzi': row.get('hanzi', ''),
            'components': components,
            'hsk_level': row.get('hsk_level', ''),
            'learned': False
        })
    
    # Track state
    learned_radicals = set()
    learned_hanzi_indices = set()
    levels = []
    current_level = 1
    radical_start_idx = 0
    
    while radical_start_idx < len(radicals_sorted):
        # Add radicals one by one until we unlock enough hanzi
        newly_unlocked = []
        radicals_in_level = []
        
        for i in range(radical_start_idx, len(radicals_sorted)):
            # Add this radical
            radical = radicals_sorted.iloc[i]['radical']
            radicals_in_level.append(i)
            learned_radicals.add(radical)
            
            # Check which new hanzi can now be learned
            for idx, hanzi_data in enumerate(hanzi_components_list):
                if idx in learned_hanzi_indices:
                    continue  # Already learned
                
                if can_learn_hanzi(hanzi_data['components'], learned_radicals):
                    newly_unlocked.append(idx)
                    learned_hanzi_indices.add(idx)
            
            # Check if we've unlocked enough hanzi
            if len(newly_unlocked) >= min_hanzi_per_level:
                # Create level
                levels.append({
                    'level': current_level,
                    'radical_indices': radicals_in_level,
                    'num_radicals': len(radicals_in_level),
                    'unlocked_hanzi': newly_unlocked[:],
                    'num_unlocked': len(newly_unlocked)
                })
                
                # Show progress
                radical_names = [radicals_sorted.iloc[ri]['radical'] for ri in radicals_in_level[:5]]
                if len(radicals_in_level) > 5:
                    radical_names_str = ', '.join(radical_names) + f', ... ({len(radicals_in_level)} total)'
                else:
                    radical_names_str = ', '.join(radical_names)
                
                print(f"Level {current_level:2d}: {len(radicals_in_level):2d} radicals → {len(newly_unlocked):3d} hanzi")
                print(f"          Radicals: {radical_names_str}")
                print()
                
                current_level += 1
                radical_start_idx = i + 1
                break
        else:
            # Reached end of radicals, create final level with remaining
            if radicals_in_level:
                levels.append({
                    'level': current_level,
                    'radical_indices': radicals_in_level,
                    'num_radicals': len(radicals_in_level),
                    'unlocked_hanzi': newly_unlocked[:],
                    'num_unlocked': len(newly_unlocked)
                })
                
                radical_names = [radicals_sorted.iloc[ri]['radical'] for ri in radicals_in_level[:5]]
                if len(radicals_in_level) > 5:
                    radical_names_str = ', '.join(radical_names) + f', ... ({len(radicals_in_level)} total)'
                else:
                    radical_names_str = ', '.join(radical_names)
                
                print(f"Level {current_level:2d}: {len(radicals_in_level):2d} radicals → {len(newly_unlocked):3d} hanzi (final)")
                print(f"          Radicals: {radical_names_str}")
                print()
            break
    
    print("=" * 70)
    print()
    return levels, radicals_sorted, hanzi_components_list


def analyze_statistics(levels, radicals_sorted, hanzi_components_list):
    """Print statistics about the breakpoint analysis"""
    print("📊 BREAKPOINT ANALYSIS STATISTICS")
    print("=" * 70)
    print()
    
    total_radicals = sum(level['num_radicals'] for level in levels)
    total_unlocked = sum(level['num_unlocked'] for level in levels)
    
    print(f"Total Levels:    {len(levels)}")
    print(f"Total Radicals:  {total_radicals}")
    print(f"Total Hanzi:     {total_unlocked}")
    print()
    
    # Radicals per level stats
    radicals_per_level = [level['num_radicals'] for level in levels]
    print(f"Radicals per Level:")
    print(f"  Min:     {min(radicals_per_level)}")
    print(f"  Max:     {max(radicals_per_level)}")
    print(f"  Average: {sum(radicals_per_level) / len(radicals_per_level):.1f}")
    print()
    
    # Hanzi per level stats
    hanzi_per_level = [level['num_unlocked'] for level in levels]
    print(f"Hanzi per Level:")
    print(f"  Min:     {min(hanzi_per_level)}")
    print(f"  Max:     {max(hanzi_per_level)}")
    print(f"  Average: {sum(hanzi_per_level) / len(hanzi_per_level):.1f}")
    print()
    
    print("=" * 70)
    print()


def compare_with_fixed_levels(levels, radicals_df):
    """Compare with fixed 5-radicals-per-level approach"""
    print("📊 COMPARISON WITH FIXED 5-RADICALS-PER-LEVEL")
    print("=" * 70)
    print()
    
    fixed_levels = (len(radicals_df) + 4) // 5  # Ceiling division
    dynamic_levels = len(levels)
    
    print(f"Fixed Approach (5 radicals/level):")
    print(f"  Levels:           {fixed_levels}")
    print(f"  Radicals/level:   5 (fixed)")
    print()
    
    print(f"Dynamic Approach (≥20 hanzi/level):")
    print(f"  Levels:           {dynamic_levels}")
    radicals_per_level = [level['num_radicals'] for level in levels]
    print(f"  Radicals/level:   {min(radicals_per_level)}-{max(radicals_per_level)} (variable)")
    hanzi_per_level = [level['num_unlocked'] for level in levels]
    print(f"  Hanzi/level:      {min(hanzi_per_level)}-{max(hanzi_per_level)} (variable)")
    print()
    
    if dynamic_levels < fixed_levels:
        print(f"✅ Dynamic approach uses {fixed_levels - dynamic_levels} fewer levels")
    elif dynamic_levels > fixed_levels:
        print(f"⚠️  Dynamic approach uses {dynamic_levels - fixed_levels} more levels")
    else:
        print(f"➡️  Same number of levels")
    
    print()
    print("=" * 70)
    print()


def show_detailed_breakdown(levels, radicals_sorted, hanzi_components_list, show_first=10):
    """Show detailed breakdown of first N levels"""
    print(f"📋 DETAILED BREAKDOWN (First {show_first} levels)")
    print("=" * 70)
    print()
    
    for i, level_data in enumerate(levels[:show_first]):
        level = level_data['level']
        radical_indices = level_data['radical_indices']
        num_radicals = level_data['num_radicals']
        num_unlocked = level_data['num_unlocked']
        
        print(f"Level {level}:")
        print(f"  Radicals ({num_radicals}):")
        
        for idx in radical_indices:
            radical_data = radicals_sorted.iloc[idx]
            print(f"    {radical_data['radical']:3s} - {radical_data['meaning']:30s} (used in {radical_data['usage_count']} chars)")
        
        print(f"  Unlocks {num_unlocked} hanzi")
        print()
    
    if len(levels) > show_first:
        print(f"... and {len(levels) - show_first} more levels")
        print()
    
    print("=" * 70)
    print()


def export_breakpoint_data(levels, radicals_sorted, hanzi_components_list, output_file='data/breakpoint_analysis.csv'):
    """Export breakpoint analysis to CSV"""
    print(f"💾 Exporting breakpoint analysis to {output_file}...")
    
    rows = []
    for level_data in levels:
        level = level_data['level']
        radical_indices = level_data['radical_indices']
        
        radical_list = [radicals_sorted.iloc[idx]['radical'] for idx in radical_indices]
        
        rows.append({
            'level': level,
            'num_radicals': level_data['num_radicals'],
            'radicals': '|'.join(radical_list),
            'num_unlocked_hanzi': level_data['num_unlocked']
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"   ✓ Exported {len(df)} levels")
    print()


def main():
    """Main analysis function"""
    print("=" * 70)
    print("🔬 LEVEL BREAKPOINT ANALYSIS")
    print("=" * 70)
    print()
    print("Analyzing optimal radical grouping based on hanzi unlocking...")
    print()
    
    # Load data
    radicals_df, hanzi_df = load_data()
    
    # Find breakpoints (default: 20 hanzi per level)
    levels, radicals_sorted, hanzi_components_list = find_breakpoints(
        radicals_df, 
        hanzi_df, 
        min_hanzi_per_level=20
    )
    
    # Show statistics
    analyze_statistics(levels, radicals_sorted, hanzi_components_list)
    
    # Compare with fixed approach
    compare_with_fixed_levels(levels, radicals_df)
    
    # Show detailed breakdown
    show_detailed_breakdown(levels, radicals_sorted, hanzi_components_list, show_first=10)
    
    # Export data
    export_breakpoint_data(levels, radicals_sorted, hanzi_components_list)
    
    print("✅ Analysis complete!")
    print()
    print("💡 To try different thresholds:")
    print("   python analyze_level_breakpoints.py")
    print()


if __name__ == '__main__':
    main()
