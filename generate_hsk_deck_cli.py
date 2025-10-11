#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI wrapper for HSK Deck Generation using the new package structure

This script maintains backward compatibility with the original generate_hsk_deck.py
"""

import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src.tian_hanzi.data_generator import HSKDeckBuilder


def main():
    """Main execution function"""
    # Build deck for HSK 1-3 (default)
    print("=" * 70)
    print("TIAN HANZI DECK GENERATOR - HSK 1-3 (Default)")
    print("=" * 70)
    print()
    
    builder = HSKDeckBuilder(hsk_levels=[1, 2, 3])
    
    # Step 1: Load vocabulary from HSK 1-3
    builder.load_vocabulary()
    
    # Step 2: Load HSK Hanzi level mappings
    builder.hanzi_to_hsk = builder.load_hsk_hanzi_levels()
    
    # Step 3: Extract hanzi from vocabulary
    builder.extract_hanzi_from_vocabulary()
    
    # Step 4: Process each hanzi (get definitions, components)
    builder.process_hanzi()
    
    # Step 5: Calculate component productivity scores
    builder.calculate_component_productivity()
    
    # Step 6: Export data
    builder.export_data()
    
    # Step 7: Print statistics
    builder.print_statistics()
    
    print("✅ HSK 1-3 Deck generation complete!")
    print()
    print("📁 Output files created:")
    print("  - vocabulary.csv/parquet")
    print("  - hanzi.csv/parquet")
    print("  - radicals.csv/parquet")


if __name__ == "__main__":
    main()
