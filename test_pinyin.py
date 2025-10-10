#!/usr/bin/env python3
"""Quick test of accented pinyin conversion"""

from generate_tian_v1_fast import init_worker, process_character_for_hanzi
from hanzipy.dictionary import HanziDictionary

# Initialize
init_worker()
dictionary = HanziDictionary()

# Test with first 3 characters
print("Testing accented pinyin conversion:\n")
for pos in [1, 2, 3]:
    char_data = dictionary.get_character_in_frequency_list_by_position(pos)
    result = process_character_for_hanzi(char_data)
    if result:
        print(f"Character: {result['character']}")
        print(f"Reading:   {result['reading']}")
        print(f"Meaning:   {result['meaning'][:60]}...")
        print()
