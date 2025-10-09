#!/usr/bin/env python3
"""
Anki Deck Generator for Tian Hanzi Deck
Creates an Anki deck with three subdecks: radicals, hanzi, and vocabulary
Inspired by WaniKani with mnemonics for radicals, hanzi characters, and vocab
"""

import random
import sys

try:
    import genanki
except ImportError:
    print("❌ Error: genanki is not installed")
    print("\nTo install genanki, run:")
    print("  pip install -r requirements.txt")
    print("\nOr install directly:")
    print("  pip install genanki")
    print("\nTo see what the deck would look like without installing, run:")
    print("  python demo.py")
    sys.exit(1)


# Define unique model IDs for each card type
RADICAL_MODEL_ID = random.randrange(1 << 30, 1 << 31)
HANZI_MODEL_ID = random.randrange(1 << 30, 1 << 31)
VOCAB_MODEL_ID = random.randrange(1 << 30, 1 << 31)

# Define unique deck IDs
MAIN_DECK_ID = random.randrange(1 << 30, 1 << 31)
RADICAL_DECK_ID = random.randrange(1 << 30, 1 << 31)
HANZI_DECK_ID = random.randrange(1 << 30, 1 << 31)
VOCAB_DECK_ID = random.randrange(1 << 30, 1 << 31)


# Card model for Radicals
radical_model = genanki.Model(
    RADICAL_MODEL_ID,
    'Tian Hanzi Radical Model',
    fields=[
        {'name': 'Radical'},
        {'name': 'Meaning'},
        {'name': 'Mnemonic'},
    ],
    templates=[
        {
            'name': 'Radical Recognition',
            'qfmt': '''
                <div class="card-type">Radical</div>
                <div class="character">{{Radical}}</div>
                <div class="question">What is the meaning of this radical?</div>
            ''',
            'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div class="meaning">{{Meaning}}</div>
                <div class="mnemonic">
                    <h3>Mnemonic:</h3>
                    {{Mnemonic}}
                </div>
            ''',
        },
    ],
    css='''
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
        .card-type {
            color: #0af;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .character {
            font-size: 100px;
            margin: 30px 0;
        }
        .question {
            font-size: 24px;
            margin: 20px 0;
        }
        .meaning {
            font-size: 32px;
            font-weight: bold;
            color: #0af;
            margin: 20px 0;
        }
        .mnemonic {
            background-color: #f0f0f0;
            padding: 15px;
            margin: 20px;
            border-radius: 5px;
            text-align: left;
        }
        .mnemonic h3 {
            margin-top: 0;
            color: #666;
        }
    '''
)


# Card model for Hanzi
hanzi_model = genanki.Model(
    HANZI_MODEL_ID,
    'Tian Hanzi Character Model',
    fields=[
        {'name': 'Character'},
        {'name': 'Meaning'},
        {'name': 'Reading'},
        {'name': 'Radicals'},
        {'name': 'MeaningMnemonic'},
        {'name': 'ReadingMnemonic'},
    ],
    templates=[
        {
            'name': 'Character Recognition',
            'qfmt': '''
                <div class="card-type">Hanzi</div>
                <div class="character">{{Character}}</div>
                <div class="question">What is the meaning and reading?</div>
            ''',
            'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div class="meaning">{{Meaning}}</div>
                <div class="reading">{{Reading}}</div>
                <div class="radicals">
                    <h3>Radicals:</h3>
                    {{Radicals}}
                </div>
                <div class="mnemonic">
                    <h3>Meaning Mnemonic:</h3>
                    {{MeaningMnemonic}}
                </div>
                <div class="mnemonic">
                    <h3>Reading Mnemonic:</h3>
                    {{ReadingMnemonic}}
                </div>
            ''',
        },
    ],
    css='''
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
        .card-type {
            color: #f0a;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .character {
            font-size: 100px;
            margin: 30px 0;
        }
        .question {
            font-size: 24px;
            margin: 20px 0;
        }
        .meaning {
            font-size: 32px;
            font-weight: bold;
            color: #f0a;
            margin: 20px 0;
        }
        .reading {
            font-size: 24px;
            color: #666;
            margin: 10px 0;
        }
        .radicals, .mnemonic {
            background-color: #f0f0f0;
            padding: 15px;
            margin: 20px;
            border-radius: 5px;
            text-align: left;
        }
        .radicals h3, .mnemonic h3 {
            margin-top: 0;
            color: #666;
        }
    '''
)


# Card model for Vocabulary
vocab_model = genanki.Model(
    VOCAB_MODEL_ID,
    'Tian Hanzi Vocabulary Model',
    fields=[
        {'name': 'Word'},
        {'name': 'Meaning'},
        {'name': 'Reading'},
        {'name': 'Characters'},
        {'name': 'Example'},
        {'name': 'Mnemonic'},
    ],
    templates=[
        {
            'name': 'Vocabulary Recognition',
            'qfmt': '''
                <div class="card-type">Vocabulary</div>
                <div class="character">{{Word}}</div>
                <div class="question">What is the meaning and reading?</div>
            ''',
            'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div class="meaning">{{Meaning}}</div>
                <div class="reading">{{Reading}}</div>
                <div class="characters">
                    <h3>Characters:</h3>
                    {{Characters}}
                </div>
                {{#Example}}
                <div class="example">
                    <h3>Example:</h3>
                    {{Example}}
                </div>
                {{/Example}}
                <div class="mnemonic">
                    <h3>Mnemonic:</h3>
                    {{Mnemonic}}
                </div>
            ''',
        },
    ],
    css='''
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
        .card-type {
            color: #a0f;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .character {
            font-size: 80px;
            margin: 30px 0;
        }
        .question {
            font-size: 24px;
            margin: 20px 0;
        }
        .meaning {
            font-size: 32px;
            font-weight: bold;
            color: #a0f;
            margin: 20px 0;
        }
        .reading {
            font-size: 24px;
            color: #666;
            margin: 10px 0;
        }
        .characters, .example, .mnemonic {
            background-color: #f0f0f0;
            padding: 15px;
            margin: 20px;
            border-radius: 5px;
            text-align: left;
        }
        .characters h3, .example h3, .mnemonic h3 {
            margin-top: 0;
            color: #666;
        }
    '''
)


def create_radical_cards(radicals_data):
    """Create radical cards from data"""
    cards = []
    for radical in radicals_data:
        note = genanki.Note(
            model=radical_model,
            fields=[
                radical['radical'],
                radical['meaning'],
                radical['mnemonic']
            ]
        )
        cards.append(note)
    return cards


def create_hanzi_cards(hanzi_data):
    """Create hanzi character cards from data"""
    cards = []
    for hanzi in hanzi_data:
        note = genanki.Note(
            model=hanzi_model,
            fields=[
                hanzi['character'],
                hanzi['meaning'],
                hanzi['reading'],
                hanzi['radicals'],
                hanzi['meaning_mnemonic'],
                hanzi['reading_mnemonic']
            ]
        )
        cards.append(note)
    return cards


def create_vocab_cards(vocab_data):
    """Create vocabulary cards from data"""
    cards = []
    for vocab in vocab_data:
        note = genanki.Note(
            model=vocab_model,
            fields=[
                vocab['word'],
                vocab['meaning'],
                vocab['reading'],
                vocab['characters'],
                vocab.get('example', ''),
                vocab['mnemonic']
            ]
        )
        cards.append(note)
    return cards


def create_deck(radicals_data=None, hanzi_data=None, vocab_data=None, output_file='anki_deck/Tian_Hanzi_Deck.apkg'):
    """
    Create an Anki deck with three subdecks: radicals, hanzi, and vocabulary
    
    Args:
        radicals_data: List of dictionaries with radical data
        hanzi_data: List of dictionaries with hanzi character data
        vocab_data: List of dictionaries with vocabulary data
        output_file: Name of the output .apkg file (default saves to anki_deck folder)
    """
    import os
    
    # Ensure the anki_deck directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Create main deck
    main_deck = genanki.Deck(MAIN_DECK_ID, 'Tian Hanzi Deck')
    
    # Create subdecks
    radical_deck = genanki.Deck(RADICAL_DECK_ID, 'Tian Hanzi Deck::1_Radicals')
    hanzi_deck = genanki.Deck(HANZI_DECK_ID, 'Tian Hanzi Deck::2_Hanzi')
    vocab_deck = genanki.Deck(VOCAB_DECK_ID, 'Tian Hanzi Deck::3_Vocabulary')
    
    # Use example data if none provided
    if radicals_data is None:
        radicals_data = get_example_radicals()
    if hanzi_data is None:
        hanzi_data = get_example_hanzi()
    if vocab_data is None:
        vocab_data = get_example_vocab()
    
    # Create and add cards to subdecks
    radical_cards = create_radical_cards(radicals_data)
    for card in radical_cards:
        radical_deck.add_note(card)
    
    hanzi_cards = create_hanzi_cards(hanzi_data)
    for card in hanzi_cards:
        hanzi_deck.add_note(card)
    
    vocab_cards = create_vocab_cards(vocab_data)
    for card in vocab_cards:
        vocab_deck.add_note(card)
    
    # Create package with all decks
    package = genanki.Package([radical_deck, hanzi_deck, vocab_deck])
    package.write_to_file(output_file)
    
    print(f"✓ Deck created successfully: {output_file}")
    print(f"  - Radicals: {len(radical_cards)} cards")
    print(f"  - Hanzi: {len(hanzi_cards)} cards")
    print(f"  - Vocabulary: {len(vocab_cards)} cards")
    print(f"  - Total: {len(radical_cards) + len(hanzi_cards) + len(vocab_cards)} cards")


def get_example_radicals():
    """Example radical data"""
    try:
        from example_data import RADICALS
        return RADICALS
    except ImportError:
        return [
            {
                'radical': '一',
                'meaning': 'Ground',
                'mnemonic': 'This radical is a single horizontal line, like the ground beneath your feet.'
            },
            {
                'radical': '亻',
                'meaning': 'Person',
                'mnemonic': 'This radical looks like a person standing upright. It\'s a simplified form of 人.'
            },
            {
                'radical': '氵',
                'meaning': 'Water',
                'mnemonic': 'Three drops of water falling down. This radical appears in many characters related to water.'
            },
        ]


def get_example_hanzi():
    """Example hanzi data"""
    try:
        from example_data import HANZI
        return HANZI
    except ImportError:
        return [
            {
                'character': '人',
                'meaning': 'Person',
                'reading': 'rén',
                'radicals': '人 (person)',
                'meaning_mnemonic': 'A person standing with two legs spread apart.',
                'reading_mnemonic': 'Sounds like "ren" in "render" - render a person in a drawing!'
            },
            {
                'character': '水',
                'meaning': 'Water',
                'reading': 'shuǐ',
                'radicals': '氵 (water)',
                'meaning_mnemonic': 'The character shows water flowing down a stream.',
                'reading_mnemonic': 'Sounds like "shway" - the sound water makes when it flows.'
            },
            {
                'character': '天',
                'meaning': 'Heaven, Sky, Day',
                'reading': 'tiān',
                'radicals': '一 (ground) + 大 (big)',
                'meaning_mnemonic': 'Something big (大) above the ground (一) - that\'s the sky!',
                'reading_mnemonic': 'Sounds like "tee-an" - imagine a big T (tee) in the sky!'
            },
        ]


def get_example_vocab():
    """Example vocabulary data"""
    try:
        from example_data import VOCABULARY
        return VOCABULARY
    except ImportError:
        return [
            {
                'word': '今天',
                'meaning': 'Today',
                'reading': 'jīn tiān',
                'characters': '今 (now) + 天 (day)',
                'example': '今天天气很好。(The weather is nice today.)',
                'mnemonic': 'The "now" day is today!'
            },
            {
                'word': '水果',
                'meaning': 'Fruit',
                'reading': 'shuǐ guǒ',
                'characters': '水 (water) + 果 (fruit)',
                'example': '我喜欢吃水果。(I like to eat fruit.)',
                'mnemonic': 'Fruits are full of water, making them juicy and refreshing.'
            },
        ]


if __name__ == '__main__':
    # Create the deck with example data
    create_deck()
