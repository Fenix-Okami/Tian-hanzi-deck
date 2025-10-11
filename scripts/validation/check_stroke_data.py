#!/usr/bin/env python3
"""
Check what data is available from hanzipy for stroke counts
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from hanzipy.decomposer import HanziDecomposer
    from hanzipy import pinyin
    
    decomposer = HanziDecomposer()
    
    print("=" * 70)
    print("HANZIPY DATA EXPLORATION")
    print("=" * 70)
    print()
    
    # Test with a few hanzi
    test_chars = ['一', '人', '中', '明', '谢', '鱼']
    
    for char in test_chars:
        print(f"\n{char} ({char}):")
        print("-" * 40)
        
        # Try to get all available data
        try:
            # Decomposition
            decomp = decomposer.decompose(char)
            print(f"  Decomposition: {decomp}")
        except:
            print(f"  Decomposition: N/A")
        
        try:
            # Components
            components = decomposer.get_components(char)
            print(f"  Components: {components}")
        except:
            print(f"  Components: N/A")
        
        # Check if there's a character object with more info
        try:
            # Try to access hanzi character data directly
            from hanzipy.chardata import char_data
            if char in char_data:
                char_info = char_data[char]
                print(f"  Char data keys: {list(char_info.keys())}")
                
                # Check for stroke count
                if 'strokes' in char_info:
                    print(f"  ✓ Strokes: {char_info['strokes']}")
                if 'stroke_count' in char_info:
                    print(f"  ✓ Stroke count: {char_info['stroke_count']}")
        except Exception as e:
            print(f"  Char data: {e}")
        
        # Try other hanzipy modules
        try:
            from hanzipy import hanzi
            h = hanzi.Hanzi(char)
            print(f"  Hanzi object: {dir(h)}")
        except Exception as e:
            print(f"  Hanzi object: {e}")
    
    print("\n" + "=" * 70)
    print("CHECKING HANZIPY MODULES")
    print("=" * 70)
    
    import hanzipy
    print(f"\nAvailable in hanzipy:")
    print([x for x in dir(hanzipy) if not x.startswith('_')])

except ImportError as e:
    print(f"❌ Error importing hanzipy: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
