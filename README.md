# 天
## T.I.A.N Hanzi Deck - Training in Asian Notation

A WaniKani-inspired Anki deck for learning Chinese characters with mnemonics. I was pushed to make this when I personally found Hanzihero and Pandanese lacking for my personal tastes

## ⚠️ Status: v1 is a Rough Prototype

**Version 1** is an experimental prototype with 3,428 cards (285 radicals, 1500 hanzi, 1643 vocabulary). It's functional but has significant limitations:

### Known Issues
- **Mnemonics need work**: Many are auto-generated and not optimized for memorability
- **Card ordering needs refinement**: Current algorithm could be improved for better learning progression
- **Quality varies**: Some cards are better than others

**Use at your own risk.** This is a proof-of-concept, not a polished learning tool.

## Quick Start

1. Download `anki_deck/Tian_Hanzi_Deck_v1.apkg`
2. Import into [Anki](https://apps.ankiweb.net)
3. Start studying

## What's Included

- **285 Radicals** - Building blocks of characters (5 per level, 57 levels)
- **1500 Hanzi** - Top characters by frequency (sorted by radical dependencies)
- **1643 Vocabulary** - Common words (sorted by hanzi dependencies)

### Learning Progression

The deck uses **dependency-based sorting** to ensure you learn components before complex characters:

1. **Radicals First**: 5 radicals per level (Levels 1-57)
2. **Hanzi Next**: Each character only uses radicals from earlier levels
3. **Vocabulary Last**: Each word only uses hanzi from earlier levels

**Example:**
- Level 1: Learn radicals 白, 勹, 丶, 一, 日
- Level 1: Then learn hanzi that use only these radicals: 的, 一, 日, 白, 百, 旦
- Level 1: Then learn vocabulary using these hanzi: 一旦

This creates a natural learning curve where you always understand the components of what you're learning.

## For Developers

### Requirements

```bash
pip install -r requirements.txt
```

### HSK-Based Deck Generation (Default ⭐)

**HSK 1-3 is now the default approach!** Generate targeted decks based on HSK levels with productive component analysis:

```bash
# Complete pipeline (3 steps)
python generate_hsk_deck.py           # Step 1: Generate data (899 hanzi, 2227 vocab, 233 radicals)
python sort_hsk_by_dependencies.py    # Step 2: Sort by dependencies into levels
python create_hsk_deck.py             # Step 3: Create Anki .apkg file
```

**Output files:**
- `data/vocabulary.csv/parquet` - 2,227 HSK 1-3 words
- `data/hanzi.csv/parquet` - 899 characters  
- `data/radicals.csv/parquet` - 233 productive components
- `anki_deck/HSK_1-3_Hanzi_Deck.apkg` - Ready-to-import Anki deck

**Why HSK-based is better:**
- ✅ 40% fewer characters than arbitrary frequency (899 vs 1500)
- ✅ 36% more vocabulary (2227 vs 1643)  
- ✅ Direct HSK exam alignment
- ✅ Scientifically calculated component productivity scores
- ✅ Learn only what you need for your HSK level
- ✅ Dependency-based learning progression

**Analysis tools:**
```bash
python analyze_hsk_components.py      # View component productivity analysis
python create_samples.py              # Create sample CSVs and HTML card previews
python show_levels.py                 # Display level distribution
python verify_sorting.py              # Verify dependency sorting
```

See [HSK_DECK_GENERATION_GUIDE.md](HSK_DECK_GENERATION_GUIDE.md) for details.

### Generate the Deck (Original Method)

**Quick Method (Recommended):**

```bash
# Windows
run_pipeline.bat

# macOS/Linux
bash run_pipeline.sh
```

**Manual Method (Step by Step):**

```bash
# Step 1: Generate data from Hanzipy (~54 seconds)
python generate_tian_v1_fast.py

# Step 2: Sort by dependencies (~1 second)
python sort_by_dependencies.py

# Step 3: Create Anki package (~10 seconds)
python create_deck_from_parquet.py
```

**View Level Details:**

```bash
python show_levels.py        # See first 10 levels
python verify_sorting.py     # Verify dependencies are correct
```

**HSK Scoring System:**

```bash
python hsk_scorer.py         # Generate HSK-based scores for vocabulary and hanzi
```

The HSK scorer assigns priority scores based on HSK level and frequency rankings. See [HSK_SCORING_GUIDE.md](HSK_SCORING_GUIDE.md) for details.

### Project Structure

```
├── anki_deck/
│   ├── Tian_Hanzi_Deck_v1.apkg         # Original deck (v1)
│   └── HSK_1-3_Hanzi_Deck.apkg         # HSK 1-3 deck (NEW!)
├── data/
│   ├── vocabulary.csv/parquet          # HSK 1-3: 2,227 words
│   ├── hanzi.csv/parquet               # HSK 1-3: 899 characters
│   ├── radicals.csv/parquet            # HSK 1-3: 233 productive components
│   └── HSK-3.0/                        # HSK 3.0 source data
│
├── Core HSK Pipeline (Use these! ⭐)
│   ├── generate_hsk_deck.py            # 1. Generate HSK 1-3 data
│   ├── sort_hsk_by_dependencies.py     # 2. Sort by dependencies
│   ├── create_hsk_deck.py              # 3. Create Anki deck
│   └── analyze_hsk_components.py       # Analyze productivity
│
├── Utilities
│   ├── pinyin_converter.py             # Pinyin conversion utility
│   ├── parquet_utils.py                # Data management utility
│   ├── show_levels.py                  # View level distribution
│   ├── verify_sorting.py               # Verify dependencies
│   └── create_samples.py               # Create sample CSVs and HTML card previews
│
├── Optional HSK Tools
│   ├── hsk_scorer.py                   # Score all HSK levels (1-9)
│   └── analyze_hsk_scores.py           # Score distribution analysis
│
└── Legacy V1 Scripts
    ├── generate_tian_v1_fast.py        # Original frequency-based generator
    ├── sort_by_dependencies.py         # Original dependency sorter
    ├── create_deck_from_parquet.py     # Original deck creator
    └── analyze_productive_components.py # Old analysis tool
```

## Documentation

- 📖 **[HSK Pipeline Quick Start](HSK_PIPELINE_QUICKSTART.md)** - Complete step-by-step guide
- 📊 **[HSK Deck Generation Guide](HSK_DECK_GENERATION_GUIDE.md)** - HSK methodology details
- 🔧 **[Script Consolidation Plan](SCRIPT_CONSOLIDATION_PLAN.md)** - Script organization reference
- 🎴 **[Card Preview Guide](CARD_PREVIEW_GUIDE.md)** - Card design and styling
- 📈 **[HSK Scoring Guide](HSK_SCORING_GUIDE.md)** - Scoring system explanation
- 🎯 **[Level System](LEVEL_SYSTEM.md)** - Dependency-based learning progression

## Roadmap / TODO

### ✅ Completed for HSK 1-3
1. ✅ **HSK-based deck generation** - Focus on HSK 1-3 vocabulary
2. ✅ **Productive component analysis** - Scientific radical selection
3. ✅ **Dependency-based sorting** - Learn components before characters
4. ✅ **Level system** - Progressive learning with 5 radicals per level
5. ✅ **HSK level tags** - Filter by HSK 1, 2, or 3
6. ✅ **Themed card designs** - Brown (radicals), Green (hanzi), Blue (vocabulary)

### Future Ideas
- Audio pronunciations
- Stroke order animations
- Better example sentences
- Traditional character support
- Improved mnemonics
- HSK 4-6 expansion

## Acknowledgments

**Data Sources:**
- [Hanzipy](https://github.com/Synkied/hanzipy) - Python libary to Hanzi
- [Hanzi](https://github.com/nieldlr/hanzi) - Character decomposition and radical data
- [HSK-3.0](https://github.com/krmanik/HSK-3.0) by [@krmanik](https://github.com/krmanik) - HSK 3.0 word lists, Hanzi, and frequency data (CC BY-SA 4.0)
- CC-CEDICT - Dictionary definitions
- Jun Da - Character frequency data

**Inspiration:**
- WaniKani - Mnemonic-based methodology
- Heisig's Remembering Hanzi

## License

Open source for personal and educational use. Data sources have their own licenses.
