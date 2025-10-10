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
    source venv/bin/activate || source venv/Scripts/activate
    echo ""
fi

# Step 1: Generate HSK data
echo "📊 Step 1/3: Generating HSK 1-3 data..."
echo "----------------------------------------"
python generate_hsk_deck.py
if [ $? -ne 0 ]; then
    echo "❌ Error in data generation!"
    exit 1
fi
echo ""

# Step 2: Sort by dependencies
echo "🔄 Step 2/3: Sorting by dependencies..."
echo "----------------------------------------"
python sort_hsk_by_dependencies.py
if [ $? -ne 0 ]; then
    echo "❌ Error in dependency sorting!"
    exit 1
fi
echo ""

# Step 3: Create Anki deck
echo "📦 Step 3/3: Creating Anki deck..."
echo "----------------------------------------"
python create_hsk_deck.py
if [ $? -ne 0 ]; then
    echo "❌ Error in deck creation!"
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
echo "📊 To view statistics:"
echo "   python analyze_hsk_components.py"
echo "   python show_levels.py"
echo ""
echo "🎴 Import the .apkg file into Anki to start learning!"
echo ""