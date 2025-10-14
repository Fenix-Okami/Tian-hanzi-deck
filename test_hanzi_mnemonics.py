#!/usr/bin/env python3
"""
Test script for hanzi mnemonic generation
Run with: python test_hanzi_mnemonics.py
"""

import sys
import subprocess

# Test with dry-run and test-mode to generate 5 sample hanzi
print("="*70)
print("🧪 Testing Hanzi Mnemonic Generation")
print("="*70)
print("\nRunning in dry-run mode with 5 test items...")
print()

result = subprocess.run([
    sys.executable,
    "generate_mnemonics.py",
    "--dry-run",
    "--test-mode",
    "--out_hanzi", "data/hanzi_mnemonic_test.csv"
], capture_output=False, text=True)

if result.returncode == 0:
    print("\n✅ Test completed successfully!")
    print("\n📁 Check the output at: data/hanzi_mnemonic_test.csv")
else:
    print("\n❌ Test failed!")
    sys.exit(1)
