import logging
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.domain.models import CharacterLoreModel, ProductModel
from src.domain.motu_canon_database import MOTU_LORE_ENCYCLOPEDIA, CURATED_SOURCE
from src.application.services.lore_dual_sync import LoreDualSync

logger = logging.getLogger("oraculo.lore_harvester")


class VerifiedLoreConflict(Exception):
    """Se intentó re-cosechar desde la wiki un personaje ya verificado sin `force=True`."""

    def __init__(self, slug: str):
        super().__init__(f"El personaje '{slug}' ya está verificado; usa force=True para sobrescribirlo.")
        self.slug = slug

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
    def get_or_create_character_lore(cls, db: Session, character_name: str, force: bool = False) -> CharacterLoreModel:
        """
        Busca el lore de un personaje en BD.
        Si ya existe y force=False, lo devuelve inmediatamente (0 peticiones a internet).
        Si no existe, consulta la enciclopedia canónica o la Wiki Grayskull API.
        Con force=True re-cosecha desde la wiki (queda is_verified=False para revisión humana).
        """
        slug = cls.resolve_character_slug(character_name)
        existing = db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == slug).first()
        if existing and not force:
            return existing

        # Comprobar si existe en la enciclopedia canónica local
        enc_key = slug.replace('_', ' ')
        for k, data in ([] if existing else MOTU_LORE_ENCYCLOPEDIA.items()):
            if k == enc_key or k in enc_key or enc_key in k:
                stats = data.get("stats", {})
                new_lore = CharacterLoreModel(
                    slug=slug,
                    canonical_name=data.get("canonical_name", character_name.title()),
                    faction=data.get("faction", "Guerreros Heroicos"),
                    theme_key=data.get("frame_theme", "castle_grayskull"),
                    type_line=data.get("type_line", "Criatura Legendaria — Guerrero Heroico"),
                    special_move=data.get("special_move", "Furia del Relámpago de Grayskull"),
                    quote=data.get("quote"),
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
                LoreDualSync.replicate_characters(db, [slug])
                logger.info(f"✨ [LORE SEED] Creado lore canónico local para {slug}")
                return new_lore

        # Cosecha externa (Coste 0): se libera la conexión SQL antes de cualquier I/O de red
        # para no retener sesiones del pooler transaccional durante peticiones HTTP lentas.
        db.rollback()
        harvested = cls.harvest_from_wiki_grayskull(character_name)
        existing = db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == slug).first()
        if existing:
            for field in cls._HARVEST_FIELDS:
                if harvested.get(field) is not None:
                    setattr(existing, field, harvested[field])
            existing.is_verified = False
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            LoreDualSync.replicate_characters(db, [slug])
            return existing

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
        LoreDualSync.replicate_characters(db, [slug])
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
                        source_url = f"https://he-man.fandom.com/wiki/{urllib.parse.quote(best_t.replace(' ', '_'), safe='')}"
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

    # Campos de character_lore que puede sobrescribir una cosecha de wiki.
    _HARVEST_FIELDS = (
        "canonical_name", "subtitle", "faction", "theme_key", "type_line",
        "special_move", "quote", "flavor_quote_author", "lore",
        "text_color", "card_version", "mana_cost", "fuerza", "magia", "defensa", "agilidad", "source_url",
    )

    @classmethod
    def seed_initial_catalog(cls, db: Session) -> Dict[str, Any]:
        """
        Siembra el canon en BD (delegando en el sembrador unificado `ProductLoreSeedService`)
        y vincula productos sin character_slug.
        """
        from src.application.services.product_lore_seed import ProductLoreSeedService

        char_res = ProductLoreSeedService.seed_canonical_characters(db=db, force=False)
        seeded_count = char_res["created"] + char_res["updated"]
        linked_products = 0
        linked_ids: List[int] = []

        # Asignar character_slug sólo a los productos que aún no tengan vinculado
        products = (
            db.query(ProductModel)
            .filter(or_(ProductModel.character_slug.is_(None), ProductModel.character_slug == ""))
            .all()
        )
        for p in products:
            slug = cls.resolve_character_slug(p.name)
            p.character_slug = slug
            linked_ids.append(p.id)
            linked_products += 1

        if linked_products > 0:
            db.commit()
        logger.info(f"✅ [LORE ENGINE SEED] {seeded_count} personajes sembrados, {linked_products} productos vinculados.")
        return {
            "seeded_characters": seeded_count,
            "linked_products": linked_products,
            "linked_ids": linked_ids,
            "touched_slugs": char_res["touched_slugs"],
        }

    @classmethod
    def seed_incremental_dual(cls, db: Session) -> Dict[str, Any]:
        """
        Sembrado incremental idempotente para arranque y altas de catálogo (Nexus):
        canon arquetípico + slugs de productos + filas faltantes de `product_lore`,
        con replica unidireccional SessionCloud -> SQLite local solo si hubo cambios.
        """
        from src.application.services.product_lore_seed import ProductLoreSeedService

        res = cls.seed_initial_catalog(db)
        prods = ProductLoreSeedService.seed_origins_products(db, force=False)
        if res["seeded_characters"] or res["linked_products"] or prods["touched_ids"]:
            LoreDualSync.replicate_characters(db, res["touched_slugs"])
            LoreDualSync.replicate_product_lore(db, prods["touched_ids"])
            LoreDualSync.replicate_character_slugs(db, res["linked_ids"])
        return {
            **res,
            "product_lore_created": prods["created"],
            "product_lore_updated": prods["updated"],
        }

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
        results = query.order_by(CharacterLoreModel.is_verified.desc(), CharacterLoreModel.canonical_name.asc()).offset(skip).limit(limit).all()
        return results, total

    @classmethod
    def update_character(cls, db: Session, slug: str, data: Dict[str, Any]) -> Optional[CharacterLoreModel]:
        """Actualiza el lore, lo marca como verificado y como curado por un administrador (Master)."""
        char = db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == slug).first()
        if not char:
            return None

        for field in [
            "canonical_name", "subtitle", "faction", "theme_key", "type_line",
            "special_move", "quote", "flavor_quote_author", "lore",
            "text_color", "card_version", "mana_cost", "fuerza", "magia", "defensa", "agilidad"
        ]:
            if field in data:
                setattr(char, field, data[field])

        char.is_verified = True  # Validación humana confirmada
        char.source_url = CURATED_SOURCE  # Procedencia: curación de administrador (inmutable salvo force)
        char.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(char)
        LoreDualSync.replicate_characters(db, [slug])
        return char

    @classmethod
    def harvest_for_product(cls, db: Session, product_id: int, force: bool = False) -> Optional[CharacterLoreModel]:
        """
        Cosecha o actualiza el lore para un producto específico desde Wiki Fandom.

        - Si el personaje ya está verificado y `force=False`, lanza `VerifiedLoreConflict`
          sin realizar ninguna petición de red.
        - Todo texto extraído de la wiki queda `is_verified=False` (pendiente de revisión humana).
        - La petición HTTP se ejecuta fuera de cualquier transacción SQL abierta.
        """
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            return None

        product_name = product.name
        slug = cls.resolve_character_slug(product_name)
        existing = db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == slug).first()
        if existing and existing.is_verified and not force:
            raise VerifiedLoreConflict(slug)

        product.character_slug = slug
        db.commit()  # Persiste el enlace y libera la conexión antes de la red

        harvested = cls.harvest_from_wiki_grayskull(product_name)
        existing = db.query(CharacterLoreModel).filter(CharacterLoreModel.slug == slug).first()

        if existing:
            for field in cls._HARVEST_FIELDS:
                if field in harvested and harvested[field] is not None:
                    setattr(existing, field, harvested[field])
            existing.is_verified = False
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            result = existing
        else:
            result = CharacterLoreModel(
                slug=slug,
                canonical_name=harvested.get("canonical_name", product_name.title()),
                subtitle=harvested.get("subtitle", "Campeón de Eternia"),
                faction=harvested.get("faction", "Guerreros Heroicos"),
                theme_key=harvested.get("theme_key", "castle_grayskull"),
                type_line=harvested.get("type_line", "Criatura Legendaria — Guerrero Heroico"),
                special_move=harvested.get("special_move", f"Poder de {product_name.title()}"),
                quote=harvested.get("quote"),
                flavor_quote_author=harvested.get("flavor_quote_author", product_name.title()),
                lore=harvested.get("lore", "Guerrero descubierto en los confines del multiverso de Eternia."),
                text_color=harvested.get("text_color", "#FFFFFF"),
                card_version=harvested.get("card_version", "showcase"),
                mana_cost=harvested.get("mana_cost", "{2}{W}{W}"),
                fuerza=harvested.get("fuerza", 85),
                magia=harvested.get("magia", 75),
                defensa=harvested.get("defensa", 85),
                agilidad=harvested.get("agilidad", 85),
                is_verified=False,
                source_url=harvested.get("source_url")
            )
            db.add(result)
            db.commit()
            db.refresh(result)

        LoreDualSync.replicate_characters(db, [slug])
        LoreDualSync.replicate_character_slugs(db, [product_id])
        return result
