import pytest
from ai_utils.text.preprocess import clean_text

def test_clean_text_basic():
    assert clean_text("Hello, World!") == "hello world"

def test_clean_text_special_chars():
    assert clean_text("Python #1 @AI") == "python 1 ai"

def test_clean_text_empty():
    assert clean_text("") == ""

def test_clean_text_invalid_input():
    with pytest.raises(TypeError):
        clean_text(123)
