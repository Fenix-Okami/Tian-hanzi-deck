#!/usr/bin/env python3
"""
Generate a CSV report showing how many radicals, hanzi, and vocabulary words are in each level.
"""

import pandas as pd
import sys
import io

# Windows UTF-8 console support
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def generate_level_report():
    """Generate a CSV report of counts per level."""
    
    print("Reading data files...")
    
    # Read the CSV files
    radicals_df = pd.read_csv('data/radicals.csv')
    hanzi_df = pd.read_csv('data/hanzi.csv')
    vocab_df = pd.read_csv('data/vocabulary.csv')
    
    print(f"Total radicals: {len(radicals_df)}")
    print(f"Total hanzi: {len(hanzi_df)}")
    print(f"Total vocabulary: {len(vocab_df)}")
    print()
    
    # Count by level
    radical_counts = radicals_df.groupby('tian_level').size().reset_index(name='radicals')
    hanzi_counts = hanzi_df.groupby('tian_level').size().reset_index(name='hanzi')
    vocab_counts = vocab_df.groupby('tian_level').size().reset_index(name='vocabulary')
    
    # Merge all counts together
    report = radical_counts.merge(hanzi_counts, on='tian_level', how='outer')
    report = report.merge(vocab_counts, on='tian_level', how='outer')
    
    # Fill NaN values with 0 and convert to int
    report = report.fillna(0).astype({'radicals': int, 'hanzi': int, 'vocabulary': int})
    
    # Sort by level
    report = report.sort_values('tian_level')
    
    # Rename column for clarity
    report = report.rename(columns={'tian_level': 'level'})
    
    # Add totals row
    totals = pd.DataFrame({
        'level': ['TOTAL'],
        'radicals': [report['radicals'].sum()],
        'hanzi': [report['hanzi'].sum()],
        'vocabulary': [report['vocabulary'].sum()]
    })
    
    report_with_totals = pd.concat([report, totals], ignore_index=True)
    
    # Save to CSV
    output_file = 'data/level_counts_report.csv'
    report_with_totals.to_csv(output_file, index=False)
    
    print(f"Level counts report saved to: {output_file}")
    print()
    print("Preview:")
    print(report_with_totals.to_string(index=False))
    
    # Calculate some statistics
    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    
    # Exclude the totals row for statistics
    stats_df = report.copy()
    
    print(f"\nTotal levels: {len(stats_df)}")
    print(f"\nAverage per level:")
    print(f"  Radicals: {stats_df['radicals'].mean():.1f}")
    print(f"  Hanzi: {stats_df['hanzi'].mean():.1f}")
    print(f"  Vocabulary: {stats_df['vocabulary'].mean():.1f}")
    
    print(f"\nMax per level:")
    print(f"  Radicals: {stats_df['radicals'].max()}")
    print(f"  Hanzi: {stats_df['hanzi'].max()}")
    print(f"  Vocabulary: {stats_df['vocabulary'].max()}")
    
    print(f"\nMin per level:")
    print(f"  Radicals: {stats_df['radicals'].min()}")
    print(f"  Hanzi: {stats_df['hanzi'].min()}")
    print(f"  Vocabulary: {stats_df['vocabulary'].min()}")

if __name__ == '__main__':
    generate_level_report()
