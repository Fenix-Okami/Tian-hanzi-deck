# 天 Tian Hanzi Deck
## Training in Asian Notation

An Anki deck for learning Chinese characters through dependency-based progression. Built from HSK 1-3 vocabulary with component productivity analysis.

## 📁 Project Structure

```
Tian-hanzi-deck/
├── src/                          # Source code package
│   └── tian_hanzi/              # Main package
│       ├── data_generator.py    # HSK data extraction
│       └── utils/               # Utility modules
│           ├── pinyin_converter.py
│           ├── parquet_manager.py
│           └── card_utils.py
│
├── tests/                       # Unit tests (pytest)
│   ├── conftest.py             # Test fixtures
│   ├── test_utilities.py       # Utility function tests
│   └── test_data_generation.py # Data generation tests
│
├── scripts/                     # Utility scripts
│   ├── analysis/               # Analysis tools
│   ├── validation/             # Data validation
│   └── legacy/                 # Old test scripts
│
├── generate_hsk_deck.py        # Pipeline step 1: Generate data
├── sort_hsk_by_dependencies.py # Pipeline step 2: Sort by deps
├── create_hsk_deck.py          # Pipeline step 3: Create deck
├── run_hsk_pipeline.sh         # Run complete pipeline
│
├── pytest.ini                  # Pytest configuration
├── setup.py                    # Package setup
└── requirements.txt            # Python dependencies
```

## 🧪 Testing

Run unit tests with pytest:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/tian_hanzi --cov-report=html
```

All tests should pass (21 tests covering utilities and data generation).

## 📖 Scripts

**Pipeline (Main):**
- `generate_hsk_deck.py` - Extract data from HSK lists
- `sort_hsk_by_dependencies.py` - Assign dependency levels
- `create_hsk_deck.py` - Build Anki package
- `run_hsk_pipeline.sh` - Run all steps
- `create_samples.py` - Sample data and HTML previews

**Mnemonics (Optional):**
- `generate_mnemonics.py` - Generate AI-powered mnemonics with OpenAI
- `run_mnemonic_generator.sh` - Quick start script
- See [MNEMONIC_GENERATOR_GUIDE.md](MNEMONIC_GENERATOR_GUIDE.md) for details

**Analysis Tools** (in `scripts/analysis/`):
- `analyze_hsk_components.py` - Component productivity analysis
- `show_levels.py` - Display level distribution
- `show_stroke_stats.py` - Show stroke count statistics

**Validation Tools** (in `scripts/validation/`):
- Various `verify_*.py` and `check_*.py` scripts for data validation
- Note: These will be migrated to proper unit tests over time

## 📋 Overview

This deck teaches Chinese characters by learning components before the characters that use them. Based on HSK 1-3 vocabulary (899 characters, 2,227 words, 233 productive radicals).

### 🎴 Deck Structure

- **233 Radicals** - Component building blocks (brown cards)
- **899 Hanzi** - Characters from HSK 1-3 (green cards)
- **2,227 Vocabulary** - HSK 1-3 words (blue cards)
- **50 Levels** - Sorted by dependencies

### 🎯 Learning Method

Each level teaches components before complex characters:
1. Learn 5 radicals
2. Learn characters that use those radicals
3. Learn words that use those characters

## 🚀 Usage

### Import the Deck

1. Download `anki_deck/HSK_1-3_Hanzi_Deck.apkg`
2. Import into Anki (File → Import)
3. Study cards in order

### Generate from Source

```bash
pip install -r requirements.txt
bash run_hsk_pipeline.sh
```

Manual steps:
```bash
python generate_hsk_deck.py           # Extract HSK data
python sort_hsk_by_dependencies.py    # Assign dependency levels
python create_hsk_deck.py             # Build Anki deck
```

## � Data Source

The deck extracts all characters from HSK 1-3 vocabulary, then identifies which components appear most frequently. This results in:

- 899 characters (only those used in HSK 1-3 words)
- 2,227 vocabulary entries (complete HSK 1-3 list)
- 233 components (sorted by productivity/usage count)

## 🔄 Dependency System

Cards are organized so components are learned before the characters that use them:

**Level Distribution:**
- Levels 1-47: Radicals (5 per level)
- Levels 2-48: Hanzi (only uses earlier radicals)
- Levels 3-50: Vocabulary (only uses earlier hanzi)

**Example:**
```
Level 1: 一 (one), 口 (mouth), 丨 (line), 丶 (dot)
Level 2: 中 (口 + 丨)
Level 3: 中 (word)
```

**Sort Order:**
Cards within each level are sorted by: Level → HSK tier (1/2/3) → Frequency or component count

## 🎴 Card Layout

### Radical Cards (Brown)
- Front: Component character
- Back: Meaning, usage count, productivity score

### Hanzi Cards (Green)
- Front: Character
- Back: Pinyin, meaning, two mnemonics, components list with meanings

### Vocabulary Cards (Blue)
- Front: Word
- Back: Per-character pinyin (ruby text), meaning, example, character breakdown

**Notes:**
- Surname references removed from meanings, stored as `is_surname` field
- Components shown with meanings: "一 (one), 口 (mouth)"
- Pinyin displayed above each character for vocabulary

## � Scripts

**Pipeline:**
- `generate_hsk_deck.py` - Extract data from HSK lists
- `sort_hsk_by_dependencies.py` - Assign dependency levels
- `create_hsk_deck.py` - Build Anki package
- `run_hsk_pipeline.sh` - Run all steps

**Analysis:**
- `analyze_hsk_components.py` - Component productivity
- `show_levels.py` - Level distribution
- `verify_sorting.py` - Dependency verification
- `create_samples.py` - Sample data and HTML previews

**Utilities:**
- `pinyin_converter.py` - Pinyin conversion
- `parquet_utils.py` - Data management

## � Data Files

Generated in both CSV and Parquet formats:

**vocabulary.csv/parquet**
```csv
word,hsk_level,frequency_position,pinyin,meaning,is_surname,level
```

**hanzi.csv/parquet**
```csv
hanzi,pinyin,meaning,components,component_count,hsk_level,is_surname,level
```

**radicals.csv/parquet**
```csv
radical,meaning,usage_count,level
```

**Data Notes:**
- Components: Pipe-separated (`口|丨`)
- Surnames: Boolean flag, text removed from meaning
- HSK levels: Integer type (Int64)

## � Statistics

- 3,359 total cards (233 radicals + 899 hanzi + 2,227 vocabulary)
- 50 dependency-based levels
- Average per level: 5 radicals, 19 hanzi, 46 vocabulary

## 🔍 Preview Cards

```bash
python create_samples.py
```

Opens HTML previews in `data/` folder with toggle buttons for front/back viewing.

## �📖 Documentation

- [HSK_PIPELINE_QUICKSTART.md](HSK_PIPELINE_QUICKSTART.md) - Pipeline guide
- [HSK_DECK_GENERATION_GUIDE.md](HSK_DECK_GENERATION_GUIDE.md) - Methodology
- [LEVEL_SYSTEM.md](LEVEL_SYSTEM.md) - Dependency levels
- [PRODUCTIVE_COMPONENTS_GUIDE.md](PRODUCTIVE_COMPONENTS_GUIDE.md) - Component scoring
- [CHANGELOG.md](CHANGELOG.md) - Version history

## ⚙️ Requirements

- Python 3.11+
- Dependencies: pandas, pyarrow, hanzipy, genanki

Pipeline takes ~45 seconds total (30s generate + 5s sort + 10s create)

## 📝 License & Credits

### Project License
**Apache License 2.0** - See [LICENSE](LICENSE)

### Data Sources

**HSK 3.0 Word Lists:**
- Source: [krmanik/HSK-3.0](https://github.com/krmanik/HSK-3.0)
- License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- Used for: Vocabulary selection (which words to include)

**CC-CEDICT (via hanzipy):**
- License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- Used for: Character and word definitions, pinyin

**Indirectly incorporated via HSK 3.0:**
- **SUBTLEX-CH** - CC BY-SA 4.0 (frequency ordering)
- **Pleco word lists** - MIT License (word selection methodology)

**Important:** The generated Anki deck (`.apkg` file) contains data derived from CC BY-SA 4.0 sources (CC-CEDICT, SUBTLEX-CH via HSK 3.0) and is therefore licensed under CC BY-SA 4.0. The source code remains Apache 2.0.

See [data/HSK-3.0/License.md](data/HSK-3.0/License.md) for full HSK 3.0 attribution details.

### Other Libraries
- Character decomposition: [hanzipy](https://github.com/Synkied/hanzipy)
- Anki deck generation: [genanki](https://github.com/kerrickstaley/genanki)

### Inspiration
- [WaniKani](https://www.wanikani.com/) - Japanese learning method
- Heisig's *Remembering the Hanzi* - Mnemonic approach
