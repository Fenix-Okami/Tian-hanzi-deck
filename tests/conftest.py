"""Pytest configuration and shared fixtures"""
import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import pytest
import pandas as pd
from typing import Dict, List


@pytest.fixture
def sample_vocabulary_data() -> List[Dict]:
    """Sample vocabulary data for testing"""
    return [
        {
            'word': '你好',
            'hsk_level': 1,
            'frequency_position': 1,
            'pinyin': 'nǐ hǎo',
            'meaning': 'hello',
            'is_surname': False
        },
        {
            'word': '中国',
            'hsk_level': 1,
            'frequency_position': 2,
            'pinyin': 'Zhōng guó',
            'meaning': 'China',
            'is_surname': False
        },
        {
            'word': '学习',
            'hsk_level': 2,
            'frequency_position': 1,
            'pinyin': 'xué xí',
            'meaning': 'to study',
            'is_surname': False
        },
    ]


@pytest.fixture
def sample_hanzi_data() -> List[Dict]:
    """Sample hanzi data for testing"""
    return [
        {
            'hanzi': '你',
            'pinyin': 'nǐ',
            'meaning': 'you',
            'components': '亻|尔',
            'component_count': 2,
            'hsk_level': 1,
            'is_surname': False
        },
        {
            'hanzi': '好',
            'pinyin': 'hǎo',
            'meaning': 'good',
            'components': '女|子',
            'component_count': 2,
            'hsk_level': 1,
            'is_surname': False
        },
        {
            'hanzi': '中',
            'pinyin': 'zhōng',
            'meaning': 'middle',
            'components': '口|丨',
            'component_count': 2,
            'hsk_level': 1,
            'is_surname': False
        },
    ]


@pytest.fixture
def sample_radicals_data() -> List[Dict]:
    """Sample radicals data for testing"""
    return [
        {
            'radical': '亻',
            'meaning': 'person',
            'usage_count': 50
        },
        {
            'radical': '口',
            'meaning': 'mouth',
            'usage_count': 45
        },
        {
            'radical': '女',
            'meaning': 'woman',
            'usage_count': 30
        },
    ]


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for testing"""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir
