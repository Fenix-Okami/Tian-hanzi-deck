# HSK Scoring System Guide

## Overview

The HSK Scoring System assigns priority scores to Chinese vocabulary and hanzi based on their HSK level (difficulty) and frequency ranking. This allows for intelligent sorting and prioritization in learning materials.

## Data Sources

- **HSK Hanzi**: Character lists from HSK levels 1-9 (`data/HSK-3.0/HSK Hanzi/`)
- **HSK Vocabulary (Frequency)**: Word lists sorted by frequency from HSK levels 1-9 (`data/HSK-3.0/HSK List (Frequency)/`)

Credit: [HSK-3.0](https://github.com/krmanik/HSK-3.0) by [@krmanik](https://github.com/krmanik)

## Scoring Formula

```
Total Score = Level Base Score + Frequency Bonus
```

### Level Base Scores (Difficulty)

Words are assigned a base score according to their HSK level, with easier levels receiving higher scores:

| HSK Level | Base Score | Description |
|-----------|------------|-------------|
| HSK 1     | 1000       | Beginner level - highest priority |
| HSK 2     | 700        | Elementary level |
| HSK 3     | 500        | Intermediate level |
| HSK 4     | 350        | Upper intermediate |
| HSK 5     | 200        | Advanced |
| HSK 6     | 100        | Proficient |
| HSK 7-9   | 0          | Master level - lowest priority |

### Frequency Bonus

Words that appear in the **top 100** positions of their frequency-ranked list receive an additional bonus:

- **Top 100 words**: +100 points
- **Below position 100**: +0 points

## Examples

### Vocabulary Examples

| Word | HSK Level | Frequency Position | Base Score | Frequency Bonus | Total Score |
|------|-----------|-------------------|------------|-----------------|-------------|
| 的   | 1         | 1                 | 1000       | +100            | **1100**    |
| 我   | 1         | 2                 | 1000       | +100            | **1100**    |
| 谢谢 | 1         | 70                | 1000       | +100            | **1100**    |
| 中国 | 1         | 335               | 1000       | +0              | **1000**    |
| 学习 | 1         | 319               | 1000       | +0              | **1000**    |

### Hanzi Examples

Hanzi (individual characters) only receive the level base score:

| Hanzi | HSK Level | Score |
|-------|-----------|-------|
| 的    | 1         | 1000  |
| 爱    | 1         | 1000  |
| 学    | 1         | 1000  |
| 习    | 1         | 1000  |

## Usage

### Running the Scorer

```bash
# Run with default settings
python hsk_scorer.py
```

This will:
1. Load HSK hanzi and vocabulary data
2. Calculate scores for all entries
3. Export scored data to CSV and Parquet formats

### Output Files

The script generates four output files in the `data/` directory:

1. **`hsk_hanzi_scored.csv`** - Scored hanzi in CSV format
2. **`hsk_vocabulary_scored.csv`** - Scored vocabulary in CSV format
3. **`hsk_hanzi_scored.parquet`** - Scored hanzi in Parquet format (efficient)
4. **`hsk_vocabulary_scored.parquet`** - Scored vocabulary in Parquet format (efficient)

### CSV Format

**Hanzi CSV columns:**
- `hanzi`: The Chinese character
- `hsk_level`: HSK level (1-6, or "7-9")
- `level_score`: Base score for the level

**Vocabulary CSV columns:**
- `word`: The Chinese word/phrase
- `hsk_level`: HSK level (1-6, or "7-9")
- `frequency_position`: Position in frequency-ranked list
- `level_score`: Base score for the level
- `frequency_bonus`: Bonus points (100 or 0)
- `total_score`: Final combined score

## Customizing Scores

You can customize the scoring parameters by modifying the `HSKScorer` initialization:

```python
from hsk_scorer import HSKScorer

# Custom level scores
custom_levels = {
    1: 2000,   # More weight on HSK 1
    2: 1500,
    3: 1000,
    4: 700,
    5: 400,
    6: 200,
    "7-9": 0
}

# Initialize with custom parameters
scorer = HSKScorer(
    level_scores=custom_levels,
    frequency_threshold=50,   # Top 50 instead of top 100
    frequency_bonus=200       # 200 points instead of 100
)

scorer.load_hsk_hanzi()
scorer.load_hsk_vocabulary()
scorer.export_scored_vocabulary_csv("data/custom_scores.csv")
```

## Integration with Tian Hanzi Deck

The HSK scores can be used to:

1. **Prioritize learning order** - Learn higher-scored words first
2. **Filter by difficulty** - Focus on specific HSK levels
3. **Balance frequency and difficulty** - Optimize learning progression
4. **Supplement dependency-based sorting** - Add frequency weighting to the existing radical/hanzi dependency system

## Statistics

Based on the HSK 3.0 dataset:

- **Total unique hanzi**: 2,999 characters across HSK 1-9
- **Total unique vocabulary**: 10,943 words across HSK 1-9
- **Distribution by level**:
  - HSK 1-6: 300 hanzi each, 497-1,134 words each
  - HSK 7-9: 1,200 hanzi, 5,619 words

## Future Enhancements

Potential improvements to the scoring system:

1. **Character frequency weighting** - Add frequency data for individual hanzi
2. **Composite scoring** - Combine with radical complexity scores
3. **Personalized weighting** - Adjust scores based on user progress
4. **Dynamic difficulty** - Adapt scores based on learning patterns
5. **Context-aware scoring** - Weight words based on usage contexts
