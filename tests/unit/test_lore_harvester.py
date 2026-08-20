import pytest
from src.application.services.lore_harvester_service import LoreHarvesterService
from src.domain.models import CharacterLoreModel
from src.infrastructure.database import SessionLocal

def test_resolve_character_slug():
    # Anti-Eternia He-Man vs He-Man
    assert LoreHarvesterService.resolve_character_slug("Anti-Eternia He-Man (Origins)") == "anti_eternia_he_man"
    assert LoreHarvesterService.resolve_character_slug("Anti Eternia He-Man") == "anti_eternia_he_man"
    assert LoreHarvesterService.resolve_character_slug("He-Man (Cartoon Collection)") == "he_man"
    assert LoreHarvesterService.resolve_character_slug("Flying Fists He-Man") == "he_man"
    
    # He-Skeletor vs Skeletor
    assert LoreHarvesterService.resolve_character_slug("He-Skeletor Origins") == "he_skeletor"
    assert LoreHarvesterService.resolve_character_slug("Battle Armor Skeletor") == "skeletor"
    
    # Preternia
    assert LoreHarvesterService.resolve_character_slug("He-Ro (Club Grayskull)") == "he_ro"
    assert LoreHarvesterService.resolve_character_slug("Great Black Wizard") == "great_black_wizard"
    
    # Evil Horde / Snake Men
    assert LoreHarvesterService.resolve_character_slug("Hordak Masters of the Universe") == "hordak"
    assert LoreHarvesterService.resolve_character_slug("King Hiss Origins") == "king_hiss"

def test_he_man_mandatory_quote():
    db = SessionLocal()
    try:
        lore = LoreHarvesterService.get_or_create_character_lore(db, "He-Man")
        assert "¡Por el poder de Grayskull, yo tengo el poder!" in lore.lore
        assert lore.faction == "Guerreros Heroicos"
        assert lore.theme_key == "castle_grayskull"
    finally:
        db.close()

def test_anti_eternia_he_man_villain():
    db = SessionLocal()
    try:
        lore = LoreHarvesterService.get_or_create_character_lore(db, "Anti-Eternia He-Man")
        assert lore.faction == "Guerreros del Mal"
        assert lore.theme_key == "snake_mountain"
        assert "Multiverso Oscuro" in lore.lore
    finally:
        db.close()

def test_inmutable_cache_no_overwrite():
    db = SessionLocal()
    try:
        first_pass = LoreHarvesterService.get_or_create_character_lore(db, "Clawful")
        original_lore = first_pass.lore
        
        LoreHarvesterService.update_character(db, "clawful", {"lore": "Edición personalizada inmutable"})
        
        second_pass = LoreHarvesterService.get_or_create_character_lore(db, "Clawful (Cartoon Collection)")
        assert second_pass.lore == "Edición personalizada inmutable"
    finally:
        db.close()
