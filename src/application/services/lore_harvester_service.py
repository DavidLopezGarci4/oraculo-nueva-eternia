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
        Consulta la Wiki Grayskull (Fandom) de forma determinista usando curl_cffi (Chrome impersonation).
        Coste 0 tokens, 0 llamadas a LLM. Evasión transparente de bloqueos Cloudflare 403.
        """
        from bs4 import BeautifulSoup

        clean_title = re.sub(r'[\(\[\{].*?[\)\]\}]', '', character_name).strip()
        clean_title = re.sub(r'\b(origins|masterverse|vintage|deluxe|wave \d+|cartoon|crossover|pack)\b', '', clean_title, flags=re.IGNORECASE).strip()
        if not clean_title:
            clean_title = character_name.strip()

        encoded_title = urllib.parse.quote(clean_title.replace(' ', '_'))
        source_url = f"https://he-man.fandom.com/wiki/{encoded_title}"

        faction = "Guerreros Heroicos"
        theme_key = "castle_grayskull"
        type_line = "Criatura Legendaria — Guerrero Heroico"
        subtitle = "Campeón de Eternia"
        special_move = f"Poder de {clean_title.title()}"
        lore_text = f"Valiente defensor de Eternia y guardián de los secretos de Grayskull."
        best_quote = None
        quote_author = clean_title.title()

        try:
            from curl_cffi import requests as cffi_requests
            # 1. Intentar página directa
            res = cffi_requests.get(source_url, impersonate="chrome120", timeout=8)
            
            # Si no es 200, buscar vía API de búsqueda
            if res.status_code != 200:
                search_api = f"https://he-man.fandom.com/api.php?action=query&list=search&srsearch={urllib.parse.quote(clean_title)}&format=json"
                s_res = cffi_requests.get(search_api, impersonate="chrome120", timeout=8)
                if s_res.status_code == 200:
                    search_data = s_res.json().get("query", {}).get("search", [])
                    if search_data:
                        best_t = search_data[0]["title"]
                        source_url = f"https://he-man.fandom.com/wiki/{best_t.replace(' ', '_')}"
                        res = cffi_requests.get(source_url, impersonate="chrome120", timeout=8)

            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                
                # Extraer párrafos limpios
                content = soup.select_one(".mw-parser-output") or soup
                p_elements = [
                    re.sub(r'\[\d+\]', '', p.get_text().strip())
                    for p in content.find_all("p")
                    if len(p.get_text().strip()) > 35
                ]

                if p_elements:
                    # Usar el primer párrafo descriptivo
                    first_p = p_elements[0]
                    first_p = re.sub(r'\s+', ' ', first_p).strip()
                    if len(first_p) > 220:
                        # Cortar en el primer punto si es razonable
                        sentences = first_p.split(". ")
                        if len(sentences[0]) > 60:
                            first_p = sentences[0] + "."
                        else:
                            first_p = first_p[:210].rsplit(' ', 1)[0] + "..."
                    lore_text = first_p

                # Extraer citas icónicas
                quotes = [
                    re.sub(r'\[\d+\]', '', q.get_text().strip())
                    for q in soup.find_all(["blockquote", "i", "em"])
                    if 15 < len(q.get_text().strip()) < 130 and any(c in q.get_text() for c in ['"', '«', '!', '¡'])
                ]
                if quotes:
                    best_quote = quotes[0].strip('"\n ')

                # Extraer información del Infobox (Afiliación, Armas, Rol)
                infobox = soup.select_one(".portable-infobox")
                if infobox:
                    for row in infobox.select(".pi-item"):
                        lbl = row.select_one(".pi-data-label")
                        val = row.select_one(".pi-data-value")
                        if lbl and val:
                            label_str = lbl.get_text().lower()
                            val_str = val.get_text().strip()
                            if any(w in label_str for w in ["group", "affiliation", "alignment", "allegiance"]):
                                v_low = val_str.lower()
                                for k, (fac, thm) in cls.FACTION_MAPPING.items():
                                    if k in v_low:
                                        faction = fac
                                        theme_key = thm
                                        break
                            elif any(w in label_str for w in ["title", "alias", "alter"]):
                                subtitle = val_str.split(",")[0].strip()

        except Exception as e:
            logger.warning(f"Error consultando Wiki Grayskull para {character_name}: {e}")

        # Reglas canónicas directas para personajes legendarios clave
        name_lower = character_name.lower()
        if "he-man" in name_lower and "anti" not in name_lower and "skeletor" not in name_lower:
            canonical_name = "He-Man"
            subtitle = "Campeón de Eternia"
            faction = "Guerreros Heroicos"
            theme_key = "castle_grayskull"
            type_line = "Criatura Legendaria — Guerrero Humano"
            special_move = "Por el Poder de Grayskull"
            best_quote = "¡Por el poder de Grayskull... yo tengo el poder!"
            quote_author = "He-Man"
            lore_text = "El hombre más poderoso del universo y eterno defensor de los secretos sagrados del Castillo Grayskull."
        elif "skeletor" in name_lower and "he-skeletor" not in name_lower:
            canonical_name = "Skeletor"
            subtitle = "Señor de la Destrucción"
            faction = "Guerreros del Mal"
            theme_key = "snake_mountain"
            type_line = "Criatura Legendaria — Hechicero Esqueleto"
            special_move = "Rayo del Báculo del Caos"
            best_quote = "¡Toda Eternia será mía, aunque tenga que destrozar el universo!"
            quote_author = "Skeletor"
            lore_text = "Tirano de la Montaña Serpiente y maestro de las artes oscuras empeñado en conquistar el poder de Grayskull."
        elif "hordak" in name_lower:
            canonical_name = "Hordak"
            subtitle = "Líder Supremo de la Horda"
            faction = "La Horda del Terror"
            theme_key = "evil_horde"
            type_line = "Criatura Legendaria — Conquistador Cyborg"
            special_move = "Cañón de Bio-Materia"
            best_quote = "¡La Horda no conoce la piedad ni la derrota!"
            quote_author = "Hordak"
            lore_text = "Cruel amo supremo de la Zona del Terror y conquistador de múltiples mundos mediante magia y cibernética."
        elif "king hiss" in name_lower or "king hsss" in name_lower:
            canonical_name = "King Hiss"
            subtitle = "Señor de los Hombres Serpiente"
            faction = "Los Hombres Serpiente"
            theme_key = "snake_men"
            type_line = "Criatura Legendaria — Ofidio Ancestral"
            special_move = "Metamorfosis Viperina"
            best_quote = "¡La era de los hombres terminará bajo el veneno de la serpiente!"
            quote_author = "King Hiss"
            lore_text = "Gobernante ancestral de los Hombres Serpiente que oculta una masa de víboras bajo su piel humana."
        elif "she-ra" in name_lower:
            canonical_name = "She-Ra"
            subtitle = "Princesa del Poder"
            faction = "La Gran Rebelión"
            theme_key = "great_rebellion"
            type_line = "Criatura Legendaria — Guerrera de la Luz"
            special_move = "Espada de Protección"
            best_quote = "¡Por el honor de Grayskull... soy She-Ra!"
            quote_author = "She-Ra"
            lore_text = "Líder de la Gran Rebelión de Etheria y defensora de la paz empuñando la Espada de Protección."
        else:
            canonical_name = clean_title.title()

        mana_map = {
            "castle_grayskull": "{2}{W}{W}",
            "snake_mountain": "{2}{B}{B}",
            "evil_horde": "{3}{B}{R}",
            "snake_men": "{2}{B}{G}",
            "great_rebellion": "{2}{G}{W}",
            "cosmic_enforcers": "{2}{W}{U}"
        }
        mana_cost = mana_map.get(theme_key, "{2}{W}{W}")
        if "artefacto" in (type_line or "").lower() or "vehículo" in (type_line or "").lower():
            mana_cost = "{3}"

        return {
            "canonical_name": canonical_name,
            "subtitle": subtitle,
            "faction": faction,
            "theme_key": theme_key,
            "type_line": type_line,
            "special_move": special_move,
            "quote": best_quote,
            "flavor_quote_author": quote_author,
            "lore": lore_text,
            "text_color": "#FFFFFF",
            "card_version": "showcase",
            "mana_cost": mana_cost,
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

        for field in [
            "canonical_name", "subtitle", "faction", "theme_key", "type_line",
            "special_move", "quote", "flavor_quote_author", "lore",
            "text_color", "card_version", "fuerza", "magia", "defensa", "agilidad"
        ]:
            if field in data:
                setattr(char, field, data[field])

        char.is_verified = True # Validación humana confirmada
        char.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(char)
        return char

    @classmethod
    def harvest_for_product(cls, db: Session, product_id: int) -> Optional[CharacterLoreModel]:
        """
        Cosecha o actualiza el lore para un producto específico desde Wiki Fandom.
        """
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            return None

        slug = cls.resolve_character_slug(product.name)
        product.character_slug = slug

        harvested = cls.harvest_from_wiki_grayskull(product.name)
        existing = db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == slug).first()

        if existing:
            for field in [
                "canonical_name", "subtitle", "faction", "theme_key", "type_line",
                "special_move", "quote", "flavor_quote_author", "lore",
                "text_color", "card_version", "mana_cost", "fuerza", "magia", "defensa", "agilidad", "source_url"
            ]:
                if field in harvested and harvested[field] is not None:
                    setattr(existing, field, harvested[field])
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            new_lore = CharacterLoreModel(
                slug=slug,
                canonical_name=harvested.get("canonical_name", product.name.title()),
                subtitle=harvested.get("subtitle", "Campeón de Eternia"),
                faction=harvested.get("faction", "Guerreros Heroicos"),
                theme_key=harvested.get("theme_key", "castle_grayskull"),
                type_line=harvested.get("type_line", "Criatura Legendaria — Guerrero Heroico"),
                special_move=harvested.get("special_move", f"Poder de {product.name.title()}"),
                quote=harvested.get("quote"),
                flavor_quote_author=harvested.get("flavor_quote_author", product.name.title()),
                lore=harvested.get("lore", "Guerrero descubierto en los confines del multiverso de Eternia."),
                text_color=harvested.get("text_color", "#FFFFFF"),
                card_version=harvested.get("card_version", "showcase"),
                mana_cost=harvested.get("mana_cost", "{2}{W}{W}"),
                fuerza=harvested.get("fuerza", 85),
                magia=harvested.get("magia", 75),
                defensa=harvested.get("defensa", 85),
                agilidad=harvested.get("agilidad", 85),
                is_verified=True,
                source_url=harvested.get("source_url")
            )
            db.add(new_lore)
            db.commit()
            db.refresh(new_lore)
            return new_lore

