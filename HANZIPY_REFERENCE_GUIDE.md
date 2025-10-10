# Hanzipy Reference Guide

A quick reference guide for using the Hanzipy library for Chinese character and NLP processing.

## Table of Contents
- [Installation](#installation)
- [Setup](#setup)
- [Dictionary Module](#dictionary-module)
- [Decomposer Module](#decomposer-module)
- [Data Sources](#data-sources)

---

## Installation

```python
pip install hanzipy
```

---

## Setup

**Always start by importing and initializing both modules:**

```python
# Import decomposer
from hanzipy.decomposer import HanziDecomposer
decomposer = HanziDecomposer()

# Import dictionary
from hanzipy.dictionary import HanziDictionary
dictionary = HanziDictionary()
```

---

## Dictionary Module

The `dictionary` module provides dictionary entries, definitions, pinyin, frequency data, and phonetic regularity analysis.

### 1. `definition_lookup(character/word, script_type=None)`

**Purpose:** Returns dictionary entries for a character or word.

**Parameters:**
- `character/word` (string): The Chinese character(s) to look up
- `script_type` (optional): `"simplified"` or `"traditional"`

**Returns:** List of dictionary entry objects with:
- `traditional`: Traditional form
- `simplified`: Simplified form
- `pinyin`: Romanization
- `definition`: English definition

**Examples:**

```python
# Basic lookup
dictionary.definition_lookup("雪")
# Returns: [
#     {"traditional": "雪", "simplified": "雪", "pinyin": "Xue3", "definition": "surname Xue"},
#     {"traditional": "雪", "simplified": "雪", "pinyin": "xue3", "definition": "snow/CL:場|场[chang2]/(literary) to wipe away (a humiliation etc)"}
# ]

# Specify script type
dictionary.definition_lookup("這", "traditional")
# Returns entries for the traditional form
```

---

### 2. `dictionary_search(characters, search_type=None)`

**Purpose:** Searches the dictionary for all entries containing the specified characters.

**Parameters:**
- `characters` (string): Character(s) to search for
- `search_type` (optional):
  - `None` (default): Returns all entries containing the characters
  - `"only"`: Returns only entries using exclusively the specified characters (no additional characters)

**Returns:** List of matching dictionary entries

**Examples:**

```python
# Find all words containing "雪"
dictionary.dictionary_search("雪")
# Returns: [
#     {"traditional": "下雪", "simplified": "下雪", "pinyin": "xia4 xue3", "definition": "to snow"},
#     {"traditional": "冰雪", "simplified": "冰雪", "pinyin": "bing1 xue3", "definition": "ice and snow"},
#     ... (many more results)
# ]

# Find words composed ONLY of the characters provided
dictionary.dictionary_search("心的小孩真", "only")
# Returns: [
#     {"traditional": "孩", "simplified": "孩", "pinyin": "hai2", "definition": "child"},
#     {"traditional": "小孩", "simplified": "小孩", "pinyin": "xiao3 hai2", "definition": "child/CL:個|个[ge4]"},
#     {"traditional": "小心", "simplified": "小心", "pinyin": "xiao3 xin1", "definition": "to be careful/to take care"},
#     ... (only words using these characters)
# ]
```

---

### 3. `get_examples(character)`

**Purpose:** Returns example words/phrases containing the character, sorted by frequency.

**Parameters:**
- `character` (string): The character to find examples for

**Returns:** Dictionary with three frequency categories:
- `high_frequency`: Most common words
- `mid_frequency`: Moderately common words
- `low_frequency`: Less common words

**Frequency determined by:** Leiden University corpus compared to dictionary search results

**Example:**

```python
dictionary.get_examples("橄")
# Returns: {
#     "high_frequency": [
#         {"traditional": "橄欖", "simplified": "橄榄", "pinyin": "gan3 lan3", "definition": "Chinese olive/olive"},
#         {"traditional": "橄欖油", "simplified": "橄榄油", "pinyin": "gan3 lan3 you2", "definition": "olive oil"}
#     ],
#     "mid_frequency": [
#         {"traditional": "橄欖球", "simplified": "橄榄球", "pinyin": "gan3 lan3 qiu2", "definition": "football played with oval-shaped ball..."}
#     ],
#     "low_frequency": [
#         {"traditional": "橄欖枝", "simplified": "橄榄枝", "pinyin": "gan3 lan3 zhi1", "definition": "olive branch/symbol of peace"}
#     ]
# }
```

---

### 4. `get_pinyin(character)`

**Purpose:** Returns all possible pinyin pronunciations for a character.

**Parameters:**
- `character` (string): Single Chinese character

**Returns:** List of pinyin strings

**Example:**

```python
dictionary.get_pinyin("的")
# Returns: ["de5", "di1", "di2", "di4"]
```

---

### 5. `get_character_frequency(character)`

**Purpose:** Returns frequency data for a character based on the Junda corpus.

**Parameters:**
- `character` (string): Single character (accepts both traditional and simplified)

**Returns:** Dictionary with:
- `number`: Rank in frequency list
- `character`: The character (simplified)
- `count`: Occurrence count in corpus
- `percentage`: Frequency percentage
- `pinyin`: Pronunciation
- `meaning`: English meaning

**Example:**

```python
dictionary.get_character_frequency("热")
# Returns: {
#     "number": 606,
#     "character": "热",
#     "count": "67051",
#     "percentage": "79.8453694124",
#     "pinyin": "re4",
#     "meaning": "heat/to heat up/fervent/hot (of weather)/warm up"
# }
```

---

### 6. `get_character_in_frequency_list_by_position(position)`

**Purpose:** Gets a character by its position in the frequency list.

**Parameters:**
- `position` (int): Position in frequency list (1-9933, based on Junda Frequency list)

**Returns:** Dictionary with frequency data (same format as `get_character_frequency`)

**Example:**

```python
dictionary.get_character_in_frequency_list_by_position(111)
# Returns: {
#     "number": 111,
#     "character": "机",
#     "count": "339823",
#     "percentage": "43.7756134862",
#     "pinyin": "ji1",
#     "meaning": "machine/opportunity/secret"
# }
```

---

### 7. `determine_phonetic_regularity(decomposition_object/character)`

**Purpose:** Analyzes the phonetic relationship between a character and its components.

**Parameters:**
- Input: Either a character string OR a decomposition object from `decomposer.decompose()`

**Returns:** Dictionary organized by pronunciation, showing:
- `character`: The analyzed character
- `component`: List of components
- `phonetic_pinyin`: Pinyin of each component
- `regularity`: Regularity score for each component

**Phonetic Regularity Scale:**
- **0** = No regularity
- **1** = Exact Match (with tone)
- **2** = Syllable Match (without tone)
- **3** = Similar in Initial (alliterates)
- **4** = Similar in Final (rhymes)

**Example:**

```python
dictionary.determine_phonetic_regularity("洋")
# Returns: {
#     "yang2": {
#         "character": "洋",
#         "component": ["氵", "羊", "羊", "氵", "羊", "羊"],
#         "phonetic_pinyin": ["shui3", "Yang2", "yang2", "shui3", "Yang2", "yang2"],
#         "regularity": [0, 1, 1, 0, 1, 1]
#     }
# }
```

---

## Decomposer Module

The `decomposer` module breaks down Chinese characters into their component parts.

### 1. `decompose(character, decomposition_type=None)`

**Purpose:** Decomposes a Chinese character into its components at various levels.

**Parameters:**
- `character` (string): Single Chinese character
- `decomposition_type` (optional):
  - `None` (default): Returns all levels
  - `1`: "Once" - decomposes character once only
  - `2`: "Radical" - decomposes into lowest radical components
  - `3`: "Graphical" - decomposes into lowest forms (strokes and small units)

**Returns:** 
- If `decomposition_type=None`: Dictionary with `once`, `radical`, and `graphical` keys
- If type specified: Dictionary with `character` and `components` keys

**Examples:**

```python
# Get all decomposition levels
decomposer.decompose("爱")
# Returns: {
#     "character": "爱",
#     "once": ["No glyph available", "友"],
#     "radical": ["爫", "冖", "𠂇", "又"],
#     "graphical": ["爫", "冖", "𠂇", "㇇", "㇏"]
# }

# Get only radical level decomposition
decomposer.decompose("爱", 2)
# Returns: {
#     "character": "爱",
#     "components": ["爫", "冖", "𠂇", "又"]
# }
```

---

### 2. `decompose_many(character_string, decomposition_type=None)`

**Purpose:** Decomposes multiple characters at once and returns one combined object.

**Parameters:**
- `character_string` (string): String of Chinese characters
- `decomposition_type` (optional): Same as `decompose()` - 1, 2, or 3

**Returns:** Dictionary where each key is a character with its decomposition data

**Example:**

```python
decomposer.decompose_many("爱橄黃")
# Returns: {
#     "爱": {
#         "character": "爱",
#         "once": ["No glyph available", "友"],
#         "radical": ["爫", "冖", "𠂇", "又"],
#         "graphical": ["爫", "冖", "𠂇", "㇇", "㇏"]
#     },
#     "橄": {
#         "character": "橄",
#         "once": ["木", "敢"],
#         "radical": ["木", "No glyph available", "耳", "⺙"],
#         "graphical": ["一", "丨", "八", "匚", "二", "丨", "二", "丿", "一", "乂"]
#     },
#     "黃": {
#         "character": "黃",
#         "once": ["廿", "No glyph available"],
#         "radical": ["黃"],
#         "graphical": ["卄", "一", "一", "二", "丨", "凵", "八"]
#     }
# }
```

---

### 3. `component_exists(character/component)`

**Purpose:** Check if a component or character exists in the decomposition data.

**Parameters:**
- `character/component` (string): Component or character to check

**Returns:** Boolean (`True` or `False`)

**Examples:**

```python
decomposer.component_exists("乂")
# Returns: True

decomposer.component_exists("$")
# Returns: False
```

---

### 4. `get_characters_with_component(component)`

**Purpose:** Find all characters that contain a specific component.

**Parameters:**
- `component` (string): Component to search for

**Returns:** List of characters containing the component

**Note:** Bound forms (e.g., 手 and 扌) are treated as the same component.

**Example:**

```python
decomposer.get_characters_with_component("囗")
# Returns: ["国", "因", "西", "回", "口", "四", "团", "图", "围", "困", "固", "园", 
#           "圆", "圈", "囚", "圃", "囤", "囿", "囡", "囫", "圜", "囵", "囹", "圄", 
#           "囝", "圉", "圊", "釦"]
```

---

### 5. `get_radical_meaning(radical)`

**Purpose:** Returns the meaning of a radical.

**Parameters:**
- `radical` (string): Chinese radical

**Returns:** String (usually one-word meaning)

**Example:**

```python
decomposer.get_radical_meaning("氵")
# Returns: "water"
```

---

## Data Sources

Hanzipy uses data from the following sources:

- **[CC-CEDICT](http://cc-cedict.org/wiki/)**: Dictionary definitions
- **[Gavin Grover's Decomposition Data](http://cjkdecomp.codeplex.com/license)**: Character decomposition
- **[Hanzi (nieldlr)](https://github.com/nieldlr/hanzi)**: Character decomposition and radical data
- **[Leiden Word Frequency Data](http://lwc.daanvanesch.nl/legal.php)**: Word frequency corpus
- **[Jun Da Character Frequency Data](http://lingua.mtsu.edu/chinese-computing/copyright.html)**: Character frequency

---

## Quick Tips

1. **Always initialize both modules** at the start of your program
2. **Script agnostic**: Most functions work with both simplified and traditional characters
3. **Phonetic regularity** is useful for understanding character components and learning patterns
4. **Frequency data** helps prioritize which words/characters to learn first
5. **Component search** is great for exploring characters by radical or structure
6. **"only" search mode** is perfect for finding compound words made from specific characters

---

## Common Use Cases

### Learning New Characters
```python
# Get definition and frequency
definition = dictionary.definition_lookup("学")
frequency = dictionary.get_character_frequency("学")
examples = dictionary.get_examples("学")

# Understand structure
decomposition = decomposer.decompose("学")
phonetic_info = dictionary.determine_phonetic_regularity("学")
```

### Building Vocabulary Lists
```python
# Find common words with a character
high_freq_words = dictionary.get_examples("水")["high_frequency"]

# Search for specific character combinations
words = dictionary.dictionary_search("水火", "only")
```

### Analyzing Character Components
```python
# Break down into radicals
parts = decomposer.decompose("想", 2)

# Find similar characters
similar = decomposer.get_characters_with_component("心")

# Get radical meaning
meaning = decomposer.get_radical_meaning("心")
```

---

*This reference guide is based on Hanzipy, which was translated from the awesome library by nieldlr: https://github.com/nieldlr/hanzi*
