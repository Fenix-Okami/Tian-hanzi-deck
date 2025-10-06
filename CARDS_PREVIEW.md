# Card Preview

This document shows what the cards will look like in Anki.

## 1. Radical Cards (Blue Theme)

### Front Side
```
┌─────────────────────────────────┐
│         Radical                 │
│                                 │
│           一                    │
│                                 │
│  What is the meaning of this    │
│         radical?                │
│                                 │
└─────────────────────────────────┘
```

### Back Side
```
┌─────────────────────────────────┐
│         Radical                 │
│                                 │
│           一                    │
│                                 │
│  What is the meaning of this    │
│         radical?                │
│─────────────────────────────────│
│                                 │
│          Ground                 │
│                                 │
│      Mnemonic:                  │
│  This radical is a single       │
│  horizontal line, like the      │
│  ground beneath your feet.      │
│                                 │
└─────────────────────────────────┘
```

**Style**: Blue color (#0af), large character (100px)

---

## 2. Hanzi Cards (Pink Theme)

### Front Side
```
┌─────────────────────────────────┐
│          Hanzi                  │
│                                 │
│           人                    │
│                                 │
│  What is the meaning and        │
│         reading?                │
│                                 │
└─────────────────────────────────┘
```

### Back Side
```
┌─────────────────────────────────┐
│          Hanzi                  │
│                                 │
│           人                    │
│                                 │
│  What is the meaning and        │
│         reading?                │
│─────────────────────────────────│
│                                 │
│         Person                  │
│          rén                    │
│                                 │
│      Radicals:                  │
│      人 (person)                │
│                                 │
│      Mnemonic:                  │
│  A person standing with two     │
│  legs spread apart.             │
│                                 │
└─────────────────────────────────┘
```

**Style**: Pink color (#f0a), large character (100px), includes radicals breakdown

---

## 3. Vocabulary Cards (Purple Theme)

### Front Side
```
┌─────────────────────────────────┐
│       Vocabulary                │
│                                 │
│          今天                   │
│                                 │
│  What is the meaning and        │
│         reading?                │
│                                 │
└─────────────────────────────────┘
```

### Back Side
```
┌─────────────────────────────────┐
│       Vocabulary                │
│                                 │
│          今天                   │
│                                 │
│  What is the meaning and        │
│         reading?                │
│─────────────────────────────────│
│                                 │
│          Today                  │
│        jīn tiān                 │
│                                 │
│      Characters:                │
│    今 (now) + 天 (day)          │
│                                 │
│      Example:                   │
│  今天天气很好。                  │
│  (The weather is nice today.)   │
│                                 │
│      Mnemonic:                  │
│  The "now" day is today!        │
│                                 │
└─────────────────────────────────┘
```

**Style**: Purple color (#a0f), medium character (80px), includes examples

---

## Card Type Colors

| Card Type | Color | Hex Code | Purpose |
|-----------|-------|----------|---------|
| Radical | Blue | #0af | Building blocks recognition |
| Hanzi | Pink | #f0a | Character learning |
| Vocabulary | Purple | #a0f | Word/phrase learning |

---

## Learning Flow

The deck is designed to follow this learning progression:

```
1. Radicals (Building Blocks)
   ↓
   Learn basic components
   
2. Hanzi (Characters)
   ↓
   Combine radicals to form characters
   Learn meanings and readings
   
3. Vocabulary (Words)
   ↓
   Combine characters to form words
   Learn usage in context
```

---

## Mnemonic System

Each card includes mnemonics to help with memorization:

- **Radicals**: Visual or conceptual associations
- **Hanzi**: Stories connecting radicals to meaning
- **Vocabulary**: Contextual or character-based associations

The mnemonic system is inspired by WaniKani's approach to make learning more memorable and engaging.

---

## Card Statistics

Based on example data:

| Category | Count | Average Fields |
|----------|-------|---------------|
| Radicals | 5 | 3 fields |
| Hanzi | 5 | 5 fields |
| Vocabulary | 4 | 6 fields |
| **Total** | **14** | - |

---

## Anki Import Structure

When imported into Anki, the deck structure will be:

```
Tian Hanzi Deck
├── 1_Radicals (5 cards)
├── 2_Hanzi (5 cards)
└── 3_Vocabulary (4 cards)
```

The numbering ensures the correct study order.

---

## Customization

You can customize:

- **CSS**: Edit the `css` parameter in each model (create_deck.py)
- **Colors**: Change hex codes in the CSS
- **Font sizes**: Adjust px values
- **Layout**: Modify the HTML templates (qfmt/afmt)
- **Fields**: Add or remove fields in the model definition

See USAGE.md for more details on customization.
