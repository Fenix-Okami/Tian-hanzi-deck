#!/usr/bin/env python3
"""
Parquet Data Utilities for Tian Hanzi Deck
Save and load RADICALS, HANZI, and VOCABULARY data in Parquet format
"""

import sys
from pathlib import Path
from typing import Dict, List

try:
    import pandas as pd
except ImportError:
    print("❌ Error: pandas and pyarrow are not installed")
    print("\nTo install required packages, run:")
    print("  pip install pandas pyarrow")
    sys.exit(1)


class ParquetDataManager:
    """Manage saving and loading Hanzi deck data in Parquet format"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the ParquetDataManager
        
        Args:
            data_dir: Directory to store parquet files (default: "data")
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.radicals_file = self.data_dir / "radicals.parquet"
        self.hanzi_file = self.data_dir / "hanzi.parquet"
        self.vocabulary_file = self.data_dir / "vocabulary.parquet"
    
    def save_radicals(self, radicals: List[Dict]) -> None:
        """
        Save radicals data to Parquet format
        
        Args:
            radicals: List of dictionaries containing radical data
        """
        if not radicals:
            print("⚠️  Warning: No radicals data to save")
            return
        
        df = pd.DataFrame(radicals)
        df.to_parquet(self.radicals_file, engine='pyarrow', compression='snappy', index=False)
        print(f"✓ Saved {len(radicals)} radicals to {self.radicals_file}")
    
    def save_hanzi(self, hanzi: List[Dict]) -> None:
        """
        Save hanzi data to Parquet format
        
        Args:
            hanzi: List of dictionaries containing hanzi data
        """
        if not hanzi:
            print("⚠️  Warning: No hanzi data to save")
            return
        
        df = pd.DataFrame(hanzi)
        df.to_parquet(self.hanzi_file, engine='pyarrow', compression='snappy', index=False)
        print(f"✓ Saved {len(hanzi)} hanzi to {self.hanzi_file}")
    
    def save_vocabulary(self, vocabulary: List[Dict]) -> None:
        """
        Save vocabulary data to Parquet format
        
        Args:
            vocabulary: List of dictionaries containing vocabulary data
        """
        if not vocabulary:
            print("⚠️  Warning: No vocabulary data to save")
            return
        
        df = pd.DataFrame(vocabulary)
        df.to_parquet(self.vocabulary_file, engine='pyarrow', compression='snappy', index=False)
        print(f"✓ Saved {len(vocabulary)} vocabulary entries to {self.vocabulary_file}")
    
    def save_all(self, radicals: List[Dict], hanzi: List[Dict], vocabulary: List[Dict]) -> None:
        """
        Save all data (radicals, hanzi, vocabulary) to Parquet files
        
        Args:
            radicals: List of radical dictionaries
            hanzi: List of hanzi dictionaries
            vocabulary: List of vocabulary dictionaries
        """
        print("💾 Saving data to Parquet format...")
        self.save_radicals(radicals)
        self.save_hanzi(hanzi)
        self.save_vocabulary(vocabulary)
        print("✅ All data saved successfully!")
    
    def load_radicals(self) -> List[Dict]:
        """
        Load radicals data from Parquet file
        
        Returns:
            List of dictionaries containing radical data
        """
        if not self.radicals_file.exists():
            print(f"❌ Error: {self.radicals_file} does not exist")
            return []
        
        df = pd.read_parquet(self.radicals_file, engine='pyarrow')
        radicals = df.to_dict('records')
        print(f"✓ Loaded {len(radicals)} radicals from {self.radicals_file}")
        return radicals
    
    def load_hanzi(self) -> List[Dict]:
        """
        Load hanzi data from Parquet file
        
        Returns:
            List of dictionaries containing hanzi data
        """
        if not self.hanzi_file.exists():
            print(f"❌ Error: {self.hanzi_file} does not exist")
            return []
        
        df = pd.read_parquet(self.hanzi_file, engine='pyarrow')
        hanzi = df.to_dict('records')
        print(f"✓ Loaded {len(hanzi)} hanzi from {self.hanzi_file}")
        return hanzi
    
    def load_vocabulary(self) -> List[Dict]:
        """
        Load vocabulary data from Parquet file
        
        Returns:
            List of dictionaries containing vocabulary data
        """
        if not self.vocabulary_file.exists():
            print(f"❌ Error: {self.vocabulary_file} does not exist")
            return []
        
        df = pd.read_parquet(self.vocabulary_file, engine='pyarrow')
        vocabulary = df.to_dict('records')
        print(f"✓ Loaded {len(vocabulary)} vocabulary entries from {self.vocabulary_file}")
        return vocabulary
    
    def load_all(self) -> tuple:
        """
        Load all data (radicals, hanzi, vocabulary) from Parquet files
        
        Returns:
            Tuple of (radicals, hanzi, vocabulary)
        """
        print("📂 Loading data from Parquet format...")
        radicals = self.load_radicals()
        hanzi = self.load_hanzi()
        vocabulary = self.load_vocabulary()
        print("✅ All data loaded successfully!")
        return radicals, hanzi, vocabulary
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get statistics about the saved Parquet files
        
        Returns:
            Dictionary containing file sizes and row counts
        """
        stats = {}
        
        for name, file_path in [
            ('radicals', self.radicals_file),
            ('hanzi', self.hanzi_file),
            ('vocabulary', self.vocabulary_file)
        ]:
            if file_path.exists():
                file_size = file_path.stat().st_size
                df = pd.read_parquet(file_path, engine='pyarrow')
                stats[name] = {
                    'file_path': str(file_path),
                    'file_size_bytes': file_size,
                    'file_size_mb': round(file_size / (1024 * 1024), 2),
                    'row_count': len(df),
                    'columns': list(df.columns)
                }
            else:
                stats[name] = {'exists': False}
        
        return stats
    
    def print_stats(self) -> None:
        """Print statistics about the saved Parquet files"""
        stats = self.get_stats()
        
        print("\n📊 Parquet Files Statistics:")
        print("=" * 60)
        
        for name, info in stats.items():
            print(f"\n{name.upper()}:")
            if info.get('exists') is False:
                print("  ❌ File does not exist")
            else:
                print(f"  📁 Path: {info['file_path']}")
                print(f"  📏 Size: {info['file_size_mb']} MB ({info['file_size_bytes']:,} bytes)")
                print(f"  📝 Rows: {info['row_count']:,}")
                print(f"  🔧 Columns: {', '.join(info['columns'])}")
        
        print("=" * 60)


def save_tian_v1_data_to_parquet(output_dir: str = "data") -> None:
    """
    Save tian_v1_data.py data to Parquet format
    
    Args:
        output_dir: Directory to save the parquet files
    """
    print("🔄 Importing tian_v1_data...")
    try:
        from tian_v1_data import RADICALS, HANZI, VOCABULARY
    except ImportError:
        print("❌ Error: Could not import tian_v1_data.py")
        print("   Make sure the file exists in the current directory")
        sys.exit(1)
    
    manager = ParquetDataManager(output_dir)
    manager.save_all(RADICALS, HANZI, VOCABULARY)
    manager.print_stats()


def load_tian_v1_data_from_parquet(data_dir: str = "data") -> tuple:
    """
    Load Tian Hanzi Deck data from Parquet files
    
    Args:
        data_dir: Directory containing the parquet files
        
    Returns:
        Tuple of (RADICALS, HANZI, VOCABULARY)
    """
    manager = ParquetDataManager(data_dir)
    return manager.load_all()


if __name__ == "__main__":
    """
    Command-line interface for Parquet data operations
    
    Usage:
        python parquet_utils.py save    # Save tian_v1_data to Parquet
        python parquet_utils.py load    # Load and verify Parquet data
        python parquet_utils.py stats   # Show statistics
    """
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python parquet_utils.py save     # Save tian_v1_data to Parquet")
        print("  python parquet_utils.py load     # Load and verify Parquet data")
        print("  python parquet_utils.py stats    # Show statistics")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "save":
        save_tian_v1_data_to_parquet()
    
    elif command == "load":
        radicals, hanzi, vocabulary = load_tian_v1_data_from_parquet()
        print("\n📊 Loaded Data Summary:")
        print(f"  • Radicals: {len(radicals)}")
        print(f"  • Hanzi: {len(hanzi)}")
        print(f"  • Vocabulary: {len(vocabulary)}")
        
        # Show sample data
        if radicals:
            print(f"\n  Sample Radical: {radicals[0]}")
        if hanzi:
            print(f"  Sample Hanzi: {hanzi[0]}")
        if vocabulary:
            print(f"  Sample Vocabulary: {vocabulary[0]}")
    
    elif command == "stats":
        manager = ParquetDataManager()
        manager.print_stats()
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Valid commands: save, load, stats")
        sys.exit(1)
