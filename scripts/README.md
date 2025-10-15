# Scripts Directory

This directory contains utility scripts organized by purpose.

## Directory Structure

### `analysis/`
Scripts for analyzing HSK data and components:
- `analyze_hsk_components.py` - Component productivity analysis
- `analyze_hsk_scores.py` - HSK score distribution
- `analyze_level_breakpoints.py` - Level breakpoint analysis
- `show_levels.py` - Display level distribution
- `show_stroke_stats.py` - Show stroke count statistics

### `validation/`
Scripts for validating data integrity and deck structure:
- `verify_*.py` - Various validation scripts for data and deck structure
- `check_*.py` - Data checking utilities
- `debug_*.py` - Debugging utilities
- `find_*.py` - Helper scripts to find specific data patterns
- `level_*.py` - Level-related validation

### `legacy/`
Old test scripts kept for reference (replaced by proper unit tests in `tests/`):
- `test_*.py` - Old-style test scripts

## Migration to Unit Tests

The validation scripts in `validation/` should eventually be converted to proper
unit tests in the `tests/` directory. For now, they remain available as standalone
scripts for quick validation during development.

## Usage

Most scripts can be run directly:

```bash
# Analysis
python scripts/analysis/analyze_hsk_components.py
python scripts/analysis/show_levels.py

# Validation
python scripts/validation/verify_final_sorting.py
python scripts/validation/verify_anki_deck.py
```

Note: Some scripts may require generated data files in the `data/` directory.
Generate them via the new CLI:

```bash
python -m tian_hanzi.cli deck build
```
