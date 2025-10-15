# Pipeline Updates - HSK Breakdown & HTML Samples

## Overview
Enhanced the Tian Hanzi Deck pipeline to include HSK-level usage breakdown for radicals and automatic HTML sample generation.

> **2025-10-10 Update:** `generate_hsk_deck.py` has been superseded by the modular `tian-hanzi deck build` CLI command which now performs the same data extraction using the refactored pipeline.

## Changes Made (October 13, 2025)

### 1. HSK Level Breakdown for Radicals

**Modified Files:**
- `tian_hanzi/core/deck_pipeline.py`
- `create_hsk_deck.py`
- `create_samples.py`

**New Data Fields:**
The radicals data now includes usage breakdown by HSK level:
- `usage_hsk1` - Usage count in HSK 1 characters
- `usage_hsk2` - Usage count in HSK 2 characters  
- `usage_hsk3` - Usage count in HSK 3 characters
- `usage_count` - Total usage count (sum of above)

**Example:**
```csv
radical,meaning,usage_count,usage_hsk1,usage_hsk2,usage_hsk3
一,one,161,52,64,45
口,mouth,143,43,48,52
```

This helps understand:
- Which radicals are more fundamental (heavy HSK 1 usage)
- Which radicals appear more in advanced characters (heavy HSK 3 usage)
- Which radicals are balanced across all levels

### 2. HTML Sample Generation in Pipeline

**Modified Files:**
- `run_hsk_pipeline.sh`

**New Pipeline Steps:**
The pipeline now has 3 steps instead of 2:
1. **Step 1/3:** Generate HSK 1-3 data (`tian-hanzi deck build`)
2. **Step 2/3:** Create Anki deck with dynamic levels (`create_hsk_deck.py`)
3. **Step 3/3:** Generate HTML card previews and sample CSVs (`create_samples.py`) ✨ NEW

**Generated Files:**
- `data/sample_radical_card.html` - Preview of a radical card
- `data/sample_hanzi_card.html` - Preview of a hanzi card
- `data/sample_vocabulary_card.html` - Preview of a vocabulary card
- `data/radicals_sample.csv` - 20 random radicals
- `data/hanzi_sample.csv` - 20 random hanzi
- `data/vocabulary_sample.csv` - 20 random vocabulary words

### 3. New Analysis Tool

**New File:**
- `scripts/analysis/show_radical_hsk_breakdown.py`

Shows interesting patterns in radical usage:
- Radicals heavily used in HSK 1 (>40% usage)
- Radicals heavily used in HSK 2 (>45% usage)
- Radicals heavily used in HSK 3 (>45% usage)
- Balanced radicals (used evenly across all levels)

**Usage:**
```bash
python scripts/analysis/show_radical_hsk_breakdown.py
```

## Running the Complete Pipeline

```bash
bash run_hsk_pipeline.sh
```

This will:
1. ✅ Generate HSK 1-3 data with radical usage breakdown
2. ✅ Create the Anki deck (3,359 cards)
3. ✅ Generate HTML card previews
4. ✅ Create sample CSV files

## Key Insights

### HSK 1 Heavy Radicals
These radicals are fundamental building blocks:
- 讠 (speech): 42% in HSK 1
- 冖 (cover): 50% in HSK 1
- 卜 (divination): 55% in HSK 1

### HSK 2 Heavy Radicals
These appear more in intermediate characters:
- 艹 (grass): 48% in HSK 2
- 亠 (lid): 48% in HSK 2
- 亅 (hook): 55% in HSK 2

### HSK 3 Heavy Radicals
These are used in more advanced characters:
- 木 (tree): 48% in HSK 3
- 扌 (hand): 54% in HSK 3
- 尸 (corpse): 70% in HSK 3

### Balanced Radicals
These are consistently used across all levels:
- 丨 (line): ~33% each level
- 辶 (walk): evenly distributed
- 二 (two): evenly distributed

## Benefits

1. **Better Understanding:** See which radicals are more important at each learning stage
2. **Data Transparency:** Sample HTML files let you preview cards before importing
3. **Quality Assurance:** Sample CSVs make it easy to verify data integrity
4. **Automated:** Everything runs automatically in one pipeline

## Files Output

After running the pipeline, you'll have:

```
data/
├── radicals.csv (with usage_hsk1, usage_hsk2, usage_hsk3)
├── radicals.parquet
├── hanzi.csv
├── hanzi.parquet
├── vocabulary.csv
├── vocabulary.parquet
├── sample_radical_card.html ✨
├── sample_hanzi_card.html ✨
├── sample_vocabulary_card.html ✨
├── radicals_sample.csv ✨
├── hanzi_sample.csv ✨
└── vocabulary_sample.csv ✨

anki_deck/
└── HSK_1-3_Hanzi_Deck.apkg
```

## Next Steps

To view the HTML card previews:
1. Open `data/sample_radical_card.html` in your browser
2. Open `data/sample_hanzi_card.html` in your browser
3. Open `data/sample_vocabulary_card.html` in your browser

The cards are interactive - click "Show Back" to flip them!
