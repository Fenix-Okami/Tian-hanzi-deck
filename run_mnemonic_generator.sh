#!/bin/bash
# Quick start script for generating mnemonics
# This script helps you generate AI-powered mnemonics for HSK 1-3

echo "=================================================="
echo "🎴 HSK Mnemonic Generator - Quick Start"
echo "=================================================="
echo ""

# Check if .env file exists
if [ -f ".env" ]; then
    echo "✓ Found .env file (API key will be loaded automatically)"
elif [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OpenAI API key not found!"
    echo ""
    echo "To use this script, you need to configure your OpenAI API key."
    echo ""
    echo "Option 1 (Recommended): Use .env file"
    echo "  1. Copy .env.example to .env: cp .env.example .env"
    echo "  2. Edit .env and add your API key"
    echo "  3. Get your key from: https://platform.openai.com/api-keys"
    echo ""
    echo "Option 2: Set environment variable"
    echo "  export OPENAI_API_KEY='sk-proj-xxxxxxxxxxxxxxxxxxxxx'"
    echo ""
    echo "Or run in test mode without API key (creates placeholders):"
    echo "  python generate_mnemonics.py --dry-run --test-mode"
    echo ""
    exit 1
else
    echo "✓ OpenAI API key found in environment"
fi
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
echo "  • Generate creative mnemonics using OpenAI"
echo ""
echo "Estimated cost: ~$0.30 - $0.50"
echo "Estimated time: ~30-45 minutes"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Run the generator (hanzi only)
python generate_mnemonics.py --types hanzi

echo ""
echo "=================================================="
echo "✨ Done!"
echo "=================================================="
echo ""
echo "Generated files:"
echo "  📝 data/hanzi_mnemonic.csv"
echo ""
echo "To generate other types, use:"
echo "  python generate_mnemonics.py --types radicals,vocab"
echo "  python generate_mnemonics.py --types all"
echo ""
