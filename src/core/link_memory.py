"""
Memoria de vinculaciones manuales del Purgatorio.

Reutiliza el historial ya existente (OfferHistoryModel con LINKED_MANUAL / LINKED_MANUAL_BULK,
que guarda el título original y el producto elegido) para reforzar en futuras predicciones
el producto que el usuario eligió ante un anuncio muy parecido.

- No requiere tablas nuevas ni migraciones (coherencia SQLite / Supabase intacta).
- NUNCA vincula automáticamente: solo sube la puntuación (máx. 99) y marca la sugerencia.
"""
import json
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, FrozenSet, List, Optional

from loguru import logger

from src.core.text_normalization import tokenize

LEARNED_ACTIONS = ("LINKED_MANUAL", "LINKED_MANUAL_BULK")
MAX_HISTORY_ROWS = 5000
CACHE_TTL_SECONDS = 600
SIMILARITY_THRESHOLD = 0.8
LEARNED_BOOST = 15.0
LEARNED_SCORE_CAP = 99.0


@dataclass
class LearnedLink:
    fingerprint: FrozenSet[str]
    product_id: int
    last_linked_at: Optional[datetime]
    hits: int = 1


@dataclass
class LearnedHit:
    product_id: int
    similarity: float
    last_linked_at: Optional[datetime]
    hits: int


def jaccard(a: FrozenSet[str], b: FrozenSet[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def parse_history_rows(rows) -> List[LearnedLink]:
    """rows: iterable de (details_json, timestamp). Ignora filas corruptas o sin título."""
    merged: Dict[tuple, LearnedLink] = {}
    for details, ts in rows:
        try:
            data = json.loads(details) if isinstance(details, str) else (details or {})
            product_id = int(data.get("product_id"))
            title = (data.get("original_item") or {}).get("scraped_name")
        except Exception:
            continue
        fingerprint = frozenset(tokenize(title or ""))
        if not fingerprint:
            continue
        key = (fingerprint, product_id)
        entry = merged.get(key)
        if entry is None:
            merged[key] = LearnedLink(fingerprint, product_id, ts, 1)
        else:
            entry.hits += 1
            if ts and (entry.last_linked_at is None or ts > entry.last_linked_at):
                entry.last_linked_at = ts
    return list(merged.values())


def find_learned_hits(title: str, entries: List[LearnedLink]) -> List[LearnedHit]:
    """Mejor coincidencia por producto con similitud Jaccard >= umbral."""
    tokens = frozenset(tokenize(title or ""))
    if not tokens or not entries:
        return []
    best: Dict[int, LearnedHit] = {}
    for e in entries:
        sim = jaccard(tokens, e.fingerprint)
        if sim < SIMILARITY_THRESHOLD:
            continue
        current = best.get(e.product_id)
        if current is None or sim > current.similarity:
            best[e.product_id] = LearnedHit(e.product_id, sim, e.last_linked_at, e.hits)
        elif sim == current.similarity:
            current.hits += e.hits
    return sorted(best.values(), key=lambda h: (-h.similarity, -h.hits))


def learned_reason(hit: LearnedHit) -> str:
    when = hit.last_linked_at.strftime("%d/%m") if hit.last_linked_at else "antes"
    return f"Lo vinculaste el {when}"


def apply_learned_hits(suggestions: List[dict], hits: List[LearnedHit], products_by_id: dict, serialize) -> List[dict]:
    """
    Refuerza (+15, máx. 99, nunca baja una puntuación) los productos aprendidos y añade los que
    no estaban entre los candidatos (puntuación = similitud x 90). Marca is_learned=True.
    """
    if not hits:
        return suggestions
    result = [dict(s) for s in suggestions]
    by_id = {s["product_id"]: s for s in result}
    for hit in hits:
        reason = learned_reason(hit)
        sug = by_id.get(hit.product_id)
        if sug is not None:
            boosted = min(LEARNED_SCORE_CAP, sug["match_score"] + LEARNED_BOOST)
            sug["match_score"] = round(max(sug["match_score"], boosted), 1)
            sug["reason"] = f"{sug.get('reason', '')} · {reason}".strip(" ·")
            sug["is_learned"] = True
            continue
        product = products_by_id.get(hit.product_id)
        if product is None:
            continue
        new = serialize(product, min(LEARNED_SCORE_CAP, hit.similarity * 90.0) / 100.0, reason)
        new["is_learned"] = True
        result.append(new)
        by_id[hit.product_id] = new
    return result


class LinkMemory:
    """Caché en memoria (TTL) de las vinculaciones manuales recientes."""

    def __init__(self):
        self._entries: List[LearnedLink] = []
        self._loaded_at: float = 0.0
        self._lock = threading.Lock()

    def invalidate(self) -> None:
        with self._lock:
            self._loaded_at = 0.0

    def get_entries(self, db) -> List[LearnedLink]:
        with self._lock:
            if self._loaded_at and time.time() - self._loaded_at < CACHE_TTL_SECONDS:
                return self._entries
        try:
            from src.domain.models import OfferHistoryModel

            rows = (
                db.query(OfferHistoryModel.details, OfferHistoryModel.timestamp)
                .filter(OfferHistoryModel.action_type.in_(LEARNED_ACTIONS))
                .order_by(OfferHistoryModel.id.desc())
                .limit(MAX_HISTORY_ROWS)
                .all()
            )
            entries = parse_history_rows(rows)
        except Exception as e:
            logger.warning(f"LinkMemory: no se pudo cargar el historial de vinculaciones: {e}")
            entries = []
        with self._lock:
            self._entries = entries
            self._loaded_at = time.time()
        return entries


link_memory = LinkMemory()
