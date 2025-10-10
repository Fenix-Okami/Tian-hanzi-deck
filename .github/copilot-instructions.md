# Copilot Instructions for Tian Hanzi Deck

## Environment Setup

**ALWAYS use the virtual environment in this repository:**
- Virtual environment location: `venv/` (in repo root)
- Activation (bash): `source venv/Scripts/activate` or `source venv/bin/activate`
- Activation (PowerShell): `.\venv\Scripts\Activate.ps1`
- Python version: 3.11.0

**Before running any Python commands:**
1. Activate the venv first
2. Check if packages are installed with `pip list`
3. Install missing packages with `pip install -r requirements.txt`

## Project Overview

**Tian Hanzi Deck** is a WaniKani-inspired Anki deck generator for learning Chinese characters.

### Core Concept
Uses **HSK 1-3** vocabulary as the foundation:
1. Extract actual vocabulary from HSK lists (2,227 words)
2. Identify unique hanzi characters used in those words (899 chars)
3. Find productive radicals/components (233 components)
4. Sort by dependencies (learn components before characters)

### Why HSK-based?
- ✅ 40% fewer characters than arbitrary frequency (899 vs 1500)
- ✅ 36% more vocabulary (2,227 vs 1,643)
- ✅ Direct HSK exam alignment
- ✅ Scientific component productivity scoring

## Data Structure

### Input Data
- `data/HSK-3.0/` - Source HSK word lists (from krmanik/HSK-3.0 repo)

### Generated Data (Clean naming, no prefixes)
- `data/vocabulary.csv/parquet` - 2,227 HSK 1-3 words
  - Columns: `word`, `hsk_level`, `frequency_position`, `pinyin`, `meaning`
- `data/hanzi.csv/parquet` - 899 characters
  - Columns: `hanzi`, `pinyin`, `meaning`, `components`, `component_count`
- `data/radicals.csv/parquet` - 233 productive components
  - Columns: `radical`, `meaning`, `usage_count`

**Important:** Column names differ from old V1 approach:
- Use `hanzi` not `character`
- Use `components` not `radicals`
- Use `word` not `vocabulary`

### Output
- `anki_deck/HSK_1-3_Hanzi_Deck.apkg` - Ready-to-import Anki deck with 3 subdecks

## Pipeline (3 Steps)

### Step 1: Generate Data
```bash
python generate_hsk_deck.py
```
**What it does:**
- Reads HSK 1-3 word lists from `data/HSK-3.0/HSK List (Frequency)/`
- Extracts all unique hanzi characters from vocabulary
- Analyzes component usage to find productive radicals
- Exports CSV and Parquet files

**Output:** 3 data files (vocabulary, hanzi, radicals)

### Step 2: Sort by Dependencies
```bash
python sort_hsk_by_dependencies.py
```
**What it does:**
- Assigns radicals to levels (5 per level)
- Assigns hanzi to levels (only after their radicals are learned)
- Assigns vocabulary to levels (only after their hanzi are learned)
- Adds `level` column to all data files

**Output:** Same files with dependency levels added

### Step 3: Create Anki Deck
```bash
python create_hsk_deck.py
```
**What it does:**
- Creates 3 subdecks:
  - `1. Radicals` (brown theme, productivity scores)
  - `2. Hanzi` (green theme, component breakdowns)
  - `3. Vocabulary` (blue theme, examples)
- Exports as `.apkg` file

**Output:** `anki_deck/HSK_1-3_Hanzi_Deck.apkg`

## Script Organization

### Core HSK Pipeline (Use these!)
- `generate_hsk_deck.py` - Generate HSK 1-3 data
- `sort_hsk_by_dependencies.py` - Sort by dependencies
- `create_hsk_deck.py` - Create Anki deck with subdecks
- `run_hsk_pipeline.sh` - Run all 3 steps automatically

### Utilities
- `pinyin_converter.py` - Convert numbered pinyin (ni3) to accented (nǐ)
- `parquet_utils.py` - Data file utilities
- `create_samples.py` - Create sample CSVs and HTML card previews

### Analysis Tools
- `analyze_hsk_components.py` - Component productivity analysis
- `show_levels.py` - Display level distribution
- `verify_sorting.py` - Verify dependencies are correct

### Optional (All HSK Levels 1-9)
- `hsk_scorer.py` - Score all HSK levels
- `analyze_hsk_scores.py` - Score distribution

### Legacy V1 (Don't use - frequency-based approach)
- `generate_tian_v1_fast.py` - Old generator (1500 chars)
- `sort_by_dependencies.py` - Old dependency sorter
- `create_deck_from_parquet.py` - Old deck creator

## Key Libraries

- **hanzipy** - Character decomposition and radical data
- **pandas** - Data manipulation
- **pyarrow** - Parquet file format
- **genanki** - Anki deck generation

## Common Tasks

### Generate a fresh deck
```bash
bash run_hsk_pipeline.sh
```

### View component statistics
```bash
python analyze_hsk_components.py
```

### Create sample data and card previews
```bash
python create_samples.py
```

### Check what's in each level
```bash
python show_levels.py
```

### Verify dependencies are correct
```bash
python verify_sorting.py
```

## Troubleshooting

### "ModuleNotFoundError"
```bash
# Activate venv first!
source venv/Scripts/activate  # or venv/bin/activate on Unix
pip install -r requirements.txt
```

### "KeyError: 'radicals'" or "KeyError: 'character'"
- The data structure uses different column names
- Check if code uses `components` (not `radicals`)
- Check if code uses `hanzi` (not `character`)

### "File not found: data/hanzi.parquet"
```bash
# Run step 1 first
python generate_hsk_deck.py
```

### UTF-8 encoding issues on Windows
- Scripts have built-in UTF-8 console support
- Uses `io.TextIOWrapper` for proper emoji display

## Code Patterns

### Reading Data
```python
import pandas as pd

# Always use these column names:
radicals_df = pd.read_parquet('data/radicals.parquet')  # radical, meaning, usage_count
hanzi_df = pd.read_parquet('data/hanzi.parquet')        # hanzi, pinyin, meaning, components
vocab_df = pd.read_parquet('data/vocabulary.parquet')   # word, hsk_level, pinyin, meaning
```

### Handling Column Name Differences
```python
# Defensive programming for compatibility:
char = row.get('hanzi', row.get('character', ''))
components = row.get('components', row.get('radicals', ''))
```

### Windows UTF-8 Console
```python
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
```

## Anki Deck Structure

```
HSK 1-3 Hanzi Deck (parent)
├── 1. Radicals (233 cards)
│   - Brown theme
│   - Shows productivity scores
│   - Tags: radical, hsk1-3, level-X
│
├── 2. Hanzi (899 cards)
│   - Green theme
│   - Shows components and mnemonics
│   - Tags: hanzi, hsk1/2/3, level-X
│
└── 3. Vocabulary (2,227 cards)
    - Blue theme
    - Shows character breakdowns and examples
    - Tags: vocabulary, hsk1/2/3, level-X
```

## Documentation

- `README.md` - Project overview
- `HSK_PIPELINE_QUICKSTART.md` - Step-by-step guide
- `HSK_DECK_GENERATION_GUIDE.md` - Methodology details
- `PROJECT_STATUS.md` - Current state and roadmap
- `DOCS_CLEANUP_PLAN.md` - Documentation organization

## Development Principles

1. **HSK-based is the default** - Not frequency-based
2. **Clean file naming** - No prefixes like `hsk1_2_3_`
3. **Dependency-based learning** - Components before characters
4. **Three subdecks** - Separate radical, hanzi, and vocabulary
5. **UTF-8 everything** - Proper Chinese character support
6. **Defensive programming** - Handle missing columns gracefully

## Performance

- **Step 1 (Generate):** ~30 seconds
- **Step 2 (Sort):** ~5 seconds  
- **Step 3 (Create Deck):** ~10 seconds
- **Total:** ~45 seconds for complete deck

## Credits

- HSK data: [krmanik/HSK-3.0](https://github.com/krmanik/HSK-3.0) (CC BY-SA 4.0)
- Character data: [hanzipy](https://github.com/Synkied/hanzipy)
- Inspired by: WaniKani, Heisig's Remembering Hanzi
