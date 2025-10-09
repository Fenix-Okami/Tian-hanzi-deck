# Anki Deck Output Folder

This folder contains the generated Anki deck files (.apkg) that can be imported into Anki.

## Files

- **Tian_Hanzi_Deck_v1.apkg** - Version 1 deck with top 1500 characters (3,428 cards)
- **Tian_Hanzi_Deck.apkg** - Custom/example deck

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
