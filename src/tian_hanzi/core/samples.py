"""Generate sample CSV files and HTML card previews from deck data."""
from __future__ import annotations

import random
import re
from pathlib import Path
from typing import Any

import pandas as pd

from .cards import create_ruby_text, format_components_with_meanings
from .deck_templates import (
    HANZI_MODEL_DEF,
    ModelDefinition,
    RADICAL_MODEL_DEF,
    VOCAB_MODEL_DEF,
)

__all__ = ["SampleGenerator"]


FIELD_PATTERN = re.compile(r"{{\s*([^{}]+?)\s*}}")

PREVIEW_BASE_CSS = """
body {
    font-family: Arial, sans-serif;
    background-color: #f0f0f0;
    padding: 20px;
}
.preview-card {
    max-width: 520px;
    margin: 0 auto;
}
.card-face {
    display: none;
}
.card-face.active {
    display: block;
}
.toggle-button {
    display: block;
    margin: 0 auto 20px;
    padding: 12px 24px;
    background-color: #444444;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px;
    font-weight: bold;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
.toggle-button:hover {
    background-color: #222222;
}
.toggle-button.radical-button {
    background-color: #8b4513;
}
.toggle-button.radical-button:hover {
    background-color: #654321;
}
.toggle-button.hanzi-button {
    background-color: #2e7d32;
}
.toggle-button.hanzi-button:hover {
    background-color: #1b5e20;
}
.toggle-button.vocab-button {
    background-color: #1565c0;
}
.toggle-button.vocab-button:hover {
    background-color: #0d47a1;
}
.card {
    border-radius: 12px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
"""


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
            radical_data = radicals_sample[0]
            html = self._render_card_preview(
                model_def=RADICAL_MODEL_DEF,
                fields=self._build_radical_fields(radical_data),
                page_title=f"Radical Card Preview - {radical_data.get('radical', '')}",
                button_class="radical-button",
            )
            (self.output_dir / 'sample_radical_card.html').write_text(html, encoding='utf-8')
            print(f"  ✓ sample_radical_card.html - {radical_data.get('radical', '')}")
        
        if hanzi_sample:
            hanzi_data = hanzi_sample[0]
            char = hanzi_data.get('hanzi', hanzi_data.get('character', ''))
            html = self._render_card_preview(
                model_def=HANZI_MODEL_DEF,
                fields=self._build_hanzi_fields(hanzi_data, radicals_df),
                page_title=f"Hanzi Card Preview - {char}",
                button_class="hanzi-button",
            )
            (self.output_dir / 'sample_hanzi_card.html').write_text(html, encoding='utf-8')
            print(f"  ✓ sample_hanzi_card.html - {char}")
        
        if vocab_sample:
            vocab_data = vocab_sample[0]
            html = self._render_card_preview(
                model_def=VOCAB_MODEL_DEF,
                fields=self._build_vocab_fields(vocab_data),
                page_title=f"Vocabulary Card Preview - {vocab_data.get('word', '')}",
                button_class="vocab-button",
            )
            (self.output_dir / 'sample_vocabulary_card.html').write_text(html, encoding='utf-8')
            print(f"  ✓ sample_vocabulary_card.html - {vocab_data.get('word', '')}")
        
        # Generate combined view
        html = self._create_combined_view_html()
        (self.output_dir / 'sample_cards_combined.html').write_text(html, encoding='utf-8')
        print("  ✓ sample_cards_combined.html (all 3 side-by-side)")
        
    def _render_card_preview(
        self,
        *,
        model_def: ModelDefinition,
        fields: dict[str, str],
        page_title: str,
        button_class: str,
    ) -> str:
        """Render a preview HTML page for a single card using shared templates."""

        sanitized_fields = {key: self._clean_text(value) for key, value in fields.items()}
        template = model_def.templates[0]
        front_inner = self._render_template(template.qfmt, sanitized_fields)
        back_inner = self._render_template(template.afmt, sanitized_fields, front_inner)

        combined_css = PREVIEW_BASE_CSS + "\n" + model_def.css

        front_html = f'<div class="card">{front_inner}</div>'
        back_html = f'<div class="card">{back_inner}</div>'

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <style>
{combined_css}
    </style>
</head>
<body>
    <button class="toggle-button {button_class}" onclick="toggleCard()">Show Back</button>
    <div class="preview-card">
        <div class="card-face front-face active">{front_html}</div>
        <div class="card-face back-face">{back_html}</div>
    </div>
    <script>
        function toggleCard() {{
            const front = document.querySelector('.front-face');
            const back = document.querySelector('.back-face');
            const button = document.querySelector('.toggle-button');
            const frontIsActive = front.classList.contains('active');

            if (frontIsActive) {{
                front.classList.remove('active');
                back.classList.add('active');
                button.textContent = 'Show Front';
            }} else {{
                back.classList.remove('active');
                front.classList.add('active');
                button.textContent = 'Show Back';
            }}
        }}
    </script>
</body>
</html>"""

    @staticmethod
    def _render_template(template: str, fields: dict[str, str], front_side: str | None = None) -> str:
        """Render an Anki template string using simple field substitution."""

        def replace(match: re.Match[str]) -> str:
            key = match.group(1).strip()
            if key == 'FrontSide':
                return front_side or ''
            return fields.get(key, '')

        return FIELD_PATTERN.sub(replace, template)

    def _build_radical_fields(self, radical_data: dict[str, Any]) -> dict[str, str]:
        """Prepare field values for the radical model."""

        return {
            'Radical': self._clean_text(radical_data.get('radical'), ''),
            'Meaning': self._clean_text(radical_data.get('meaning'), 'Unknown'),
            'Productivity': self._clean_text(radical_data.get('usage_count'), '0'),
            'HSK1Count': self._clean_text(radical_data.get('usage_hsk1'), '0'),
            'HSK2Count': self._clean_text(radical_data.get('usage_hsk2'), '0'),
            'HSK3Count': self._clean_text(radical_data.get('usage_hsk3'), '0'),
            'Level': self._level_value(radical_data),
        }

    def _build_hanzi_fields(
        self,
        hanzi_data: dict[str, Any],
        radicals_df: pd.DataFrame,
    ) -> dict[str, str]:
        """Prepare field values for the hanzi model."""

        char = self._clean_text(hanzi_data.get('hanzi', hanzi_data.get('character')), '')
        components_raw = hanzi_data.get('components', hanzi_data.get('radicals', ''))
        components = format_components_with_meanings(components_raw, radicals_df)

        return {
            'Character': char,
            'Meaning': self._clean_text(hanzi_data.get('meaning'), 'Unknown'),
            'Reading': self._clean_text(hanzi_data.get('pinyin'), ''),
            'Radicals': components,
            'MeaningMnemonic': self._clean_text(hanzi_data.get('meaning_mnemonic'), ''),
            'ReadingMnemonic': self._clean_text(hanzi_data.get('reading_mnemonic'), ''),
            'HSKLevel': self._clean_text(hanzi_data.get('hsk_level'), ''),
            'Level': self._level_value(hanzi_data),
            'Audio': self._audio_placeholder(char),
        }

    def _build_vocab_fields(self, vocab_data: dict[str, Any]) -> dict[str, str]:
        """Prepare field values for the vocabulary model."""

        word = self._clean_text(vocab_data.get('word'), '')
        pinyin = self._clean_text(vocab_data.get('pinyin'), '')
        ruby_text = create_ruby_text(word, pinyin)
        breakdown = self._clean_text(vocab_data.get('hanzi_breakdown'), '')
        if not breakdown and word:
            breakdown = ' '.join(list(word))

        return {
            'Word': word,
            'Meaning': self._clean_text(vocab_data.get('meaning'), 'Unknown'),
            'Reading': pinyin,
            'RubyText': ruby_text,
            'HanziBreakdown': breakdown or 'No breakdown available.',
            'Description': self._clean_text(vocab_data.get('description'), ''),
            'HSKLevel': self._clean_text(vocab_data.get('hsk_level'), ''),
            'Level': self._level_value(vocab_data),
            'Audio': self._audio_placeholder(word),
        }

    def _print_file_list(self) -> None:
        """Print list of generated files."""
        print("\nGenerated files:")
        print("  📊 CSV Samples:")
        print(f"     • {self.output_dir / 'radicals_sample.csv'}")
        print(f"     • {self.output_dir / 'hanzi_sample.csv'}")
        print(f"     • {self.output_dir / 'vocabulary_sample.csv'}")
        print("\n  🎴 HTML Card Previews:")
        print(f"     • {self.output_dir / 'sample_radical_card.html'}")
        print(f"     • {self.output_dir / 'sample_hanzi_card.html'}")
        print(f"     • {self.output_dir / 'sample_vocabulary_card.html'}")
        print(f"     • {self.output_dir / 'sample_cards_combined.html'}")
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
    def _level_value(row: dict[str, Any]) -> str:
        """Extract Tian level or fall back to a default placeholder."""
        for key in ('tian_level', 'level'):
            value = row.get(key)
            text = SampleGenerator._clean_text(value, '')
            if text:
                return text
        return '?'

    @staticmethod
    def _audio_placeholder(value: str) -> str:
        """Return a simple audio indicator for preview purposes."""
        return '🔊' if value else ''
    
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
