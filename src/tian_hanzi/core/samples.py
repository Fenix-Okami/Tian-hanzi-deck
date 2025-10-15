"""Generate sample CSV files and HTML card previews from deck data."""
from __future__ import annotations

import random
from pathlib import Path
from typing import Any

import pandas as pd

from .cards import create_ruby_text, format_components_with_meanings

__all__ = ["SampleGenerator"]


class SampleGenerator:
    """Generate sample CSVs and HTML previews from deck data."""
    
    def __init__(self, output_dir: str | Path = "data", seed: int = 42):
        """Initialize the sample generator.
        
        Args:
            output_dir: Directory to save samples to
            seed: Random seed for reproducibility
        """
        self.output_dir = Path(output_dir)
        self.seed = seed
        random.seed(seed)
    
    def generate(
        self,
        radicals_df: pd.DataFrame,
        hanzi_df: pd.DataFrame,
        vocabulary_df: pd.DataFrame,
        sample_size: int = 20
    ) -> None:
        """Generate sample CSVs and HTML previews.
        
        Args:
            radicals_df: Radicals dataframe (optionally with tian_level)
            hanzi_df: Hanzi dataframe (optionally with tian_level)
            vocabulary_df: Vocabulary dataframe (optionally with tian_level)
            sample_size: Number of samples to generate
        """
        print("\n" + "=" * 70)
        print("📊 GENERATING SAMPLE FILES")
        print("=" * 70)
        
        # Check if tian_level column exists
        has_levels = 'tian_level' in radicals_df.columns
        if not has_levels:
            print("ℹ️  Note: Data doesn't have tian_level yet - run sorting to add levels")
        
        # Create sample CSVs
        self._create_sample_csvs(radicals_df, hanzi_df, vocabulary_df, sample_size)
        
        # Create HTML previews
        self._create_html_previews(radicals_df, hanzi_df, vocabulary_df, sample_size)
        
        print("\n" + "=" * 70)
        print("✨ Sample generation complete!")
        print("=" * 70)
        self._print_file_list()
    
    def _create_sample_csvs(
        self,
        radicals_df: pd.DataFrame,
        hanzi_df: pd.DataFrame,
        vocabulary_df: pd.DataFrame,
        sample_size: int
    ) -> None:
        """Create sample CSV files."""
        print("\n🎲 Creating sample CSV files...")
        
        # Convert to lists and sample
        radicals = radicals_df.to_dict('records')
        hanzi = hanzi_df.to_dict('records')
        vocabulary = vocabulary_df.to_dict('records')
        
        radicals_sample = random.sample(radicals, min(sample_size, len(radicals)))
        hanzi_sample = random.sample(hanzi, min(sample_size, len(hanzi)))
        vocab_sample = random.sample(vocabulary, min(sample_size, len(vocabulary)))
        
        # Save samples
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        pd.DataFrame(radicals_sample).to_csv(
            self.output_dir / 'radicals_sample.csv', index=False, encoding='utf-8'
        )
        print(f"  ✓ radicals_sample.csv ({len(radicals_sample)}/{len(radicals)})")
        
        pd.DataFrame(hanzi_sample).to_csv(
            self.output_dir / 'hanzi_sample.csv', index=False, encoding='utf-8'
        )
        print(f"  ✓ hanzi_sample.csv ({len(hanzi_sample)}/{len(hanzi)})")
        
        pd.DataFrame(vocab_sample).to_csv(
            self.output_dir / 'vocabulary_sample.csv', index=False, encoding='utf-8'
        )
        print(f"  ✓ vocabulary_sample.csv ({len(vocab_sample)}/{len(vocabulary)})")
    
    def _create_html_previews(
        self,
        radicals_df: pd.DataFrame,
        hanzi_df: pd.DataFrame,
        vocabulary_df: pd.DataFrame,
        sample_size: int
    ) -> None:
        """Create HTML card previews."""
        print("\n🎴 Creating HTML card previews...")
        
        # Get first sample from each (for preview consistency)
        radicals_sample = radicals_df.head(1).to_dict('records')
        hanzi_sample = hanzi_df.head(1).to_dict('records')
        vocab_sample = vocabulary_df.head(1).to_dict('records')
        
        # Generate individual card previews
        if radicals_sample:
            html = self._create_radical_card_html(radicals_sample[0])
            (self.output_dir / 'sample_radical_card.html').write_text(html, encoding='utf-8')
            print(f"  ✓ sample_radical_card.html - {radicals_sample[0].get('radical', '')}")
        
        if hanzi_sample:
            html = self._create_hanzi_card_html(hanzi_sample[0], radicals_df)
            (self.output_dir / 'sample_hanzi_card.html').write_text(html, encoding='utf-8')
            char = hanzi_sample[0].get('hanzi', hanzi_sample[0].get('character', ''))
            print(f"  ✓ sample_hanzi_card.html - {char}")
        
        if vocab_sample:
            html = self._create_vocab_card_html(vocab_sample[0])
            (self.output_dir / 'sample_vocabulary_card.html').write_text(html, encoding='utf-8')
            print(f"  ✓ sample_vocabulary_card.html - {vocab_sample[0].get('word', '')}")
        
        # Generate combined view
        html = self._create_combined_view_html()
        (self.output_dir / 'sample_cards_combined.html').write_text(html, encoding='utf-8')
        print("  ✓ sample_cards_combined.html (all 3 side-by-side)")
    
    def _print_file_list(self) -> None:
        """Print list of generated files."""
        print("\nGenerated files:")
        print("  📊 CSV Samples:")
        print("     • data/radicals_sample.csv")
        print("     • data/hanzi_sample.csv")
        print("     • data/vocabulary_sample.csv")
        print("\n  🎴 HTML Card Previews:")
        print("     • data/sample_radical_card.html")
        print("     • data/sample_hanzi_card.html")
        print("     • data/sample_vocabulary_card.html")
        print("     • data/sample_cards_combined.html")
        print("\n💡 Open the HTML files in your browser to see card previews!")
    
    @staticmethod
    def _clean_text(value: Any, fallback: str = "") -> str:
        """Normalize values (handling NaN/None) for display."""
        if value is None:
            return fallback
        try:
            if pd.isna(value):  # type: ignore[arg-type]
                return fallback
        except TypeError:
            pass
        text = str(value).strip()
        return text if text else fallback

    @staticmethod
    def _create_radical_card_html(radical_data: dict[str, Any]) -> str:
        """Generate HTML for a radical card preview."""
        meaning = SampleGenerator._clean_text(radical_data.get('meaning'), "Unknown")
        usage_count = int(SampleGenerator._clean_text(radical_data.get('usage_count'), "0"))
        
        # Get HSK counts
        hsk1 = int(SampleGenerator._clean_text(radical_data.get('usage_hsk1'), "0"))
        hsk2 = int(SampleGenerator._clean_text(radical_data.get('usage_hsk2'), "0"))
        hsk3 = int(SampleGenerator._clean_text(radical_data.get('usage_hsk3'), "0"))
        
        # Calculate percentages for bar widths
        total = usage_count if usage_count > 0 else (hsk1 + hsk2 + hsk3)
        hsk1_pct = (hsk1 / total * 100) if total > 0 else 0
        hsk2_pct = (hsk2 / total * 100) if total > 0 else 0
        hsk3_pct = (hsk3 / total * 100) if total > 0 else 0

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
        .hsk-breakdown {{
            margin: 25px auto;
            max-width: 400px;
            background-color: rgba(255, 255, 255, 0.6);
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #8b4513;
        }}
        .breakdown-title {{
            font-size: 18px;
            font-weight: bold;
            color: #654321;
            margin-bottom: 15px;
            text-align: center;
        }}
        .breakdown-bars {{
            text-align: left;
        }}
        .breakdown-row {{
            margin: 10px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .breakdown-label {{
            font-size: 14px;
            font-weight: bold;
            color: #5a4a3a;
            min-width: 50px;
        }}
        .breakdown-bar-container {{
            flex: 1;
            background-color: rgba(139, 69, 19, 0.1);
            border-radius: 10px;
            overflow: hidden;
            height: 30px;
            position: relative;
        }}
        .breakdown-bar {{
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            transition: width 0.3s ease;
            min-width: 30px;
        }}
        .breakdown-bar.hsk1 {{
            background: linear-gradient(90deg, #ff6b6b 0%, #ff8787 100%);
        }}
        .breakdown-bar.hsk2 {{
            background: linear-gradient(90deg, #4dabf7 0%, #74c0fc 100%);
        }}
        .breakdown-bar.hsk3 {{
            background: linear-gradient(90deg, #51cf66 0%, #8ce99a 100%);
        }}
        .breakdown-count {{
            font-size: 13px;
            font-weight: bold;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
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
            <div class="card-type">Radical • Tian Level {radical_data.get('tian_level', '?')}</div>
            <div class="character">{radical_data.get('radical', '')}</div>
        </div>
        <div class="back">
            <div class="card-type">Radical • Tian Level {radical_data.get('tian_level', '?')}</div>
            <div class="character">{radical_data.get('radical', '')}</div>
            <hr style="border: 1px solid rgba(0,0,0,0.1); margin: 20px 0;">
            <div class="meaning">{meaning}</div>
            <div class="hsk-breakdown">
                <div class="breakdown-title">HSK Distribution</div>
                <div class="breakdown-bars">
                    <div class="breakdown-row">
                        <div class="breakdown-label">HSK 1</div>
                        <div class="breakdown-bar-container">
                            <div class="breakdown-bar hsk1" style="width: {hsk1_pct}%;">
                                <span class="breakdown-count">{hsk1}</span>
                            </div>
                        </div>
                    </div>
                    <div class="breakdown-row">
                        <div class="breakdown-label">HSK 2</div>
                        <div class="breakdown-bar-container">
                            <div class="breakdown-bar hsk2" style="width: {hsk2_pct}%;">
                                <span class="breakdown-count">{hsk2}</span>
                            </div>
                        </div>
                    </div>
                    <div class="breakdown-row">
                        <div class="breakdown-label">HSK 3</div>
                        <div class="breakdown-bar-container">
                            <div class="breakdown-bar hsk3" style="width: {hsk3_pct}%;">
                                <span class="breakdown-count">{hsk3}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
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
    
    @staticmethod
    def _create_hanzi_card_html(hanzi_data: dict[str, Any], radicals_df: pd.DataFrame) -> str:
        """Generate HTML for a hanzi card preview."""
        char = hanzi_data.get('hanzi', hanzi_data.get('character', ''))
        components_raw = hanzi_data.get('components', hanzi_data.get('radicals', 'Unknown'))
        components = format_components_with_meanings(components_raw, radicals_df)
        meaning_text = SampleGenerator._clean_text(hanzi_data.get('meaning'), "Unknown")
        meaning_mnemonic = SampleGenerator._clean_text(
            hanzi_data.get('meaning_mnemonic'), "No meaning mnemonic has been added yet."
        )
        reading_mnemonic = SampleGenerator._clean_text(
            hanzi_data.get('reading_mnemonic'), "No reading mnemonic has been added yet."
        )
        
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
            <div class="card-type">Hanzi • HSK {hanzi_data.get('hsk_level', '?')} • Tian Level {hanzi_data.get('tian_level', '?')}</div>
            <div class="character">{char}</div>
        </div>
        <div class="back">
            <div class="card-type">Hanzi • HSK {hanzi_data.get('hsk_level', '?')} • Tian Level {hanzi_data.get('tian_level', '?')}</div>
            <div class="character-with-reading">
                <ruby>
                    <rb class="character">{char}</rb>
                    <rt class="pinyin-reading">{hanzi_data.get('pinyin', '?')}</rt>
                </ruby>
            </div>
            <hr style="border: 1px solid rgba(0,0,0,0.1); margin: 20px 0;">
            <div class="meaning">{meaning_text}</div>
            <div class="section">
                <div class="section-title">Meaning Mnemonic</div>
                <div class="components">{meaning_mnemonic}</div>
            </div>
            <div class="section">
                <div class="section-title">Reading Mnemonic</div>
                <div class="components">{reading_mnemonic}</div>
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
    
    @staticmethod
    def _create_vocab_card_html(vocab_data: dict[str, Any]) -> str:
        """Generate HTML for a vocabulary card preview."""
        meaning_text = SampleGenerator._clean_text(vocab_data.get('meaning'), "Unknown")
        example = SampleGenerator._clean_text(vocab_data.get('example'), "")
        description = SampleGenerator._clean_text(vocab_data.get('description'), "")
        if not example:
            example = description
        if not example:
            example = "Example sentence not available."
        breakdown = " ".join(list(vocab_data.get('word', ''))) or "N/A"

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
            <div class="card-type">Vocabulary • HSK {vocab_data.get('hsk_level', '?')} • Tian Level {vocab_data.get('tian_level', '?')}</div>
            <div class="word">{vocab_data.get('word', '')}</div>
        </div>
        <div class="back">
            <div class="card-type">Vocabulary • HSK {vocab_data.get('hsk_level', '?')} • Tian Level {vocab_data.get('tian_level', '?')}</div>
            <div class="word-with-reading">
                {create_ruby_text(vocab_data.get('word', ''), vocab_data.get('pinyin', ''))}
            </div>
            <hr style="border: 1px solid rgba(0,0,0,0.1); margin: 20px 0;">
            <div class="meaning">{meaning_text}</div>
            <div class="section">
                <div class="section-title">Example</div>
                <div class="content">{example}</div>
            </div>
            <div class="section">
                <div class="section-title">Character Breakdown</div>
                <div class="content">{breakdown}</div>
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
    
    @staticmethod
    def _create_combined_view_html() -> str:
        """Generate combined HTML view with all three card types."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tian Hanzi Deck - Card Type Comparison</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .cards-container {
            display: flex;
            gap: 20px;
            justify-content: space-between;
            flex-wrap: wrap;
        }
        .card-wrapper {
            flex: 1;
            min-width: 400px;
            max-width: 550px;
        }
        .card-label {
            text-align: center;
            color: white;
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            padding: 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
        }
        iframe {
            width: 100%;
            height: 700px;
            border: none;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            background: white;
        }
        @media (max-width: 1400px) {
            .cards-container {
                flex-direction: column;
                align-items: center;
            }
            .card-wrapper {
                max-width: 700px;
                width: 100%;
            }
        }
        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
            font-size: 1.1em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎴 Tian Hanzi Deck - Card Type Comparison</h1>
        
        <div class="cards-container">
            <div class="card-wrapper">
                <div class="card-label">1. Radical Card (Brown)</div>
                <iframe src="sample_radical_card.html"></iframe>
            </div>
            
            <div class="card-wrapper">
                <div class="card-label">2. Hanzi Card (Green)</div>
                <iframe src="sample_hanzi_card.html"></iframe>
            </div>
            
            <div class="card-wrapper">
                <div class="card-label">3. Vocabulary Card (Blue)</div>
                <iframe src="sample_vocabulary_card.html"></iframe>
            </div>
        </div>
        
        <div class="footer">
            💡 Each card can be flipped independently by clicking its "Show Back" button
        </div>
    </div>
</body>
</html>"""
