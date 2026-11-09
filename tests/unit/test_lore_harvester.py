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


# ─── Grimorio MOTU: slugs, facciones, procedencia e inmutabilidad (hermético, BD en memoria) ───

from src.domain.models import ProductModel
from src.domain.motu_canon_database import (
    CURATED_SOURCE,
    FACTION_TO_THEME,
    VALID_FACTIONS,
    canonicalize_slug,
    resolve_motu_profile,
)
from src.application.services.lore_harvester_service import VerifiedLoreConflict
from src.application.services.product_lore_seed import ProductLoreSeedService
from tests.conftest import _TestSession


def test_canonicalize_slug_strips_accents():
    assert canonicalize_slug("Príncipe Adam") == "principe_adam"
    assert canonicalize_slug("Anti-Eternia He-Man") == "anti_eternia_he_man"


def test_closed_faction_catalog_has_eight_factions_over_six_themes():
    assert len(VALID_FACTIONS) == 8
    assert "Gobernantes de Solaria" in VALID_FACTIONS and "Alianzas del Multiverso" in VALID_FACTIONS
    assert len(set(FACTION_TO_THEME.values())) == 6


def test_resolve_profile_factions_for_sun_man_and_crossovers():
    assert resolve_motu_profile("Sun-Man")["faction"] == "Gobernantes de Solaria"
    assert resolve_motu_profile("Lion-O")["faction"] == "Alianzas del Multiverso"


def test_update_character_persists_mana_cost_and_marks_curated(client):
    with _TestSession() as db:
        slug = "grimorio_test_mana"
        db.add(CharacterLoreModel(
            slug=slug, canonical_name="Mana Test", faction="Guerreros Heroicos", theme_key="castle_grayskull",
            type_line="t", special_move="s", lore="l", is_verified=False, source_url="https://wiki",
        ))
        db.commit()
        updated = LoreHarvesterService.update_character(db, slug, {"mana_cost": "{1}{R}{R}", "fuerza": 99})
        assert updated.mana_cost == "{1}{R}{R}"
        assert updated.fuerza == 99
        assert updated.is_verified is True
        assert updated.source_url == CURATED_SOURCE
        db.delete(updated)
        db.commit()


def test_seed_updates_system_canon_but_preserves_curated(client):
    with _TestSession() as db:
        ProductLoreSeedService.seed_canonical_characters(db, force=True)
        slug = canonicalize_slug("Ruler of the Sun")
        row = db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == slug).first()
        assert row is not None and row.faction == "Gobernantes de Solaria"

        # Edicion humana: queda curada y el sembrado normal no la pisa
        LoreHarvesterService.update_character(db, slug, {"lore": "Edición del Master"})
        ProductLoreSeedService.seed_canonical_characters(db, force=False)
        db.expire_all()
        assert db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == slug).first().lore == "Edición del Master"

        # force=True sobrescribe lo curado y devuelve el canon del sistema
        ProductLoreSeedService.seed_canonical_characters(db, force=True)
        db.expire_all()
        restored = db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == slug).first()
        assert restored.lore != "Edición del Master"
        assert restored.source_url == "Canon MOTU Oficial"


def test_seed_is_idempotent_and_reports_no_changes_second_pass(client):
    with _TestSession() as db:
        ProductLoreSeedService.seed_canonical_characters(db, force=False)
        second = ProductLoreSeedService.seed_canonical_characters(db, force=False)
        assert second["created"] == 0 and second["updated"] == 0


def test_harvest_for_product_requires_force_for_verified_character(client, monkeypatch):
    calls = []

    def fake_wiki(name):
        calls.append(name)
        return {"canonical_name": "Verified Hero", "lore": "texto de wiki", "faction": "Guerreros Heroicos",
                "theme_key": "castle_grayskull", "source_url": "https://he-man.fandom.com/wiki/Verified_Hero"}

    monkeypatch.setattr(LoreHarvesterService, "harvest_from_wiki_grayskull", staticmethod(fake_wiki))

    with _TestSession() as db:
        product = ProductModel(name="Verified Hero", category="Action Figures", sub_category="Origins",
                               figure_id="LORE-HARVEST-1", is_vintage=False)
        db.add(product)
        db.add(CharacterLoreModel(
            slug="verified_hero", canonical_name="Verified Hero", faction="Guerreros Heroicos",
            theme_key="castle_grayskull", type_line="t", special_move="s", lore="curado", is_verified=True,
            source_url=CURATED_SOURCE,
        ))
        db.commit()

        with pytest.raises(VerifiedLoreConflict):
            LoreHarvesterService.harvest_for_product(db, product.id)
        assert calls == []  # sin peticion de red

        forced = LoreHarvesterService.harvest_for_product(db, product.id, force=True)
        assert calls == ["Verified Hero"]
        assert forced.is_verified is False  # todo raspado web queda pendiente de revision

        db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == "verified_hero").delete()
        db.delete(product)
        db.commit()
