# Quick Reference - Pipeline Commands

## Full Pipeline (Recommended)

### Windows
```bash
run_pipeline.bat
```

### macOS/Linux
```bash
bash run_pipeline.sh
```

**What it does:**
1. Generates data from Hanzipy (1500 hanzi + vocabulary)
2. Sorts by dependencies (radicals → hanzi → vocab)
3. Creates Anki package file

**Output:** `anki_deck/Tian_Hanzi_Deck_v1.apkg`

---

## Individual Steps

### Step 1: Generate Data
```bash
python generate_tian_v1_fast.py
```
- Fetches top 1500 characters by frequency
- Extracts 285 unique radicals
- Generates 1643 vocabulary words
- Converts pinyin to accented format (yī, èr, sān)
- Saves to: `data/*.parquet`
- Time: ~54 seconds

### Step 2: Sort by Dependencies
```bash
python sort_by_dependencies.py
```
- Assigns radicals to levels (5 per level)
- Sorts hanzi so components come first
- Sorts vocabulary by hanzi dependencies
- Updates: `data/*.parquet` (adds `level` column)
- Time: ~1 second

### Step 3: Create Anki Package
```bash
python create_deck_from_parquet.py
```
- Reads sorted parquet files
- Creates 3,428 Anki flashcards
- Generates: `anki_deck/Tian_Hanzi_Deck_v1.apkg`
- Time: ~10 seconds

---

## Utility Commands

### View Level Details
```bash
python show_levels.py
```
Shows first 10 levels with radicals, hanzi, and vocabulary

### Verify Sorting
```bash
python verify_sorting.py
```
Checks that all dependencies are correct:
- Hanzi only use earlier radicals ✓
- Vocabulary only uses earlier hanzi ✓

### Load and Inspect Data
```bash
python parquet_utils.py load
```
Displays sample entries from each parquet file

### View Statistics
```bash
python parquet_utils.py stats
```
Shows size and structure of parquet files

### Analyze Productive Components
```bash
python analyze_productive_components.py
```
Calculates component productivity scores (like HanziCraft)

---

## Common Workflows

### Regenerate Everything
```bash
# Delete old data
rm -rf data/*.parquet anki_deck/*.apkg

# Run full pipeline
run_pipeline.bat  # or bash run_pipeline.sh
```

### Just Rebuild Anki Deck
```bash
# If you already have sorted data
python create_deck_from_parquet.py
```

### Test Changes to Sorting
```bash
# Re-sort existing data
python sort_by_dependencies.py

# Verify it worked
python verify_sorting.py

# Rebuild deck
python create_deck_from_parquet.py
```

### Quick Preview
```bash
# Generate and sort data
python generate_tian_v1_fast.py
python sort_by_dependencies.py

# View without creating full deck
python show_levels.py
```

---

## File Locations

### Input Data
- Uses Hanzipy library (installed via pip)
- Jun Da Character Frequency List (built into Hanzipy)

### Generated Data
- `data/radicals.parquet` - 285 radicals with levels
- `data/hanzi.parquet` - 1500 characters with levels
- `data/vocabulary.parquet` - 1643 words with levels

### Output
- `anki_deck/Tian_Hanzi_Deck_v1.apkg` - Import this into Anki

### Sample Data
- `data/*_sample.csv` - Random 20 entries (for preview)

---

## Troubleshooting

### "hanzipy not found"
```bash
pip install -r requirements.txt
```

### "pandas not found" 
```bash
source venv/Scripts/activate  # Activate virtual environment first
pip install pandas pyarrow
```

### Pipeline script won't run
```bash
# Windows: Make sure you're in the project directory
cd C:\Users\YourName\VSCode\Tian-hanzi-deck
run_pipeline.bat

# macOS/Linux: Make script executable
chmod +x run_pipeline.sh
bash run_pipeline.sh
```

### Deck import fails in Anki
- Make sure you're using Anki 2.1.50+
- Try deleting old version first
- Check that .apkg file isn't corrupted (should be ~500KB)

---

## Configuration

### Change Number of Characters
Edit `generate_tian_v1_fast.py`:
```python
TOP_N_HANZI = 1500  # Change this number
```

### Change Radicals Per Level
Edit `sort_by_dependencies.py`:
```python
RADICALS_PER_LEVEL = 5  # Change this number
```

### Change Vocabulary Per Character
Edit `generate_tian_v1_fast.py`:
```python
VOCAB_PER_HANZI = 2  # Change this number
```

---

## Performance

### With Multiprocessing (15 cores)
- Generate data: 54 seconds
- Sort dependencies: 1 second
- Create deck: 10 seconds
- **Total: ~65 seconds**

### Single Core (for comparison)
- Generate data: ~4 minutes
- Sort dependencies: 1 second
- Create deck: 10 seconds
- **Total: ~4.5 minutes**
