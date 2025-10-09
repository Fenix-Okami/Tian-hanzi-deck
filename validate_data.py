#!/usr/bin/env python3
"""
Data validation script for Tian Hanzi Deck
Validates the structure of radicals, hanzi, and vocabulary data
"""

def validate_radical(radical, index):
    """Validate a radical entry"""
    errors = []
    required_fields = ['radical', 'meaning', 'mnemonic']
    
    for field in required_fields:
        if field not in radical:
            errors.append(f"Radical {index}: Missing required field '{field}'")
        elif not radical[field] or not isinstance(radical[field], str):
            errors.append(f"Radical {index}: Field '{field}' must be a non-empty string")
    
    return errors


def validate_hanzi(hanzi, index):
    """Validate a hanzi entry"""
    errors = []
    required_fields = ['character', 'meaning', 'reading', 'radicals', 'meaning_mnemonic', 'reading_mnemonic']
    
    for field in required_fields:
        if field not in hanzi:
            errors.append(f"Hanzi {index}: Missing required field '{field}'")
        elif not hanzi[field] or not isinstance(hanzi[field], str):
            errors.append(f"Hanzi {index}: Field '{field}' must be a non-empty string")
    
    return errors


def validate_vocab(vocab, index):
    """Validate a vocabulary entry"""
    errors = []
    required_fields = ['word', 'meaning', 'reading', 'characters', 'mnemonic']
    
    for field in required_fields:
        if field not in vocab:
            errors.append(f"Vocab {index}: Missing required field '{field}'")
        elif not vocab[field] or not isinstance(vocab[field], str):
            errors.append(f"Vocab {index}: Field '{field}' must be a non-empty string")
    
    # Example is optional
    if 'example' in vocab and vocab['example'] and not isinstance(vocab['example'], str):
        errors.append(f"Vocab {index}: Field 'example' must be a string if provided")
    
    return errors


def validate_data(radicals_data, hanzi_data, vocab_data):
    """Validate all data structures"""
    all_errors = []
    
    # Validate radicals
    for i, radical in enumerate(radicals_data, 1):
        all_errors.extend(validate_radical(radical, i))
    
    # Validate hanzi
    for i, hanzi in enumerate(hanzi_data, 1):
        all_errors.extend(validate_hanzi(hanzi, i))
    
    # Validate vocabulary
    for i, vocab in enumerate(vocab_data, 1):
        all_errors.extend(validate_vocab(vocab, i))
    
    return all_errors


if __name__ == '__main__':
    try:
        from example_data import RADICALS, HANZI, VOCABULARY
        
        print("Validating data structures...")
        print(f"  Radicals: {len(RADICALS)} entries")
        print(f"  Hanzi: {len(HANZI)} entries")
        print(f"  Vocabulary: {len(VOCABULARY)} entries")
        
        errors = validate_data(RADICALS, HANZI, VOCABULARY)
        
        if errors:
            print("\n❌ Validation failed with the following errors:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("\n✓ All data structures are valid!")
            print(f"  Total cards: {len(RADICALS) + len(HANZI) + len(VOCABULARY)}")
    
    except ImportError as e:
        print(f"❌ Error importing example_data: {e}")
        print("Make sure example_data.py exists and contains RADICALS, HANZI, and VOCABULARY")
