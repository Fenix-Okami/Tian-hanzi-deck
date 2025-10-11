#!/usr/bin/env python3
"""
Shared utility functions for card creation
Used by both create_hsk_deck.py and create_samples.py
"""

import pandas as pd


def create_ruby_text(word, pinyin):
    """
    Create HTML ruby text with pinyin above each character.
    Splits multi-syllable pinyin and pairs with each character.
    
    Example: create_ruby_text("故事", "gù shi") 
    Returns: <ruby><rb>故</rb><rt>gù</rt></ruby><ruby><rb>事</rb><rt>shi</rt></ruby>
    
    Args:
        word: Chinese word/character(s)
        pinyin: Pinyin reading (space-separated for multi-character words)
    
    Returns:
        HTML ruby text string
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
        return f'<ruby><rb class="vocab-word">{word}</rb><rt class="pinyin-reading">{pinyin}</rt></ruby>'


def format_components_with_meanings(components_str, radicals_df):
    """
    Format components with their meanings.
    
    Example: "一|口|丨" -> "一 (one), 口 (mouth), 丨 (line)"
    
    Args:
        components_str: Pipe-separated or comma-separated components string
        radicals_df: DataFrame with radical meanings
    
    Returns:
        Formatted string with components and meanings
    """
    # Handle missing/empty components
    if not components_str or pd.isna(components_str) or components_str == 'Unknown':
        return "No components"
    
    # Split components by | or comma
    if '|' in str(components_str):
        components = [c.strip() for c in str(components_str).split('|')]
    else:
        components = [c.strip() for c in str(components_str).split(',')]
    
    formatted_parts = []
    for comp in components:
        if not comp:
            continue
        
        # Look up meaning in radicals dataframe
        radical_row = radicals_df[radicals_df['radical'] == comp]
        if not radical_row.empty:
            meaning = radical_row.iloc[0].get('meaning', '')
            # Truncate long meanings
            if meaning and len(meaning) > 30:
                meaning = meaning[:27] + '...'
            formatted_parts.append(f"{comp} ({meaning})")
        else:
            formatted_parts.append(comp)
    
    return ', '.join(formatted_parts) if formatted_parts else "No components"
