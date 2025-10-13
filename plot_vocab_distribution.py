#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vocabulary Distribution by Tian Level and HSK Level
Creates a multi-bar plot showing how vocabulary is distributed across learning levels
"""

import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def create_vocab_distribution_plot():
    """Create a multi-bar plot of vocabulary distribution by Tian level and HSK level"""
    
    print("📊 Loading vocabulary data...")
    vocab_df = pd.read_parquet('data/vocabulary.parquet')
    
    # Group by tian_level and hsk_level
    distribution = vocab_df.groupby(['tian_level', 'hsk_level']).size().reset_index(name='count')
    
    # Pivot to get HSK levels as columns
    pivot_df = distribution.pivot(index='tian_level', columns='hsk_level', values='count').fillna(0)
    
    print(f"✓ Loaded {len(vocab_df)} vocabulary words")
    print(f"✓ Distribution across {len(pivot_df)} Tian levels")
    print()
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(16, 8))
    
    # Set up the bar positions
    tian_levels = pivot_df.index.values
    x = np.arange(len(tian_levels))
    width = 0.25  # Width of each bar
    
    # Colors for each HSK level
    colors = {
        1: '#FF6B6B',  # Red - HSK 1 (easiest)
        2: '#4ECDC4',  # Teal - HSK 2
        3: '#45B7D1'   # Blue - HSK 3
    }
    
    # Create bars for each HSK level
    bars = []
    for i, hsk_level in enumerate(sorted(pivot_df.columns)):
        offset = (i - 1) * width  # Center the bars
        bar = ax.bar(x + offset, pivot_df[hsk_level], width, 
                     label=f'HSK {int(hsk_level)}',
                     color=colors.get(int(hsk_level), '#95A5A6'),
                     alpha=0.8,
                     edgecolor='white',
                     linewidth=0.5)
        bars.append(bar)
    
    # Customize the plot
    ax.set_xlabel('Tian Level', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Vocabulary Words', fontsize=12, fontweight='bold')
    ax.set_title('Vocabulary Distribution by Tian Level and HSK Level\nHSK 1-3 Deck (2,227 words)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(tian_levels, fontsize=9)
    ax.legend(title='HSK Level', fontsize=10, title_fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Add value labels on top of bars (only if count > 0)
    for bar_group in bars:
        for bar in bar_group:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=7, alpha=0.8)
    
    plt.tight_layout()
    
    # Save the plot
    output_file = 'data/vocab_distribution_by_level.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Plot saved to: {output_file}")
    
    # Show summary statistics
    print("\n" + "=" * 70)
    print("VOCABULARY DISTRIBUTION SUMMARY")
    print("=" * 70)
    print()
    
    # Total by HSK level
    hsk_totals = vocab_df.groupby('hsk_level').size()
    print("📚 Total Vocabulary by HSK Level:")
    for hsk in sorted(hsk_totals.index):
        count = hsk_totals[hsk]
        pct = (count / len(vocab_df)) * 100
        print(f"   HSK {int(hsk)}: {count:4d} words ({pct:5.1f}%)")
    print(f"   Total:  {len(vocab_df):4d} words")
    print()
    
    # Distribution by Tian level
    tian_totals = vocab_df.groupby('tian_level').size()
    print("📊 Words per Tian Level:")
    print(f"   Min:    {tian_totals.min():.0f} words")
    print(f"   Max:    {tian_totals.max():.0f} words")
    print(f"   Mean:   {tian_totals.mean():.1f} words")
    print(f"   Median: {tian_totals.median():.0f} words")
    print()
    
    # Show top 10 levels with most vocabulary
    print("🏆 Top 10 Levels by Vocabulary Count:")
    top_levels = tian_totals.sort_values(ascending=False).head(10)
    for level, count in top_levels.items():
        hsk_breakdown = vocab_df[vocab_df['tian_level'] == level].groupby('hsk_level').size()
        hsk_str = " | ".join([f"HSK{int(h)}:{c}" for h, c in hsk_breakdown.items()])
        print(f"   Level {level:2d}: {count:3d} words ({hsk_str})")
    print()
    
    # Show detailed table for first 10 levels
    print("📋 Detailed Breakdown (First 10 Levels):")
    print("-" * 70)
    print(f"{'Level':>5} | {'HSK1':>5} | {'HSK2':>5} | {'HSK3':>5} | {'Total':>5}")
    print("-" * 70)
    for level in sorted(pivot_df.index)[:10]:
        hsk1 = int(pivot_df.loc[level, 1]) if 1 in pivot_df.columns else 0
        hsk2 = int(pivot_df.loc[level, 2]) if 2 in pivot_df.columns else 0
        hsk3 = int(pivot_df.loc[level, 3]) if 3 in pivot_df.columns else 0
        total = hsk1 + hsk2 + hsk3
        print(f"{level:5d} | {hsk1:5d} | {hsk2:5d} | {hsk3:5d} | {total:5d}")
    print("-" * 70)
    print()
    
    print("=" * 70)
    print()
    print(f"💡 Open {output_file} to view the plot!")
    
    # Close the plot (don't display interactively)
    plt.close()


if __name__ == "__main__":
    create_vocab_distribution_plot()
