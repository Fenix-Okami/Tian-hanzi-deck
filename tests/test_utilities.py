"""Unit tests for utility functions"""
import pytest
from tian_hanzi.core.pinyin import numbered_to_accented


class TestPinyinConverter:
    """Tests for pinyin tone converter"""
    
    def test_single_syllable_tones(self):
        """Test conversion of single syllables with different tones"""
        assert numbered_to_accented("xue3") == "xuě"
        assert numbered_to_accented("Zhong1") == "Zhōng"
        assert numbered_to_accented("jing4") == "jìng"
        assert numbered_to_accented("qun2") == "qún"
    
    def test_multiple_syllables(self):
        """Test conversion of multiple syllables"""
        assert numbered_to_accented("xiao3 hai2") == "xiǎo hái"
        assert numbered_to_accented("yi1 lai4") == "yī lài"
        assert numbered_to_accented("que1 fa2") == "quē fá"
    
    def test_neutral_tone(self):
        """Test neutral tone (tone 5 or 0) has no mark"""
        assert numbered_to_accented("de5") == "de"
        assert numbered_to_accented("de0") == "de"
    
    def test_no_tone_number(self):
        """Test syllables without tone numbers are unchanged"""
        assert numbered_to_accented("hello") == "hello"
        assert numbered_to_accented("test word") == "test word"
    
    def test_empty_string(self):
        """Test empty string handling"""
        assert numbered_to_accented("") == ""
        assert numbered_to_accented(None) is None
    
    def test_tone_placement_rules(self):
        """Test correct placement of tone marks"""
        # 'a' and 'e' always get the tone
        assert numbered_to_accented("ai4") == "ài"
        assert numbered_to_accented("ei1") == "ēi"
        
        # 'o' gets it if no 'a' or 'e'
        assert numbered_to_accented("ou3") == "ǒu"
        
        # Last vowel gets it otherwise
        assert numbered_to_accented("iu4") == "iù"
    
    def test_v_to_u_umlaut(self):
        """Test v is converted to ü"""
        assert numbered_to_accented("lv3") == "lǚ"
        assert numbered_to_accented("nv3") == "nǚ"
    
    def test_capitalization_preserved(self):
        """Test that capitalization is preserved"""
        assert numbered_to_accented("Zhong1") == "Zhōng"
        assert numbered_to_accented("ZHONG1") == "ZHŌNG"


class TestDataCleaning:
    """Tests for data cleaning functions"""
    
    def test_clean_surname_from_definition(self):
        """Test surname removal from definitions"""
        from tian_hanzi.core.cards import clean_surname_from_definition
        
        # Simple surname at start
        result, is_surname = clean_surname_from_definition("surname Wang")
        assert result == ""
        assert is_surname == True
        
        # Surname with other meanings
        result, is_surname = clean_surname_from_definition("China/Chinese/surname Zhong")
        assert result == "China/Chinese"
        assert is_surname == True
        
        # Multiple meanings with surname
        result, is_surname = clean_surname_from_definition("to lean; to depend; surname Li")
        assert result == "to lean; to depend"
        assert is_surname == True
        
        # No surname
        result, is_surname = clean_surname_from_definition("hello; hi")
        assert result == "hello; hi"
        assert is_surname == False
        
        # Empty string
        result, is_surname = clean_surname_from_definition("")
        assert result == ""
        assert is_surname == False
