# Tian-hanzi-deck
A custom deck inspired by WaniKani with mnemonics for radicals, hanzi characters, and vocab

## Overview

This project provides a framework to create Anki decks using Python and the genanki library. The deck is organized into three subdecks:

1. **Radicals** - Basic building blocks of Chinese characters
2. **Hanzi** - Chinese characters with meanings and readings
3. **Vocabulary** - Chinese words and phrases

Each card includes:
- The character/word
- Meaning
- Reading (pinyin)
- Mnemonics to help with memorization
- Context and examples (for vocabulary)

## Installation

1. Install Python 3.6 or higher

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

Generate a deck with example data:

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
        'mnemonic': 'A person standing with legs apart'
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
- `mnemonic`: A memorable story to remember it

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

## Contributing

Feel free to add more example data or improve the card templates!

## License

This project is open source and available for personal and educational use.
