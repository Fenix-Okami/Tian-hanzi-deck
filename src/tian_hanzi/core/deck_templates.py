"""Shared Anki model templates used for deck generation and previews."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence, TYPE_CHECKING

__all__ = [
    "TemplateDefinition",
    "ModelDefinition",
    "RADICAL_MODEL_DEF",
    "HANZI_MODEL_DEF",
    "VOCAB_MODEL_DEF",
    "MODEL_DEFINITIONS",
    "create_genanki_model",
]


if TYPE_CHECKING:  # pragma: no cover - typing aid only
    import genanki


@dataclass(frozen=True)
class TemplateDefinition:
    """Structure describing an Anki card template."""

    name: str
    qfmt: str
    afmt: str


@dataclass(frozen=True)
class ModelDefinition:
    """Structure describing an Anki model definition."""

    name: str
    fields: Sequence[str]
    templates: Sequence[TemplateDefinition]
    css: str


RADICAL_MODEL_DEF = ModelDefinition(
    name="HSK Radical Model",
    fields=(
        "Radical",
        "Meaning",
        "Productivity",
        "HSK1Count",
        "HSK2Count",
        "HSK3Count",
        "Level",
    ),
    templates=(
        TemplateDefinition(
            name="Radical Recognition",
            qfmt='''
                <div class="card-type radical-type">Radical • Level {{Level}}</div>
                <div class="character radical-char">{{Radical}}</div>
            ''',
            afmt='''
                {{FrontSide}}
                <div class="meaning radical-meaning">{{Meaning}}</div>
                <div class="hsk-stats">
                    <div class="stat-row">
                        <span class="stat-text">Appears in</span>
                        <span class="stat-box hsk1-box">{{HSK1Count}}</span>
                        <span class="stat-text">HSK 1 Hanzi</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-text">Appears in</span>
                        <span class="stat-box hsk2-box">{{HSK2Count}}</span>
                        <span class="stat-text">HSK 2 Hanzi</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-text">Appears in</span>
                        <span class="stat-box hsk3-box">{{HSK3Count}}</span>
                        <span class="stat-text">HSK 3 Hanzi</span>
                    </div>
                </div>
            ''',
        ),
    ),
    css='''
        .card {
            font-family: Arial, "Microsoft YaHei", SimSun, sans-serif;
            text-align: center;
            color: #4a3728;
            background: linear-gradient(135deg, #f5e6d3 0%, #e8d5c4 100%);
            padding: 20px;
        }
        .card-type {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .radical-type { color: #8b4513; }
        .character {
            font-size: 120px;
            margin: 30px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .radical-char { color: #654321; }
        .prompt {
            font-size: 20px;
            color: #6b5544;
            margin: 20px 0;
        }
        .meaning {
            font-size: 32px;
            font-weight: bold;
            margin: 20px 0;
        }
        .radical-meaning { color: #8b4513; }
        .hsk-stats {
            margin: 25px auto;
            max-width: 500px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .stat-row {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            font-size: 18px;
            color: #654321;
        }
        .stat-text {
            font-weight: normal;
        }
        .stat-box {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 45px;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 20px;
            font-weight: bold;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            border: 2px solid rgba(0,0,0,0.2);
        }
        .hsk1-box {
            background: linear-gradient(135deg, #ff6b6b 0%, #ff8787 100%);
        }
        .hsk2-box {
            background: linear-gradient(135deg, #4dabf7 0%, #74c0fc 100%);
        }
        .hsk3-box {
            background: linear-gradient(135deg, #51cf66 0%, #8ce99a 100%);
        }
    ''',
)


HANZI_MODEL_DEF = ModelDefinition(
    name="HSK Hanzi Model",
    fields=(
        "Character",
        "Meaning",
        "Reading",
        "Radicals",
        "MeaningMnemonic",
        "ReadingMnemonic",
        "HSKLevel",
        "Level",
        "Audio",
    ),
    templates=(
        TemplateDefinition(
            name="Character Recognition",
            qfmt='''
                <div class="card-type hanzi-type">Hanzi • HSK {{HSKLevel}} • Level {{Level}}</div>
                <div class="character hanzi-char">{{Character}}</div>
            ''',
            afmt='''
                <div class="card-type hanzi-type">Hanzi • HSK {{HSKLevel}} • Level {{Level}}</div>
                <div class="character-with-reading">
                    <div class="character-row">
                        <ruby class="hanzi-ruby">
                            <rb class="hanzi-char">{{Character}}</rb>
                            <rt class="pinyin-reading">{{Reading}}</rt>
                        </ruby>
                        <span class="audio-inline">{{Audio}}</span>
                    </div>
                </div>
                <div class="meaning hanzi-meaning">{{Meaning}}</div>
                <div class="section">
                    <div class="section-title">Meaning Mnemonic</div>
                    <div class="mnemonic">{{MeaningMnemonic}}</div>
                </div>
                <div class="section">
                    <div class="section-title">Reading Mnemonic</div>
                    <div class="mnemonic">{{ReadingMnemonic}}</div>
                </div>
                <div class="section">
                    <div class="section-title">Components</div>
                    <div class="radicals">{{Radicals}}</div>
                </div>
            ''',
        ),
    ),
    css='''
        .card {
            font-family: Arial, "Microsoft YaHei", SimSun, sans-serif;
            text-align: center;
            color: #2d4a2b;
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            padding: 20px;
        }
        .card-type {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .hanzi-type { color: #2e7d32; }
        .character {
            font-size: 120px;
            margin: 30px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .hanzi-char { color: #1b5e20; }
        .prompt {
            font-size: 20px;
            color: #4a6741;
            margin: 20px 0;
        }
        .meaning {
            font-size: 32px;
            font-weight: bold;
            margin: 20px 0;
        }
        .hanzi-meaning { color: #2e7d32; }
        .character-with-reading {
            margin: 30px 0;
            line-height: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 16px;
        }
        .character-row {
            display: inline-flex;
            align-items: center;
            gap: 12px;
        }
        .hanzi-ruby {
            ruby-position: over;
        }
        .hanzi-ruby .hanzi-char {
            font-size: 120px;
            color: #1b5e20;
        }
        .hanzi-ruby .pinyin-reading {
            font-size: 28px;
            color: #558b2f;
            font-weight: bold;
            ruby-align: center;
        }
        .character-with-reading .hanzi-char {
            font-size: 120px;
            color: #1b5e20;
        }
        .pinyin-reading {
            font-size: 28px;
            color: #558b2f;
            font-weight: bold;
        }
        .audio-inline {
            display: inline-flex;
            align-items: center;
        }
        .section {
            background-color: rgba(255, 255, 255, 0.5);
            padding: 15px;
            margin: 15px 20px;
            border-radius: 12px;
            border-left: 4px solid #2e7d32;
        }
        .section-title {
            font-weight: bold;
            color: #2e7d32;
            margin-bottom: 10px;
            font-size: 16px;
        }
        .radicals {
            font-size: 18px;
            color: #4a6741;
        }
        .mnemonic {
            font-size: 16px;
            color: #4a6741;
            text-align: center;
        }
    ''',
)


VOCAB_MODEL_DEF = ModelDefinition(
    name="HSK Vocabulary Model",
    fields=(
        "Word",
        "Meaning",
        "Reading",
        "RubyText",
        "HanziBreakdown",
        "Description",
        "HSKLevel",
        "Level",
        "Audio",
    ),
    templates=(
        TemplateDefinition(
            name="Word Recognition",
            qfmt='''
                <div class="card-type vocab-type">Vocabulary • HSK {{HSKLevel}} • Level {{Level}}</div>
                <div class="word vocab-word">{{Word}}</div>
            ''',
            afmt='''
                <div class="card-type vocab-type">Vocabulary • HSK {{HSKLevel}} • Level {{Level}}</div>
                <div class="word-with-reading">
                    <div class="word-row">
                        {{RubyText}}
                        <span class="audio-inline">{{Audio}}</span>
                    </div>
                </div>
                <div class="meaning vocab-meaning">{{Meaning}}</div>
                <div class="section">
                    <div class="section-title">Description</div>
                    <div class="description">{{Description}}</div>
                </div>
                <div class="section">
                    <div class="section-title">Hanzi Breakdown</div>
                    <div class="characters">{{HanziBreakdown}}</div>
                </div>
            ''',
        ),
    ),
    css='''
        .card {
            font-family: Arial, "Microsoft YaHei", SimSun, sans-serif;
            text-align: center;
            color: #1a237e;
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 20px;
        }
        .card-type {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .vocab-type { color: #1565c0; }
        .word {
            font-size: 80px;
            margin: 30px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .vocab-word { color: #0d47a1; }
        .prompt {
            font-size: 20px;
            color: #283593;
            margin: 20px 0;
        }
        .meaning {
            font-size: 32px;
            font-weight: bold;
            margin: 20px 0;
        }
        .vocab-meaning { color: #1565c0; }
        .word-with-reading {
            margin: 30px 0;
            line-height: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 16px;
        }
        .word-row {
            display: inline-flex;
            align-items: center;
            gap: 12px;
        }
        .reading-display {
            font-size: 28px;
            color: #1976d2;
            font-weight: bold;
        }
        .audio-inline {
            display: inline-flex;
            align-items: center;
        }
        ruby {
            ruby-position: over;
        }
        rt {
            ruby-align: center;
            margin-bottom: 15px;
        }
        .word-with-reading .vocab-word {
            font-size: 80px;
            color: #0d47a1;
        }
        .word-with-reading .vocab-char {
            font-size: 80px;
            color: #0d47a1;
        }
        .vocab-word {
            font-size: 80px;
            color: #0d47a1;
        }
        .vocab-char {
            font-size: 80px;
            color: #0d47a1;
        }
        .pinyin-reading {
            font-size: 24px;
            color: #1976d2;
            font-weight: bold;
        }
        .audio-controls {
            margin: 15px 0;
            display: flex;
            align-items: center;
            gap: 15px;
            justify-content: center;
        }
        .audio-controls button {
            background-color: #1565c0;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .audio-controls button:hover {
            background-color: #0d47a1;
        }
        .audio-controls label {
            font-size: 14px;
            color: #555;
            cursor: pointer;
        }
        .audio-controls input[type="checkbox"] {
            cursor: pointer;
        }
        .section {
            background-color: rgba(255, 255, 255, 0.5);
            padding: 15px;
            margin: 15px 20px;
            border-radius: 12px;
            border-left: 4px solid #1565c0;
            text-align: left;
        }
        .section-title {
            font-weight: bold;
            color: #1565c0;
            margin-bottom: 10px;
            font-size: 16px;
        }
        .characters {
            font-size: 18px;
            color: #283593;
            line-height: 1.6;
        }
        .description {
            font-size: 16px;
            color: #283593;
            line-height: 1.8;
            text-align: left;
        }
    ''',
)


MODEL_DEFINITIONS: Dict[str, ModelDefinition] = {
    "radical": RADICAL_MODEL_DEF,
    "hanzi": HANZI_MODEL_DEF,
    "vocabulary": VOCAB_MODEL_DEF,
}


def create_genanki_model(model_id: int, definition: ModelDefinition) -> "genanki.Model":
    """Instantiate a ``genanki.Model`` from a stored definition."""
    import genanki  # Imported lazily to avoid hard dependency for preview generation.

    return genanki.Model(
        model_id,
        definition.name,
        fields=[{"name": field} for field in definition.fields],
        templates=[
            {"name": template.name, "qfmt": template.qfmt, "afmt": template.afmt}
            for template in definition.templates
        ],
        css=definition.css,
    )
