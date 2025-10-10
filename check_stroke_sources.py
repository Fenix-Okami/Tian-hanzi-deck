#!/usr/bin/env python3
"""
Check if we can get stroke counts from external sources
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("STROKE COUNT DATA SOURCES")
print("=" * 70)
print()

# Test characters
test_chars = ['一', '人', '中', '明', '谢', '鱼', '龙']

# Known stroke counts for verification
known_strokes = {
    '一': 1,
    '人': 2,
    '中': 4,
    '明': 8,
    '谢': 12,
    '鱼': 8,
    '龙': 5
}

print("1. Check if hanzipy has stroke data:")
print("-" * 70)
try:
    from hanzipy.decomposer import HanziDecomposer
    decomposer = HanziDecomposer()
    
    # Check internal data structure
    print("Checking decomposer internals...")
    if hasattr(decomposer, 'dict'):
        sample = list(decomposer.dict.items())[:3]
        print(f"Sample decomposer.dict entries: {sample}")
        
        # Check what data is available for '一'
        if '一' in decomposer.dict:
            print(f"Data for '一': {decomposer.dict['一']}")
    
    print("\n✗ hanzipy doesn't include stroke count data")
    
except Exception as e:
    print(f"Error: {e}")

print("\n2. Check for Unicode CJK stroke data:")
print("-" * 70)
print("Unicode provides some stroke count info via CJK Unified Ideographs...")
print("But it requires external databases like Unihan.")

print("\n3. Potential solutions:")
print("-" * 70)
print("""
Options for adding stroke count data:

A) Use external Python library:
   - 'chinese-strokes' package (if available)
   - 'hanzidentifier' package (has some data)
   
B) Download Unihan database:
   - https://unicode.org/charts/unihan.html
   - Parse kTotalStrokes field
   
C) Use online API:
   - Chinese Character Web API
   - MDBG Chinese Dictionary API
   
D) Manual data file:
   - Create stroke_counts.csv with hanzi → stroke_count mapping
   - Only need 899 characters for our HSK 1-3 set

Recommendation: Option D (manual file) is simplest and most reliable
for our use case.
""")

print("\n4. Testing if any packages are already installed:")
print("-" * 70)

# Try common packages
packages_to_try = [
    ('hanzidentifier', 'has_chinese'),
    ('zhon', 'hanzi'),
]

for package, module in packages_to_try:
    try:
        exec(f"import {package}")
        print(f"✓ {package} is installed")
    except ImportError:
        print(f"✗ {package} not installed")

print("\n" + "=" * 70)
