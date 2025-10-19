#!/usr/bin/env python3
"""
Create HSK 1-3 Hanzi Deck Anki Package
=======================================
Loads HSK 1-3 data from CSV files and creates a complete Anki deck
with radicals, hanzi, and vocabulary cards.

Features:
- Level-based learning order (requires sort_hsk_by_dependencies.py first)
- Dynamic breakpoint analysis (shows optimal radical grouping)
- HSK-appropriate styling and card types
- Productivity scores for radicals
- Component breakdowns for hanzi
- Example sentences for vocabulary
"""

import random
import sys
import os
import io
import subprocess
from pathlib import Path

# Ensure the local package is importable when running from the repository root.
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / 'src'
if SRC_DIR.exists() and str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Windows console UTF-8 setup
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import genanki
    import pandas as pd
    from tian_hanzi.core.cards import create_ruby_text, format_components_with_meanings
    from tian_hanzi.core.deck_templates import (
        HANZI_MODEL_DEF,
        RADICAL_MODEL_DEF,
        VOCAB_MODEL_DEF,
        create_genanki_model,
    )
except ImportError as e:
    print(f"❌ Error: Required library not installed - {e}")
    print("\nTo install dependencies, run:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

# Card utility functions
def pinyin_to_numbered(pinyin: str) -> str:
    """
    Convert accented pinyin to numbered format for yoyo audio lookup.
    Example: 'nǐ' -> 'ni3', 'hǎo' -> 'hao3'
    """
    # Tone mark to number mapping
    tone_map = {
        'ā': ('a', '1'), 'á': ('a', '2'), 'ǎ': ('a', '3'), 'à': ('a', '4'),
        'ē': ('e', '1'), 'é': ('e', '2'), 'ě': ('e', '3'), 'è': ('e', '4'),
        'ī': ('i', '1'), 'í': ('i', '2'), 'ǐ': ('i', '3'), 'ì': ('i', '4'),
        'ō': ('o', '1'), 'ó': ('o', '2'), 'ǒ': ('o', '3'), 'ò': ('o', '4'),
        'ū': ('u', '1'), 'ú': ('u', '2'), 'ǔ': ('u', '3'), 'ù': ('u', '4'),
        'ǖ': ('v', '1'), 'ǘ': ('v', '2'), 'ǚ': ('v', '3'), 'ǜ': ('v', '4'),
        'ü': ('v', '5'),  # neutral tone ü
    }
    
    syllable = pinyin.lower().strip()
    tone = '5'  # default neutral tone
    
    # Find tone mark and convert
    for char in syllable:
        if char in tone_map:
            base, tone = tone_map[char]
            syllable = syllable.replace(char, base)
            break
    
    return f"{syllable}{tone}"


def find_audio_file(pinyin: str, char_or_word: str, audio_type: str = 'hanzi') -> str:
    """
    Find audio file prioritizing yoyo audio, falling back to specific audio.
    
    Args:
        pinyin: The pinyin (accented format like 'nǐ hǎo' for multi-syllable)
        char_or_word: The character or word (like '你' or '你好')
        audio_type: Either 'hanzi' or 'vocabulary'
    
    Returns:
        Filename(s) to use in [sound:...] tags, or empty string if not found
    """
    # For multi-syllable words, create multiple [sound:] tags
    if audio_type == 'vocabulary' and ' ' in pinyin:
        syllables = pinyin.split()
        sound_tags = []
        all_found = True
        
        for syllable in syllables:
            numbered = pinyin_to_numbered(syllable)
            yoyo_path = f"data/yoyo_audio/{numbered}.mp3"
            
            if os.path.exists(yoyo_path):
                sound_tags.append(f"[sound:{numbered}.mp3]")
            else:
                all_found = False
                break
        
        # If all syllables found in yoyo, return concatenated tags
        if all_found and sound_tags:
            return "".join(sound_tags)
        
        # Fall back to specific word audio
        specific_path = f"data/audio/vocabulary/{char_or_word}.mp3"
        if os.path.exists(specific_path):
            return f"[sound:{char_or_word}.mp3]"
        
        return ""
    
    # Single syllable - check yoyo audio first
    numbered_pinyin = pinyin_to_numbered(pinyin)
    yoyo_path = f"data/yoyo_audio/{numbered_pinyin}.mp3"
    
    if os.path.exists(yoyo_path):
        # Return just the filename (genanki flattens all media to root)
        return f"[sound:{numbered_pinyin}.mp3]"
    
    # Fall back to specific audio
    if audio_type == 'hanzi':
        specific_path = f"data/audio/hanzi/{char_or_word}.mp3"
        if os.path.exists(specific_path):
            return f"[sound:{char_or_word}.mp3]"
    elif audio_type == 'vocabulary':
        specific_path = f"data/audio/vocabulary/{char_or_word}.mp3"
        if os.path.exists(specific_path):
            return f"[sound:{char_or_word}.mp3]"
    
    return ""


def run_breakpoint_analysis():
    """Run breakpoint analysis and display results"""
    print("🔍 Running breakpoint analysis...")
    print("=" * 70)
    
    try:
        # Run the breakpoint analysis script
        result = subprocess.run(
            [sys.executable, 'scripts/analysis/analyze_level_breakpoints.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            # Parse key statistics from output
            output_lines = result.stdout.split('\n')
            
            for line in output_lines:
                if 'Total Levels:' in line or 'Total Radicals:' in line or 'Total Hanzi:' in line:
                    print(f"   {line.strip()}")
                elif 'Dynamic approach uses' in line:
                    print(f"   ✓ {line.strip()}")
            
            print("=" * 70)
            print()
            
            # Load the breakpoint analysis results
            if Path('data/breakpoint_analysis.csv').exists():
                breakpoints_df = pd.read_csv('data/breakpoint_analysis.csv')
                return breakpoints_df
            else:
                print("⚠️  Warning: Breakpoint analysis file not found, continuing with current data...")
                return None
        else:
            print("⚠️  Warning: Breakpoint analysis failed, continuing with current data...")
            print(f"Error: {result.stderr[:200]}")
            return None
            
    except Exception as e:
        print(f"⚠️  Warning: Could not run breakpoint analysis: {e}")
        print("Continuing with current data...")
        return None


# Run breakpoint analysis first
breakpoints_df = run_breakpoint_analysis()

# Load HSK data from CSV files
print("📂 Loading HSK 1-3 data from CSV files...")
try:
    radicals_df = pd.read_csv('data/radicals.csv')
    hanzi_df = pd.read_csv('data/hanzi.csv')
    vocab_df = pd.read_csv('data/vocabulary.csv')
    print(f"✓ Loaded {len(radicals_df)} radicals, {len(hanzi_df)} hanzi, {len(vocab_df)} vocabulary entries\n")
except Exception as e:
    print(f"\n❌ Error loading CSV files: {e}")
    print("\nMake sure to generate data files first:")
    print("  python generate_hsk_deck.py")
    sys.exit(1)

# Load radicals_tian.csv for better meanings and HSK breakdown
print("📂 Loading enhanced radical data from radicals_tian.csv...")
try:
    radicals_tian_df = pd.read_csv('data/radicals_tian.csv')
    print(f"✓ Loaded enhanced data for {len(radicals_tian_df)} radicals\n")
except Exception as e:
    print(f"⚠️  Warning: Could not load radicals_tian.csv: {e}")
    print("   Continuing with standard radical data\n")
    radicals_tian_df = None


def load_mnemonic_table(path: str, key_column: str) -> pd.DataFrame:
    """
    Load a mnemonic CSV by its key column, returning the last entry per key.
    If the file is missing or invalid, returns an empty DataFrame with the key column.
    """
    csv_path = Path(path)
    if not csv_path.exists():
        print(f"Mnemonic file not found: {path}. Continuing without it.")
        return pd.DataFrame(columns=[key_column])

    try:
        df = pd.read_csv(csv_path)
    except Exception as exc:
        print(f"Failed to load {path}: {exc}. Mnemonics will be left blank.")
        return pd.DataFrame(columns=[key_column])

    if key_column not in df.columns:
        print(f"Mnemonic file {path} is missing the '{key_column}' column. Skipping merge.")
        return pd.DataFrame(columns=[key_column])

    return df.drop_duplicates(subset=[key_column], keep='last')


def apply_dynamic_levels(radicals_df, hanzi_df, vocab_df, breakpoints_df):
    """
    Apply dynamic level assignments from breakpoint analysis.
    
    Args:
        radicals_df: DataFrame with radical data
        hanzi_df: DataFrame with hanzi data
        vocab_df: DataFrame with vocabulary data
        breakpoints_df: DataFrame with breakpoint analysis results
    
    Returns:
        Tuple of (radicals_df, hanzi_df, vocab_df) with updated levels
    """
    if breakpoints_df is None:
        print("⚠️  Using existing level assignments (no breakpoint data available)")
        return radicals_df, hanzi_df, vocab_df
    
    print("🔄 Applying dynamic level assignments from breakpoint analysis...")
    
    # Create a copy to avoid modifying original data
    radicals_df = radicals_df.copy()
    hanzi_df = hanzi_df.copy()
    vocab_df = vocab_df.copy()
    
    # Build radical to level mapping
    radical_to_level = {}
    for _, bp_row in breakpoints_df.iterrows():
        level = bp_row['level']
        radicals_str = bp_row['radicals']
        if pd.notna(radicals_str):
            radicals_list = radicals_str.split('|')
            for radical in radicals_list:
                radical = radical.strip()
                if radical and radical != 'No glyph available':
                    radical_to_level[radical] = level
    
    # Apply levels to radicals
    print(f"   → Mapping {len(radical_to_level)} radicals to {len(set(radical_to_level.values()))} levels...")
    radicals_df['level'] = radicals_df['radical'].map(radical_to_level)
    
    # For any radicals without a level, assign to last level
    max_level = breakpoints_df['level'].max() if len(breakpoints_df) > 0 else 1
    unmapped_count = radicals_df['level'].isna().sum()
    if unmapped_count > 0:
        print(f"   → Assigning {unmapped_count} unmapped radicals to level {max_level}")
    radicals_df['level'] = radicals_df['level'].fillna(max_level)
    
    # Apply levels to hanzi based on their components
    def calculate_hanzi_level(row):
        """Calculate hanzi level as max(component levels) + 1
        
        Special case: If component_count is 0, the hanzi IS a radical itself.
        It should unlock at the SAME level as when that radical is introduced,
        not default to level 1.
        """
        hanzi_char = row.get('hanzi', row.get('character', ''))
        components_str = row['components']
        component_count = row.get('component_count', 0)
        
        # If no components, the hanzi IS a radical itself
        # Find when this radical is introduced and use that level
        if component_count == 0 or pd.isna(components_str) or not components_str:
            # Look up this hanzi in the radical_to_level mapping
            if hanzi_char in radical_to_level:
                return radical_to_level[hanzi_char]
            else:
                # If not in radical list, assign to last level
                return max_level
        
        # For hanzi with components, calculate based on component levels
        components = [c.strip() for c in str(components_str).split('|')]
        component_levels = []
        
        for comp in components:
            if comp and comp in radical_to_level:
                component_levels.append(radical_to_level[comp])
        
        if component_levels:
            # Assign to same level as the highest component (not +1)
            # Hanzi unlock when all their components are available
            return max(component_levels)
        else:
            # If components exist but aren't in our radical list, assign to max level
            return max_level
    
    hanzi_df['level'] = hanzi_df.apply(calculate_hanzi_level, axis=1)
    
    # Cap hanzi levels at max_level + 1 (since they're components + 1)
    hanzi_df['level'] = hanzi_df['level'].clip(upper=max_level + 1)
    
    # Apply levels to vocabulary based on their characters
    def calculate_vocab_level(word):
        """Calculate vocabulary level as max(hanzi tian_levels)"""
        if pd.isna(word) or not word:
            return max_level + 2
        
        hanzi_levels = []
        for char in str(word):
            if char in hanzi_df['hanzi'].values:
                char_level = hanzi_df[hanzi_df['hanzi'] == char]['level'].iloc[0]
                hanzi_levels.append(char_level)
        
        if hanzi_levels:
            # Vocabulary unlocks at the same level as its most advanced hanzi
            return max(hanzi_levels)
        else:
            # If no hanzi found (shouldn't happen), assign to max level
            return max_level + 2
    
    vocab_df['level'] = vocab_df['word'].apply(calculate_vocab_level)
    
    # Cap vocab levels appropriately
    vocab_df['level'] = vocab_df['level'].clip(upper=max_level + 10)
    
    # Print statistics
    print(f"   ✓ Assigned {len(radicals_df['level'].unique())} radical levels (1-{int(radicals_df['level'].max())})")
    print(f"   ✓ Assigned {len(hanzi_df['level'].unique())} hanzi levels (1-{int(hanzi_df['level'].max())})")
    print(f"   ✓ Assigned {len(vocab_df['level'].unique())} vocabulary levels (1-{int(vocab_df['level'].max())})")
    print()
    
    return radicals_df, hanzi_df, vocab_df


# Apply dynamic levels if breakpoint analysis was successful
radicals_df, hanzi_df, vocab_df = apply_dynamic_levels(
    radicals_df, hanzi_df, vocab_df, breakpoints_df
)

# Merge Tian meanings BEFORE saving (so they're reflected in the CSV outputs)
if radicals_tian_df is not None:
    print("🔄 Merging enhanced radical meanings from radicals_tian.csv...")
    # Keep only the columns we need from tian_df
    tian_cols = ['radical', 'meaning']
    tian_merge = radicals_tian_df[tian_cols].copy()
    
    # Merge with radicals_df, preferring Tian meanings
    radicals_df = radicals_df.merge(
        tian_merge,
        on='radical',
        how='left',
        suffixes=('_old', '_tian')
    )
    
    # Use Tian meaning if available, otherwise fall back to original
    if 'meaning_tian' in radicals_df.columns:
        radicals_df['meaning'] = radicals_df['meaning_tian'].fillna(radicals_df.get('meaning_old', radicals_df.get('meaning', '')))
        # Clean up temporary columns
        radicals_df = radicals_df.drop(columns=['meaning_old', 'meaning_tian'], errors='ignore')
    
    print(f"   ✓ Enhanced {len(radicals_df)} radicals with Tian meanings\n")

# Save the updated data with dynamic levels and reordered columns
if breakpoints_df is not None:
    print("💾 Saving updated data with dynamic levels...")
    
    # Drop 'tian_level' if it already exists (from previous runs)
    if 'tian_level' in radicals_df.columns:
        radicals_df = radicals_df.drop(columns=['tian_level'])
    if 'tian_level' in hanzi_df.columns:
        hanzi_df = hanzi_df.drop(columns=['tian_level'])
    if 'tian_level' in vocab_df.columns:
        vocab_df = vocab_df.drop(columns=['tian_level'])
    
    # Sort dataframes FIRST (using 'level' column), then rename
    # Radicals: Sort by level (ascending), then productivity_score (descending - HSK1-weighted score)
    radicals_df = radicals_df.sort_values(['level', 'productivity_score'], ascending=[True, False])
    
    # Hanzi: Sort by level, hsk_level, component_count (simpler first)
    hanzi_df = hanzi_df.sort_values(['level', 'hsk_level', 'component_count'], ascending=[True, True, True])
    
    # Vocabulary: Sort by level, hsk_level, frequency_position (lower = more frequent)
    vocab_df = vocab_df.sort_values(['level', 'hsk_level', 'frequency_position'], ascending=[True, True, True])
    
    # NOW rename 'level' to 'tian_level' for clarity
    radicals_df = radicals_df.rename(columns={'level': 'tian_level'})
    hanzi_df = hanzi_df.rename(columns={'level': 'tian_level'})
    vocab_df = vocab_df.rename(columns={'level': 'tian_level'})
    
    # Convert tian_level to integers (no decimals)
    radicals_df['tian_level'] = radicals_df['tian_level'].astype(int)
    hanzi_df['tian_level'] = hanzi_df['tian_level'].astype(int)
    vocab_df['tian_level'] = vocab_df['tian_level'].astype(int)
    
    # Reorder columns: tian_level first, then other important columns
    # Radicals: tian_level, radical, meaning, productivity_score, usage_count, usage_hsk1, usage_hsk2, usage_hsk3, stroke_count
    radical_cols = ['tian_level', 'radical', 'meaning', 'productivity_score', 'usage_count', 'usage_hsk1', 'usage_hsk2', 'usage_hsk3', 'stroke_count']
    radicals_df = radicals_df[radical_cols]
    
    # Hanzi: tian_level, hsk_level, hanzi, pinyin, meaning, components, component_count, stroke_count, is_surname
    hanzi_cols = ['tian_level', 'hsk_level', 'hanzi', 'pinyin', 'meaning', 'components', 'component_count', 'stroke_count', 'is_surname']
    hanzi_df = hanzi_df[hanzi_cols]
    
    # Vocabulary: tian_level, hsk_level, frequency_position, word, pinyin, meaning, stroke_count, is_surname
    # Note: 'description' column will be added later from vocabulary_mnemonic.csv
    vocab_cols = ['tian_level', 'hsk_level', 'frequency_position', 'word', 'pinyin', 'meaning', 'stroke_count', 'is_surname']
    # Only include description if it exists
    if 'description' in vocab_df.columns:
        vocab_cols.insert(6, 'description')
    vocab_df = vocab_df[vocab_cols]
    
    
    # Save CSV files
    radicals_df.to_csv('data/radicals.csv', index=False, encoding='utf-8-sig')
    hanzi_df.to_csv('data/hanzi.csv', index=False, encoding='utf-8-sig')
    vocab_df.to_csv('data/vocabulary.csv', index=False, encoding='utf-8-sig')
    
    print("   ✓ Saved updated CSV files\n")

# Merge mnemonic CSV data so deck fields use generated mnemonics
radical_mn_df = load_mnemonic_table('data/radicals_mnemonic.csv', 'radical')
if not radical_mn_df.empty:
    mn_col = 'meaning_mnemonic' if 'meaning_mnemonic' in radical_mn_df.columns else 'openai_meaning_mnemonic'
    if mn_col in radical_mn_df.columns:
        radical_merge = radical_mn_df[['radical', mn_col]].rename(columns={mn_col: 'meaning_mnemonic'})
        radicals_df = radicals_df.merge(radical_merge, on='radical', how='left')
if 'meaning_mnemonic' not in radicals_df.columns:
    radicals_df['meaning_mnemonic'] = ''
else:
    radicals_df['meaning_mnemonic'] = radicals_df['meaning_mnemonic'].fillna('')

hanzi_mn_df = load_mnemonic_table('data/hanzi_mnemonic.csv', 'hanzi')
if not hanzi_mn_df.empty:
    hanzi_merge = hanzi_mn_df.copy()
    if 'meaning' in hanzi_merge.columns:
        hanzi_merge = hanzi_merge.rename(columns={'meaning': 'mnemonic_meaning'})
    hanzi_cols = ['hanzi']
    for col in ('mnemonic_meaning', 'meaning_mnemonic', 'reading_mnemonic'):
        if col in hanzi_merge.columns:
            hanzi_cols.append(col)
    if len(hanzi_cols) > 1:
        hanzi_df = hanzi_df.merge(hanzi_merge[hanzi_cols], on='hanzi', how='left')
for col in ('meaning_mnemonic', 'reading_mnemonic'):
    if col not in hanzi_df.columns:
        hanzi_df[col] = ''
    else:
        hanzi_df[col] = hanzi_df[col].fillna('')
if 'mnemonic_meaning' in hanzi_df.columns:
    hanzi_df['meaning'] = hanzi_df['mnemonic_meaning'].fillna(hanzi_df['meaning'])
    hanzi_df = hanzi_df.drop(columns=['mnemonic_meaning'])
hanzi_df['meaning'] = hanzi_df['meaning'].fillna('')

vocabulary_mn_df = load_mnemonic_table('data/vocabulary_mnemonic.csv', 'word')
if not vocabulary_mn_df.empty:
    print("🔄 Merging vocabulary mnemonics from vocabulary_mnemonic.csv...")
    print(f"   Loaded {len(vocabulary_mn_df)} vocabulary entries with columns: {list(vocabulary_mn_df.columns)}")
    
    vocabulary_merge = vocabulary_mn_df.copy()
    
    # Handle both old column names (openai_*) and new column names (direct)
    backward_map = {
        'openai_meaning_mnemonic': 'meaning_mnemonic',
        'openai_usage_mnemonic': 'description_mnemonic',
    }
    vocabulary_merge = vocabulary_merge.rename(
        columns={old: new for old, new in backward_map.items() if old in vocabulary_merge.columns}
    )

    merge_cols = ['word']
    
    # If CSV has 'meaning' column, use it (rename to avoid collision)
    if 'meaning' in vocabulary_merge.columns:
        vocabulary_merge = vocabulary_merge.rename(columns={'meaning': 'meaning_simple'})
        merge_cols.append('meaning_simple')
    elif 'meaning_mnemonic' in vocabulary_merge.columns:
        vocabulary_merge = vocabulary_merge.rename(columns={'meaning_mnemonic': 'meaning_simple'})
        merge_cols.append('meaning_simple')
    
    # If CSV has 'description' column, use it directly
    if 'description' in vocabulary_merge.columns:
        merge_cols.append('description')
        print("   ✓ Found 'description' column")
    elif 'description_mnemonic' in vocabulary_merge.columns:
        vocabulary_merge = vocabulary_merge.rename(columns={'description_mnemonic': 'description'})
        merge_cols.append('description')
        print("   ✓ Found 'description_mnemonic' column (renamed to 'description')")
    
    # If CSV has 'hanzi_breakdown' column, use it
    if 'hanzi_breakdown' in vocabulary_merge.columns:
        merge_cols.append('hanzi_breakdown')
        print("   ✓ Found 'hanzi_breakdown' column")

    print(f"   Merging columns: {merge_cols}")
    
    if len(merge_cols) > 1:
        vocab_df = vocab_df.merge(vocabulary_merge[merge_cols], on='word', how='left')
        print("   ✓ Merged vocabulary data")

        # Debug: Check first few rows
        sample_word = vocab_df.iloc[0]['word']
        sample_desc = vocab_df.iloc[0].get('description', 'NOT FOUND')
        sample_breakdown = vocab_df.iloc[0].get('hanzi_breakdown', 'NOT FOUND')
        print(f"   Debug sample (first word '{sample_word}'):")
        print(f"      description: {sample_desc[:50] if sample_desc != 'NOT FOUND' else 'NOT FOUND'}...")
        print(f"      hanzi_breakdown: {sample_breakdown}")

if 'meaning_simple' in vocab_df.columns:
    vocab_df['meaning'] = vocab_df['meaning_simple'].fillna(vocab_df['meaning'])
    vocab_df = vocab_df.drop(columns=['meaning_simple'])

if 'description' not in vocab_df.columns:
    vocab_df['description'] = ''
else:
    vocab_df['description'] = vocab_df['description'].fillna('')

if 'tian_level' not in vocab_df.columns:
    base_levels = vocab_df['level'] if 'level' in vocab_df.columns else 0
    vocab_df['tian_level'] = pd.to_numeric(base_levels, errors='coerce').fillna(0).astype(int)
else:
    vocab_df['tian_level'] = pd.to_numeric(vocab_df['tian_level'], errors='coerce').fillna(0).astype(int)

# Define unique model IDs for each card type
RADICAL_MODEL_ID = random.randrange(1 << 30, 1 << 31)
HANZI_MODEL_ID = random.randrange(1 << 30, 1 << 31)
VOCAB_MODEL_ID = random.randrange(1 << 30, 1 << 31)

# Define unique deck IDs (parent and seven subdecks)
PARENT_DECK_ID = random.randrange(1 << 30, 1 << 31)
RADICAL_DECK_ID = random.randrange(1 << 30, 1 << 31)
HANZI_HSK1_DECK_ID = random.randrange(1 << 30, 1 << 31)
HANZI_HSK2_DECK_ID = random.randrange(1 << 30, 1 << 31)
HANZI_HSK3_DECK_ID = random.randrange(1 << 30, 1 << 31)
VOCAB_HSK1_DECK_ID = random.randrange(1 << 30, 1 << 31)
VOCAB_HSK2_DECK_ID = random.randrange(1 << 30, 1 << 31)
VOCAB_HSK3_DECK_ID = random.randrange(1 << 30, 1 << 31)

# Card models (shared templates defined in tian_hanzi.core.deck_templates)
radical_model = create_genanki_model(RADICAL_MODEL_ID, RADICAL_MODEL_DEF)
hanzi_model = create_genanki_model(HANZI_MODEL_ID, HANZI_MODEL_DEF)
vocab_model = create_genanki_model(VOCAB_MODEL_ID, VOCAB_MODEL_DEF)

# Create parent deck and seven subdecks
radical_deck = genanki.Deck(
    RADICAL_DECK_ID,
    '天 T.I.A.N. Simplified Mandarin::1. Radicals'
)

# Hanzi subdecks by HSK level
hanzi_hsk1_deck = genanki.Deck(
    HANZI_HSK1_DECK_ID,
    '天 T.I.A.N. Simplified Mandarin::2. Hanzi::HSK 1'
)

hanzi_hsk2_deck = genanki.Deck(
    HANZI_HSK2_DECK_ID,
    '天 T.I.A.N. Simplified Mandarin::2. Hanzi::HSK 2'
)

hanzi_hsk3_deck = genanki.Deck(
    HANZI_HSK3_DECK_ID,
    '天 T.I.A.N. Simplified Mandarin::2. Hanzi::HSK 3'
)

# Vocabulary subdecks by HSK level
vocab_hsk1_deck = genanki.Deck(
    VOCAB_HSK1_DECK_ID,
    '天 T.I.A.N. Simplified Mandarin::3. Vocabulary::HSK 1'
)

vocab_hsk2_deck = genanki.Deck(
    VOCAB_HSK2_DECK_ID,
    '天 T.I.A.N. Simplified Mandarin::3. Vocabulary::HSK 2'
)

vocab_hsk3_deck = genanki.Deck(
    VOCAB_HSK3_DECK_ID,
    '天 T.I.A.N. Simplified Mandarin::3. Vocabulary::HSK 3'
)

print("🎴 Creating Anki cards...")

# Ensure HSK breakdown columns exist (meanings were already merged earlier)
# Check if HSK count columns are missing and add them if needed
if radicals_tian_df is not None:
    for col in ['usage_hsk1', 'usage_hsk2', 'usage_hsk3']:
        if col not in radicals_df.columns:
            print(f"🔄 Adding {col} column from radicals_tian.csv...")
            # Merge just the HSK columns
            tian_hsk = radicals_tian_df[['radical', col]].copy()
            radicals_df = radicals_df.merge(tian_hsk, on='radical', how='left')
            radicals_df[col] = radicals_df[col].fillna(0).astype(int)
else:
    # If no Tian data, create default HSK count columns
    for col in ['usage_hsk1', 'usage_hsk2', 'usage_hsk3']:
        if col not in radicals_df.columns:
            radicals_df[col] = 0

# Add radical cards
print(f"🔷 Adding {len(radicals_df)} radical cards...")
for idx, row in radicals_df.iterrows():
    hsk1 = int(row.get('usage_hsk1', 0))
    hsk2 = int(row.get('usage_hsk2', 0))
    hsk3 = int(row.get('usage_hsk3', 0))
    
    note = genanki.Note(
        model=radical_model,
        fields=[
            str(row['radical']),
            str(row['meaning']),
            str(int(row['usage_count'])),
            str(hsk1),
            str(hsk2),
            str(hsk3),
            str(int(row['tian_level'])),
        ],
        tags=['radical', 'hsk1-3', f'tian-{int(row["tian_level"])}']
    )
    radical_deck.add_note(note)

print(f"   ✓ Added {len(radicals_df)} radical cards")

# Add hanzi cards to appropriate HSK subdeck
print(f"\n🔤 Adding {len(hanzi_df)} hanzi cards...")
hanzi_counts = {'hsk1': 0, 'hsk2': 0, 'hsk3': 0, 'unknown': 0}

for idx, row in hanzi_df.iterrows():
    # Use correct column names: 'hanzi' not 'character', 'components' not 'radicals'
    char = row.get('hanzi', row.get('character', ''))
    components_str = row.get('components', row.get('radicals', ''))
    
    # Format components with their meanings
    formatted_components = format_components_with_meanings(components_str, radicals_df)
    
    # Handle potential NaN values for hsk_level
    hsk_level = row.get('hsk_level', '')
    if pd.notna(hsk_level):
        hsk_level_int = int(hsk_level)
        hsk_level_str = str(hsk_level_int)
        hsk_tag = f'hsk{hsk_level_int}'
        
        # Select the appropriate deck
        if hsk_level_int == 1:
            target_deck = hanzi_hsk1_deck
            hanzi_counts['hsk1'] += 1
        elif hsk_level_int == 2:
            target_deck = hanzi_hsk2_deck
            hanzi_counts['hsk2'] += 1
        elif hsk_level_int == 3:
            target_deck = hanzi_hsk3_deck
            hanzi_counts['hsk3'] += 1
        else:
            target_deck = hanzi_hsk1_deck  # Default to HSK1
            hanzi_counts['unknown'] += 1
    else:
        hsk_level_str = ''
        hsk_tag = 'hsk-unknown'
        target_deck = hanzi_hsk1_deck  # Default to HSK1
        hanzi_counts['unknown'] += 1
    
    # Generate audio field using yoyo audio (prioritized) or specific hanzi audio (fallback)
    audio_field = find_audio_file(str(row['pinyin']), char, 'hanzi')
    
    note = genanki.Note(
        model=hanzi_model,
        fields=[
            str(char),
            str(row['meaning']),
            str(row['pinyin']),
            formatted_components,
            str(row.get('meaning_mnemonic', '') or ''),
            str(row.get('reading_mnemonic', '') or ''),
            hsk_level_str,
            str(int(row['tian_level'])),
            audio_field,
        ],
        tags=['hanzi', hsk_tag, f'tian-{int(row["tian_level"])}']
    )
    target_deck.add_note(note)

print(f"   ✓ Added {len(hanzi_df)} hanzi cards:")
print(f"      • HSK 1: {hanzi_counts['hsk1']} cards")
print(f"      • HSK 2: {hanzi_counts['hsk2']} cards")
print(f"      • HSK 3: {hanzi_counts['hsk3']} cards")

# Add vocabulary cards to appropriate HSK subdeck
print(f"\n📚 Adding {len(vocab_df)} vocabulary cards...")
vocab_counts = {'hsk1': 0, 'hsk2': 0, 'hsk3': 0}

for idx, row in vocab_df.iterrows():
    word = str(row['word'])
    pinyin = str(row['pinyin'])
    ruby_text = create_ruby_text(word, pinyin)
    
    # Get hanzi_breakdown from CSV, fallback to space-separated characters
    hanzi_breakdown = str(row.get('hanzi_breakdown', ''))
    if not hanzi_breakdown or hanzi_breakdown == 'nan':
        hanzi_breakdown = ' '.join(list(word))
    
    # Get description from CSV
    description = str(row.get('description', ''))
    if description == 'nan':
        description = ''
    
    hsk_level = int(row['hsk_level'])
    
    # Select the appropriate deck
    if hsk_level == 1:
        target_deck = vocab_hsk1_deck
        vocab_counts['hsk1'] += 1
    elif hsk_level == 2:
        target_deck = vocab_hsk2_deck
        vocab_counts['hsk2'] += 1
    elif hsk_level == 3:
        target_deck = vocab_hsk3_deck
        vocab_counts['hsk3'] += 1
    else:
        target_deck = vocab_hsk1_deck  # Default to HSK1
        vocab_counts['hsk1'] += 1
    
    # Generate audio field using yoyo audio (prioritized) or specific vocab audio (fallback)
    audio_field = find_audio_file(pinyin, word, 'vocabulary')
    
    note = genanki.Note(
        model=vocab_model,
        fields=[
            word,
            str(row['meaning']),
            pinyin,
            ruby_text,
            hanzi_breakdown,
            description,
            str(hsk_level),
            str(int(row['tian_level'])),
            audio_field,
        ],
        tags=['vocabulary', f'hsk{hsk_level}', f'tian-{int(row["tian_level"])}']
    )
    target_deck.add_note(note)

print(f"   ✓ Added {len(vocab_df)} vocabulary cards:")
print(f"      • HSK 1: {vocab_counts['hsk1']} cards")
print(f"      • HSK 2: {vocab_counts['hsk2']} cards")
print(f"      • HSK 3: {vocab_counts['hsk3']} cards")

# Create output directory if it doesn't exist
os.makedirs('anki_deck', exist_ok=True)

# Collect audio files for media
print("\n🔊 Collecting audio files...")
media_files = []
yoyo_used = set()
specific_used = set()

# Collect hanzi audio files (prioritize yoyo, fallback to specific)
hanzi_audio_dir = 'data/audio/hanzi'
yoyo_audio_dir = 'data/yoyo_audio'

for idx, row in hanzi_df.iterrows():
    char = row.get('hanzi', row.get('character', ''))
    pinyin = str(row['pinyin'])
    
    # Try yoyo audio first
    numbered_pinyin = pinyin_to_numbered(pinyin)
    yoyo_path = os.path.join(yoyo_audio_dir, f"{numbered_pinyin}.mp3")
    
    if os.path.exists(yoyo_path) and yoyo_path not in yoyo_used:
        media_files.append(yoyo_path)
        yoyo_used.add(yoyo_path)
    else:
        # Fall back to specific hanzi audio
        specific_path = os.path.join(hanzi_audio_dir, f"{char}.mp3")
        if os.path.exists(specific_path):
            media_files.append(specific_path)
            specific_used.add(specific_path)

# Collect vocabulary audio files (prioritize yoyo syllables, fallback to specific)
vocab_audio_dir = 'data/audio/vocabulary'

for idx, row in vocab_df.iterrows():
    word = str(row['word'])
    pinyin = str(row['pinyin'])
    
    # For multi-syllable words, collect each syllable's yoyo audio
    if ' ' in pinyin:
        syllables = pinyin.split()
        all_syllables_found = True
        
        for syllable in syllables:
            numbered = pinyin_to_numbered(syllable)
            yoyo_path = os.path.join(yoyo_audio_dir, f"{numbered}.mp3")
            
            if os.path.exists(yoyo_path):
                if yoyo_path not in yoyo_used:
                    media_files.append(yoyo_path)
                    yoyo_used.add(yoyo_path)
            else:
                all_syllables_found = False
                break
        
        # If not all syllables found in yoyo, fall back to specific word audio
        if not all_syllables_found:
            specific_path = os.path.join(vocab_audio_dir, f"{word}.mp3")
            if os.path.exists(specific_path):
                media_files.append(specific_path)
                specific_used.add(specific_path)
    else:
        # Single syllable - try yoyo first
        numbered_pinyin = pinyin_to_numbered(pinyin)
        yoyo_path = os.path.join(yoyo_audio_dir, f"{numbered_pinyin}.mp3")
        
        if os.path.exists(yoyo_path) and yoyo_path not in yoyo_used:
            media_files.append(yoyo_path)
            yoyo_used.add(yoyo_path)
        else:
            # Fall back to specific vocab audio
            specific_path = os.path.join(vocab_audio_dir, f"{word}.mp3")
            if os.path.exists(specific_path):
                media_files.append(specific_path)
                specific_used.add(specific_path)

print(f"   ✓ Found {len(media_files)} audio files:")
print(f"      • {len(yoyo_used)} yoyo syllable audio")
print(f"      • {len(specific_used)} specific character/word audio")

# Save the deck package with all three subdecks
output_file = 'anki_deck/HSK_1-3_Hanzi_Deck.apkg'
print(f"\n💾 Saving Anki deck to {output_file}...")

try:
    # Package all seven subdecks together
    all_decks = [
        radical_deck,
        hanzi_hsk1_deck, hanzi_hsk2_deck, hanzi_hsk3_deck,
        vocab_hsk1_deck, vocab_hsk2_deck, vocab_hsk3_deck
    ]
    genanki.Package(all_decks, media_files=media_files).write_to_file(output_file)
    print("   ✓ Deck saved successfully!")
    
    total_cards = len(radicals_df) + len(hanzi_df) + len(vocab_df)
    print(f"\n{'='*60}")
    print(f"✅ SUCCESS! Created Anki deck with {total_cards} cards:")
    print("   📦 天 T.I.A.N. Simplified Mandarin (parent)")
    print(f"      ├── 1. Radicals: {len(radicals_df)} cards")
    print("      ├── 2. Hanzi:")
    print(f"      │   ├── HSK 1: {hanzi_counts['hsk1']} cards")
    print(f"      │   ├── HSK 2: {hanzi_counts['hsk2']} cards")
    print(f"      │   └── HSK 3: {hanzi_counts['hsk3']} cards")
    print("      └── 3. Vocabulary:")
    print(f"          ├── HSK 1: {vocab_counts['hsk1']} cards")
    print(f"          ├── HSK 2: {vocab_counts['hsk2']} cards")
    print(f"          └── HSK 3: {vocab_counts['hsk3']} cards")
    print(f"{'='*60}")
    print(f"\n📦 Import {output_file} into Anki to start learning!")
    
    if 'level' in radicals_df.columns:
        max_level = max(
            radicals_df['level'].max(),
            hanzi_df.get('level', pd.Series([0])).max(),
            vocab_df.get('level', pd.Series([0])).max()
        )
        print(f"\n🎯 Cards are organized into {int(max_level)} dependency-based levels")
        print("   Use custom study or filter by level tags in Anki!")
    
except Exception as e:
    print(f"\n❌ Error creating deck: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
