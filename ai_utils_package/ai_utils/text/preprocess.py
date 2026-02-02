import re

def clean_text(text):
    """
    ลบตัวอักษรพิเศษและแปลงเป็น lowercase
    Removes special characters and converts to lowercase.
    Note: Currently supports English alphanumeric characters.
    """
    if not isinstance(text, str):
        raise TypeError("Input text must be a string")
    return re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
