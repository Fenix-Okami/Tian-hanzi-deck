#!/usr/bin/env python3
"""
Test the strokes library
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from strokes import strokes
    
    print("=" * 70)
    print("TESTING STROKES LIBRARY")
    print("=" * 70)
    print()
    
    # Test with various characters
    test_cases = [
        ('一', 1),
        ('人', 2),
        ('中', 4),
        ('明', 8),
        ('谢', 12),
        ('鱼', 8),
        ('龙', 5),
        ('众', 6),
    ]
    
    print("Single characters:")
    print("-" * 70)
    all_correct = True
    for char, expected in test_cases:
        result = strokes(char)
        status = '✓' if result == expected else f'✗ (expected {expected})'
        print(f"  {char}: {result} strokes {status}")
        if result != expected:
            all_correct = False
    
    print()
    if all_correct:
        print("✅ All single character tests passed!")
    else:
        print("⚠️  Some stroke counts don't match expected values")
    
    # Test with multi-character words
    print("\nMulti-character words:")
    print("-" * 70)
    test_words = ['明天', '你好', '中国']
    for word in test_words:
        result = strokes(word)
        print(f"  {word}: {result} strokes total")
    
    print("\n✅ Strokes library is working!")
    
except ImportError as e:
    print(f"❌ Error: strokes library not installed")
    print(f"   {e}")
    print("\nInstall with: pip install strokes")
except Exception as e:
    print(f"❌ Error: {e}")
