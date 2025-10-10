# Quick Start - Running the Full Pipeline

## TL;DR

```bash
# Windows
run_pipeline.bat

# macOS/Linux  
bash run_pipeline.sh
```

That's it! The script will:
1. Generate all data (~54 seconds)
2. Sort by dependencies (~1 second)
3. Create Anki package (~10 seconds)

**Output:** `anki_deck/Tian_Hanzi_Deck_v1.apkg`

---

## What Gets Created

### Data Files (in `data/`)
- `radicals.parquet` - 285 radicals organized into 57 levels (5 per level)
- `hanzi.parquet` - 1500 characters sorted by radical dependencies
- `vocabulary.parquet` - 1643 words sorted by hanzi dependencies

### Anki Deck (in `anki_deck/`)
- `Tian_Hanzi_Deck_v1.apkg` - **3,428 flashcards** ready to import into Anki

---

## The 3-Step Process

### Step 1: Generate Data
**Script:** `generate_tian_v1_fast.py`
- Fetches top 1500 Chinese characters by frequency
- Extracts 285 unique radicals
- Finds 2 vocabulary words per character
- Converts pinyin to accented format (yī èr sān)
- **Time:** ~54 seconds with 15 CPU cores

### Step 2: Sort by Dependencies  
**Script:** `sort_by_dependencies.py`
- Organizes radicals into levels (5 per level)
- Sorts hanzi so you learn radicals before complex characters
- Sorts vocabulary so you learn hanzi before words
- **Time:** ~1 second

### Step 3: Create Anki Package
**Script:** `create_deck_from_parquet.py`
- Reads the sorted parquet data
- Creates 3,428 Anki flashcards
  - 285 radical cards
  - 1500 hanzi cards
  - 1643 vocabulary cards
- Exports as `.apkg` file
- **Time:** ~10 seconds

**Total Time: ~65 seconds**

---

## Manual Run (If Scripts Don't Work)

```bash
# Activate virtual environment
source venv/Scripts/activate  # macOS/Linux
# or
venv\Scripts\activate.bat     # Windows

# Run each step
python generate_tian_v1_fast.py
python sort_by_dependencies.py
python create_deck_from_parquet.py
```

---

## Verify Everything Worked

```bash
# Check the data was created
ls data/*.parquet

# View first 10 levels
python show_levels.py

# Verify dependencies are correct
python verify_sorting.py

# Check deck was created
ls anki_deck/*.apkg
```

---

## Next Steps

1. Open Anki
2. Click "Import File"
3. Select `anki_deck/Tian_Hanzi_Deck_v1.apkg`
4. Start studying!

The deck is organized into 57 levels where you'll learn:
- 5 radicals per level
- Then hanzi using those radicals
- Then vocabulary using those hanzi

This way you always understand the components before learning complex characters.

---

## Need Help?

See `PIPELINE_GUIDE.md` for detailed documentation.
