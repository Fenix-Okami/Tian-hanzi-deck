# Contributing to Tian Hanzi Deck

Thank you for your interest in contributing! This document provides guidelines for development.

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Fenix-Okami/Tian-hanzi-deck.git
cd Tian-hanzi-deck
```

### 2. Set Up Python Environment

We recommend using Python 3.11 or later:

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### 3. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/tian_hanzi --cov-report=html

# Run specific test file
pytest tests/test_utilities.py -v

# Run tests with specific marker
pytest tests/ -m unit -v
```

### 4. Code Style

- Follow PEP 8 style guidelines
- Use descriptive variable names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose

## Project Structure

```
src/tian_hanzi/          # Main package
├── data_generator.py    # HSK data extraction logic
├── utils/              # Utility modules
└── __init__.py

tests/                   # Unit tests
├── conftest.py         # Pytest fixtures
├── test_utilities.py   # Utility tests
└── test_data_generation.py

scripts/                 # Utility scripts
├── analysis/           # Data analysis tools
├── validation/         # Validation scripts
└── legacy/            # Old test scripts
```

## Adding Tests

When adding new functionality, always include tests:

1. **Unit Tests** - For individual functions/classes
   - Use mocks to isolate dependencies
   - Test edge cases and error handling
   - Place in `tests/test_*.py`

2. **Integration Tests** - For full workflows
   - Test with real data files
   - Mark with `@pytest.mark.integration`
   - May require HSK data files

Example test:

```python
from unittest.mock import MagicMock

import pytest
from tian_hanzi.core.deck_pipeline import DeckBuilder, DeckBuildConfig


class TestMyFeature:
    @pytest.mark.unit
    def test_basic_functionality(self, monkeypatch):
        builder = DeckBuilder(
            DeckBuildConfig(hsk_levels=(1,), output_dir="/tmp"),
            dictionary=MagicMock(),
            decomposer=MagicMock(),
            stroke_counter=lambda _: 1,
        )
        monkeypatch.setattr(builder.repository, "load_vocabulary", lambda *_: [])
        monkeypatch.setattr(builder.repository, "load_hanzi_levels", lambda *_: {})
        monkeypatch.setattr(builder.repository, "extract_hanzi_from_vocabulary", lambda *_: set())
        result = builder.build()
        assert "vocabulary" in result

    @pytest.mark.integration
    def test_with_real_data(self, tmp_path):
        builder = DeckBuilder(DeckBuildConfig(output_dir=str(tmp_path)))
        builder.build()
        assert tmp_path.joinpath("vocabulary.csv").exists()
```

## Making Changes

### Workflow

1. Create a feature branch
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make your changes
   - Write code
   - Add tests
   - Update documentation

3. Test thoroughly
   ```bash
   pytest tests/ -v
   ```

4. Commit with clear messages
   ```bash
   git add .
   git commit -m "Add feature: description of change"
   ```

5. Push and create PR
   ```bash
   git push origin feature/my-feature
   ```

### Commit Messages

Use clear, descriptive commit messages:

- ✅ Good: "Add unit tests for pinyin converter edge cases"
- ✅ Good: "Fix bug in component productivity calculation"
- ❌ Bad: "Update files"
- ❌ Bad: "WIP"

## Areas for Contribution

### High Priority

1. **More Unit Tests** - Expand test coverage
   - Test sorting logic
   - Test deck creation
   - Test edge cases

2. **Refactor Validation Scripts** - Convert to unit tests
   - Move logic from `scripts/validation/` to `tests/`
   - Create proper test fixtures
   - Add assertions and error handling

3. **Documentation** - Improve docs
   - Add more examples
   - Document internal APIs
   - Create tutorials

### Medium Priority

4. **Performance Optimization**
   - Profile slow operations
   - Optimize data processing
   - Cache expensive operations

5. **CLI Improvements**
   - Better command-line interface
   - Progress bars
   - Better error messages

### Nice to Have

6. **Additional Features**
   - Support more HSK levels (4-9)
   - Custom vocabulary lists
   - Different card templates

## Code Review

All contributions require:
- ✅ Tests pass (`pytest tests/ -v`)
- ✅ No new warnings
- ✅ Documentation updated
- ✅ Clear commit messages

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about the codebase
- Documentation improvements

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).
