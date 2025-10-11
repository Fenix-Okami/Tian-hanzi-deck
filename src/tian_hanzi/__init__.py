"""
Tian Hanzi Deck - Core Package

HSK-based Chinese character learning deck generator
"""

__version__ = "2.0.0"

from .data_generator import HSKDeckBuilder

__all__ = [
    'HSKDeckBuilder',
]
