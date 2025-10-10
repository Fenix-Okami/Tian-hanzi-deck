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

### Generate the Deck

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

### Project Structure

```
├── anki_deck/
│   └── Tian_Hanzi_Deck_v1.apkg    # The deck file
├── data/
│   ├── radicals.parquet            # Radical data (with levels)
│   ├── hanzi.parquet               # Character data (with levels)
│   └── vocabulary.parquet          # Vocabulary data (with levels)
├── generate_tian_v1_fast.py        # Data generation
├── sort_by_dependencies.py         # Dependency-based sorting
├── create_deck_from_parquet.py     # Deck creation
├── parquet_utils.py                # Data utilities
└── pinyin_converter.py             # Numbered → accented pinyin
```

## Roadmap / TODO

### Priority Work for v2
1. **Improve mnemonics** - Review and rewrite auto-generated mnemonics for clarity and memorability
2. **~~Better card ordering algorithm~~** - ✅ **DONE!** Implemented dependency-based sorting:
   - ✅ Radicals are learned first (5 per level)
   - ✅ Hanzi only use previously learned radicals
   - ✅ Vocabulary only uses previously learned hanzi
   - Future: Consider frequency and difficulty within each level

### Future Ideas
- Audio pronunciations
- Stroke order animations
- Better example sentences
- Traditional character support
- HSK level tags

## Acknowledgments

**Data Sources:**
- [Hanzipy](https://github.com/Synkied/hanzipy) - Python libary to Hanzi
- [Hanzi](https://github.com/nieldlr/hanzi) - Character decomposition and radical data
- CC-CEDICT - Dictionary definitions
- Jun Da - Character frequency data

**Inspiration:**
- WaniKani - Mnemonic-based methodology
- Heisig's Remembering Hanzi

## License

Open source for personal and educational use. Data sources have their own licenses.
