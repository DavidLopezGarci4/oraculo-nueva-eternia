"""
Predicciones acompañantes del Purgatorio.

Las figuras Origins "He-Man (Vintage Sculpt)" y "Skeletor (Vintage Sculpt)" (NO son vintage:
pertenecen a Origins, ambientadas en la línea vintage) casi nunca se mencionan en los anuncios.
Cuando la predicción es el He-Man / Skeletor básico de la línea "Origins" principal, se ofrece
también su versión Vintage Sculpt justo detrás, para que el usuario decida.
"""
from typing import Callable, Dict, List, Optional

from src.core.text_normalization import tokenize, GENERIC_SERIES_TOKENS

# Tokens del nombre básico -> nombre exacto del acompañante en el catálogo
VINTAGE_SCULPT_COMPANIONS: Dict[frozenset, str] = {
    frozenset({"heman"}): "He-Man (Vintage Sculpt)",
    frozenset({"skeletor"}): "Skeletor (Vintage Sculpt)",
}
# Solo la línea Origins principal dispara el acompañante (no Thundercats, TOG, Exclusives...)
TRIGGER_SUB_CATEGORY = "origins"
COMPANION_REASON = "Vintage Sculpt companion"


def _norm_name(name: Optional[str]) -> str:
    return (name or "").strip().lower()


def build_companion_lookup(products: list) -> Dict[str, object]:
    """Mapa nombre exacto (minúsculas) -> producto NO vintage, solo para los acompañantes conocidos."""
    wanted = {_norm_name(n) for n in VINTAGE_SCULPT_COMPANIONS.values()}
    lookup = {}
    for p in products:
        key = _norm_name(p.name)
        if key in wanted and not p.is_vintage:
            lookup.setdefault(key, p)
    return lookup


def inject_vintage_sculpt_companions(
    suggestions: List[dict],
    companion_lookup: Dict[str, object],
    scraped_name: str,
    is_identity: Callable[[str], bool],
    serialize: Callable[[object, float, str], dict],
) -> List[dict]:
    """
    Inserta (o reubica) el acompañante Vintage Sculpt justo detrás de cada He-Man / Skeletor
    básico de la línea Origins. Nunca lo coloca por delante del básico ni reordena el resto.
    No se añade si el anuncio describe otra variante (tokens de identidad ajenos al acompañante).
    """
    result = list(suggestions)
    scraped_tokens = tokenize(scraped_name or "")

    for base in list(result):
        if base.get("is_vintage") or base.get("is_companion"):
            continue
        if _norm_name(base.get("sub_category")) != TRIGGER_SUB_CATEGORY:
            continue
        companion_name = VINTAGE_SCULPT_COMPANIONS.get(frozenset(tokenize(base.get("name") or "")))
        if not companion_name:
            continue
        companion = companion_lookup.get(_norm_name(companion_name))
        if companion is None:
            continue

        allowed = tokenize(companion.name) | tokenize(companion.sub_category or "") | GENERIC_SERIES_TOKENS
        if any(is_identity(t) and t not in allowed for t in scraped_tokens):
            continue  # el anuncio describe otra variante (Battle Armor, Terror Claw, 200x...)

        companion_score = max(0.0, round(base["match_score"] - 1.0, 1))
        existing = next((s for s in result if s.get("product_id") == companion.id), None)
        if existing is not None and result.index(existing) < result.index(base):
            continue  # el anuncio ya apunta al Vintage Sculpt por encima del básico: no tocar
        if existing is not None:
            # Ya estaba en la lista (p.ej. el anuncio dice "sculpt"): se reubica tras el básico
            result.remove(existing)
            entry = dict(existing)
        else:
            entry = serialize(companion, companion_score / 100.0, COMPANION_REASON)
        # Siempre justo por debajo del básico para que nunca quede preseleccionado
        entry["match_score"] = companion_score
        entry["reason"] = COMPANION_REASON
        entry["is_companion"] = True

        result.insert(result.index(base) + 1, entry)

    return result
