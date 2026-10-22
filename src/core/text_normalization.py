"""
Normalización de texto compartida por el motor de matching (brain_engine),
el motor de pesos IDF (weight_engine) y el índice de candidatos del Purgatorio.

Usar SIEMPRE estas funciones para que catálogo y anuncios se tokenicen igual.
"""
import re
import unicodedata
from typing import Set, Tuple

# Nombres compuestos que deben tratarse como un único token ("he-man", "he man", "heman")
COMPOUND_NAMES = [
    (re.compile(r"\bhe[\s\-_.]*man\b"), "heman"),
    (re.compile(r"\bshe[\s\-_.]*ra\b"), "shera"),
    (re.compile(r"\bbeast[\s\-_.]*man\b"), "beastman"),
    (re.compile(r"\bman[\s\-_.]*at[\s\-_.]*arms\b"), "manatarms"),
    (re.compile(r"\bmer[\s\-_.]*man\b"), "merman"),
    (re.compile(r"\bram[\s\-_.]*man\b"), "ramman"),
    (re.compile(r"\bmoss[\s\-_.]*man\b"), "mossman"),
    (re.compile(r"\bsun[\s\-_.]*man\b"), "sunman"),
    (re.compile(r"\bman[\s\-_.]*e[\s\-_.]*faces\b"), "manefaces"),
    (re.compile(r"\btri[\s\-_.]*klops\b"), "triklops"),
    (re.compile(r"\bevil[\s\-_.]*lyn\b"), "evillyn"),
    (re.compile(r"\bsy[\s\-_.]*klone\b"), "syklone"),
    (re.compile(r"\bbuzz[\s\-_.]*off\b"), "buzzoff"),
    (re.compile(r"\bkobra[\s\-_.]*khan\b"), "kobrakhan"),
    (re.compile(r"\btrap[\s\-_.]*jaw\b"), "trapjaw"),
    (re.compile(r"\bscare[\s\-_.]*glow\b"), "scareglow"),
]

# Sinónimos (multilingües) -> forma canónica del catálogo (inglés)
SYNONYMS = {
    "tmnt": "turtles",
    "tortugas": "turtles",
    "tartarughe": "turtles",
    "motu": "masters",
    "master": "masters",
    "universe": "masters",
    "universo": "masters",
    "univers": "masters",
    "maitres": "masters",
    "maestros": "masters",
    "origenes": "origins",
    "armour": "armor",
    "armadura": "armor",
    "armatura": "armor",
    "castillo": "castle",
    "castello": "castle",
    "chateau": "castle",
    "montana": "mountain",
    "serpiente": "snake",
    "serpent": "snake",
    "garra": "claw",
    "garras": "claw",
    "claws": "claw",
    "pelicula": "movie",
    "film": "movie",
    "evilyn": "evillyn",
}

STOP_WORDS = {
    # Marca / tipo de producto
    "mattel", "figure", "figures", "figura", "figuras", "figurine", "figurina", "figur", "personaggio",
    "action", "accion", "toy", "toys", "juguete", "muneco", "munecos", "jouet", "spielzeug", "giocattolo",
    "cm", "inch", "pulgadas",
    # "collector" NO es stopword: es un personaje ("The Collector")
    "wave", "deluxe", "collection", "edicion", "edition", "coleccion",
    "super7", "reaction", "pop", "funko", "vinyl",
    # Estado / venta (jerga de segunda mano)
    "new", "nuevo", "nueva", "neuf", "nuovo", "neu", "caja", "box", "original", "authentic",
    "loose", "moc", "misb", "mib", "nib", "lote", "completo", "completa", "complete", "usado", "usada",
    "segunda", "mano", "precintado", "precintada", "sealed", "perfecto", "estado", "unpunched",
    "comprar", "venta", "oferta", "precio", "barato", "envio", "gratis", "incluido", "incluida",
    "frikiverso", "articulada", "unidades", "unidad", "stock", "disponible", "entrega", "articulo",
    # Conectores ES/EN/IT/FR/DE
    "of", "the", "del", "de", "la", "el", "los", "las", "y", "and", "con", "with", "et", "und",
    "di", "der", "die", "das", "le", "les", "du", "des", "en", "para", "por", "per",
}

_PAREN_RE = re.compile(r"\(([^)]*)\)")

# Tokens de serie/marca genéricos: nunca indican una variante concreta de una figura
GENERIC_SERIES_TOKENS = frozenset({"masters", "origins"})


def _ascii_lower(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("utf-8")
    return text.lower()


def tokenize(text: str) -> Set[str]:
    """Tokens significativos normalizados (compuestos unidos, sinónimos, sin stopwords)."""
    if not text:
        return set()
    lowered = _ascii_lower(text)
    for pattern, replacement in COMPOUND_NAMES:
        lowered = pattern.sub(replacement, lowered)
    lowered = re.sub(r"[^a-z0-9]", " ", lowered)
    tokens = set()
    for raw in lowered.split():
        tok = SYNONYMS.get(raw, raw)
        if tok in STOP_WORDS:
            continue
        if len(tok) > 1 or tok.isdigit():
            tokens.add(tok)
    return tokens


def split_catalog_name(name: str) -> Tuple[Set[str], Set[str]]:
    """
    Separa un nombre de catálogo en (tokens núcleo, tokens calificadores).
    Los calificadores son los que van entre paréntesis, p.ej. "Skeletor (Vintage Sculpt)"
    -> ({"skeletor"}, {"vintage", "sculpt"}). Un calificador repetido en el núcleo cuenta como núcleo.
    """
    qualifier_text = " ".join(_PAREN_RE.findall(name or ""))
    core_text = _PAREN_RE.sub(" ", name or "")
    core = tokenize(core_text)
    qualifiers = tokenize(qualifier_text) - core
    return core, qualifiers
