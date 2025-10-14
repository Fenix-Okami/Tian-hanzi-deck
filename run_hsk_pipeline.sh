#!/bin/bash
# HSK 1-3 Deck Generation Pipeline
# This script generates a complete Anki deck from HSK 1-3 vocabulary

set -e  # Exit on error

echo "========================================"
echo "HSK 1-3 DECK GENERATION PIPELINE"
echo "========================================"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    # Try Windows path first (since we're running bash on Windows)
    if [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    elif [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
    echo ""
fi

# Step 1: Generate HSK data
echo "📊 Step 1/3: Generating HSK 1-3 data..."
echo "----------------------------------------"
python -m tian_hanzi.cli deck build --level 1 --level 2 --level 3
if [ $? -ne 0 ]; then
    echo "❌ Error in data generation!"
    exit 1
fi
echo ""

# Step 2: Create Anki deck with dynamic breakpoint analysis
# NOTE: We skip the old sort_hsk_by_dependencies.py because it uses fixed
# levels (5 radicals per level). Instead, create_hsk_deck.py now runs
# breakpoint analysis to determine optimal variable-sized levels.
echo "📦 Step 2/3: Creating Anki deck with dynamic levels..."
echo "----------------------------------------"
python create_hsk_deck.py
if [ $? -ne 0 ]; then
    echo "❌ Error in deck creation!"
    exit 1
fi
echo ""

# Step 3: Generate HTML samples and sample CSVs
echo "🎴 Step 3/3: Generating HTML card previews and sample CSVs..."
echo "----------------------------------------"
python create_samples.py
if [ $? -ne 0 ]; then
    echo "❌ Error in sample generation!"
    exit 1
fi
echo ""

# Success!
echo "========================================"
echo "✅ SUCCESS!"
echo "========================================"
echo ""
echo "📦 Your deck is ready:"
echo "   anki_deck/HSK_1-3_Hanzi_Deck.apkg"
echo ""
echo "🎴 HTML card previews created:"
echo "   data/sample_radical_card.html"
echo "   data/sample_hanzi_card.html"
echo "   data/sample_vocabulary_card.html"
echo "   data/sample_cards_combined.html (all 3 side-by-side) ⭐"
echo ""
echo "📊 To view statistics:"
echo "   python scripts/analysis/analyze_hsk_components.py"
echo "   python scripts/analysis/show_levels.py"
echo "   python scripts/analysis/show_radical_hsk_breakdown.py"
echo ""
echo "🎴 Import the .apkg file into Anki to start learning!"
echo ""