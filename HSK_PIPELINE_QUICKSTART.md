# HSK Pipeline Quick Start Guide

## Complete Pipeline (3 Steps)

### Step 1: Generate Data
```bash
python generate_hsk_deck.py
```
**What it does:**
- Extracts all vocabulary from HSK 1-3 word lists
- Identifies 899 unique hanzi characters from those words
- Finds 233 productive radicals (components used in multiple characters)
- Calculates productivity scores for each radical
- Exports to `data/vocabulary.csv/parquet`, `data/hanzi.csv/parquet`, `data/radicals.csv/parquet`

**Output:**
- ✅ 2,227 vocabulary words
- ✅ 899 hanzi characters
- ✅ 233 productive radicals

---

### Step 2: Sort by Dependencies
```bash
python sort_hsk_by_dependencies.py
```
**What it does:**
- Organizes radicals into levels (5 per level)
- Assigns hanzi to levels based on their radicals (hanzi comes after radicals)
- Assigns vocabulary to levels based on their hanzi (vocabulary comes after hanzi)
- Adds `level` column to all data files
- Ensures you learn components before complex characters

**Output:**
- ✅ Level-sorted data files (same files, with `level` column added)
- ✅ ~47 radical levels, then hanzi levels, then vocabulary levels

---

### Step 3: Create Anki Deck
```bash
python create_hsk_deck.py
```
**What it does:**
- Reads level-sorted data
- Creates Anki cards with:
  - **Radicals**: Brown theme, productivity scores
  - **Hanzi**: Green theme, component breakdowns, mnemonics
  - **Vocabulary**: Blue theme, character breakdowns, examples
- Adds level tags and HSK level tags
- Exports ready-to-import Anki deck

**Output:**
- ✅ `anki_deck/HSK_1-3_Hanzi_Deck.apkg`
- ✅ Total: 3,359 cards (233 + 899 + 2,227)

---

## Analysis & Verification

### Analyze Components
```bash
python analyze_hsk_components.py
```
Shows component productivity distribution, top radicals, and learning recommendations.

### View Levels
```bash
python show_levels.py
```
Displays what's in each level (first 10 levels by default).

### Verify Dependencies
```bash
python verify_sorting.py
```
Checks that all dependencies are satisfied (no forward references).

---

## Utilities

### Create Sample CSVs
```bash
python create_sample_csvs.py
```
Creates sample CSV files to preview data structure and fields.

### Convert Pinyin
```bash
python -c "from pinyin_converter import numbered_to_accented; print(numbered_to_accented('ni3hao3'))"
```
Converts numbered pinyin (ni3hao3) to accented (nǐhǎo).

---

## Optional: All HSK Levels (1-9)

### Score All HSK Levels
```bash
python hsk_scorer.py
```
Generates HSK scores for ALL vocabulary and hanzi (not just 1-3).

### Analyze Scores
```bash
python analyze_hsk_scores.py
```
Shows score distribution for all HSK levels.

---

## Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "File not found: data/radicals.parquet"
Run step 1 first:
```bash
python generate_hsk_deck.py
```

### "No 'level' column found"
Run step 2 first:
```bash
python sort_hsk_by_dependencies.py
```

### UTF-8 Encoding Issues on Windows
Scripts have built-in UTF-8 support. If you still see issues:
```bash
chcp 65001  # Set console to UTF-8
```

---

## Expected Output Structure

```
data/
├── vocabulary.csv          # 2,228 lines (header + 2,227 words)
├── vocabulary.parquet      # Same data, more efficient
├── hanzi.csv               # 900 lines (header + 899 chars)
├── hanzi.parquet           # Same data, more efficient
├── radicals.csv            # 234 lines (header + 233 radicals)
└── radicals.parquet        # Same data, more efficient

anki_deck/
├── Tian_Hanzi_Deck_v1.apkg      # Original deck (1500 chars)
└── HSK_1-3_Hanzi_Deck.apkg      # New HSK deck (899 chars) ⭐
```

---

## Importing into Anki

1. Open Anki
2. **File** → **Import**
3. Select `anki_deck/HSK_1-3_Hanzi_Deck.apkg`
4. Click **Import**
5. Start studying!

**Tip:** Use custom study or filter by tags:
- `level-1` through `level-XXX` - Dependency levels
- `hsk1`, `hsk2`, `hsk3` - HSK levels
- `radical`, `hanzi`, `vocabulary` - Card types

---

## Performance

| Step | Time | Output |
|------|------|--------|
| 1. Generate | ~30s | CSV + Parquet files |
| 2. Sort | ~5s | Updated files with levels |
| 3. Create Deck | ~10s | .apkg file |
| **Total** | **~45s** | **Ready-to-use Anki deck** |

---

## Complete Example

```bash
# Start from scratch
cd c:\Users\Raymu\VSCode\Tian-hanzi-deck

# Run complete pipeline
python generate_hsk_deck.py            # Wait ~30s
python sort_hsk_by_dependencies.py     # Wait ~5s
python create_hsk_deck.py              # Wait ~10s

# Verify results
python analyze_hsk_components.py       # Check productivity
python show_levels.py                  # View levels

# Import into Anki
# File → Import → anki_deck/HSK_1-3_Hanzi_Deck.apkg

# Done! Start learning! 🎉
```

---

## Need Help?

- Check `README.md` for overview
- Check `HSK_DECK_GENERATION_GUIDE.md` for HSK methodology
- Check `SCRIPT_CONSOLIDATION_PLAN.md` for script details
- Check `CARD_PREVIEW_GUIDE.md` for card design info
