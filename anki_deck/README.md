# Anki Deck Output Folder

This folder contains the generated Anki deck files (.apkg) that can be imported into Anki.

## Files

- **HSK_1-3_Hanzi_Deck.apkg** - HSK 1-3 based deck (3,359 cards: 233 radicals + 899 hanzi + 2,227 vocabulary)

## License

⚠️ **Important:** The `.apkg` deck file is licensed under **CC BY-SA 4.0**, not Apache 2.0.

The deck contains data derived from:
- CC-CEDICT (CC BY-SA 4.0)
- SUBTLEX-CH (CC BY-SA 4.0)
- Pleco HSK 3.0 word lists (MIT)

See the [NOTICE](../NOTICE) file for complete attribution details.

## How to Use

1. Open Anki
2. Click **File → Import**
3. Navigate to this folder
4. Select the `.apkg` file you want to import
5. Click **Open**
6. Start studying!

## File Sizes

The deck files are typically:
- v1 deck: ~400-600 KB
- Custom decks: Varies by content

## Regenerating Decks

To regenerate the deck files:

```bash
# For v1 deck (top 1500 characters)
python generate_tian_v1.py        # Generate data
python create_tian_v1_deck.py     # Create deck

# For custom decks
python create_deck.py              # Uses example_data.py
```

All .apkg files will be saved to this folder automatically.

## Note

The `.apkg` files in this folder are **not tracked by git** to keep the repository size small. You'll need to generate them yourself using the scripts above.
