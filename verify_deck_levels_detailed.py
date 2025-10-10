#!/usr/bin/env python3
"""Detailed level breakdown by card type"""

import sqlite3
import sys
import io
import zipfile
import tempfile
import os

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

apkg_path = 'anki_deck/HSK_1-3_Hanzi_Deck.apkg'

print("=" * 70)
print("📦 Detailed Anki Deck Level Analysis")
print("=" * 70)

try:
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(apkg_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)
        
        db_path = os.path.join(tmpdir, 'collection.anki2')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Analyze by card type
        for card_type in ['radical', 'hanzi', 'vocabulary']:
            cursor.execute(f"""
                SELECT tags
                FROM notes 
                WHERE tags LIKE '%{card_type}%'
            """)
            
            level_counts = {}
            for (tags,) in cursor.fetchall():
                for tag in tags.split():
                    if tag.startswith('level-'):
                        level_num = int(tag.split('-')[1])
                        level_counts[level_num] = level_counts.get(level_num, 0) + 1
            
            if level_counts:
                print(f"\n📊 {card_type.upper()} cards:")
                print(f"   Total: {sum(level_counts.values())} cards")
                print(f"   Levels: {min(level_counts.keys())}-{max(level_counts.keys())}")
                print(f"   Distribution:")
                for level in sorted(level_counts.keys())[:15]:
                    count = level_counts[level]
                    bar = '█' * (count // 5)
                    print(f"      Level {level:2d}: {count:3d} cards {bar}")
        
        conn.close()
        
        print("\n" + "=" * 70)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
