# Tian Hanzi Deck

A WaniKani-inspired Anki deck for learning Chinese characters with mnemonics.

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

- **285 Radicals** - Building blocks of characters
- **1500 Hanzi** - Top characters by frequency 
- **1643 Vocabulary** - Common words using these characters

## For Developers

### Requirements

```bash
pip install -r requirements.txt
```

### Generate the Deck

```bash
# Generate data from Hanzipy
python generate_tian_v1_fast.py

# Create the Anki package
python create_deck_from_parquet.py
```

### Project Structure

```
├── anki_deck/
│   └── Tian_Hanzi_Deck_v1.apkg    # The deck file
├── data/
│   ├── radicals.parquet            # Radical data
│   ├── hanzi.parquet               # Character data
│   └── vocabulary.parquet          # Vocabulary data
├── generate_tian_v1_fast.py        # Data generation
├── create_deck_from_parquet.py     # Deck creation
└── parquet_utils.py                # Data utilities
```

## Roadmap / TODO

### Priority Work for v2
1. **Improve mnemonics** - Review and rewrite auto-generated mnemonics for clarity and memorability
2. **Better card ordering algorithm** - Develop a more sophisticated approach to card sequencing:
   - Consider radical dependencies
   - Balance difficulty progression
   - Optimize for spaced repetition
   - Account for semantic and phonetic relationships

### Future Ideas
- Audio pronunciations
- Stroke order animations
- Better example sentences
- Traditional character support
- HSK level tags

## Acknowledgments

**Data Sources:**
- [Hanzipy](https://github.com/Synkied/hanzipy) - Character analysis
- CC-CEDICT - Dictionary definitions
- Jun Da - Character frequency data

**Inspiration:**
- WaniKani - Mnemonic-based methodology
- Heisig's Remembering Hanzi

## License

Open source for personal and educational use. Data sources have their own licenses.
