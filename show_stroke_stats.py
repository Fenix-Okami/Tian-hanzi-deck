#!/usr/bin/env python3
"""
Display stroke count statistics
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd

print('='*70)
print('STROKE COUNT SUMMARY')
print('='*70)

hanzi_df = pd.read_csv('data/hanzi.csv')
vocab_df = pd.read_csv('data/vocabulary.csv')

print('\nHanzi Stroke Statistics:')
print(f'  Min:    {hanzi_df["stroke_count"].min()} strokes')
print(f'  Max:    {hanzi_df["stroke_count"].max()} strokes')
print(f'  Mean:   {hanzi_df["stroke_count"].mean():.1f} strokes')
print(f'  Median: {hanzi_df["stroke_count"].median():.0f} strokes')

print('\nVocabulary Stroke Statistics:')
print(f'  Min:    {vocab_df["stroke_count"].min()} strokes')
print(f'  Max:    {vocab_df["stroke_count"].max()} strokes')
print(f'  Mean:   {vocab_df["stroke_count"].mean():.1f} strokes')
print(f'  Median: {vocab_df["stroke_count"].median():.0f} strokes')

print('\nMost Complex Hanzi (by strokes):')
top_hanzi = hanzi_df.nlargest(5, 'stroke_count')[['hanzi', 'pinyin', 'stroke_count']]
for _, row in top_hanzi.iterrows():
    h = row['hanzi']
    p = row['pinyin']
    s = row['stroke_count']
    print(f'  {h} ({p}) - {s} strokes')

print('\nMost Complex Vocabulary (by strokes):')
top_vocab = vocab_df.nlargest(5, 'stroke_count')[['word', 'pinyin', 'stroke_count']]
for _, row in top_vocab.iterrows():
    w = row['word']
    p = row['pinyin']
    s = row['stroke_count']
    print(f'  {w} ({p}) - {s} strokes')
