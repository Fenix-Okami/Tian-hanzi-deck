# Tian Hanzi Deck - CLI Setup Guide

## Quick Setup

### 1. Activate Virtual Environment

**On Windows (Git Bash/WSL):**
```bash
source venv/Scripts/activate
```

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

### 2. Install the CLI

Install the project in editable mode to enable the `tian-hanzi` command:

```bash
pip install -e .
```

This will:
- Install the `tian-hanzi` command globally (in your venv)
- Make all your code changes immediately available without reinstalling
- Install all required dependencies from `setup.py`

### 3. Verify Installation

Test that the CLI is working:

```bash
tian-hanzi --help
```

You should see:
```
Usage: tian-hanzi [OPTIONS] COMMAND [ARGS]...

  Tian Hanzi command line interface

Commands:
  deck       Build and manage Tian Hanzi decks.
  analyze    Analysis utilities for Tian Hanzi datasets.
  validate   Run validation routines against generated decks.
```

## Available Commands

### `tian-hanzi deck build`

Build a deck with automatic sample generation.

**Basic usage:**
```bash
tian-hanzi deck build
```

**Options:**
- `-l, --level INTEGER` - HSK levels to include (default: 1, 2, 3)
- `--hsk-data-dir PATH` - Directory containing raw HSK files (default: data/HSK-3.0)
- `--output-dir PATH` - Destination for generated artifacts (default: data)
- `--skip-samples` - Skip generating sample HTML previews

**Examples:**
```bash
# Build HSK 1-3 deck (default)
tian-hanzi deck build

# Build only HSK 1 and 2
tian-hanzi deck build -l 1 -l 2

# Build HSK 1-3 but skip sample generation
tian-hanzi deck build --skip-samples

# Build with custom output directory
tian-hanzi deck build --output-dir my_data
```

**What it does:**
1. Generates three data files:
   - `data/vocabulary.csv` and `.parquet`
   - `data/hanzi.csv` and `.parquet`
   - `data/radicals.csv` and `.parquet`

2. Automatically creates sample files (unless `--skip-samples`):
   - `data/radicals_sample.csv`
   - `data/hanzi_sample.csv`
   - `data/vocabulary_sample.csv`
   - `data/sample_radical_card.html`
   - `data/sample_hanzi_card.html`
   - `data/sample_vocabulary_card.html`
   - `data/sample_cards_combined.html`

**Note:** The generated data doesn't have `tian_level` yet. To add dependency-based levels, run the sorting script:
```bash
python sort_hsk_by_dependencies.py
```

### `tian-hanzi analyze`

Analysis utilities for deck data.

```bash
tian-hanzi analyze --help
```

**Available subcommands:**
- `distribution` - Generate distribution reports

### `tian-hanzi validate`

Validation utilities for generated decks.

```bash
tian-hanzi validate --help
```

## Full Pipeline

To generate a complete, sorted deck with all samples:

```bash
# 1. Generate initial data with samples
tian-hanzi deck build

# 2. Sort by dependencies (adds tian_level column)
python sort_hsk_by_dependencies.py

# 3. Regenerate samples with updated levels
python create_samples.py

# 4. Create final Anki deck
python create_hsk_deck.py
```

Or use the convenience script:
```bash
bash run_hsk_pipeline.sh
```

## Automatic Sample Generation

**New Feature:** When you run `tian-hanzi deck build`, samples are automatically generated!

This means you'll always have up-to-date HTML card previews after building a deck. The sample files show you exactly what the cards will look like before importing into Anki.

**Preview your cards:**
1. Build the deck: `tian-hanzi deck build`
2. Open `data/sample_cards_combined.html` in your browser
3. See all three card types (radicals, hanzi, vocabulary) side by side

## Shell Completion (Optional)

Enable tab-completion for the CLI:

**Bash:**
```bash
tian-hanzi --install-completion bash
source ~/.bashrc
```

**Zsh:**
```bash
tian-hanzi --install-completion zsh
source ~/.zshrc
```

**PowerShell:**
```powershell
tian-hanzi --install-completion powershell
# Follow the instructions printed
```

## Troubleshooting

### "tian-hanzi: command not found"

Make sure you:
1. Activated the virtual environment
2. Ran `pip install -e .`

### "RuntimeError: Type not yet supported"

This was fixed! If you see this, make sure you've pulled the latest changes and reinstalled:
```bash
git pull
pip install -e .
```

### "No module named 'tian_hanzi'"

The package is installed in the `src/` directory. Make sure you're in the project root and have run `pip install -e .`

### Sample generation fails

If samples fail to generate, you can:
1. Use `--skip-samples` to skip them: `tian-hanzi deck build --skip-samples`
2. Generate them manually later: `python create_samples.py`
3. Check that the parquet files exist in `data/`

## Development Tips

### Making Changes

Since the package is installed in editable mode (`-e`), any changes you make to the code in `src/tian_hanzi/` are immediately available when you run `tian-hanzi`.

No need to reinstall after code changes!

### Adding New Commands

1. Add your command to the appropriate CLI module:
   - `src/tian_hanzi/cli/deck.py` - Deck building commands
   - `src/tian_hanzi/cli/analytics.py` - Analysis commands
   - `src/tian_hanzi/cli/validate.py` - Validation commands

2. Use Typer decorators:
```python
@app.command()
def my_command(
    option: str = typer.Option("default", help="Description")
) -> None:
    """Command description shown in --help"""
    # Your code here
```

3. Test immediately: `tian-hanzi deck my-command --help`

### Debugging

Run with Python directly to get full stack traces:
```bash
python -m tian_hanzi.cli deck build
```

## See Also

- **[HSK_PIPELINE_QUICKSTART.md](HSK_PIPELINE_QUICKSTART.md)** - Complete pipeline guide
- **[README.md](README.md)** - Project overview
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - Full development guide
