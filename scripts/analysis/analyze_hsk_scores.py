#!/usr/bin/env python3
"""
Analyze HSK Score Distribution
Shows statistics and distribution of HSK scores across levels
"""

import pandas as pd
from pathlib import Path


def analyze_vocabulary_scores():
    """Analyze vocabulary score distribution"""
    vocab_file = Path("data/hsk_vocabulary_scored.csv")
    
    if not vocab_file.exists():
        print("❌ Vocabulary file not found. Run hsk_scorer.py first.")
        return
    
    df = pd.read_csv(vocab_file)
    
    print("=" * 70)
    print("HSK VOCABULARY SCORE DISTRIBUTION")
    print("=" * 70)
    print(f"\nTotal vocabulary words: {len(df):,}")
    
    print("\n📊 Distribution by HSK Level:")
    print("-" * 70)
    level_stats = df.groupby('hsk_level').agg({
        'word': 'count',
        'total_score': ['min', 'max', 'mean'],
        'frequency_bonus': 'sum'
    }).round(1)
    
    for level in ['1', '2', '3', '4', '5', '6', '7-9']:
        if level in level_stats.index:
            count = int(level_stats.loc[level, ('word', 'count')])
            min_score = int(level_stats.loc[level, ('total_score', 'min')])
            max_score = int(level_stats.loc[level, ('total_score', 'max')])
            avg_score = level_stats.loc[level, ('total_score', 'mean')]
            bonus_count = int(level_stats.loc[level, ('frequency_bonus', 'sum')] / 100)
            
            print(f"HSK {level:>3}: {count:>5} words | "
                  f"Scores: {min_score:>4}-{max_score:>4} | "
                  f"Avg: {avg_score:>6.1f} | "
                  f"Top 100: {bonus_count:>3} words")
    
    print("\n🏆 Top 20 Highest Scored Words:")
    print("-" * 70)
    top_20 = df.nlargest(20, 'total_score')[['word', 'hsk_level', 'frequency_position', 'total_score']]
    for idx, row in top_20.iterrows():
        print(f"{row['word']:>6} | HSK {row['hsk_level']:>3} | "
              f"Pos #{row['frequency_position']:<4} | Score: {int(row['total_score'])}")
    
    print("\n📈 Score Distribution:")
    print("-" * 70)
    score_ranges = [
        (1100, 1100, "Top HSK 1 (1100)"),
        (1000, 1099, "HSK 1 Base (1000)"),
        (700, 799, "HSK 2 (700-800)"),
        (500, 599, "HSK 3 (500-600)"),
        (350, 449, "HSK 4 (350-450)"),
        (200, 299, "HSK 5 (200-300)"),
        (100, 199, "HSK 6 (100-200)"),
        (0, 99, "HSK 7-9 (0-100)")
    ]
    
    for min_s, max_s, label in score_ranges:
        count = len(df[(df['total_score'] >= min_s) & (df['total_score'] <= max_s)])
        if count > 0:
            pct = (count / len(df)) * 100
            bar = "█" * int(pct / 2)
            print(f"{label:>20}: {count:>5} words ({pct:>5.1f}%) {bar}")


def analyze_hanzi_scores():
    """Analyze hanzi score distribution"""
    hanzi_file = Path("data/hsk_hanzi_scored.csv")
    
    if not hanzi_file.exists():
        print("❌ Hanzi file not found. Run hsk_scorer.py first.")
        return
    
    df = pd.read_csv(hanzi_file)
    
    print("\n" + "=" * 70)
    print("HSK HANZI SCORE DISTRIBUTION")
    print("=" * 70)
    print(f"\nTotal hanzi characters: {len(df):,}")
    
    print("\n📊 Distribution by HSK Level:")
    print("-" * 70)
    level_counts = df['hsk_level'].value_counts().sort_index()
    level_scores = df.groupby('hsk_level')['level_score'].mean()
    
    for level in ['1', '2', '3', '4', '5', '6', '7-9']:
        if level in level_counts.index:
            count = int(level_counts[level])
            score = int(level_scores[level])
            pct = (count / len(df)) * 100
            bar = "█" * int(pct / 3)
            print(f"HSK {level:>3}: {count:>4} hanzi ({pct:>5.1f}%) | Score: {score:>4} {bar}")
    
    print("\n🔤 Sample Hanzi by Level:")
    print("-" * 70)
    for level in ['1', '2', '3', '4', '5', '6', '7-9']:
        if level in df['hsk_level'].values:
            sample = df[df['hsk_level'] == level]['hanzi'].head(20).tolist()
            sample_str = ''.join(sample)
            print(f"HSK {level:>3}: {sample_str}")


def main():
    """Run all analyses"""
    analyze_vocabulary_scores()
    analyze_hanzi_scores()
    print("\n" + "=" * 70)
    print("✅ Analysis complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
