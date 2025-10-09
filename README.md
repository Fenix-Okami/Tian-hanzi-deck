# Tian Hanzi Deck
A comprehensive Anki deck for learning Chinese characters with mnemonics, inspired by WaniKani

## 🎉 Version 1.0 Released!

**Ready-to-use deck with 3,428 cards covering the top 1500 most frequent Chinese characters!**

### 🚀 Quick Start for Learners
1. Download `Tian_Hanzi_Deck_v1.apkg`
2. Import into Anki
3. Start learning!

📖 **[Read the Quick Start Guide](QUICK_START_GUIDE.md)** for complete instructions.

### 📊 What's Included
- **285 Radicals** - Building blocks of Chinese characters
- **1500 Hanzi** - Top characters by frequency (covers ~95% of texts)
- **1643 Vocabulary** - High-frequency words using these characters
- **Total: 3,428 flashcards**

📋 **[Read the Release Notes](TIAN_V1_RELEASE_NOTES.md)** for full details.

---

## Overview

This project provides both:
1. **A ready-to-use Anki deck** (v1.0) with the top 1500 Chinese characters
2. **A framework** to create custom Anki decks using Python

The deck is organized into three subdecks:

1. **Radicals** - Basic building blocks of Chinese characters
2. **Hanzi** - Chinese characters with meanings and readings
3. **Vocabulary** - Chinese words and phrases

Each card includes:
- The character/word
- Meaning
- Reading (pinyin)
- Mnemonics to help with memorization
- Radical composition (for characters)
- Context and examples (for vocabulary)

## For Learners: Using the Pre-built Deck

### Installation

1. Download `anki_deck/Tian_Hanzi_Deck_v1.apkg` from this repository
2. Install [Anki](https://apps.ankiweb.net) if you haven't already
3. In Anki: **File → Import** → Select the `.apkg` file
4. Start studying!

See **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** for detailed instructions.

---

## For Developers: Building Custom Decks

### Prerequisites

1. Install Python 3.6 or higher

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Option 1: Generate the v1 Deck (Top 1500 Characters)

```bash
# Generate data from Hanzipy
python generate_tian_v1.py

# Create the Anki deck
python create_tian_v1_deck.py
```

This creates `Tian_Hanzi_Deck_v1.apkg` with 3,428 cards.

### Option 2: Create a Custom Deck with Example Data

```bash
python create_deck.py
```

This will create a file named `Tian_Hanzi_Deck.apkg` that can be imported into Anki.

### Custom Data

To create a deck with your own data:

1. Edit `example_data.py` to add your radicals, hanzi, and vocabulary
2. Run the script:
```bash
python create_deck.py
```

### Using in Your Own Scripts

You can also use the framework programmatically:

```python
from create_deck import create_deck

# Define your data
my_radicals = [
    {
        'radical': '一',
        'meaning': 'Ground',
        'mnemonic': 'A horizontal line like the ground'
    }
]

my_hanzi = [
    {
        'character': '人',
        'meaning': 'Person',
        'reading': 'rén',
        'radicals': '人 (person)',
        'meaning_mnemonic': 'A person standing with legs apart',
        'reading_mnemonic': 'Sounds like "ren" in "render" - render a person!'
    }
]

my_vocab = [
    {
        'word': '今天',
        'meaning': 'Today',
        'reading': 'jīn tiān',
        'characters': '今 (now) + 天 (day)',
        'example': '今天天气很好。',
        'mnemonic': 'The "now" day is today!'
    }
]

# Create the deck
create_deck(
    radicals_data=my_radicals,
    hanzi_data=my_hanzi,
    vocab_data=my_vocab,
    output_file='My_Custom_Deck.apkg'
)
```

## Data Structure

### Radicals

Each radical should have:
- `radical`: The radical character
- `meaning`: The meaning/name of the radical
- `mnemonic`: A memorable story or image to remember it

### Hanzi

Each hanzi character should have:
- `character`: The Chinese character
- `meaning`: The English meaning
- `reading`: The pinyin reading
- `radicals`: The component radicals
- `meaning_mnemonic`: A memorable story to remember the meaning
- `reading_mnemonic`: A memorable story to remember the pronunciation

### Vocabulary

Each vocabulary word should have:
- `word`: The Chinese word
- `meaning`: The English meaning
- `reading`: The pinyin reading
- `characters`: Breakdown of the component characters
- `example`: An example sentence (optional)
- `mnemonic`: A memorable story to remember it

## Card Templates

The deck includes custom card templates inspired by WaniKani:

- **Radicals**: Blue theme, focuses on radical recognition
- **Hanzi**: Pink theme, includes radical breakdown
- **Vocabulary**: Purple theme, includes example sentences

All cards feature a clean, minimalist design with:
- Large, clear characters
- Color-coded card types
- Mnemonic sections for memory aids
- Responsive layout

## Importing into Anki

1. Open Anki
2. Go to File → Import
3. Select the generated `.apkg` file
4. The deck will be imported with three subdecks:
   - Tian Hanzi Deck::1_Radicals
   - Tian Hanzi Deck::2_Hanzi
   - Tian Hanzi Deck::3_Vocabulary

## 📚 Documentation

- **[Quick Start Guide](QUICK_START_GUIDE.md)** - Get started in 5 minutes
- **[Release Notes](TIAN_V1_RELEASE_NOTES.md)** - Complete v1 deck information
- **[v1 Summary](TIAN_V1_SUMMARY.md)** - Overview of what was built
- **[Hanzipy Reference](HANZIPY_REFERENCE_GUIDE.md)** - How to use Hanzipy library
- **[Usage Guide](USAGE.md)** - Detailed framework usage
- **[Parquet Guide](PARQUET_GUIDE.md)** - Efficient data storage with Parquet format

## 🔧 Project Structure

```
Tian-hanzi-deck/
├── anki_deck/                    # Output folder for Anki decks
│   ├── Tian_Hanzi_Deck_v1.apkg  # Ready-to-use deck (v1.0)
│   └── README.md                 # Anki deck folder info
├── data/                         # Parquet data files (NEW!)
│   ├── radicals.parquet          # Radicals in Parquet format
│   ├── hanzi.parquet             # Hanzi in Parquet format
│   ├── vocabulary.parquet        # Vocabulary in Parquet format
│   └── README.md                 # Data directory info
├── generate_tian_v1.py           # Generate v1 data
├── generate_tian_v1_fast.py      # Generate v1 data (multiprocessing)
├── create_tian_v1_deck.py        # Build v1 Anki package
├── tian_v1_data.py               # Generated v1 data (3,428 cards)
├── parquet_utils.py              # Parquet data utilities (NEW!)
├── create_deck.py                # Base framework for custom decks
├── example_data.py               # Example data for custom decks
├── validate_data.py              # Data validation script
└── requirements.txt              # Python dependencies
```

## 🌟 Features

### Frequency-Based Learning
- Characters ordered by actual usage frequency (Jun Da corpus)
- Learn the most common characters first
- 1500 characters cover ~95% of typical Chinese texts

### Mnemonic Support
- Every card includes memory aids
- Radical-based explanations
- WaniKani-inspired methodology

### Three-Tier Structure
1. **Learn radicals** → understand building blocks
2. **Learn characters** → see how radicals combine
3. **Learn vocabulary** → reinforce with real words

### Beautiful Card Design
- Clean, minimal interface
- Color-coded by type (Radical/Hanzi/Vocabulary)
- Large, readable characters
- Responsive layout

### Efficient Data Storage (NEW!)
- **Parquet format support** for fast, compressed data storage
- **12x faster** data loading compared to Python imports
- **50% smaller** file sizes with Snappy compression
- Compatible with pandas, Apache Spark, and data analysis tools

```python
# Load data from Parquet (fast!)
from parquet_utils import load_tian_v1_data_from_parquet
radicals, hanzi, vocabulary = load_tian_v1_data_from_parquet()
```

See **[PARQUET_GUIDE.md](PARQUET_GUIDE.md)** for complete documentation.

## 🛠️ Advanced Usage

### Regenerate with Custom Parameters

Edit `generate_tian_v1.py` to change:
- Number of characters (default: 1500)
- Vocabulary per character (default: 2)
- Mnemonic templates
- Frequency sources

### Validate Your Data

```bash
python validate_data.py
```

### Create Completely Custom Decks

See [USAGE.md](USAGE.md) for detailed framework documentation.

## 📈 What You'll Learn

With the v1 deck, you'll master:
- **285 radicals** - Building blocks
- **1500 characters** - 90-95% reading comprehension
- **1643 words** - Common vocabulary
- **Ready for**: HSK 6, reading newspapers, Chinese novels

Estimated completion time:
- **Moderate pace**: 6-8 months (15 cards/day)
- **Intensive pace**: 4-6 months (20 cards/day)

## 🙏 Acknowledgments

### Data Sources
- **Hanzipy** by Synkied - Character analysis library
- **CC-CEDICT** - Dictionary definitions
- **Jun Da** - Character frequency data
- **Leiden University** - Word frequency corpus
- **Gavin Grover** - Character decomposition

### Inspiration
- **WaniKani** - Mnemonic-based learning approach
- **Heisig's Remembering Hanzi** - Systematic methodology

## Contributing

Contributions welcome! Ideas for v2:
- Audio pronunciations
- Stroke order animations
- Additional example sentences
- Traditional character support
- HSK level tags

## License

This project is open source and available for personal and educational use.

Data sources have their own licenses:
- CC-CEDICT: Creative Commons
- Character decomposition: Open Source
- Frequency data: Academic use

---

**Happy learning! 加油！(jiā yóu - Keep going!)** 🚀
