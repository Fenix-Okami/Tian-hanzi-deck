"""Unit tests for data generation functionality"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from tian_hanzi.data_generator import HSKDeckBuilder


class TestHSKDeckBuilder:
    """Tests for HSKDeckBuilder class"""
    
    def test_initialization(self):
        """Test HSKDeckBuilder initialization"""
        builder = HSKDeckBuilder(hsk_levels=[1, 2, 3])
        
        assert builder.hsk_levels == [1, 2, 3]
        assert builder.vocabulary == []
        assert builder.hanzi_set == set()
        assert builder.hanzi_data == {}
        assert builder.components == {}
    
    def test_initialization_custom_levels(self):
        """Test initialization with custom HSK levels"""
        builder = HSKDeckBuilder(hsk_levels=[1, 2])
        assert builder.hsk_levels == [1, 2]
        
        builder = HSKDeckBuilder(hsk_levels=[3, 4, 5])
        assert builder.hsk_levels == [3, 4, 5]
    
    @pytest.mark.unit
    def test_extract_hanzi_from_vocabulary(self):
        """Test extraction of hanzi from vocabulary"""
        builder = HSKDeckBuilder()
        builder.vocabulary = [
            {'word': '你好', 'hsk_level': 1},
            {'word': '学习', 'hsk_level': 2},
            {'word': 'hello', 'hsk_level': 1},  # Non-Chinese
        ]
        
        hanzi_set = builder.extract_hanzi_from_vocabulary()
        
        # Should extract only Chinese characters
        assert '你' in hanzi_set
        assert '好' in hanzi_set
        assert '学' in hanzi_set
        assert '习' in hanzi_set
        assert 'h' not in hanzi_set
        assert 'e' not in hanzi_set
    
    @pytest.mark.unit
    def test_hanzi_extraction_deduplication(self):
        """Test that duplicate hanzi are properly deduplicated"""
        builder = HSKDeckBuilder()
        builder.vocabulary = [
            {'word': '好好', 'hsk_level': 1},
            {'word': '你好', 'hsk_level': 1},
        ]
        
        hanzi_set = builder.extract_hanzi_from_vocabulary()
        
        # Should have unique characters only
        assert len(hanzi_set) == 2
        assert '好' in hanzi_set
        assert '你' in hanzi_set
    
    @pytest.mark.unit
    def test_empty_vocabulary(self):
        """Test handling of empty vocabulary"""
        builder = HSKDeckBuilder()
        builder.vocabulary = []
        
        hanzi_set = builder.extract_hanzi_from_vocabulary()
        assert len(hanzi_set) == 0
    
    @pytest.mark.unit
    def test_component_productivity_calculation(self):
        """Test component productivity score calculation"""
        from collections import Counter
        builder = HSKDeckBuilder()
        
        # Mock component productivity counter
        builder.component_productivity = Counter({
            '亻': 50,
            '口': 45,
            '女': 30,
        })
        
        # Mock decomposer to return meanings
        with patch.object(builder.decomposer, 'get_radical_meaning') as mock_get_meaning:
            mock_get_meaning.side_effect = lambda x: {
                '亻': 'person',
                '口': 'mouth',
                '女': 'woman'
            }.get(x, f'Component {x}')
            
            components = builder.calculate_component_productivity()
        
        assert len(components) == 3
        assert components['亻']['usage_count'] == 50
        assert components['口']['usage_count'] == 45
        assert components['女']['usage_count'] == 30
        assert components['亻']['meaning'] == 'person'
    
    @pytest.mark.unit
    def test_component_without_meaning(self):
        """Test components without meanings get default label"""
        from collections import Counter
        builder = HSKDeckBuilder()
        builder.component_productivity = Counter({'X': 5})
        
        with patch.object(builder.decomposer, 'get_radical_meaning') as mock_get_meaning:
            mock_get_meaning.return_value = None
            components = builder.calculate_component_productivity()
        
        assert 'X' in components
        assert 'Component X' in components['X']['meaning']


class TestDataExport:
    """Tests for data export functionality"""
    
    @pytest.mark.unit
    def test_vocabulary_dataframe_creation(self, sample_vocabulary_data, temp_data_dir):
        """Test vocabulary data can be converted to DataFrame"""
        import pandas as pd
        
        df = pd.DataFrame(sample_vocabulary_data)
        
        assert len(df) == 3
        assert 'word' in df.columns
        assert 'hsk_level' in df.columns
        assert 'pinyin' in df.columns
        assert df.iloc[0]['word'] == '你好'
    
    @pytest.mark.unit
    def test_hanzi_dataframe_creation(self, sample_hanzi_data):
        """Test hanzi data can be converted to DataFrame"""
        import pandas as pd
        
        df = pd.DataFrame(sample_hanzi_data)
        
        assert len(df) == 3
        assert 'hanzi' in df.columns
        assert 'components' in df.columns
        assert 'component_count' in df.columns
        assert df.iloc[0]['hanzi'] == '你'
    
    @pytest.mark.unit
    def test_radicals_dataframe_creation(self, sample_radicals_data):
        """Test radicals data can be converted to DataFrame"""
        import pandas as pd
        
        df = pd.DataFrame(sample_radicals_data)
        
        assert len(df) == 3
        assert 'radical' in df.columns
        assert 'meaning' in df.columns
        assert 'usage_count' in df.columns
        assert df.iloc[0]['radical'] == '亻'


class TestDataStatistics:
    """Tests for statistics calculation"""
    
    @pytest.mark.unit
    def test_statistics_with_data(self):
        """Test statistics calculation with populated data"""
        builder = HSKDeckBuilder()
        builder.vocabulary = [
            {'hsk_level': 1}, {'hsk_level': 1}, {'hsk_level': 2}
        ]
        builder.hanzi_data = {'你': {}, '好': {}, '学': {}}
        builder.components = {
            '亻': {'productivity_score': 50, 'meaning': 'person'},
            '口': {'productivity_score': 45, 'meaning': 'mouth'}
        }
        
        # Should not raise any exceptions
        builder.print_statistics()
    
    @pytest.mark.unit
    def test_statistics_with_empty_data(self):
        """Test statistics calculation with empty data"""
        builder = HSKDeckBuilder()
        
        # Should handle empty data gracefully
        builder.print_statistics()
