# Productive Components Analysis

## Overview

This script analyzes Chinese character components and ranks them by "productivity" - how useful they are for learning based on:
1. How many characters contain the component
2. Weighted by the frequency of those characters (more common characters contribute more to the score)

## Configuration

Edit the `HANZI_FREQUENCY_LIMIT` setting at the top of `analyze_productive_components.py`:

```python
# Set to a specific number to analyze only top N most frequent characters
HANZI_FREQUENCY_LIMIT = 1500  # Top 1500 characters

# Set to None to analyze the full dataset (9933 characters)
HANZI_FREQUENCY_LIMIT = None   # Full dataset
```

## Results for Top 1500 Characters

When analyzing the top 1500 most frequent characters, we found **225 productive components**.

### Top 10 Most Productive Components:

| Rank | Component | Score | Count | Notes |
|------|-----------|-------|-------|-------|
| 1 | 一 | 1.47 | 272 | Horizontal line - most productive! |
| 2 | 丶 | 1.25 | 85 | Dot stroke |
| 3 | 勹 | 1.04 | 27 | Wrap radical |
| 4 | 白 | 1.02 | 13 | White |
| 5 | 口 | 0.72 | 207 | Mouth - appears in many characters |
| 6 | 丨 | 0.72 | 144 | Vertical line |
| 7 | 日 | 0.57 | 84 | Sun/day |
| 8 | 亻 | 0.57 | 88 | Person radical (side form) |
| 9 | 丿 | 0.43 | 66 | Left-falling stroke |
| 10 | 龰 | 0.36 | 4 | Small component, high-frequency characters |

## Methodology

Based on HanziCraft's productive components methodology:
- **Formula**: `score = sum(1/frequency_rank)` for each character containing the component
- **Weighting**: Characters that appear more frequently (lower rank number) contribute MORE to the score
- **Filtering**: Only components appearing in 2+ characters are included

### Example:
If component 口 appears in:
- 中 (rank 14): contributes 1/14 = 0.071
- 和 (rank 19): contributes 1/19 = 0.053
- 说 (rank 24): contributes 1/24 = 0.042
- ... (and 204 more characters)

Total score = 0.72

## Output Files

**`data/productive_components.csv`** - Complete ranked list with:
- Rank (1-225)
- Component character
- Productivity score
- Character count (how many characters contain it)
- Sample characters with their frequency ranks

## Use Cases

1. **Order radicals for learning** - Teach the most productive components first
2. **Deck generation** - Include only the most useful components in your flashcard deck
3. **Analysis** - Understand which building blocks are most important
4. **Customization** - Generate different component lists for different character set sizes

## Comparison with Full Dataset

| Setting | Components Found | Top Component | Processing Time |
|---------|------------------|---------------|-----------------|
| 1500 characters | 225 | 一 (1.47) | ~2 seconds |
| 9933 characters (full) | 333 | 一 (1.76) | ~2 seconds |

The top components are similar, but scores and rankings shift slightly when analyzing the full dataset.

## Integration with Deck Generation

This data can be used in `generate_tian_v1_fast.py` to:
1. Order radicals by productivity score (most useful first)
2. Filter out rare/unproductive components
3. Create a more pedagogically sound learning progression

## References

- HanziCraft Productive Components: https://hanzicraft.com/lists/productive-components
- Jun Da Character Frequency List (9933 characters)
- Hanzipy library for character decomposition
