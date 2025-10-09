# Usage Guide for Tian Hanzi Deck

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate the Deck

```bash
python create_deck.py
```

This creates `Tian_Hanzi_Deck.apkg` with example data.

### 3. Import into Anki

1. Open Anki
2. File → Import
3. Select `Tian_Hanzi_Deck.apkg`
4. Start studying!

## Deck Structure

```
Tian Hanzi Deck
├── 1_Radicals (Building blocks)
├── 2_Hanzi (Characters)
└── 3_Vocabulary (Words & Phrases)
```

### Study Order Recommendation

1. **Start with Radicals** - Learn the basic building blocks
2. **Move to Hanzi** - Learn characters using the radicals
3. **Practice Vocabulary** - Learn words using the characters

## Customizing Your Deck

### Option 1: Edit example_data.py

Simply edit the lists in `example_data.py`:

```python
RADICALS = [
    {
        'radical': '一',
        'meaning': 'Ground',
        'mnemonic': 'Your mnemonic here'
    },
    # Add more radicals...
]
```

### Option 2: Use Programmatically

Create your own Python script:

```python
from create_deck import create_deck

my_data = {
    'radicals': [...],
    'hanzi': [...],
    'vocab': [...]
}

create_deck(
    radicals_data=my_data['radicals'],
    hanzi_data=my_data['hanzi'],
    vocab_data=my_data['vocab'],
    output_file='my_deck.apkg'
)
```

## Data Structure Reference

### Radical Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| radical | string | Yes | The radical character |
| meaning | string | Yes | English meaning/name |
| mnemonic | string | Yes | Memory aid story |

### Hanzi Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| character | string | Yes | The Chinese character |
| meaning | string | Yes | English meaning |
| reading | string | Yes | Pinyin pronunciation |
| radicals | string | Yes | Component radicals |
| meaning_mnemonic | string | Yes | Memory aid for the meaning |
| reading_mnemonic | string | Yes | Memory aid for the pronunciation |

### Vocabulary Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| word | string | Yes | The Chinese word |
| meaning | string | Yes | English meaning |
| reading | string | Yes | Pinyin pronunciation |
| characters | string | Yes | Component characters |
| example | string | No | Example sentence |
| mnemonic | string | Yes | Memory aid story |

## Card Templates

### Radical Cards (Blue Theme)

**Front:**
- Shows the radical character
- Asks for the meaning

**Back:**
- Shows the meaning
- Displays the mnemonic

### Hanzi Cards (Pink Theme)

**Front:**
- Shows the character
- Asks for meaning and reading

**Back:**
- Shows meaning and reading
- Displays component radicals
- Shows the meaning mnemonic
- Shows the reading mnemonic

### Vocabulary Cards (Purple Theme)

**Front:**
- Shows the word
- Asks for meaning and reading

**Back:**
- Shows meaning and reading
- Displays component characters
- Shows example sentence (if provided)
- Shows the mnemonic

## Tips for Creating Good Mnemonics

1. **Make them visual** - Create a mental image
2. **Make them personal** - Connect to your experiences
3. **Make them absurd** - Strange things are more memorable
4. **Use radicals** - Build on what you've already learned
5. **Keep them concise** - Short stories work best

## Validation

Validate your data before generating the deck:

```bash
python validate_data.py
```

This checks:
- All required fields are present
- All fields have the correct type
- No empty values

## Demo Mode

See what your deck will look like without installing genanki:

```bash
python demo.py
```

This shows:
- Deck structure
- Card counts
- Sample cards from each category

## Troubleshooting

### "ModuleNotFoundError: No module named 'genanki'"

Install the requirements:
```bash
pip install -r requirements.txt
```

### "Validation failed"

Run the validation script to see specific errors:
```bash
python validate_data.py
```

### Characters not displaying correctly

Make sure your terminal/editor supports UTF-8 encoding.

## Advanced Usage

### Multiple Decks

Generate multiple decks for different levels:

```python
from create_deck import create_deck
from example_data import RADICALS, HANZI, VOCABULARY

# Beginner deck (first 5 of each)
create_deck(
    radicals_data=RADICALS[:5],
    hanzi_data=HANZI[:5],
    vocab_data=VOCABULARY[:5],
    output_file='Beginner_Deck.apkg'
)

# Advanced deck (rest)
create_deck(
    radicals_data=RADICALS[5:],
    hanzi_data=HANZI[5:],
    vocab_data=VOCABULARY[5:],
    output_file='Advanced_Deck.apkg'
)
```

### Custom Card Styling

Edit the `css` field in the model definitions in `create_deck.py` to customize the appearance.

### Loading Data from Files

Load your data from CSV, JSON, or other formats:

```python
import json
from create_deck import create_deck

# Load from JSON
with open('my_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

create_deck(
    radicals_data=data['radicals'],
    hanzi_data=data['hanzi'],
    vocab_data=data['vocabulary']
)
```

## Resources

- [Anki Manual](https://docs.ankiweb.net/)
- [genanki Documentation](https://github.com/kerrickstaley/genanki)
- [WaniKani Method](https://www.wanikani.com/methodology)

## Contributing

To add more example data:

1. Edit `example_data.py`
2. Run `python validate_data.py`
3. Test with `python demo.py`
4. Generate deck with `python create_deck.py`
5. Import into Anki and test

Feel free to share your custom data and mnemonics!
