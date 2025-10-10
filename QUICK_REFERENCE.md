# Tian Hanzi Deck - Quick Reference

## 🚀 Most Common Tasks

### Generate Complete Deck
```bash
bash run_hsk_pipeline.sh
```
Output: `anki_deck/HSK_1-3_Hanzi_Deck.apkg`

### View Statistics
```bash
python show_levels.py                  # See level distribution
python analyze_hsk_components.py       # Component productivity
python verify_sorting.py               # Check dependencies
```

### Create Samples
```bash
python create_samples.py
```
Output: Sample CSVs + HTML card previews in `data/`

## 📊 Generated Data

| File | Records | Description |
|------|---------|-------------|
| `data/vocabulary.parquet` | 2,227 | HSK 1-3 vocabulary |
| `data/hanzi.parquet` | 899 | Characters from vocab |
| `data/radicals.parquet` | 233 | Productive components |

## 🎴 Deck Structure

```
HSK 1-3 Hanzi Deck (3,359 cards, 50 levels)
├── 1. Radicals (233 cards, brown)
├── 2. Hanzi (899 cards, green)
└── 3. Vocabulary (2,227 cards, blue)
```

## 📂 Key Files

### Pipeline
- `generate_hsk_deck.py` - Extract HSK data
- `sort_hsk_by_dependencies.py` - Assign levels
- `create_hsk_deck.py` - Build Anki deck

### Utilities
- `pinyin_converter.py` - Convert pinyin
- `parquet_utils.py` - Data utilities
- `create_samples.py` - Generate samples

### Analysis
- `analyze_hsk_components.py` - Component stats
- `show_levels.py` - Level distribution
- `verify_sorting.py` - Dependency check

## 🔍 Data Fields

### Vocabulary
```python
word, hsk_level, frequency_position, pinyin, meaning, is_surname, level
```

### Hanzi
```python
hanzi, pinyin, meaning, components, component_count, hsk_level, is_surname, level
```

### Radicals
```python
radical, meaning, usage_count, level
```

## 🎯 Learning Flow

1. **Learn 5 radicals** (e.g., Level 1: 一, 口, 丨, 丶)
2. **Learn hanzi using those radicals** (e.g., Level 2: 中 = 口 + 丨)
3. **Learn vocabulary using those hanzi** (e.g., Level 3: 中 = China/middle)
4. **Repeat** for next level

## 💡 Pro Tips

- **Sorting**: Level → HSK → Frequency/Simplicity
- **Components**: Formatted as "一 (one), 口 (mouth)"
- **Surnames**: Stored as `is_surname` boolean, removed from text
- **Ruby text**: Per-character pinyin above each character
- **Pipeline**: Takes ~45 seconds for complete regeneration

## 📖 Documentation

- **README.md** - Main documentation
- **CHANGELOG.md** - Version history
- **HSK_PIPELINE_QUICKSTART.md** - Step-by-step guide
- **CLEANUP_SUMMARY.md** - Repository cleanup status

## 🐛 Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "File not found: data/hanzi.parquet"
```bash
python generate_hsk_deck.py  # Run step 1 first
```

### Check data integrity
```bash
python verify_sorting.py  # Verify dependencies are correct
```

## 🔧 Requirements

- Python 3.11+
- Virtual environment (recommended)
- Dependencies: pandas, pyarrow, hanzipy, genanki

## 📈 Version

**Current**: 2.0.0 (HSK-based with surname handling)
**Previous**: 1.0.0 (Frequency-based prototype)

---

Last Updated: 2025-10-10
