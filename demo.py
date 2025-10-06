#!/usr/bin/env python3
"""
Demo script for Tian Hanzi Deck framework
Shows how to use the deck creation framework without actually generating a deck
"""

def demo_framework():
    """Demonstrate the deck framework"""
    print("=" * 60)
    print("Tian Hanzi Deck Framework Demo")
    print("=" * 60)
    
    try:
        from example_data import RADICALS, HANZI, VOCABULARY
        
        print("\n📦 Deck Structure:")
        print("  └─ Tian Hanzi Deck (Main Deck)")
        print("     ├─ 1_Radicals")
        print("     ├─ 2_Hanzi")
        print("     └─ 3_Vocabulary")
        
        print(f"\n📊 Content Summary:")
        print(f"  • Radicals: {len(RADICALS)} cards")
        print(f"  • Hanzi: {len(HANZI)} cards")
        print(f"  • Vocabulary: {len(VOCABULARY)} cards")
        print(f"  • Total: {len(RADICALS) + len(HANZI) + len(VOCABULARY)} cards")
        
        print("\n🎴 Sample Cards:")
        
        # Show a sample radical
        if RADICALS:
            radical = RADICALS[0]
            print(f"\n  Radical Card:")
            print(f"    Front: {radical['radical']}")
            print(f"    Back: {radical['meaning']}")
            print(f"    Mnemonic: {radical['mnemonic'][:50]}...")
        
        # Show a sample hanzi
        if HANZI:
            hanzi = HANZI[0]
            print(f"\n  Hanzi Card:")
            print(f"    Front: {hanzi['character']}")
            print(f"    Back: {hanzi['meaning']} ({hanzi['reading']})")
            print(f"    Radicals: {hanzi['radicals']}")
            print(f"    Mnemonic: {hanzi['mnemonic'][:50]}...")
        
        # Show a sample vocabulary
        if VOCABULARY:
            vocab = VOCABULARY[0]
            print(f"\n  Vocabulary Card:")
            print(f"    Front: {vocab['word']}")
            print(f"    Back: {vocab['meaning']} ({vocab['reading']})")
            print(f"    Characters: {vocab['characters']}")
            if vocab.get('example'):
                print(f"    Example: {vocab['example'][:50]}...")
            print(f"    Mnemonic: {vocab['mnemonic'][:50]}...")
        
        print("\n" + "=" * 60)
        print("✓ Framework loaded successfully!")
        print("\nTo generate the actual deck, run:")
        print("  python create_deck.py")
        print("\nMake sure you have genanki installed:")
        print("  pip install -r requirements.txt")
        print("=" * 60)
        
    except ImportError as e:
        print(f"\n❌ Error: Could not load example data")
        print(f"   {e}")


if __name__ == '__main__':
    demo_framework()
