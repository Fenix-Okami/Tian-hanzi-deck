# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed
- **README.md** - Rewrote to be more honest about v1 status
  - Clearly marked v1 as a rough prototype
  - Acknowledged known issues with mnemonics and card ordering
  - Removed overly promotional language
  - Added prominent TODO section highlighting needed improvements
  - Significantly shortened documentation (80% reduction)

## [1.0.0] - 2025-10-08

### ⚠️ Prototype Release - Tian Hanzi Deck v1

**Note:** This is an experimental prototype release. Mnemonics are auto-generated and card ordering needs refinement. Use with caution.

#### Added
- **Prototype deck with 3,428 cards**
  - 285 Radical cards
  - 1,500 Hanzi cards (top frequency characters)
  - 1,643 Vocabulary cards (high-frequency words)

- **Automated generation using Hanzipy**
  - `generate_tian_v1.py` / `generate_tian_v1_fast.py` - Data generation
  - `create_deck_from_parquet.py` - Builds Anki package
  - `parquet_utils.py` - Data utilities
  - `Tian_Hanzi_Deck_v1.apkg` - Ready-to-import Anki deck

- **Frequency-based character selection**
  - Uses Jun Da Character Frequency List
  - Covers top 1500 most common characters
  - Vocabulary sorted by Leiden corpus frequency

- **Radical decomposition**
  - Automatic extraction of 285 unique radicals
  - Component breakdown for each character

- **Auto-generated mnemonics** (needs improvement)
  - Memory aids for all radicals
  - Meaning mnemonics for characters
  - Reading mnemonics for pronunciation
  - Vocabulary mnemonics for words

#### Features
- Three-tier learning structure (Radicals → Hanzi → Vocabulary)
- WaniKani-inspired card design
- Color-coded card types (Blue/Pink/Purple)
- Parquet data format for efficient storage

#### Known Issues
- Mnemonics are auto-generated and often not optimized for memorability
- Card ordering algorithm needs refinement for better learning progression
- Quality varies significantly across cards

#### Technical
- Python 3.11+ support
- Integration with Hanzipy library
- Uses genanki for Anki package generation
- Parquet format for data storage

#### Data Sources
- Hanzipy library for character analysis
- Hanzi (nieldlr) for character decomposition and radical data
- CC-CEDICT for definitions
- Jun Da for character frequency
- Leiden University for word frequency

---

## [0.2.0] - Framework Improvements

### Recent Changes - Separate Mnemonics for Hanzi

### Summary
Split the single `mnemonic` field for Hanzi cards into two separate fields:
- `meaning_mnemonic`: Memory aid for remembering the character's meaning
- `reading_mnemonic`: Memory aid for remembering the character's pronunciation (pinyin)

### Files Modified

1. **create_deck.py**
   - Updated `hanzi_model` fields to include `MeaningMnemonic` and `ReadingMnemonic`
   - Modified card template to display both mnemonics separately with clear labels
   - Updated `create_hanzi_cards()` function to use new field names
   - Updated fallback example data in `get_example_hanzi()`

2. **example_data.py**
   - Updated all HANZI entries to use `meaning_mnemonic` and `reading_mnemonic` fields
   - Added example reading mnemonics that focus on sound/pronunciation aids

3. **validate_data.py**
   - Updated `validate_hanzi()` to check for both new required fields
   - Removed old `mnemonic` field from validation

4. **USAGE.md**
   - Updated Hanzi Fields table to document the two new mnemonic fields
   - Updated card description to mention both meaning and reading mnemonics

5. **README.md**
   - Updated Hanzi data structure documentation
   - Updated code example to show both mnemonic fields

6. **demo.py**
   - Updated Hanzi card display to show both mnemonics separately

### Benefits

- **Clearer Learning**: Separates the cognitive task of learning meaning vs. pronunciation
- **Better Mnemonics**: Allows for specialized memory aids for each aspect
- **More Like WaniKani**: Follows the WaniKani pattern of separate meaning and reading mnemonics
- **Improved Study Flow**: Users can focus on one aspect at a time if needed

### Migration Guide

If you have existing data with a single `mnemonic` field, update your entries to use both fields:

**Before:**
```python
{
    'character': '人',
    'meaning': 'Person',
    'reading': 'rén',
    'radicals': '人 (person)',
    'mnemonic': 'A person standing with legs apart'
}
```

**After:**
```python
{
    'character': '人',
    'meaning': 'Person',
    'reading': 'rén',
    'radicals': '人 (person)',
    'meaning_mnemonic': 'A person standing with two legs spread apart.',
    'reading_mnemonic': 'Sounds like "ren" in "render" - render a person in a drawing!'
}
```

### Testing

All changes have been validated:
- ✓ Data structure validation passes
- ✓ Demo script runs successfully
- ✓ All example data updated with new fields
