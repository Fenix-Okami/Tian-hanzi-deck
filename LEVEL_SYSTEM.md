# Level-Based Learning System

## Overview

The Tian Hanzi Deck uses a **dependency-based leveling system** that ensures you always learn the building blocks before encountering complex characters. This mimics how WaniKani teaches kanji - you learn radicals first, then characters that use those radicals, then words using those characters.

## How Levels Work

### Radicals (Levels 1-57)
- **5 radicals per level**
- 285 total radicals ÷ 5 = 57 levels
- These are the atomic building blocks of characters

### Hanzi (Levels 1-57)
- Each hanzi is assigned to a level based on its **most advanced radical**
- A hanzi can only appear at a level if ALL its component radicals have been introduced in previous levels
- Example:
  - Level 1 hanzi: 的, 一, 日, 白 (use only Level 1 radicals)
  - Level 5 hanzi: 这, 们, 中 (may use radicals from Levels 1-5)

### Vocabulary (Levels 1-58)
- Each word is assigned to a level based on its **most advanced hanzi**
- A word can only appear at a level if ALL its component hanzi have been introduced in previous levels
- Example:
  - Level 1 vocab: 一旦 (uses hanzi from Level 1)
  - Level 5 vocab: 我们 (uses hanzi from Levels 4-5)

## Learning Progression

```
Level 1:
  ├─ Radicals: 白 勹 丶 一 日
  ├─ Hanzi: 的 一 日 白 百 旦
  └─ Vocabulary: 一旦

Level 2:
  ├─ Radicals: 龰 丿 卜 ㇇ 亅
  ├─ Hanzi: 是 不 了 下 丁
  └─ Vocabulary: 一下

Level 3:
  ├─ Radicals: 𠂇 亻 土 人 月
  ├─ Hanzi: 在 人 有 但 明 月 且 今 土 伯 ...
  └─ Vocabulary: 今日 但是 坦白 明白
```

## Benefits

### 1. Natural Learning Curve
You never encounter a character without knowing its components first. This:
- Reduces cognitive load
- Makes mnemonics more effective
- Provides immediate visual recognition patterns

### 2. Progressive Difficulty
Early levels have:
- Fewer hanzi (Level 1: 6 hanzi)
- Simpler characters
- Basic vocabulary

Later levels have:
- More hanzi (Level 10: 61 hanzi)
- Complex characters with many components
- Advanced vocabulary

### 3. Built-in Review
When you learn a new hanzi, you're automatically reviewing the radicals it contains. When you learn new vocabulary, you're reviewing the hanzi.

## Statistics

### Distribution
- **Radicals**: Evenly distributed (5 per level)
- **Hanzi**: Variable (6-61 per level, avg 26.3)
- **Vocabulary**: Variable (1-31 per level in first 10, avg 28.3)

### Total Content
- 57 radical levels
- 57 hanzi levels (parallel to radicals)
- 58 vocabulary levels (one extra for advanced words)
- **3,428 total cards**

## Example: Level 5 Breakdown

### Radicals (5 new)
辶, 文, 门, 口, 木

### Hanzi (42 characters using radicals from Levels 1-5)
这, 们, 中, 可, 还, 本, 间, 问, 文, 体, 开, 叶, 时, 加, 门, 吃, 听, 只, 古, 占, 台, 卡, 右, 另, 只, 号, 句, 叫, 司, 史, 召, 可, 句, 号, 各, 另, 只, 吉, 吊, 右, 台, 占

### Vocabulary (11 words using hanzi from Levels 1-5)
我们, 末日, 保卫, 含有, 这个, 不可, 五月天, 右手, 左右, 史上, 人中

## Implementation

The sorting is performed by `sort_by_dependencies.py`:

```python
# Assign radical levels (5 per level)
radicals['level'] = (position // 5) + 1

# Assign hanzi levels (max of component radical levels)
for each hanzi:
    level = max(radical_level for each component radical)

# Assign vocab levels (max of component hanzi levels)
for each word:
    level = max(hanzi_level for each character)
```

## Future Improvements

While the current system ensures dependencies are met, future versions could:

1. **Balance level sizes** - Distribute hanzi more evenly across levels
2. **Consider frequency** - Prioritize more common characters within each level
3. **Phonetic grouping** - Group characters with similar pronunciations
4. **Semantic clustering** - Group related concepts together
5. **Difficulty scoring** - Account for stroke count and visual complexity

## Verification

To verify the sorting is correct:

```bash
python verify_sorting.py
```

This checks that:
- ✓ Every hanzi uses only radicals from its level or earlier
- ✓ Every word uses only hanzi from its level or earlier

To view level details:

```bash
python show_levels.py
```
