# Migration Plan: Validation Scripts → Unit Tests

This document tracks the migration of ad-hoc validation scripts to proper unit tests.

## Status

- ✅ **Completed**: Core utilities and data generation have unit tests
- 🚧 **In Progress**: None currently
- 📋 **Todo**: Migrate validation scripts below

## Scripts to Migrate

### Priority 1: Critical Validation

These scripts validate core functionality and should be converted first:

| Script | Purpose | Target Test File | Status |
|--------|---------|------------------|--------|
| `verify_final_sorting.py` | Validates sorting order | `test_sorting.py` | 📋 Todo |
| `verify_anki_deck.py` | Validates deck structure | `test_deck_creation.py` | 📋 Todo |
| `verify_stroke_counts.py` | Validates stroke data | `test_data_validation.py` | 📋 Todo |

### Priority 2: Data Validation

These scripts check data integrity:

| Script | Purpose | Target Test File | Status |
|--------|---------|------------------|--------|
| `check_zero_components.py` | Check hanzi without components | `test_data_validation.py` | 📋 Todo |
| `check_hanzi_per_level.py` | Validate level distribution | `test_data_validation.py` | 📋 Todo |
| `check_multi_char_vocab.py` | Check multi-character words | `test_data_validation.py` | 📋 Todo |
| `verify_vocabulary_levels.py` | Validate vocab level assignment | `test_sorting.py` | 📋 Todo |
| `verify_dynamic_levels.py` | Validate dynamic level system | `test_sorting.py` | 📋 Todo |

### Priority 3: Analysis Tools

These can remain as scripts but should be refactored for better maintainability:

| Script | Purpose | Action | Status |
|--------|---------|--------|--------|
| `analyze_hsk_components.py` | Component analysis | Keep as script | ✅ Done |
| `show_levels.py` | Display levels | Keep as script | ✅ Done |
| `show_stroke_stats.py` | Stroke statistics | Keep as script | ✅ Done |
| `analyze_hsk_scores.py` | Score analysis | Keep as script | ✅ Done |

### Priority 4: Debug Scripts

These are one-off scripts and can be removed after verification:

| Script | Purpose | Action | Status |
|--------|---------|--------|--------|
| `debug_breakpoint_mismatch.py` | Debug specific issue | Archive | 📋 Todo |
| `find_level_1_eligible.py` | Find eligible items | Archive | 📋 Todo |
| `level_summary.py` | Summary stats | Merge into analysis | 📋 Todo |

## Migration Guidelines

### 1. Converting a Validation Script

**Before** (`scripts/validation/verify_something.py`):
```python
#!/usr/bin/env python3
import pandas as pd

print("Checking something...")
df = pd.read_csv('data/hanzi.csv')
if len(df) > 0:
    print("✅ Looks good")
else:
    print("❌ Problem found")
```

**After** (`tests/test_data_validation.py`):
```python
import pytest
import pandas as pd

@pytest.mark.integration
def test_something_is_valid(temp_data_dir):
    """Test that something is valid in the data"""
    # Setup test data
    df = pd.DataFrame([...])
    df.to_csv(temp_data_dir / "hanzi.csv")
    
    # Load and validate
    result = validate_something(temp_data_dir)
    
    # Assert expectations
    assert result.is_valid()
    assert len(result.issues) == 0
```

### 2. Benefits of Migration

- **Automated**: Tests run automatically on changes
- **Isolated**: Each test is independent
- **Fast**: Mocked dependencies run quickly  
- **CI/CD**: Can integrate with GitHub Actions
- **Regression**: Catch bugs before they ship

### 3. Test Organization

Create logical test files:

- `test_data_validation.py` - Data integrity checks
- `test_sorting.py` - Dependency sorting logic
- `test_deck_creation.py` - Anki deck generation
- `test_integration.py` - End-to-end workflows

### 4. When to Keep as Script

Keep as standalone script if:
- It's primarily for human inspection (analysis)
- It has complex interactive output
- It's used infrequently for debugging
- It requires special data files not in repo

## Timeline

### Phase 1 (Current)
- ✅ Set up pytest infrastructure
- ✅ Create test fixtures and utilities
- ✅ Write tests for core utilities
- ✅ Write tests for data generation

### Phase 2 (Next)
- 📋 Add tests for sorting logic
- 📋 Add tests for deck creation
- 📋 Add data validation tests
- 📋 Refactor key validation scripts

### Phase 3 (Future)
- 📋 Add integration tests
- 📋 Set up CI/CD pipeline
- 📋 Add test coverage reports
- 📋 Archive obsolete debug scripts

## Contributing

Want to help with migration? See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Writing tests
- Test structure
- Running tests
- Submitting PRs

Focus on **Priority 1** scripts first as they validate the most critical functionality.
