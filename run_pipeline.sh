#!/bin/bash
# Full Pipeline - Generate Tian Hanzi Deck from Scratch
# This script runs all steps to create the complete Anki deck

set -e  # Exit on any error

echo "============================================================"
echo "🎴 TIAN HANZI DECK - FULL PIPELINE"
echo "============================================================"
echo ""

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/Scripts/activate

echo ""
echo "============================================================"
echo "STEP 1: Generate Data from Hanzipy"
echo "============================================================"
python generate_tian_v1_fast.py

echo ""
echo "============================================================"
echo "STEP 2: Sort by Dependencies (Radicals → Hanzi → Vocab)"
echo "============================================================"
python sort_by_dependencies.py

echo ""
echo "============================================================"
echo "STEP 3: Create Anki Package"
echo "============================================================"
python create_deck_from_parquet.py

echo ""
echo "============================================================"
echo "✅ PIPELINE COMPLETE!"
echo "============================================================"
echo ""
echo "📁 Output: anki_deck/Tian_Hanzi_Deck_v1.apkg"
echo ""
echo "🎯 Next steps:"
echo "   1. Import anki_deck/Tian_Hanzi_Deck_v1.apkg into Anki"
echo "   2. Start studying!"
echo ""
echo "📊 Optional: View level details"
echo "   python show_levels.py"
echo ""
