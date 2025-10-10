#!/usr/bin/env python3
"""
HSK Data Scorer - Scoring system for HSK vocabulary and hanzi
Assigns scores based on HSK level and frequency position within each level

Scoring Formula:
- HSK Level Base Score (difficulty):
  - HSK 1: 1000 points
  - HSK 2: 700 points
  - HSK 3: 500 points
  - HSK 4: 350 points
  - HSK 5: 200 points
  - HSK 6: 100 points
  - HSK 7-9: 0 points
  
- Frequency Bonus:
  - Top 100 in frequency list: +100 points
  - Below 100: +0 points

Total Score = Level Base Score + Frequency Bonus
"""

from pathlib import Path
from typing import Dict, Tuple
import pandas as pd


class HSKScorer:
    """Score HSK vocabulary and hanzi based on level and frequency"""
    
    # Default scoring parameters (adjustable)
    DEFAULT_LEVEL_SCORES = {
        1: 1000,
        2: 700,
        3: 500,
        4: 350,
        5: 200,
        6: 100,
        "7-9": 0,
    }
    
    FREQUENCY_BONUS_THRESHOLD = 100
    FREQUENCY_BONUS_POINTS = 100
    
    def __init__(self, hsk_data_dir: str = "data/HSK-3.0", 
                 level_scores: Dict = None,
                 frequency_threshold: int = None,
                 frequency_bonus: int = None):
        """
        Initialize HSK Scorer
        
        Args:
            hsk_data_dir: Path to HSK-3.0 data directory
            level_scores: Custom level scoring dict (optional)
            frequency_threshold: Custom frequency bonus threshold (optional)
            frequency_bonus: Custom frequency bonus points (optional)
        """
        self.hsk_dir = Path(hsk_data_dir)
        self.hanzi_dir = self.hsk_dir / "HSK Hanzi"
        self.frequency_dir = self.hsk_dir / "HSK List (Frequency)"
        
        # Use custom or default scoring parameters
        self.level_scores = level_scores if level_scores else self.DEFAULT_LEVEL_SCORES
        self.frequency_threshold = frequency_threshold if frequency_threshold else self.FREQUENCY_BONUS_THRESHOLD
        self.frequency_bonus = frequency_bonus if frequency_bonus else self.FREQUENCY_BONUS_POINTS
        
        # Storage for loaded data
        self.hanzi_data = {}
        self.vocab_data = {}
    
    def load_hsk_hanzi(self) -> Dict[str, Dict]:
        """
        Load all HSK hanzi from text files
        
        Returns:
            Dict mapping hanzi to their HSK level and data
        """
        print("📖 Loading HSK Hanzi data...")
        hanzi_dict = {}
        
        for level in [1, 2, 3, 4, 5, 6, "7-9"]:
            file_path = self.hanzi_dir / f"HSK {level}.txt"
            
            if not file_path.exists():
                print(f"⚠️  Warning: {file_path} not found")
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                hanzi_list = [line.strip() for line in f if line.strip()]
            
            for hanzi in hanzi_list:
                if hanzi not in hanzi_dict:  # Keep lowest level if duplicate
                    hanzi_dict[hanzi] = {
                        'hanzi': hanzi,
                        'hsk_level': level,
                        'level_score': self.level_scores.get(level, 0)
                    }
            
            print(f"  ✓ HSK {level}: {len(hanzi_list)} hanzi")
        
        self.hanzi_data = hanzi_dict
        print(f"✅ Loaded {len(hanzi_dict)} unique hanzi across all HSK levels\n")
        return hanzi_dict
    
    def load_hsk_vocabulary(self) -> Dict[str, Dict]:
        """
        Load all HSK vocabulary with frequency rankings
        
        Returns:
            Dict mapping vocabulary to their HSK level, frequency position, and score
        """
        print("📖 Loading HSK Vocabulary (Frequency) data...")
        vocab_dict = {}
        
        for level in [1, 2, 3, 4, 5, 6, "7-9"]:
            file_path = self.frequency_dir / f"HSK {level}.txt"
            
            if not file_path.exists():
                print(f"⚠️  Warning: {file_path} not found")
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                vocab_list = [line.strip() for line in f if line.strip()]
            
            for position, word in enumerate(vocab_list, start=1):
                if word not in vocab_dict:  # Keep lowest level if duplicate
                    # Calculate frequency bonus
                    freq_bonus = self.frequency_bonus if position <= self.frequency_threshold else 0
                    
                    vocab_dict[word] = {
                        'word': word,
                        'hsk_level': level,
                        'frequency_position': position,
                        'level_score': self.level_scores.get(level, 0),
                        'frequency_bonus': freq_bonus,
                        'total_score': self.level_scores.get(level, 0) + freq_bonus
                    }
            
            print(f"  ✓ HSK {level}: {len(vocab_list)} words")
        
        self.vocab_data = vocab_dict
        print(f"✅ Loaded {len(vocab_dict)} unique vocabulary words across all HSK levels\n")
        return vocab_dict
    
    def get_hanzi_score(self, hanzi: str) -> Tuple[int, Dict]:
        """
        Get the score for a specific hanzi character
        
        Args:
            hanzi: The Chinese character
            
        Returns:
            Tuple of (score, data_dict)
        """
        if hanzi in self.hanzi_data:
            data = self.hanzi_data[hanzi]
            return (data['level_score'], data)
        return (0, {})
    
    def get_vocab_score(self, word: str) -> Tuple[int, Dict]:
        """
        Get the score for a specific vocabulary word
        
        Args:
            word: The vocabulary word
            
        Returns:
            Tuple of (total_score, data_dict)
        """
        if word in self.vocab_data:
            data = self.vocab_data[word]
            return (data['total_score'], data)
        return (0, {})
    
    def export_scored_hanzi_csv(self, output_file: str = "data/hsk_hanzi_scored.csv"):
        """Export scored hanzi data to CSV"""
        if not self.hanzi_data:
            print("⚠️  No hanzi data loaded. Call load_hsk_hanzi() first.")
            return
        
        df = pd.DataFrame(list(self.hanzi_data.values()))
        df = df.sort_values('level_score', ascending=False)
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✅ Exported {len(df)} scored hanzi to {output_file}")
    
    def export_scored_vocabulary_csv(self, output_file: str = "data/hsk_vocabulary_scored.csv"):
        """Export scored vocabulary data to CSV"""
        if not self.vocab_data:
            print("⚠️  No vocabulary data loaded. Call load_hsk_vocabulary() first.")
            return
        
        df = pd.DataFrame(list(self.vocab_data.values()))
        df = df.sort_values('total_score', ascending=False)
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✅ Exported {len(df)} scored vocabulary to {output_file}")
    
    def export_scored_hanzi_parquet(self, output_file: str = "data/hsk_hanzi_scored.parquet"):
        """Export scored hanzi data to Parquet"""
        if not self.hanzi_data:
            print("⚠️  No hanzi data loaded. Call load_hsk_hanzi() first.")
            return
        
        df = pd.DataFrame(list(self.hanzi_data.values()))
        # Convert hsk_level to string to handle "7-9" mixed with integers
        df['hsk_level'] = df['hsk_level'].astype(str)
        df = df.sort_values('level_score', ascending=False)
        df.to_parquet(output_file, engine='pyarrow', compression='snappy', index=False)
        print(f"✅ Exported {len(df)} scored hanzi to {output_file}")
    
    def export_scored_vocabulary_parquet(self, output_file: str = "data/hsk_vocabulary_scored.parquet"):
        """Export scored vocabulary data to Parquet"""
        if not self.vocab_data:
            print("⚠️  No vocabulary data loaded. Call load_hsk_vocabulary() first.")
            return
        
        df = pd.DataFrame(list(self.vocab_data.values()))
        # Convert hsk_level to string to handle "7-9" mixed with integers
        df['hsk_level'] = df['hsk_level'].astype(str)
        df = df.sort_values('total_score', ascending=False)
        df.to_parquet(output_file, engine='pyarrow', compression='snappy', index=False)
        print(f"✅ Exported {len(df)} scored vocabulary to {output_file}")
    
    def print_score_summary(self):
        """Print a summary of the scoring system"""
        print("=" * 60)
        print("HSK SCORING SYSTEM SUMMARY")
        print("=" * 60)
        print("\n📊 LEVEL BASE SCORES (Difficulty):")
        for level, score in self.level_scores.items():
            print(f"  HSK {level}: {score} points")
        
        print("\n🎯 FREQUENCY BONUS:")
        print(f"  Top {self.frequency_threshold} words: +{self.frequency_bonus} points")
        print(f"  Below {self.frequency_threshold}: +0 points")
        
        print("\n📈 SCORING FORMULA:")
        print("  Total Score = Level Base Score + Frequency Bonus")
        print("=" * 60 + "\n")


def main():
    """Example usage of HSKScorer"""
    # Initialize scorer with default settings
    scorer = HSKScorer()
    
    # Print scoring summary
    scorer.print_score_summary()
    
    # Load data
    scorer.load_hsk_hanzi()
    scorer.load_hsk_vocabulary()
    
    # Show some examples
    print("📝 EXAMPLE SCORES:")
    print("\nHanzi Examples:")
    example_hanzi = ['的', '爱', '学', '习']
    for hanzi in example_hanzi:
        score, data = scorer.get_hanzi_score(hanzi)
        if data:
            print(f"  {hanzi}: HSK {data['hsk_level']}, Score: {score}")
    
    print("\nVocabulary Examples:")
    example_vocab = ['你好', '中国', '学习', '谢谢']
    for word in example_vocab:
        score, data = scorer.get_vocab_score(word)
        if data:
            freq = data['frequency_position']
            bonus = data['frequency_bonus']
            print(f"  {word}: HSK {data['hsk_level']}, Pos #{freq}, Score: {score} (base: {data['level_score']} + bonus: {bonus})")
    
    # Export data
    print("\n💾 Exporting scored data...")
    scorer.export_scored_hanzi_csv()
    scorer.export_scored_vocabulary_csv()
    scorer.export_scored_hanzi_parquet()
    scorer.export_scored_vocabulary_parquet()
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
