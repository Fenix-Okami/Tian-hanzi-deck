#!/bin/bash
# -*- coding: utf-8 -*-
# Generate audio files for hanzi and vocabulary using OpenAI TTS API

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════"
echo "🎵 HSK Audio Generation Pipeline"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo ""
    echo "To use this script, you need to configure your OpenAI API key."
    echo ""
    echo "Steps:"
    echo "  1. Copy .env.example to .env"
    echo "  2. Edit .env and add your OpenAI API key"
    echo "  3. Get your key from: https://platform.openai.com/api-keys"
    echo ""
    echo "Example .env content:"
    echo "  OPENAI_API_KEY='sk-proj-xxxxxxxxxxxxxxxxxxxxx'"
    echo ""
    exit 1
elif [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OpenAI API key not found!"
    echo ""
    echo "Please set your OPENAI_API_KEY in the .env file"
    echo ""
    exit 1
else
    echo "✓ OpenAI API key found in environment"
fi

# Check for required data files
if [ ! -f data/hanzi.csv ]; then
    echo ""
    echo "❌ data/hanzi.csv not found!"
    echo "   Run the main pipeline first:"
    echo "   bash run_hsk_pipeline.sh"
    echo ""
    exit 1
fi

if [ ! -f data/vocabulary.csv ]; then
    echo ""
    echo "❌ data/vocabulary.csv not found!"
    echo "   Run the main pipeline first:"
    echo "   bash run_hsk_pipeline.sh"
    echo ""
    exit 1
fi

echo "✓ Data files found"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    if [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate  # Windows Git Bash
    elif [ -f "venv/bin/activate" ]; then
        source venv/bin/activate  # Unix
    fi
    echo "✓ Virtual environment activated"
else
    echo "⚠️  No virtual environment found (venv/)"
    echo "   Using system Python"
fi

# Install/upgrade required packages
echo ""
echo "Checking dependencies..."
pip install -q --upgrade openai tqdm python-dotenv pandas

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🎵 Starting Audio Generation"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "This will generate MP3 audio files using OpenAI's TTS API:"
echo "  • 899 hanzi characters → data/audio/hanzi/"
echo "  • 2,227 vocabulary words → data/audio/vocabulary/"
echo ""
echo "Using high-quality TTS model (gpt-4o-mini-tts)"
echo "Voice: nova (optimized for Chinese)"
echo "Speed: 0.85x (slightly slower for learning)"
echo ""
echo "⚠️  COST WARNING:"
echo "  • gpt-4o-mini-tts: \$0.030 per 1,000 characters"
echo "  • Estimated total: ~3,000 characters = ~\$0.09"
echo "  • Already generated files will be skipped"
echo ""

# Prompt for confirmation
read -p "Continue with audio generation? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""

# Run the audio generation script
python generate_audio.py --all

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Audio Generation Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Audio files saved to:"
echo "  • data/audio/hanzi/"
echo "  • data/audio/vocabulary/"
echo ""
echo "Next steps:"
echo "  1. Test the audio files"
echo "  2. Integrate them into your Anki deck"
echo ""
