#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HSK-Based Deck Generator
Creates a targeted deck based on HSK levels by:
1. Taking vocabulary words from specified HSK levels
2. Extracting all hanzi used in those words
3. Identifying radicals/components with productive scores
4. Building a complete deck with proper dependencies

This approach is more pedagogically sound than arbitrary frequency cutoffs.
"""

import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from pathlib import Path
from collections import Counter
from typing import Dict, List, Set
import pandas as pd
from pinyin_converter import numbered_to_accented

try:
    from hanzipy.decomposer import HanziDecomposer
    from hanzipy.dictionary import HanziDictionary
except ImportError:
    print("❌ Error: hanzipy is not installed")
    print("\nTo install hanzipy, run:")
    print("  pip install hanzipy")
    sys.exit(1)


def clean_surname_from_definition(definition: str) -> tuple[str, bool]:
    """
    Remove surname references from definition and return cleaned text with surname flag.
    
    Args:
        definition: The original definition text
        
    Returns:
        Tuple of (cleaned_definition, is_surname)
    """
    if not definition:
        return definition, False
    
    is_surname = False
    parts = []
    
    # Split by semicolons to handle multiple meanings
    for part in definition.split(';'):
        part = part.strip()
        
        # Check if this part is a surname reference
        if part.lower().startswith('surname '):
            is_surname = True
            continue  # Skip this part
        
        # Check for inline surname references like "China/Chinese/surname Zhong"
        if 'surname ' in part.lower():
            is_surname = True
            # Split by slash and filter out surname parts
            subparts = part.split('/')
            cleaned_subparts = []
            for subpart in subparts:
                subpart = subpart.strip()
                if not subpart.lower().startswith('surname '):
                    cleaned_subparts.append(subpart)
            if cleaned_subparts:
                parts.append('/'.join(cleaned_subparts))
        else:
            parts.append(part)
    
    # Join remaining parts
    cleaned = '; '.join(parts) if parts else ''
    
    # Clean up extra whitespace and trailing punctuation
    cleaned = cleaned.strip()
    if cleaned.endswith(';'):
        cleaned = cleaned[:-1].strip()
    
    return cleaned, is_surname


class HSKDeckBuilder:
    """Build a deck based on HSK levels with productive component analysis"""
    
    def __init__(self, hsk_levels: List[int] = [1, 2, 3], 
                 hsk_data_dir: str = "data/HSK-3.0"):
        """
        Initialize the HSK Deck Builder
        
        Args:
            hsk_levels: List of HSK levels to include (e.g., [1, 2, 3])
            hsk_data_dir: Path to HSK-3.0 data directory
        """
        self.hsk_levels = hsk_levels
        self.hsk_dir = Path(hsk_data_dir)
        self.frequency_dir = self.hsk_dir / "HSK List (Frequency)"
        
        # Initialize Hanzipy
        self.decomposer = HanziDecomposer()
        self.dictionary = HanziDictionary()
        
        # Data storage
        self.vocabulary = []
        self.hanzi_set = set()
        self.hanzi_data = {}
        self.components = {}
        self.component_productivity = Counter()
        
    def load_vocabulary(self) -> List[Dict]:
        """
        Load vocabulary words from specified HSK levels
        
        Returns:
            List of vocabulary dictionaries
        """
        print(f"📖 Loading vocabulary from HSK levels: {self.hsk_levels}")
        all_vocab = []
        
        for level in self.hsk_levels:
            file_path = self.frequency_dir / f"HSK {level}.txt"
            
            if not file_path.exists():
                print(f"⚠️  Warning: {file_path} not found")
                continue
            
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                words = [line.strip() for line in f if line.strip()]
            
            for position, word in enumerate(words, start=1):
                # Get pinyin and definition from dictionary
                try:
                    definitions = self.dictionary.definition_lookup(word)
                    
                    if definitions:
                        first_def = definitions[0]
                        pinyin = numbered_to_accented(first_def.get('pinyin', ''))
                        # Get all definitions, separated by semicolons
                        all_meanings = []
                        is_surname = False
                        for def_entry in definitions:
                            def_text = def_entry.get('definition', '')
                            if def_text:
                                all_meanings.append(def_text)
                        
                        # Clean surname references from meanings
                        combined_meaning = '; '.join(all_meanings) if all_meanings else ''
                        meaning, is_surname = clean_surname_from_definition(combined_meaning)
                    else:
                        pinyin = ''
                        meaning = ''
                        is_surname = False
                except (KeyError, Exception):
                    # Word not in dictionary - skip definitions
                    pinyin = ''
                    meaning = ''
                    is_surname = False
                
                vocab_entry = {
                    'word': word,
                    'hsk_level': level,
                    'frequency_position': position,
                    'pinyin': pinyin,
                    'meaning': meaning,
                    'is_surname': is_surname
                }
                all_vocab.append(vocab_entry)
            
            print(f"  ✓ HSK {level}: {len(words)} words")
        
        self.vocabulary = all_vocab
        print(f"✅ Loaded {len(all_vocab)} vocabulary words\n")
        return all_vocab
    
    def load_hsk_hanzi_levels(self) -> Dict[str, int]:
        """
        Load HSK Hanzi files to determine which HSK level each hanzi belongs to.
        
        Returns:
            Dictionary mapping hanzi to their HSK level
        """
        print("📖 Loading HSK Hanzi level mappings...")
        hanzi_to_hsk = {}
        hanzi_folder = self.hsk_dir / "HSK Hanzi"
        
        for level in self.hsk_levels:
            file_path = hanzi_folder / f"HSK {level}.txt"
            
            if not file_path.exists():
                print(f"  ⚠️  Warning: {file_path} not found")
                continue
            
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                hanzi_chars = [line.strip() for line in f if line.strip()]
            
            for char in hanzi_chars:
                if char not in hanzi_to_hsk:  # Only set if not already assigned (prefer lower HSK level)
                    hanzi_to_hsk[char] = level
            
            print(f"  ✓ HSK {level}: {len(hanzi_chars)} hanzi")
        
        print(f"✅ Loaded HSK levels for {len(hanzi_to_hsk)} hanzi\n")
        return hanzi_to_hsk
    
    def extract_hanzi_from_vocabulary(self) -> Set[str]:
        """
        Extract all unique hanzi characters used in the vocabulary
        
        Returns:
            Set of hanzi characters
        """
        print("🔍 Extracting hanzi from vocabulary...")
        hanzi_set = set()
        
        for vocab in self.vocabulary:
            word = vocab['word']
            for char in word:
                # Check if it's a Chinese character (basic CJK range)
                if '\u4e00' <= char <= '\u9fff':
                    hanzi_set.add(char)
        
        self.hanzi_set = hanzi_set
        print(f"✅ Found {len(hanzi_set)} unique hanzi characters\n")
        return hanzi_set
    
    def process_hanzi(self) -> Dict[str, Dict]:
        """
        Process each hanzi to get its data (definition, pinyin, components)
        
        Returns:
            Dictionary mapping hanzi to their data
        """
        print(f"⚙️  Processing {len(self.hanzi_set)} hanzi characters...")
        hanzi_data = {}
        processed = 0
        
        for char in sorted(self.hanzi_set):
            # Get definitions
            definitions = self.dictionary.definition_lookup(char)
            if not definitions:
                continue
            
            first_def = definitions[0]
            pinyin = numbered_to_accented(first_def.get('pinyin', ''))
            # Get all definitions, separated by semicolons
            all_meanings = []
            for def_entry in definitions:
                def_text = def_entry.get('definition', '')
                if def_text:
                    all_meanings.append(def_text)
            
            # Clean surname references from meanings
            combined_meaning = '; '.join(all_meanings) if all_meanings else ''
            meaning, is_surname = clean_surname_from_definition(combined_meaning)
            
            # Get decomposition (components/radicals)
            try:
                decomposition = self.decomposer.decompose(char, 2)
                components = []
                
                if decomposition and 'components' in decomposition:
                    for component in decomposition['components']:
                        if component and component != char:
                            components.append(component)
                            # Track component usage for productivity score
                            self.component_productivity[component] += 1
            except Exception:
                components = []
            
            # Get HSK level for this hanzi
            hsk_level = self.hanzi_to_hsk.get(char, '')
            
            hanzi_data[char] = {
                'hanzi': char,
                'pinyin': pinyin,
                'meaning': meaning,
                'components': components,
                'component_count': len(components),
                'hsk_level': hsk_level,
                'is_surname': is_surname
            }
            
            processed += 1
            if processed % 100 == 0:
                print(f"  Processed {processed}/{len(self.hanzi_set)} hanzi...")
        
        self.hanzi_data = hanzi_data
        print(f"✅ Processed {len(hanzi_data)} hanzi with definitions\n")
        return hanzi_data
    
    def calculate_component_productivity(self) -> Dict[str, Dict]:
        """
        Calculate productivity scores for components/radicals
        Productivity = how many different characters use this component
        
        Returns:
            Dictionary mapping components to their data and productivity scores
        """
        print("📊 Calculating component productivity scores...")
        
        # Get meanings for components
        component_data = {}
        for component, count in self.component_productivity.most_common():
            # Get meaning for component
            try:
                meaning = self.decomposer.get_radical_meaning(component)
                if not meaning or meaning == component:
                    meaning = f"Component {component}"
            except Exception:
                meaning = f"Component {component}"
            
            component_data[component] = {
                'component': component,
                'meaning': meaning,
                'productivity_score': count,
                'usage_count': count
            }
        
        self.components = component_data
        
        # Show top productive components
        print(f"✅ Found {len(component_data)} unique components\n")
        print("🏆 Top 20 Most Productive Components:")
        print("-" * 60)
        for component, data in list(component_data.items())[:20]:
            score = data['productivity_score']
            meaning = data['meaning'][:40]
            print(f"  {component:>2} | Score: {score:>3} | {meaning}")
        print()
        
        return component_data
    
    def export_data(self, output_dir: str = "data"):
        """Export all data to CSV and Parquet files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"💾 Exporting data for HSK levels {self.hsk_levels}...")
        
        # Export vocabulary
        if self.vocabulary:
            vocab_df = pd.DataFrame(self.vocabulary)
            vocab_csv = output_path / "vocabulary.csv"
            vocab_parquet = output_path / "vocabulary.parquet"
            vocab_df.to_csv(vocab_csv, index=False, encoding='utf-8')
            vocab_df.to_parquet(vocab_parquet, engine='pyarrow', compression='snappy', index=False)
            print(f"  ✓ Vocabulary: {len(vocab_df)} words → {vocab_csv.name}")
        
        # Export hanzi
        if self.hanzi_data:
            hanzi_list = []
            for char, data in self.hanzi_data.items():
                hsk_level = data.get('hsk_level', '')
                # Ensure hsk_level is int or None for parquet compatibility
                if hsk_level == '' or hsk_level is None:
                    hsk_level = None
                else:
                    hsk_level = int(hsk_level)
                
                hanzi_list.append({
                    'hanzi': data['hanzi'],
                    'pinyin': data['pinyin'],
                    'meaning': data['meaning'],
                    'components': '|'.join(data['components']),
                    'component_count': data['component_count'],
                    'hsk_level': hsk_level,
                    'is_surname': data.get('is_surname', False)
                })
            
            hanzi_df = pd.DataFrame(hanzi_list)
            # Convert hsk_level to Int64 (nullable integer type)
            hanzi_df['hsk_level'] = hanzi_df['hsk_level'].astype('Int64')
            hanzi_csv = output_path / "hanzi.csv"
            hanzi_parquet = output_path / "hanzi.parquet"
            hanzi_df.to_csv(hanzi_csv, index=False, encoding='utf-8')
            hanzi_df.to_parquet(hanzi_parquet, engine='pyarrow', compression='snappy', index=False)
            print(f"  ✓ Hanzi: {len(hanzi_df)} characters → {hanzi_csv.name}")
        
        # Export components (as radicals for consistency)
        if self.components:
            comp_df = pd.DataFrame(list(self.components.values()))
            comp_df = comp_df.sort_values('productivity_score', ascending=False)
            # Rename columns for consistency with original format
            # Drop the duplicate usage_count column and rename appropriately
            comp_df = comp_df[['component', 'meaning', 'productivity_score']].rename(columns={
                'component': 'radical',
                'productivity_score': 'usage_count'
            })
            radicals_csv = output_path / "radicals.csv"
            radicals_parquet = output_path / "radicals.parquet"
            comp_df.to_csv(radicals_csv, index=False, encoding='utf-8')
            comp_df.to_parquet(radicals_parquet, engine='pyarrow', compression='snappy', index=False)
            print(f"  ✓ Radicals: {len(comp_df)} components → {radicals_csv.name}")
        
        print("✅ All data exported successfully!\n")
    
    def print_statistics(self):
        """Print summary statistics"""
        print("=" * 70)
        print(f"HSK DECK BUILDER STATISTICS (Levels {self.hsk_levels})")
        print("=" * 70)
        print(f"\n📚 Vocabulary: {len(self.vocabulary)} words")
        print(f"🔤 Hanzi: {len(self.hanzi_data)} characters")
        print(f"🧩 Components: {len(self.components)} unique components")
        
        if self.vocabulary:
            print("\n📊 Vocabulary by HSK Level:")
            level_counts = Counter(v['hsk_level'] for v in self.vocabulary)
            for level in sorted(level_counts.keys()):
                count = level_counts[level]
                print(f"  HSK {level}: {count} words")
        
        if self.components:
            top_5 = sorted(self.components.items(), 
                          key=lambda x: x[1]['productivity_score'], 
                          reverse=True)[:5]
            print("\n🏆 Top 5 Most Productive Components:")
            for comp, data in top_5:
                print(f"  {comp} ({data['meaning'][:30]}): used in {data['productivity_score']} characters")
        
        print("=" * 70 + "\n")


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
