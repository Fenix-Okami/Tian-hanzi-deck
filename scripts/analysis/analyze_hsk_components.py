#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze HSK 1-3 Component Productivity
Shows distribution and statistics of component productivity scores
"""

import sys
import io
import pandas as pd
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def analyze_hsk_components():
    """Analyze component productivity from HSK 1-3 data"""
    comp_file = Path("data/radicals.csv")
    hanzi_file = Path("data/hanzi.csv")
    vocab_file = Path("data/vocabulary.csv")
    
    if not comp_file.exists():
        print("❌ Component file not found. Run `tian-hanzi deck build` first.")
        return
    
    comp_df = pd.read_csv(comp_file)
    hanzi_df = pd.read_csv(hanzi_file) if hanzi_file.exists() else None
    vocab_df = pd.read_csv(vocab_file) if vocab_file.exists() else None
    
    print("=" * 70)
    print("HSK 1-3 COMPONENT PRODUCTIVITY ANALYSIS")
    print("=" * 70)
    
    if vocab_df is not None:
        print(f"\n📚 Vocabulary: {len(vocab_df):,} words")
        vocab_by_level = vocab_df.groupby('hsk_level').size()
        for level in sorted(vocab_by_level.index):
            count = vocab_by_level[level]
            print(f"  HSK {level}: {count:,} words")
    
    if hanzi_df is not None:
        print(f"\n🔤 Hanzi: {len(hanzi_df):,} characters")
    
    print(f"\n🧩 Components: {len(comp_df):,} unique components")
    
    # Productivity score distribution
    print("\n📊 Productivity Score Distribution:")
    print("-" * 70)
    
    ranges = [
        (100, float('inf'), "Very High (100+)"),
        (50, 99, "High (50-99)"),
        (20, 49, "Medium (20-49)"),
        (10, 19, "Low (10-19)"),
        (1, 9, "Very Low (1-9)")
    ]
    
    for min_score, max_score, label in ranges:
        count = len(comp_df[(comp_df['usage_count'] >= min_score) & 
                           (comp_df['usage_count'] <= max_score)])
        if count > 0:
            pct = (count / len(comp_df)) * 100
            bar = "█" * int(pct / 2)
            print(f"{label:>20}: {count:>3} components ({pct:>5.1f}%) {bar}")
    
    # Top 30 components
    print("\n🏆 Top 30 Most Productive Components:")
    print("-" * 70)
    print(f"{'Rank':<6}{'Radical':<12}{'Score':<8}{'Meaning':<45}")
    print("-" * 70)
    
    top_30 = comp_df.nlargest(30, 'usage_count')
    for idx, (_, row) in enumerate(top_30.iterrows(), 1):
        radical = row['radical']
        score = int(row['usage_count'])
        meaning = str(row['meaning'])[:44]
        print(f"{idx:<6}{radical:<12}{score:<8}{meaning:<45}")
    
    # Statistics
    print("\n📈 Statistical Summary:")
    print("-" * 70)
    print(f"Mean productivity score: {comp_df['usage_count'].mean():.1f}")
    print(f"Median productivity score: {comp_df['usage_count'].median():.1f}")
    print(f"Std deviation: {comp_df['usage_count'].std():.1f}")
    print(f"Max score: {comp_df['usage_count'].max()}")
    print(f"Min score: {comp_df['usage_count'].min()}")
    
    # Learning recommendations
    print("\n💡 Learning Recommendations:")
    print("-" * 70)
    
    high_priority = len(comp_df[comp_df['usage_count'] >= 50])
    medium_priority = len(comp_df[(comp_df['usage_count'] >= 20) & 
                                   (comp_df['usage_count'] < 50)])
    low_priority = len(comp_df[comp_df['usage_count'] < 20])
    
    print(f"\n1️⃣  HIGH PRIORITY ({high_priority} components):")
    print("   Learn these first! Each appears in 50+ characters.")
    print(f"   Components: {', '.join(comp_df[comp_df['usage_count'] >= 50]['radical'].head(10).tolist())}, ...")
    
    print(f"\n2️⃣  MEDIUM PRIORITY ({medium_priority} components):")
    print("   Learn these second. Each appears in 20-49 characters.")
    
    print(f"\n3️⃣  LOW PRIORITY ({low_priority} components):")
    print("   Learn these last. Each appears in fewer than 20 characters.")
    
    # Coverage analysis
    print("\n🎯 Learning Coverage:")
    print("-" * 70)
    
    milestones = [10, 20, 30, 50, 100]
    
    for milestone in milestones:
        if milestone <= len(comp_df):
            top_n = comp_df.nlargest(milestone, 'usage_count')
            coverage = top_n['usage_count'].sum()
            
            print(f"Learning top {milestone:>3} components = coverage for ~{coverage:>4} character occurrences")
    
    print("\n" + "=" * 70)
    print("✅ Analysis complete!")
    print("=" * 70 + "\n")


def main():
    """Run analysis"""
    analyze_hsk_components()


if __name__ == "__main__":
    main()
