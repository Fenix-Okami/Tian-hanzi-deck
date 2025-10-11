#!/bin/bash
# Run unit tests with pytest

set -e  # Exit on error

echo "========================================"
echo "Running Tian Hanzi Deck Unit Tests"
echo "========================================"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing..."
    pip install pytest pytest-cov
fi

# Run tests
echo "Running tests..."
pytest tests/ -v

echo ""
echo "========================================"
echo "✅ All tests completed!"
echo "========================================"
