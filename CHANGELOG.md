# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-10-08

### 🎉 Initial Release - Tian Hanzi Deck v1

#### Added
- **Complete deck with 3,428 cards**
  - 285 Radical cards
  - 1,500 Hanzi cards (top frequency characters)
  - 1,643 Vocabulary cards (high-frequency words)

- **Automated generation using Hanzipy**
  - `generate_tian_v1.py` - Generates data from frequency lists
  - `create_tian_v1_deck.py` - Builds Anki package
  - `tian_v1_data.py` - Generated data file (26,000+ lines)
  - `Tian_Hanzi_Deck_v1.apkg` - Ready-to-import Anki deck

- **Comprehensive documentation**
  - `QUICK_START_GUIDE.md` - User-friendly getting started guide
  - `TIAN_V1_RELEASE_NOTES.md` - Complete deck information
  - `TIAN_V1_SUMMARY.md` - Overview of what was built
  - `HANZIPY_REFERENCE_GUIDE.md` - Hanzipy library reference
  - Updated `README.md` with v1 information

- **Frequency-based character selection**
  - Uses Jun Da Character Frequency List
  - Covers top 1500 most common characters (~95% of texts)
  - Vocabulary sorted by Leiden corpus frequency

- **Radical decomposition**
  - Automatic extraction of 285 unique radicals
  - Radical meanings and mnemonics
  - Component breakdown for each character

- **Mnemonic support**
  - Memory aids for all radicals
  - Meaning mnemonics for characters
  - Reading mnemonics for pronunciation
  - Vocabulary mnemonics for words

#### Features
- Three-tier learning structure (Radicals → Hanzi → Vocabulary)
- WaniKani-inspired card design
- Color-coded card types (Blue/Pink/Purple)
- Clean, minimal interface
- Ready-to-import Anki package

#### Technical
- Python 3.11 support
- Integration with Hanzipy library
- Uses genanki 0.13.1 for Anki package generation
- Automatic quote escaping in generated data
- Data validation scripts
- Modular, extensible framework

#### Data Sources
- CC-CEDICT for definitions
- Jun Da for character frequency
- Leiden University for word frequency
- Gavin Grover for character decomposition

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
