"""
Example data for the Tian Hanzi Deck
Add your own radicals, hanzi, and vocabulary here
"""

# Example radical data structure
RADICALS = [
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
    {
        'radical': '口',
        'meaning': 'Mouth',
        'mnemonic': 'A square opening, like a mouth.'
    },
    {
        'radical': '木',
        'meaning': 'Tree',
        'mnemonic': 'A tree with branches extending out and roots below.'
    },
]

# Example hanzi data structure
HANZI = [
    {
        'character': '人',
        'meaning': 'Person',
        'reading': 'rén',
        'radicals': '人 (person)',
        'mnemonic': 'A person standing with two legs spread apart.'
    },
    {
        'character': '水',
        'meaning': 'Water',
        'reading': 'shuǐ',
        'radicals': '氵 (water)',
        'mnemonic': 'The character shows water flowing down a stream.'
    },
    {
        'character': '天',
        'meaning': 'Heaven, Sky, Day',
        'reading': 'tiān',
        'radicals': '一 (ground) + 大 (big)',
        'mnemonic': 'Something big (大) above the ground (一) - that\'s the sky!'
    },
    {
        'character': '大',
        'meaning': 'Big',
        'reading': 'dà',
        'radicals': '大 (big)',
        'mnemonic': 'A person (人) with arms stretched wide to show something is BIG!'
    },
    {
        'character': '小',
        'meaning': 'Small',
        'reading': 'xiǎo',
        'radicals': '小 (small)',
        'mnemonic': 'A person with arms close to the body, showing something small.'
    },
]

# Example vocabulary data structure
VOCABULARY = [
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
    {
        'word': '大人',
        'meaning': 'Adult',
        'reading': 'dà rén',
        'characters': '大 (big) + 人 (person)',
        'example': '他是一个大人。(He is an adult.)',
        'mnemonic': 'A big person is an adult!'
    },
    {
        'word': '小孩',
        'meaning': 'Child',
        'reading': 'xiǎo hái',
        'characters': '小 (small) + 孩 (child)',
        'example': '这个小孩很可爱。(This child is very cute.)',
        'mnemonic': 'A small person is a child.'
    },
]
