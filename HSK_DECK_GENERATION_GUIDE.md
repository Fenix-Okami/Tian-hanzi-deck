# HSK-Based Deck Generation Guide

## Overview

Instead of using an arbitrary 1500-character frequency cutoff, this approach builds pedagogically sound decks by:

1. **Starting with HSK vocabulary** - Select words from specific HSK levels (e.g., HSK 1-3)
2. **Extracting actual hanzi used** - Identify all characters used in those vocabulary words
3. **Calculating productive components** - Determine which radicals/components appear in multiple characters
4. **Building with dependencies** - Create a deck with proper learning order

## Why This Approach?

### ✅ Advantages

- **Pedagogically sound**: Learn characters you'll actually use in real vocabulary
- **Goal-oriented**: Target specific HSK levels for exams or proficiency milestones
- **Efficient**: No wasted time on rare characters
- **Productive learning**: Focus on components that appear frequently
- **Natural progression**: Learn building blocks before complex characters

### ❌ Problems with Arbitrary Frequency

- May include characters not in HSK vocabulary
- May miss important HSK characters
- No alignment with learning goals
- Doesn't consider actual word usage

## HSK 1-3 Deck Statistics

Based on actual HSK 3.0 data:

| Metric | Count | Description |
|--------|-------|-------------|
| **Vocabulary** | 2,227 words | All words from HSK 1-3 frequency lists |
| **Hanzi** | 899 characters | Unique characters used in those words |
| **Components** | 233 radicals | Building blocks with productivity scores |

### Vocabulary Distribution

- **HSK 1**: 497 words (beginner essentials)
- **HSK 2**: 764 words (elementary level)
- **HSK 3**: 966 words (intermediate level)

### Top Productive Components

Components ranked by how many characters use them:

| Component | Meaning | Used In | Productivity Score |
|-----------|---------|---------|-------------------|
| 一 | one | 161 characters | 161 |
| 口 | mouth | 143 characters | 143 |
| 丨 | line | 89 characters | 89 |
| 丶 | dot | 51 characters | 51 |
| 日 | sun/day | 49 characters | 49 |
| 人/亻 | human | 48 characters each | 48 |
| 木 | tree | 48 characters | 48 |
| 二 | two | 47 characters | 47 |
| 十 | ten | 44 characters | 44 |
| 丿 | bend | 42 characters | 42 |

## Usage

### Generate HSK 1-3 Deck

```bash
python generate_hsk_deck.py
```

This creates six files in the `data/` directory:

1. **`hsk1_2_3_vocabulary.csv`** - All vocabulary with pinyin and meanings
2. **`hsk1_2_3_vocabulary.parquet`** - Same data in efficient Parquet format
3. **`hsk1_2_3_hanzi.csv`** - All characters with components
4. **`hsk1_2_3_hanzi.parquet`** - Same data in Parquet format
5. **`hsk1_2_3_components.csv`** - Components with productivity scores
6. **`hsk1_2_3_components.parquet`** - Same data in Parquet format

### Customize HSK Levels

Edit the `main()` function in `generate_hsk_deck.py`:

```python
# For HSK 1-3 (default)
builder = HSKDeckBuilder(hsk_levels=[1, 2, 3])

# For HSK 1-2 (beginner only)
builder = HSKDeckBuilder(hsk_levels=[1, 2])

# For HSK 1-6 (comprehensive)
builder = HSKDeckBuilder(hsk_levels=[1, 2, 3, 4, 5, 6])

# For specific levels
builder = HSKDeckBuilder(hsk_levels=[4, 5])
```

## Data Files

### Vocabulary CSV Format

```csv
word,hsk_level,frequency_position,pinyin,meaning
的,1,1,de,"of/~'s (possessive particle)..."
我,1,2,wǒ,"I/me/my"
你,1,3,nǐ,"you (informal)..."
```

**Columns:**
- `word`: Chinese word/phrase
- `hsk_level`: HSK level (1-6)
- `frequency_position`: Position in frequency-ranked list for that level
- `pinyin`: Romanization with tone marks
- `meaning`: English definition

### Hanzi CSV Format

```csv
hanzi,pinyin,meaning,components,component_count
一,yī,"one/1/single...",,0
七,qī,"seven/7","乚|一",2
不,bù,"(negative prefix)/not/no","一|丿|卜",3
```

**Columns:**
- `hanzi`: Chinese character
- `pinyin`: Romanization with tone marks
- `meaning`: English definition
- `components`: Pipe-separated list of components/radicals
- `component_count`: Number of components

### Components CSV Format

```csv
component,meaning,productivity_score,usage_count
一,one,161,161
口,mouth,143,143
丨,line,89,89
```

**Columns:**
- `component`: The radical/component character
- `meaning`: English meaning or description
- `productivity_score`: Number of different characters using this component
- `usage_count`: Same as productivity_score (for compatibility)

## Productivity Score Explained

The **productivity score** measures how useful a component is for learning:

- **High score** (100+): Learn this component early - it appears in many characters
- **Medium score** (20-99): Moderately useful component
- **Low score** (1-19): Rare component, less priority

### Example: 口 (mouth) - Score 143

The component 口 appears in 143 different characters in the HSK 1-3 vocabulary, including:
- 吃 (eat)
- 呢 (question particle)
- 喝 (drink)
- 叫 (call/be called)
- 听 (listen)
- 唱 (sing)
- And 137 more!

Learning 口 first helps you recognize and remember all these characters.

## Integration with Tian Deck Pipeline

This HSK-based data can be used to:

1. **Replace arbitrary frequency cutoff** - Use `hsk1_2_3_hanzi.csv` instead of "top 1500"
2. **Prioritize components** - Use productivity scores to order radical learning
3. **Create level-specific decks** - Generate separate decks for each HSK level
4. **Optimize dependencies** - Ensure high-productivity components are learned first
5. **Add HSK tags** - Tag cards with their HSK level for filtering

## Next Steps

### For HSK 1-3 Deck:
1. ✅ Generate HSK-based data with productivity scores
2. ⏳ Sort by dependencies (radicals → hanzi → vocabulary)
3. ⏳ Integrate with Anki deck creation
4. ⏳ Add mnemonics based on productive components
5. ⏳ Create leveled progression (HSK 1 → 2 → 3)

### Future Enhancements:
- Generate separate decks for each HSK level
- Combine productivity scores with frequency rankings
- Add vocabulary usage examples
- Include stroke order for high-productivity components
- Create "component family" groups (all characters using 口, etc.)

## Comparison with Original Approach

| Aspect | Original (Frequency) | New (HSK-Based) |
|--------|---------------------|-----------------|
| **Selection Method** | Top 1500 by frequency | Actual HSK 1-3 vocabulary |
| **Character Count** | 1500 characters | 899 characters (40% fewer!) |
| **Vocabulary** | ~1643 words | 2,227 words (36% more!) |
| **Alignment** | General frequency | HSK exam alignment |
| **Productivity** | Not calculated | 233 components scored |
| **Efficiency** | Some wasted learning | Learn only what's needed |
| **Goal** | General literacy | HSK 1-3 certification |

## Summary

The HSK-based approach is **more efficient** and **more goal-oriented** than arbitrary frequency cutoffs:

- **40% fewer characters** to learn (899 vs 1500)
- **36% more vocabulary** to practice (2227 vs 1643)
- **Direct HSK exam preparation**
- **Scientifically calculated** component productivity
- **No wasted effort** on rare characters

Perfect for learners targeting HSK certification or structured progression!
