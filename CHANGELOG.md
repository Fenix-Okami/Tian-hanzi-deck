# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-10-10

### 🎯 Major Release: HSK-Based Deck with Complete Overhaul

Complete redesign of the deck generation pipeline with HSK alignment, surname handling, improved card layouts, and proper dependency-based sorting.

#### ✨ New Features

**HSK-Based Deck (Now Default)**
- Generated from actual HSK 1-3 vocabulary (2,227 words)
- Extracts only hanzi used in HSK words (899 characters)
- Identifies productive components scientifically (233 radicals)
- 40% fewer characters, 36% more vocabulary than frequency approach
- Direct HSK exam alignment for focused studying

**Surname Handling**
- Added `is_surname` boolean field to hanzi and vocabulary
- Removed surname text from definitions (e.g., "surname Zhong" removed)
- Cleaner, more focused meanings
- Surname information preserved as metadata flag

**Improved Card Layouts**
- **Hanzi cards**: Reordered sections (Meaning → Audio → Meaning Mnemonic → Reading Mnemonic → Components at bottom)
- **Vocabulary cards**: Reordered sections (Meaning → Audio → Example → Character Breakdown at bottom)
- **Components**: Formatted with meanings - "一 (one), 口 (mouth), 丨 (line)"
- **Character breakdown**: Space-separated without "+" (故 事, not 故 + 事)
- Both meaning and reading mnemonics displayed for hanzi

**Ruby Text & Pinyin**
- Per-character ruby text for vocabulary cards
- Pinyin displayed above individual characters (not whole word)
- Proper `ruby-position: over` CSS for correct positioning
- Bold, larger pinyin (24-28px) with proper spacing

**Smart Multi-Level Sorting**
- Sort order: Level → HSK Level → Frequency/Simplicity
- Hanzi sorted by: Level → HSK → Component count (simpler first)
- Vocabulary sorted by: Level → HSK → Frequency position (common first)
- Ensures optimal learning progression within each level

**Data Quality**
- All definitions from CC-CEDICT (semicolon-separated)
- Integer HSK levels (not floats) using Int64 dtype
- Pipe-separated components (`口|丨` not `口 + 丨`)
- Fixed component parsing (was using wrong separator)

**Three Subdecks**
- `1. Radicals` (233 cards, brown theme)
- `2. Hanzi` (899 cards, green theme)
- `3. Vocabulary` (2,227 cards, blue theme)

#### 🔧 Technical Improvements

**New Scripts**
- `generate_hsk_deck.py` - HSK-based data extraction
- `sort_hsk_by_dependencies.py` - Dependency-based level assignment
- `create_hsk_deck.py` - Three-subdeck Anki package creation
- `analyze_hsk_components.py` - Component productivity analysis
- `create_samples.py` - Sample CSVs and HTML card previews
- `run_hsk_pipeline.sh` - Automated 3-step pipeline

**Data Files**
- `vocabulary.csv/parquet` - 2,227 HSK 1-3 words with is_surname field
- `hanzi.csv/parquet` - 899 characters with is_surname field
- `radicals.csv/parquet` - 233 productive components
- Both CSV and Parquet formats for flexibility

**Utilities**
- `clean_surname_from_definition()` - Remove surname text, return boolean
- `format_components_with_meanings()` - Format components with their meanings
- `create_ruby_text()` - Per-character pinyin ruby text
- Improved Windows UTF-8 console handling

#### 🐛 Bug Fixes

**Fixed Dependency Parsing**
- Components now correctly parsed with `|` separator (was using ` + `)
- All hanzi now properly distributed across levels (was: all at level 1)
- All vocabulary now properly distributed across levels (was: all at level 3)
- Dependency-based sorting now actually works!

**Card Template Fixes**
- Removed redundant "What is" text from card fronts
- Fixed ruby text positioning (above, not below characters)
- Removed unnecessary "+" separators from character breakdowns
- Components moved to bottom for better focus on meaning first

#### 📊 Statistics

**HSK 1-3 Deck**
- Total cards: 3,359 (233 radicals + 899 hanzi + 2,227 vocabulary)
- Total levels: 50 dependency-based levels
- Radicals: Levels 1-47 (5 per level)
- Hanzi: Levels 2-48 (distributed by component complexity)
- Vocabulary: Levels 3-50 (distributed by character complexity)

**Performance**
- Generation: ~30 seconds
- Sorting: ~5 seconds
- Deck creation: ~10 seconds
- Total pipeline: ~45 seconds

#### 📝 Documentation

**Updated**
- `README.md` - Complete rewrite with HSK focus
- `CHANGELOG.md` - This comprehensive changelog
- `.github/copilot-instructions.md` - Development guidelines

**Existing Guides** (still relevant)
- `HSK_PIPELINE_QUICKSTART.md` - Step-by-step guide
- `HSK_DECK_GENERATION_GUIDE.md` - Methodology details
- `LEVEL_SYSTEM.md` - Dependency level explanation
- `PRODUCTIVE_COMPONENTS_GUIDE.md` - Component scoring
- `HANZIPY_REFERENCE_GUIDE.md` - Library usage
- `PROJECT_STATUS.md` - Current state

#### 🗑️ Removed

**Obsolete Files** (frequency-based approach)
- Removed: `generate_tian_v1.py`, `generate_tian_v1_fast.py`
- Removed: `sort_by_dependencies.py` (replaced by `sort_hsk_by_dependencies.py`)
- Removed: `create_deck_from_parquet.py` (replaced by `create_hsk_deck.py`)
- Removed: `create_deck.py` (obsolete)
- Removed: Various V1-era test files

**Kept for Reference**
- `hsk_scorer.py` - HSK scoring system (all levels 1-9)
- `analyze_hsk_scores.py` - Score distribution analysis

#### ⚠️ Breaking Changes

- **Default deck is now HSK-based**, not frequency-based
- **Data column names changed**: `hanzi` (not `character`), `components` (not `radicals`)
- **File names cleaned**: No more `hsk1_2_3_` prefixes
- **Sorting order changed**: Now Level → HSK → Frequency (was just Level)
- **is_surname field added**: May affect tools parsing the data

---

## [1.0.0] - 2025-10-08

### ⚠️ Prototype Release - Tian Hanzi Deck v1

**Note:** This is an experimental prototype release. Mnemonics are auto-generated and card ordering needs refinement. Use with caution.

#### Added
- **Prototype deck with 3,428 cards**
  - 285 Radical cards
  - 1,500 Hanzi cards (top frequency characters)
  - 1,643 Vocabulary cards (high-frequency words)

- **Automated generation using Hanzipy**
  - `generate_tian_v1.py` / `generate_tian_v1_fast.py` - Data generation
  - `create_deck_from_parquet.py` - Builds Anki package
  - `parquet_utils.py` - Data utilities
  - `Tian_Hanzi_Deck_v1.apkg` - Ready-to-import Anki deck

- **Frequency-based character selection**
  - Top 1,500 hanzi by usage frequency
  - Common vocabulary words

- **Basic dependency system**
  - Radicals before hanzi
  - Hanzi before vocabulary
  - Initial level assignments

- **Documentation**
  - `README.md` - Project overview
  - `QUICKSTART.md` - Getting started guide
  - Basic setup instructions

#### Known Issues (v1)
- Mnemonics are auto-generated and not optimized
- Card ordering algorithm needs refinement
- Quality varies between cards
- No HSK alignment
- Frequency-based approach includes unnecessary characters

---

## Development Notes

### Version Numbering
- **Major versions** (2.0.0): Complete redesign or breaking changes
- **Minor versions** (2.1.0): New features, significant improvements
- **Patch versions** (2.0.1): Bug fixes, minor tweaks

### Current Status
The project is now in a stable state with HSK-based generation as the default. Future improvements will focus on:
- Better mnemonic generation
- Additional HSK levels (4-6)
- Audio integration
- Example sentence improvements
