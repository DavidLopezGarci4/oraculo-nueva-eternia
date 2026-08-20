import logging
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.domain.models import CharacterLoreModel, ProductModel
from src.domain.motu_canon_database import MOTU_LORE_ENCYCLOPEDIA

logger = logging.getLogger("oraculo.lore_harvester")

class LoreHarvesterService:
    """
    Servicio de Gestión de Lore y Entidades Canónicas MOTU.
    Opera bajo política de coste 0 (Sin IA ni tokens).
    Regla de Oro: Una vez que un personaje tiene lore en BD, no se vuelve a cosechar.
    """

    FACTION_MAPPING: Dict[str, Tuple[str, str]] = {
        # Inglés -> (Facción en Español, theme_key)
        "heroic": ("Guerreros Heroicos", "castle_grayskull"),
        "grayskull": ("Guerreros Heroicos", "castle_grayskull"),
        "evil warriors": ("Guerreros del Mal", "snake_mountain"),
        "snake mountain": ("Guerreros del Mal", "snake_mountain"),
        "horde": ("La Horda del Terror", "evil_horde"),
        "evil horde": ("La Horda del Terror", "evil_horde"),
        "snake men": ("Los Hombres Serpiente", "snake_men"),
        "serpent": ("Los Hombres Serpiente", "snake_men"),
        "great rebellion": ("La Gran Rebelión", "great_rebellion"),
        "rebellion": ("La Gran Rebelión", "great_rebellion"),
        "princess of power": ("La Gran Rebelión", "great_rebellion"),
        "cosmic": ("Guardianes Cósmicos", "cosmic_enforcers"),
        "enforcers": ("Guardianes Cósmicos", "cosmic_enforcers"),
        "rulers of the sun": ("Gobernantes de Solaria", "castle_grayskull"),
        "sun-man": ("Gobernantes de Solaria", "castle_grayskull"),
        "anti-eternia": ("Guerreros del Mal", "snake_mountain")
    }

    @classmethod
    def normalize_slug(cls, name: str) -> str:
        """Convierte un nombre en slug limpio de personaje."""
        if not name:
            return "desconocido"
        
        clean = name.lower().strip()
        # Eliminar sufijos de líneas de juguetes y oleadas
        clean = re.sub(r'[\(\[\{].*?[\)\]\}]', '', clean)
        clean = re.sub(r'\b(origins|cartoon|masterverse|vintage|new eternia|revelation|club grayskull|commemorative|classics|deluxe|wave \d+|40th anniversary|cgc|moc|loose)\b', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'[^a-z0-9\s\-]', '', clean).strip()
        clean = re.sub(r'[\s\-]+', '_', clean)
        return clean or "motu_figure"

    @classmethod
    def resolve_character_slug(cls, product_name: str) -> str:
        """
        Resuelve el slug canónico de un producto con prioridad para personajes oscuros.
        """
        clean = (product_name or '').lower()

        # Prioridad Máxima: Multiverso Oscuro
        if "anti-eternia" in clean or "anti eternia" in clean or "anti-he-man" in clean:
            return "anti_eternia_he_man"
        if "he-skeletor" in clean or "heskeletor" in clean:
            return "he_skeletor"
        if "great black wizard" in clean:
            return "great_black_wizard"
        if "he-ro" in clean or ("hero" in clean and "grayskull" not in clean):
            return "he_ro"
        if "she-ra" in clean or "shera" in clean:
            return "she_ra"
        if "prince adam" in clean or "adam" in clean:
            return "prince_adam"
        if "he-man" in clean or "he man" in clean:
            return "he_man"
        if "skeletor" in clean:
            return "skeletor"
        if "hordak" in clean:
            return "hordak"
        if "king hiss" in clean or "king hsss" in clean:
            return "king_hiss"

        return cls.normalize_slug(product_name)

    @classmethod
    def get_or_create_character_lore(cls, db: Session, character_name: str) -> CharacterLoreModel:
        """
        Busca el lore de un personaje en BD.
        Si ya existe, lo devuelve inmediatamente (0 peticiones a internet).
        Si no existe, consulta la enciclopedia canónica o la Wiki Grayskull API.
        """
        slug = cls.resolve_character_slug(character_name)
        existing = db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == slug).first()
        if existing:
            return existing

        # Comprobar si existe en la enciclopedia canónica local
        enc_key = slug.replace('_', ' ')
        for k, data in MOTU_LORE_ENCYCLOPEDIA.items():
            if k == enc_key or k in enc_key or enc_key in k:
                stats = data.get("stats", {})
                new_lore = CharacterLoreModel(
                    slug=slug,
                    canonical_name=data.get("canonical_name", character_name.title()),
                    faction=data.get("faction", "Guerreros Heroicos"),
                    theme_key=data.get("frame_theme", "castle_grayskull"),
                    type_line=data.get("type_line", "Criatura Legendaria — Guerrero Heroico"),
                    special_move=data.get("special_move", "Furia del Relámpago de Grayskull"),
                    quote=data.get("lore", "")[:60] if data.get("lore") else None,
                    lore=data.get("lore", "Noble defensor de la corte real de Eternia y custodio de los secretos de Grayskull."),
                    fuerza=stats.get("fuerza", 88),
                    magia=stats.get("magia", 78),
                    defensa=stats.get("defensa", 90),
                    agilidad=stats.get("agilidad", 85),
                    is_verified=True,
                    source_url="Canon MOTU Local"
                )
                db.add(new_lore)
                db.commit()
                db.refresh(new_lore)
                logger.info(f"✨ [LORE SEED] Creado lore canónico local para {slug}")
                return new_lore

        # Si no existe en la enciclopedia local, cosechar desde Wiki Grayskull API (Coste 0)
        harvested = cls.harvest_from_wiki_grayskull(character_name)
        new_lore = CharacterLoreModel(
            slug=slug,
            canonical_name=harvested.get("canonical_name", character_name.title()),
            faction=harvested.get("faction", "Guerreros Heroicos"),
            theme_key=harvested.get("theme_key", "castle_grayskull"),
            type_line=harvested.get("type_line", "Criatura Legendaria — Guerrero Heroico"),
            special_move=harvested.get("special_move", "Furia del Relámpago de Grayskull"),
            quote=harvested.get("quote"),
            lore=harvested.get("lore", "Guerrero descubierto en los confines del multiverso de Eternia."),
            fuerza=harvested.get("fuerza", 85),
            magia=harvested.get("magia", 75),
            defensa=harvested.get("defensa", 85),
            agilidad=harvested.get("agilidad", 85),
            is_verified=False,
            source_url=harvested.get("source_url")
        )
        db.add(new_lore)
        db.commit()
        db.refresh(new_lore)
        logger.info(f"🌐 [LORE HARVEST] Cosechado nuevo personaje {slug} de Wiki Grayskull (Pendiente de Revisión)")
        return new_lore

    @classmethod
    def harvest_from_wiki_grayskull(cls, character_name: str) -> Dict[str, Any]:
        """
        Consulta la API pública y gratuita de MediaWiki de Wiki Grayskull (Fandom).
        0 tokens, 0 coste.
        """
        clean_title = re.sub(r'[\(\[\{].*?[\)\]\}]', '', character_name).strip()
        encoded_title = urllib.parse.quote(clean_title)
        api_url = f"https://he-man.fandom.com/api.php?action=query&prop=extracts|info&inprop=url&explaintext=1&exintro=1&titles={encoded_title}&format=json"

        faction = "Guerreros Heroicos"
        theme_key = "castle_grayskull"
        lore_text = f"Valiente guerrero de Eternia al servicio de la justicia cósmica."
        source_url = f"https://he-man.fandom.com/wiki/{encoded_title}"

        try:
            import requests
            res = requests.get(api_url, timeout=5, headers={"User-Agent": "OraculoNuevaEternia/3.0"})
            if res.status_code == 200:
                data = res.json()
                pages = data.get("query", {}).get("pages", {})
                for page_id, page_info in pages.items():
                    if page_id != "-1":
                        extract = page_info.get("extract", "").strip()
                        if extract:
                            # Limpiar referencias y acortar a máx 180 caracteres limpios
                            first_sentence = extract.split("\n")[0]
                            first_sentence = re.sub(r'\s+', ' ', first_sentence).strip()
                            if len(first_sentence) > 175:
                                first_sentence = first_sentence[:172] + "..."
                            lore_text = first_sentence
                            source_url = page_info.get("fullurl", source_url)

                            # Detección determinista de facción por palabras clave
                            ext_lower = extract.lower()
                            for k, (fac, thm) in cls.FACTION_MAPPING.items():
                                if k in ext_lower:
                                    faction = fac
                                    theme_key = thm
                                    break
        except Exception as e:
            logger.warning(f"No se pudo consultar Wiki Grayskull para {character_name}: {e}")

        # Comprobación de regla fija para He-Man
        if "he-man" in character_name.lower() and "anti" not in character_name.lower():
            lore_text = "¡Por el poder de Grayskull, yo tengo el poder! El hombre más poderoso del universo y defensor eterno de los secretos sagrados del castillo."
            faction = "Guerreros Heroicos"
            theme_key = "castle_grayskull"

        return {
            "canonical_name": clean_title.title(),
            "faction": faction,
            "theme_key": theme_key,
            "type_line": f"Criatura Legendaria — {faction}",
            "special_move": f"Furia de {clean_title.title()}",
            "quote": None,
            "lore": lore_text,
            "fuerza": 88,
            "magia": 80,
            "defensa": 88,
            "agilidad": 85,
            "source_url": source_url
        }

    @classmethod
    def seed_initial_catalog(cls, db: Session) -> Dict[str, int]:
        """
        Siembra la enciclopedia canónica en BD y vincula el 100% de los 507 productos existentes.
        """
        seeded_count = 0
        linked_products = 0

        # 1. Sembrar personajes canónicos de MOTU_LORE_ENCYCLOPEDIA
        for key, data in MOTU_LORE_ENCYCLOPEDIA.items():
            slug = key.replace(' ', '_').replace('-', '_')
            existing = db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == slug).first()
            if not existing:
                stats = data.get("stats", {})
                new_char = CharacterLoreModel(
                    slug=slug,
                    canonical_name=data.get("canonical_name", key.title()),
                    faction=data.get("faction", "Guerreros Heroicos"),
                    theme_key=data.get("frame_theme", "castle_grayskull"),
                    type_line=data.get("type_line", "Criatura Legendaria — Guerrero Heroico"),
                    special_move=data.get("special_move", "Furia del Relámpago de Grayskull"),
                    quote=data.get("lore", "")[:60] if data.get("lore") else None,
                    lore=data.get("lore", "Noble defensor de la corte real de Eternia."),
                    fuerza=stats.get("fuerza", 88),
                    magia=stats.get("magia", 78),
                    defensa=stats.get("defensa", 90),
                    agilidad=stats.get("agilidad", 85),
                    is_verified=True,
                    source_url="Canon MOTU Local"
                )
                db.add(new_char)
                seeded_count += 1

        db.commit()

        # 2. Asignar character_slug a todos los productos del catálogo
        products = db.query(ProductModel).all()
        for p in products:
            slug = cls.resolve_character_slug(p.name)
            p.character_slug = slug
            linked_products += 1

        db.commit()
        logger.info(f"✅ [LORE ENGINE SEED] {seeded_count} personajes sembrados, {linked_products} productos vinculados.")
        return {"seeded_characters": seeded_count, "linked_products": linked_products}

    @classmethod
    def list_characters(
        cls,
        db: Session,
        search: Optional[str] = None,
        faction: Optional[str] = None,
        pending_only: bool = False,
        skip: int = 0,
        limit: int = 150
    ) -> Tuple[List[CharacterLoreModel], int]:
        """Lista perfiles con filtrado y paginación."""
        query = db.query(CharacterLoreModel)

        if pending_only:
            query = query.filter(CharacterLoreModel.is_verified == False)
        if faction and faction != "ALL":
            query = query.filter(CharacterLoreModel.faction == faction)
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    CharacterLoreModel.canonical_name.ilike(search_term),
                    CharacterLoreModel.slug.ilike(search_term),
                    CharacterLoreModel.lore.ilike(search_term),
                    CharacterLoreModel.special_move.ilike(search_term)
                )
            )

        total = query.count()
        results = query.order_by(CharacterLoreModel.is_verified.asc(), CharacterLoreModel.canonical_name.asc()).offset(skip).limit(limit).all()
        return results, total

    @classmethod
    def update_character(cls, db: Session, slug: str, data: Dict[str, Any]) -> Optional[CharacterLoreModel]:
        """Actualiza el lore y lo marca como verificado."""
        char = db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == slug).first()
        if not char:
            return None

        for field in ["canonical_name", "faction", "theme_key", "type_line", "special_move", "quote", "lore", "fuerza", "magia", "defensa", "agilidad"]:
            if field in data:
                setattr(char, field, data[field])

        char.is_verified = True # Validación humana confirmada
        char.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(char)
        return char
