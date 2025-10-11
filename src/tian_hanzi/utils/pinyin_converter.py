"""
Pinyin Tone Converter
Converts numbered pinyin (xue3) to accented pinyin (xuě)
"""

# Tone marks for each vowel (neutral, tone 1-4)
TONE_MARKS = {
    'a': ['a', 'ā', 'á', 'ǎ', 'à'],
    'e': ['e', 'ē', 'é', 'ě', 'è'],
    'i': ['i', 'ī', 'í', 'ǐ', 'ì'],
    'o': ['o', 'ō', 'ó', 'ǒ', 'ò'],
    'u': ['u', 'ū', 'ú', 'ǔ', 'ù'],
    'ü': ['ü', 'ǖ', 'ǘ', 'ǚ', 'ǜ'],
    'A': ['A', 'Ā', 'Á', 'Ǎ', 'À'],
    'E': ['E', 'Ē', 'É', 'Ě', 'È'],
    'I': ['I', 'Ī', 'Í', 'Ǐ', 'Ì'],
    'O': ['O', 'Ō', 'Ó', 'Ǒ', 'Ò'],
    'U': ['U', 'Ū', 'Ú', 'Ǔ', 'Ù'],
    'Ü': ['Ü', 'Ǖ', 'Ǘ', 'Ǚ', 'Ǜ'],
}

def numbered_to_accented(pinyin_str):
    """
    Convert numbered pinyin to accented pinyin.
    
    Examples:
        xue3 -> xuě
        Zhong1 -> Zhōng
        xiao3 hai2 -> xiǎo hái
        de5 -> de (tone 5/neutral has no mark)
    
    Args:
        pinyin_str: String with numbered pinyin (e.g., "xue3" or "xiao3 hai2")
    
    Returns:
        String with accented pinyin
    """
    if not pinyin_str:
        return pinyin_str
    
    # Handle multiple syllables separated by spaces
    syllables = pinyin_str.split()
    converted = []
    
    for syllable in syllables:
        # Extract tone number (last character if it's a digit)
        if syllable and syllable[-1].isdigit():
            tone = int(syllable[-1])
            base = syllable[:-1]
        else:
            # No tone number, keep as is
            converted.append(syllable)
            continue
        
        # Tone 5 (neutral) has no mark
        if tone == 5 or tone == 0:
            converted.append(base)
            continue
        
        # Find which vowel gets the tone mark
        # Priority: a, o, e, then last vowel
        tone_position = -1
        
        # Convert v to ü for proper handling
        base_chars = list(base.replace('v', 'ü').replace('V', 'Ü'))
        
        # Rule 1: 'a' or 'e' always get the tone
        for i, char in enumerate(base_chars):
            if char.lower() in ['a', 'e']:
                tone_position = i
                break
        
        # Rule 2: If no 'a' or 'e', 'o' gets it
        if tone_position == -1:
            for i, char in enumerate(base_chars):
                if char.lower() == 'o':
                    tone_position = i
                    break
        
        # Rule 3: Otherwise the last vowel gets it
        if tone_position == -1:
            for i in range(len(base_chars) - 1, -1, -1):
                if base_chars[i].lower() in ['i', 'u', 'ü']:
                    tone_position = i
                    break
        
        # Apply the tone mark
        if tone_position != -1:
            original_char = base_chars[tone_position]
            if original_char in TONE_MARKS:
                base_chars[tone_position] = TONE_MARKS[original_char][tone]
        
        converted.append(''.join(base_chars))
    
    return ' '.join(converted)


if __name__ == "__main__":
    # Test cases
    test_cases = [
        "xue3",
        "Zhong1",
        "xiao3 hai2",
        "de5",
        "yi1 lai4",
        "que1 fa2",
        "jing4",
        "qun2",
    ]
    
    print("Testing pinyin conversion:")
    for test in test_cases:
        result = numbered_to_accented(test)
        print(f"{test:20} -> {result}")
