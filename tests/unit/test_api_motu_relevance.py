import pytest
from src.core.vintage_utils import validate_motu_relevance

def test_validate_motu_relevance_valid_cases():
    valid_titles = [
        "He-Man Origins Mattel 2020",
        "Skeletor vintage 1982 loose",
        "Castle Grayskull vintage retro MOTU",
        "Hordak New Eternia Master of the Universe",
        "Turtles of Grayskull Donatello",
        "She-Ra Princess of Power Vintage figure",
        "Lote Figuras MOTU",
        "Moss Man Origins",
        "Transformers MOTU crossover He-Man Origins",
        "Stranger Things He-Man Masters of the Universe",
        "Turtles of Grayskull Shredder MOTU",
        "Maitres de l'univers He-Man vintage",
        "Maitres de l univers Skeletor 1983"
    ]
    for title in valid_titles:
        is_relevant, reason = validate_motu_relevance(title)
        assert is_relevant is True, f"Fallo en título esperado válido: '{title}', motivo: {reason}"

def test_validate_motu_relevance_invalid_funko():
    funko_titles = [
        "Funko Pop He-man Masters of the Universe",
        "Skeletor pop MOTU figura",
        "Funko pop! Hordak 2021"
    ]
    for title in funko_titles:
        is_relevant, reason = validate_motu_relevance(title)
        assert is_relevant is False
        assert "funko" in reason.lower() or "pop" in reason.lower()

def test_validate_motu_relevance_invalid_big_jim():
    big_jim_titles = [
        "Big Jim vintage 1978 Mattel",
        "Figura Bigjim retro loose",
        "Big-Jim ropa y accesorios"
    ]
    for title in big_jim_titles:
        is_relevant, reason = validate_motu_relevance(title)
        assert is_relevant is False
        assert "big jim" in reason.lower()

def test_validate_motu_relevance_invalid_masterverse():
    masterverse_titles = [
        "He-Man Masterverse Mattel figura",
        "Skeletor Masterverse Revelation",
        "Masterverse Revelation Teela figure"
    ]
    for title in masterverse_titles:
        is_relevant, reason = validate_motu_relevance(title)
        assert is_relevant is False
        assert "masterverse" in reason.lower()

def test_validate_motu_relevance_non_motu_vintage():
    non_motu_titles = [
        "Barbie vintage 1985 Mattel",
        "Transformers vintage G1 Optimus Prime",
        "G.I. Joe vintage figura de accion",
        "Max Steel vintage figura 1999"
    ]
    for title in non_motu_titles:
        is_relevant, reason = validate_motu_relevance(title)
        assert is_relevant is False
        assert "no contiene" in reason.lower() or "marca excluida" in reason.lower()
