# Card Preview Guide

## Overview

Three HTML preview files have been created to show how the Anki cards will look:

1. **`preview_radical_card.html`** - Radical/Component cards
2. **`preview_hanzi_card.html`** - Character cards
3. **`preview_vocabulary_card.html`** - Vocabulary/Word cards

## How to View

Open any of these files in your web browser:
- Double-click the HTML file in Windows Explorer
- Or drag and drop into your browser
- Or right-click → Open with → Your browser

## Card Types

### 1. Radical Cards (Components)

**Color Theme:** Brown (#8B4513)

**Front Side:**
- Card type label: "RADICAL / COMPONENT"
- Large radical character (120px)
- English meaning

**Back Side (Additional Info):**
- Productivity score (how many characters use this radical)
- Visual progress bar showing relative productivity
- Usage information and priority level
- Example characters that use this radical

**Examples shown:**
- 口 (mouth) - 143 characters - High priority
- 一 (one) - 161 characters - #1 most productive!

---

### 2. Hanzi Cards (Characters)

**Color Theme:** Green (#2E7D32)

**Front Side:**
- Card type label: "HANZI / CHARACTER"
- Large hanzi character (140px)
- Recognition test (no hints)

**Back Side (Full Information):**
- Character
- Pinyin pronunciation (with tone marks)
- English meaning
- **Component breakdown** showing radicals used (with meanings)
- **Mnemonic story** to help remember the character
- Full definition from dictionary

**Examples shown:**
- 吃 (chī - to eat) - Components: 口 (mouth) + 乞 (beg)
- 听 (tīng - to listen) - Components: 口 (mouth) + 斤 (axe)

---

### 3. Vocabulary Cards (Words)

**Color Theme:** Blue (#1976D2)

**Front Side:**
- Card type label: "VOCABULARY / WORD"
- Large vocabulary word (100px)
- Recognition test

**Back Side (Full Information):**
- Complete word
- Pinyin with spaces between syllables
- English meaning
- **Hanzi breakdown** showing each character with:
  - Individual pinyin
  - Individual meaning
- **Example sentences** with translations
- Full definition
- Frequency ranking and HSK level badge

**Examples shown:**
- 吃饭 (chī fàn - to eat a meal)
- 你好 (nǐ hǎo - hello)
- 学习 (xué xí - to study/learn)

## Design Features

### Visual Hierarchy
- Clear card type indicators at top
- Large, readable characters
- Progressive information disclosure
- Color-coded by card type

### Component Integration
- Radical cards show productivity scores
- Hanzi cards show component breakdown
- Vocabulary cards show hanzi breakdown
- All linked together pedagogically

### Learning Aids
- **Mnemonics** for characters (using components)
- **Example sentences** for vocabulary
- **Component meanings** to aid memory
- **Productivity scores** to prioritize learning

### HSK Integration
- HSK level badges on vocabulary cards
- Frequency position within HSK level
- Aligned with HSK 1-3 curriculum

## Card Progression

The three card types work together:

```
1. Learn RADICALS (口, 一, 日, etc.)
   ↓
2. Learn HANZI using those radicals (吃, 听, etc.)
   ↓
3. Learn VOCABULARY using those hanzi (吃饭, 你好, etc.)
```

This dependency-based progression ensures you always understand the components of what you're learning.

## Technical Details

### Styling
- Clean, modern card design
- Mobile-responsive layouts
- Subtle shadows and spacing
- Color-coded by card type
- Professional typography

### Information Density
- Front: Minimal (for recognition)
- Back: Rich context (for learning)
- Progressive disclosure model
- All information accessible but organized

### Accessibility
- High contrast text
- Clear fonts (Segoe UI)
- Logical information hierarchy
- Mobile-friendly sizes

## Next Steps

These preview files serve as:
1. **Design reference** for the actual Anki card templates
2. **User preview** to show learners what to expect
3. **Development guide** for card generation code

The actual Anki cards will use similar HTML/CSS but adapted for Anki's template system.
