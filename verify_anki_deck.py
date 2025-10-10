#!/usr/bin/env python3
"""Quick check of the generated Anki deck structure"""

import sqlite3
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# The .apkg file is a zip file containing a SQLite database
import zipfile
import tempfile
import os

apkg_path = 'anki_deck/HSK_1-3_Hanzi_Deck.apkg'

print("=" * 70)
print("📦 Anki Deck Structure Check")
print("=" * 70)

try:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Extract the .apkg file
        with zipfile.ZipFile(apkg_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)
        
        # Connect to the collection database
        db_path = os.path.join(tmpdir, 'collection.anki2')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get total card count
        cursor.execute("SELECT COUNT(*) FROM cards")
        total_cards = cursor.fetchone()[0]
        print(f"\n✅ Total cards: {total_cards}")
        
        # Get notes with tags
        cursor.execute("""
            SELECT tags, COUNT(*) 
            FROM notes 
            GROUP BY tags 
            ORDER BY COUNT(*) DESC
            LIMIT 20
        """)
        
        print(f"\n📋 Sample tag distribution:")
        level_counts = {}
        for tags, count in cursor.fetchall():
            print(f"   {tags[:50]:50s} = {count:4d} cards")
            # Extract level tags
            for tag in tags.split():
                if tag.startswith('level-'):
                    level_num = int(tag.split('-')[1])
                    level_counts[level_num] = level_counts.get(level_num, 0) + count
        
        # Show level distribution
        print(f"\n📊 Level distribution:")
        print(f"   Total unique levels: {len(level_counts)}")
        print(f"   Level range: {min(level_counts.keys())}-{max(level_counts.keys())}")
        print(f"\n   First 10 levels:")
        for level in sorted(level_counts.keys())[:10]:
            print(f"      Level {level:2d}: {level_counts[level]:4d} cards")
        
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ Deck verification complete!")
        print("=" * 70)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
