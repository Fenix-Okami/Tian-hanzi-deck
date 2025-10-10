#!/bin/bash
# Quick start script for generating mnemonics
# This script helps you generate AI-powered mnemonics for HSK 1-3

echo "=================================================="
echo "🎴 HSK Mnemonic Generator - Quick Start"
echo "=================================================="
echo ""

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OpenAI API key not found!"
    echo ""
    echo "To use this script, you need to set your OpenAI API key."
    echo ""
    echo "Get your API key from: https://platform.openai.com/api-keys"
    echo ""
    echo "Then set it with:"
    echo "  export OPENAI_API_KEY='your-key-here'"
    echo ""
    echo "Or run in test mode without API key (creates placeholders):"
    echo "  python test_mnemonic_generator.py"
    echo ""
    exit 1
fi

echo "✓ OpenAI API key found"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/Scripts/activate || source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "⚠️  Virtual environment not found"
    echo "Run: python -m venv venv"
    exit 1
fi

echo ""
echo "Installing dependencies..."
pip install -q openai

echo ""
echo "=================================================="
echo "Starting mnemonic generation..."
echo "=================================================="
echo ""
echo "This will:"
echo "  • Process 899 hanzi characters"
echo "  • Process 2,227 vocabulary words"
echo "  • Generate creative mnemonics using OpenAI"
echo ""
echo "Estimated cost: ~$0.50 - $1.00"
echo "Estimated time: ~1 hour"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Run the generator
python generate_mnemonics.py

echo ""
echo "=================================================="
echo "✨ Done!"
echo "=================================================="
echo ""
echo "Generated files:"
echo "  📝 data/hanzi_mnemonics.csv"
echo "  📚 data/vocabulary_mnemonics.csv"
echo ""
