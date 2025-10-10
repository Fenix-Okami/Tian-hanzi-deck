#!/usr/bin/env python3
"""
Create sample CSV files and HTML card previews from parquet data
Shows 20 random entries from each subdeck
Also generates HTML preview cards for radicals, hanzi, and vocabulary
"""

import random
import csv
import sys
import os

try:
    import pandas as pd
except ImportError:
    print("❌ Error: pandas is not installed")
    print("Please run: pip install pandas pyarrow")
    sys.exit(1)

# Set seed for reproducibility
random.seed(42)

print("📊 Creating sample CSV files from parquet data...\n")

# Load data from parquet files
print("📂 Loading data from parquet files...")
radicals_df = pd.read_parquet('data/radicals.parquet')
hanzi_df = pd.read_parquet('data/hanzi.parquet')
vocabulary_df = pd.read_parquet('data/vocabulary.parquet')

# Convert to list of dictionaries
radicals = radicals_df.to_dict('records')
hanzi = hanzi_df.to_dict('records')
vocabulary = vocabulary_df.to_dict('records')

# Sample 20 random entries from each
print("\n🎲 Sampling 20 random entries from each...")
radicals_sample = random.sample(radicals, min(20, len(radicals)))
hanzi_sample = random.sample(hanzi, min(20, len(hanzi)))
vocab_sample = random.sample(vocabulary, min(20, len(vocabulary)))

# Save to CSV
print("\n💾 Saving sample CSV files...\n")

# Save radicals
with open('data/radicals_sample.csv', 'w', newline='', encoding='utf-8') as f:
    if radicals:
        writer = csv.DictWriter(f, fieldnames=radicals[0].keys())
        writer.writeheader()
        writer.writerows(radicals_sample)

print('✓ Created data/radicals_sample.csv')
if radicals:
    print(f'  Fields: {list(radicals[0].keys())}')
print(f'  Entries: {len(radicals_sample)}/{len(radicals)}')

print()

# Save hanzi
with open('data/hanzi_sample.csv', 'w', newline='', encoding='utf-8') as f:
    if hanzi:
        writer = csv.DictWriter(f, fieldnames=hanzi[0].keys())
        writer.writeheader()
        writer.writerows(hanzi_sample)

print('✓ Created data/hanzi_sample.csv')
if hanzi:
    print(f'  Fields: {list(hanzi[0].keys())}')
print(f'  Entries: {len(hanzi_sample)}/{len(hanzi)}')

print()

# Save vocabulary
with open('data/vocabulary_sample.csv', 'w', newline='', encoding='utf-8') as f:
    if vocabulary:
        writer = csv.DictWriter(f, fieldnames=vocabulary[0].keys())
        writer.writeheader()
        writer.writerows(vocab_sample)

print('✓ Created data/vocabulary_sample.csv')
if vocabulary:
    print(f'  Fields: {list(vocabulary[0].keys())}')
print(f'  Entries: {len(vocab_sample)}/{len(vocabulary)}')

print("\n" + "=" * 60)
print("✨ Sample CSV files created successfully!")
print("=" * 60)
print("\nPreview the files:")
print("  • data/radicals_sample.csv")
print("  • data/hanzi_sample.csv")
print("  • data/vocabulary_sample.csv")

# Now generate HTML card previews
print("\n" + "=" * 60)
print("🎴 Generating HTML card previews...")
print("=" * 60)

def create_ruby_text_html(word, pinyin):
    """
    Create HTML ruby text with pinyin above each character.
    Splits multi-syllable pinyin and pairs with each character.
    """
    if not word or not pinyin:
        return word
    
    # Split pinyin by spaces
    pinyin_parts = pinyin.strip().split()
    characters = list(word)
    
    # If we have the same number of pinyin parts and characters, pair them
    if len(pinyin_parts) == len(characters):
        ruby_parts = []
        for char, pin in zip(characters, pinyin_parts):
            ruby_parts.append(f'<ruby><rb class="vocab-char">{char}</rb><rt class="pinyin-reading">{pin}</rt></ruby>')
        return ''.join(ruby_parts)
    else:
        # Fallback: show all pinyin above entire word
        return f'<ruby><rb class="word">{word}</rb><rt class="pinyin-reading">{pinyin}</rt></ruby>'

def format_components_with_meanings(components_str, radicals_df):
    """
    Format components with their meanings.
    Example: "一|口|丨" becomes "一 (one), 口 (mouth), 丨 (line)"
    """
    if not components_str or components_str == 'Unknown':
        return 'Unknown'
    
    # Split components by | or comma
    if '|' in components_str:
        components = [c.strip() for c in components_str.split('|')]
    else:
        components = [c.strip() for c in components_str.split(',')]
    
    formatted_parts = []
    for component in components:
        if not component:
            continue
        
        # Look up meaning in radicals dataframe
        meaning = None
        radical_row = radicals_df[radicals_df['radical'] == component]
        if not radical_row.empty:
            meaning = radical_row.iloc[0].get('meaning', '')
            # Truncate long meanings
            if meaning and len(meaning) > 30:
                meaning = meaning[:27] + '...'
        
        if meaning:
            formatted_parts.append(f"{component} ({meaning})")
        else:
            formatted_parts.append(component)
    
    return ', '.join(formatted_parts)

def create_radical_card_html(radical_data):
    """Generate HTML for a radical card preview"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radical Card Preview - {radical_data.get('radical', '')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            padding: 20px;
        }}
        .toggle-button {{
            display: block;
            margin: 0 auto 20px;
            padding: 12px 24px;
            background-color: #8b4513;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .toggle-button:hover {{
            background-color: #654321;
        }}
        .card {{
            font-family: Arial, "Microsoft YaHei", SimSun, sans-serif;
            text-align: center;
            color: #4a3728;
            background: linear-gradient(135deg, #f5e6d3 0%, #e8d5c4 100%);
            padding: 20px;
            max-width: 500px;
            margin: 0 auto;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .card-type {{
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #8b4513;
        }}
        .character {{
            font-size: 120px;
            margin: 30px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            color: #654321;
        }}
        .prompt {{
            font-size: 20px;
            color: #6b5544;
            margin: 20px 0;
        }}
        .meaning {{
            font-size: 32px;
            font-weight: bold;
            margin: 20px 0;
            color: #8b4513;
        }}
        .productivity {{
            font-size: 16px;
            color: #8b6914;
            background-color: rgba(139, 69, 19, 0.1);
            padding: 8px 16px;
            border-radius: 20px;
            display: inline-block;
            margin: 10px 0;
        }}
        .mnemonic {{
            font-size: 18px;
            color: #5a4a3a;
            margin: 20px;
            padding: 20px;
            background-color: rgba(255, 255, 255, 0.5);
            border-radius: 12px;
            border-left: 4px solid #8b4513;
        }}
        .info {{
            font-size: 14px;
            color: #666;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid rgba(0,0,0,0.1);
        }}
        .back {{
            display: none;
        }}
    </style>
</head>
<body>
    <button class="toggle-button" onclick="toggleCard()">Show Back</button>
    <div class="card">
        <div class="front">
            <div class="card-type">Radical • Level {radical_data.get('level', '?')}</div>
            <div class="character">{radical_data.get('radical', '')}</div>
            <div class="prompt">What does this radical mean?</div>
        </div>
        <div class="back">
            <div class="card-type">Radical • Level {radical_data.get('level', '?')}</div>
            <div class="character">{radical_data.get('radical', '')}</div>
            <div class="prompt">What does this radical mean?</div>
            <hr style="border: 1px solid rgba(0,0,0,0.1); margin: 20px 0;">
            <div class="meaning">{radical_data.get('meaning', 'Unknown')}</div>
            <div class="productivity">Used in {radical_data.get('usage_count', 0)} characters</div>
            <div class="mnemonic">Remember this radical!</div>
            <div class="info">Brown theme • Productivity-based sorting</div>
        </div>
    </div>
    <script>
        let showingFront = true;
        function toggleCard() {{
            const front = document.querySelector('.front');
            const back = document.querySelector('.back');
            const button = document.querySelector('.toggle-button');
            
            if (showingFront) {{
                front.style.display = 'none';
                back.style.display = 'block';
                button.textContent = 'Show Front';
            }} else {{
                front.style.display = 'block';
                back.style.display = 'none';
                button.textContent = 'Show Back';
            }}
            showingFront = !showingFront;
        }}
    </script>
</body>
</html>"""

def create_hanzi_card_html(hanzi_data, radicals_df):
    """Generate HTML for a hanzi card preview"""
    char = hanzi_data.get('hanzi', hanzi_data.get('character', ''))
    components_raw = hanzi_data.get('components', hanzi_data.get('radicals', 'Unknown'))
    components = format_components_with_meanings(components_raw, radicals_df)
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hanzi Card Preview - {char}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            padding: 20px;
        }}
        .toggle-button {{
            display: block;
            margin: 0 auto 20px;
            padding: 12px 24px;
            background-color: #2e7d32;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .toggle-button:hover {{
            background-color: #1b5e20;
        }}
        .card {{
            font-family: Arial, "Microsoft YaHei", SimSun, sans-serif;
            text-align: center;
            color: #2d4a2b;
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            padding: 20px;
            max-width: 500px;
            margin: 0 auto;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .card-type {{
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #2e7d32;
        }}
        .character {{
            font-size: 120px;
            margin: 30px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            color: #1b5e20;
        }}
        .prompt {{
            font-size: 20px;
            color: #4a6741;
            margin: 20px 0;
        }}
        .meaning {{
            font-size: 32px;
            font-weight: bold;
            margin: 20px 0;
            color: #2e7d32;
        }}
        .character-with-reading {{
            margin: 30px 0;
            line-height: 1;
        }}
        ruby {{
            ruby-position: over;
        }}
        rt {{
            ruby-align: center;
            margin-bottom: 15px;
        }}
        .character-with-reading .character {{
            font-size: 120px;
            color: #1b5e20;
        }}
        .pinyin-reading {{
            font-size: 28px;
            color: #558b2f;
            font-weight: bold;
        }}
        .audio-placeholder {{
            font-size: 16px;
            color: #666;
            margin: 10px 0;
            opacity: 0.7;
        }}
        .section {{
            background-color: rgba(255, 255, 255, 0.5);
            padding: 15px;
            margin: 15px 20px;
            border-radius: 12px;
            border-left: 4px solid #2e7d32;
            text-align: left;
        }}
        .section-title {{
            font-weight: bold;
            color: #2e7d32;
            margin-bottom: 10px;
            font-size: 16px;
        }}
        .components {{
            font-size: 18px;
            color: #4a6741;
        }}
        .info {{
            font-size: 14px;
            color: #666;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid rgba(0,0,0,0.1);
        }}
        .back {{
            display: none;
        }}
    </style>
</head>
<body>
    <button class="toggle-button" onclick="toggleCard()">Show Back</button>
    <div class="card">
        <div class="front">
            <div class="card-type">Hanzi • HSK {hanzi_data.get('hsk_level', '?')} • Level {hanzi_data.get('level', '?')}</div>
            <div class="character">{char}</div>
        </div>
        <div class="back">
            <div class="card-type">Hanzi • HSK {hanzi_data.get('hsk_level', '?')} • Level {hanzi_data.get('level', '?')}</div>
            <div class="character-with-reading">
                <ruby>
                    <rb class="character">{char}</rb>
                    <rt class="pinyin-reading">{hanzi_data.get('pinyin', '?')}</rt>
                </ruby>
            </div>
            <hr style="border: 1px solid rgba(0,0,0,0.1); margin: 20px 0;">
            <div class="meaning">{hanzi_data.get('meaning', 'Unknown')}</div>
            <div class="audio-placeholder">🔊 [Audio: {hanzi_data.get('pinyin', '?')}]</div>
            <div class="section">
                <div class="section-title">Meaning Mnemonic</div>
                <div class="components">Think about the meaning of each component to remember what this character means.</div>
            </div>
            <div class="section">
                <div class="section-title">Reading Mnemonic</div>
                <div class="components">Associate the sound "{hanzi_data.get('pinyin', '?')}" with the character's components.</div>
            </div>
            <div class="section">
                <div class="section-title">Components</div>
                <div class="components">{components}</div>
            </div>
            <div class="info">Green theme • Component-based learning</div>
        </div>
    </div>
    <script>
        let showingFront = true;
        function toggleCard() {{
            const front = document.querySelector('.front');
            const back = document.querySelector('.back');
            const button = document.querySelector('.toggle-button');
            
            if (showingFront) {{
                front.style.display = 'none';
                back.style.display = 'block';
                button.textContent = 'Show Front';
            }} else {{
                front.style.display = 'block';
                back.style.display = 'none';
                button.textContent = 'Show Back';
            }}
            showingFront = !showingFront;
        }}
    </script>
</body>
</html>"""

def create_vocab_card_html(vocab_data):
    """Generate HTML for a vocabulary card preview"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vocabulary Card Preview - {vocab_data.get('word', '')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            padding: 20px;
        }}
        .toggle-button {{
            display: block;
            margin: 0 auto 20px;
            padding: 12px 24px;
            background-color: #1565c0;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .toggle-button:hover {{
            background-color: #0d47a1;
        }}
        .card {{
            font-family: Arial, "Microsoft YaHei", SimSun, sans-serif;
            text-align: center;
            color: #1a237e;
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 20px;
            max-width: 500px;
            margin: 0 auto;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .card-type {{
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #1565c0;
        }}
        .word {{
            font-size: 80px;
            margin: 30px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            color: #0d47a1;
        }}
        .prompt {{
            font-size: 20px;
            color: #283593;
            margin: 20px 0;
        }}
        .meaning {{
            font-size: 32px;
            font-weight: bold;
            margin: 20px 0;
            color: #1565c0;
        }}
        .word-with-reading {{
            margin: 30px 0;
            line-height: 1;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            gap: 5px;
        }}
        ruby {{
            ruby-position: over;
        }}
        rt {{
            ruby-align: center;
            margin-bottom: 15px;
        }}
        .word-with-reading .word {{
            font-size: 80px;
            color: #0d47a1;
        }}
        .word-with-reading .vocab-char {{
            font-size: 80px;
            color: #0d47a1;
        }}
        .pinyin-reading {{
            font-size: 24px;
            color: #1976d2;
            font-weight: bold;
        }}
        .audio-placeholder {{
            font-size: 16px;
            color: #666;
            margin: 10px 0;
            opacity: 0.7;
        }}
        .section {{
            background-color: rgba(255, 255, 255, 0.5);
            padding: 15px;
            margin: 15px 20px;
            border-radius: 12px;
            border-left: 4px solid #1565c0;
            text-align: left;
        }}
        .section-title {{
            font-weight: bold;
            color: #1565c0;
            margin-bottom: 10px;
            font-size: 16px;
        }}
        .content {{
            font-size: 18px;
            color: #283593;
            line-height: 1.6;
        }}
        .info {{
            font-size: 14px;
            color: #666;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid rgba(0,0,0,0.1);
        }}
        .back {{
            display: none;
        }}
    </style>
</head>
<body>
    <button class="toggle-button" onclick="toggleCard()">Show Back</button>
    <div class="card">
        <div class="front">
            <div class="card-type">Vocabulary • HSK {vocab_data.get('hsk_level', '?')} • Level {vocab_data.get('level', '?')}</div>
            <div class="word">{vocab_data.get('word', '')}</div>
        </div>
        <div class="back">
            <div class="card-type">Vocabulary • HSK {vocab_data.get('hsk_level', '?')} • Level {vocab_data.get('level', '?')}</div>
            <div class="word-with-reading">
                {create_ruby_text_html(vocab_data.get('word', ''), vocab_data.get('pinyin', ''))}
            </div>
            <hr style="border: 1px solid rgba(0,0,0,0.1); margin: 20px 0;">
            <div class="meaning">{vocab_data.get('meaning', 'Unknown')}</div>
            <div class="audio-placeholder">🔊 [Audio: {vocab_data.get('pinyin', '?')}]</div>
            <div class="section">
                <div class="section-title">Example</div>
                <div class="content">Example sentence would go here.</div>
            </div>
            <div class="section">
                <div class="section-title">Character Breakdown</div>
                <div class="content">{' '.join(list(vocab_data.get('word', '')))}</div>
            </div>
            <div class="info">Blue theme • Context-based learning</div>
        </div>
    </div>
    <script>
        let showingFront = true;
        function toggleCard() {{
            const front = document.querySelector('.front');
            const back = document.querySelector('.back');
            const button = document.querySelector('.toggle-button');
            
            if (showingFront) {{
                front.style.display = 'none';
                back.style.display = 'block';
                button.textContent = 'Show Front';
            }} else {{
                front.style.display = 'block';
                back.style.display = 'none';
                button.textContent = 'Show Back';
            }}
            showingFront = !showingFront;
        }}
    </script>
</body>
</html>"""

# Generate sample HTML cards
print("\n📝 Generating HTML card previews...")

# Pick first sample from each
if radicals_sample:
    html = create_radical_card_html(radicals_sample[0])
    with open('data/sample_radical_card.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✓ Created data/sample_radical_card.html - {radicals_sample[0].get('radical', '')}")

if hanzi_sample:
    html = create_hanzi_card_html(hanzi_sample[0], radicals_df)
    with open('data/sample_hanzi_card.html', 'w', encoding='utf-8') as f:
        f.write(html)
    char = hanzi_sample[0].get('hanzi', hanzi_sample[0].get('character', ''))
    print(f"✓ Created data/sample_hanzi_card.html - {char}")

if vocab_sample:
    html = create_vocab_card_html(vocab_sample[0])
    with open('data/sample_vocabulary_card.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✓ Created data/sample_vocabulary_card.html - {vocab_sample[0].get('word', '')}")

print("\n" + "=" * 60)
print("✨ All samples created successfully!")
print("=" * 60)
print("\nFiles created:")
print("  📊 CSV Samples:")
print("     • data/radicals_sample.csv")
print("     • data/hanzi_sample.csv")
print("     • data/vocabulary_sample.csv")
print("\n  🎴 HTML Card Previews:")
print("     • data/sample_radical_card.html")
print("     • data/sample_hanzi_card.html")
print("     • data/sample_vocabulary_card.html")
print("\n💡 Open the HTML files in your browser to see card previews!")
