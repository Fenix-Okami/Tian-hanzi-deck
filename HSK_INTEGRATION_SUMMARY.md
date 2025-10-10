# HSK Integration Summary

## What We've Done

Successfully integrated the HSK-3.0 dataset into the Tian Hanzi Deck project with a customizable scoring system.

## New Features

### 1. HSK Data Integration
- Incorporated HSK 3.0 Hanzi data (2,999 unique characters)
- Incorporated HSK 3.0 Frequency vocabulary lists (10,943 unique words)
- Data sourced from: https://github.com/krmanik/HSK-3.0

### 2. Scoring System (`hsk_scorer.py`)

Created a flexible scoring algorithm that assigns priority scores to vocabulary and hanzi based on:

#### Level-Based Scoring (Difficulty)
- **HSK 1**: 1000 points (highest priority - beginner level)
- **HSK 2**: 700 points
- **HSK 3**: 500 points
- **HSK 4**: 350 points (gradually tapering)
- **HSK 5**: 200 points
- **HSK 6**: 100 points
- **HSK 7-9**: 0 points (lowest priority - master level)

#### Frequency-Based Bonus
- **Top 100** words in frequency list: +100 bonus points
- **Below 100**: +0 bonus points

#### Formula
```
Total Score = Level Base Score + Frequency Bonus
```

### 3. Adjustable Parameters

The scoring system is fully customizable via the `HSKScorer` class:

```python
scorer = HSKScorer(
    level_scores={1: 2000, 2: 1500, ...},  # Custom level weights
    frequency_threshold=50,                  # Top N for bonus
    frequency_bonus=200                      # Bonus point amount
)
```

## Generated Data Files

The scorer generates four output files:

1. **`data/hsk_hanzi_scored.csv`** - Scored hanzi (CSV format)
2. **`data/hsk_vocabulary_scored.csv`** - Scored vocabulary (CSV format)
3. **`data/hsk_hanzi_scored.parquet`** - Scored hanzi (Parquet format - efficient)
4. **`data/hsk_vocabulary_scored.parquet`** - Scored vocabulary (Parquet format - efficient)

### Data Structure

**Hanzi Fields:**
- `hanzi`: Character
- `hsk_level`: HSK level (1-6, or "7-9")
- `level_score`: Priority score

**Vocabulary Fields:**
- `word`: Chinese word/phrase
- `hsk_level`: HSK level (1-6, or "7-9")
- `frequency_position`: Position in frequency list
- `level_score`: Base score from HSK level
- `frequency_bonus`: Bonus points (100 or 0)
- `total_score`: Combined score

## Documentation

Created two new documentation files:

1. **`HSK_SCORING_GUIDE.md`** - Comprehensive guide to the scoring system
2. Updated **`README.md`** - Added HSK integration info and credited the source

## Credits Added

Added proper attribution in README.md:
- [HSK-3.0](https://github.com/krmanik/HSK-3.0) by [@krmanik](https://github.com/krmanik)
- HSK 3.0 word lists, Hanzi, and frequency data (CC BY-SA 4.0)

## Usage

```bash
# Generate HSK scores
python hsk_scorer.py

# Output will show:
# - 2,999 unique hanzi across HSK 1-9
# - 10,943 unique vocabulary words across HSK 1-9
# - Scored data exported to CSV and Parquet formats
```

## Statistics

### Data Coverage
- **HSK 1-6**: 300 hanzi each level
- **HSK 7-9**: 1,200 hanzi
- **HSK 1**: 497 vocabulary words
- **HSK 2**: 764 vocabulary words
- **HSK 3**: 966 vocabulary words
- **HSK 4**: 995 vocabulary words
- **HSK 5**: 1,067 vocabulary words
- **HSK 6**: 1,134 vocabulary words
- **HSK 7-9**: 5,619 vocabulary words

### Example Scores

| Word | HSK | Position | Base | Bonus | Total |
|------|-----|----------|------|-------|-------|
| 的   | 1   | #1       | 1000 | +100  | 1100  |
| 我   | 1   | #2       | 1000 | +100  | 1100  |
| 谢谢 | 1   | #70      | 1000 | +100  | 1100  |
| 中国 | 1   | #335     | 1000 | +0    | 1000  |

## Future Applications

The HSK scoring system can be used to:

1. **Enhance deck generation** - Prioritize high-frequency, lower-difficulty words
2. **Optimize learning order** - Balance frequency with HSK level progression
3. **Filter content** - Generate specialized decks by HSK level
4. **Combine with dependency sorting** - Add frequency/difficulty weighting to the existing radical-based system
5. **Track progress** - Map learning progress to HSK levels

## Next Steps

Potential future enhancements:
1. Integrate HSK scores into the main deck generation pipeline
2. Create HSK-level-specific decks
3. Add vocabulary filtering based on score thresholds
4. Combine dependency sorting with HSK scoring for optimal learning order
5. Add HSK level tags to Anki cards
