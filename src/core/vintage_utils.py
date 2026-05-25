import re

def check_is_vintage(text: str) -> bool:
    """
    Checks if the given text indicates a vintage item.
    Returns True if the text contains 'vintage' (case-insensitive)
    or a 4-digit year in the range 1980-1989.
    """
    if not text:
        return False
    
    text_lower = text.lower()
    if "vintage" in text_lower:
        return True
        
    # Match any word boundaries containing a year between 1980 and 1989
    years = re.findall(r"\b(198[0-9])\b", text)
    if years:
        return True
        
    return False
