import re
from typing import Set, Tuple, Optional
from loguru import logger
from rapidfuzz import fuzz
from src.core.weight_engine import weights_manager, IDENTITY_WEIGHT
from src.core.text_normalization import tokenize, split_catalog_name, STOP_WORDS, GENERIC_SERIES_TOKENS

# Los tokens entre paréntesis del catálogo ("Skeletor (Vintage Sculpt)") son calificadores:
# si faltan en el anuncio NO vetan el match, solo restan cobertura con este factor de peso.
QUALIFIER_WEIGHT_FACTOR = 0.5
# Un token del anuncio que el candidato no tiene penaliza si es un token conocido del catálogo con este peso mínimo
VARIANT_TOKEN_MIN_WEIGHT = 4.0
# La penalización por variante nunca baja la puntuación por debajo de este factor
VARIANT_PENALTY_FLOOR = 0.5
FUZZY_THRESHOLD = 85
# Tokens de serie/marca genéricos que nunca cuentan como "variante" (compartidos)
NEVER_VARIANT_TOKENS = GENERIC_SERIES_TOKENS


def _fuzzy_in(token: str, pool: Set[str]) -> bool:
    return any(fuzz.ratio(token, other) >= FUZZY_THRESHOLD for other in pool)


class PythonBrainEngine:
    """
    Motor de respaldo en Python optimizado.
    Utiliza WeightEngine para asignar pesos dinámicos basados en la rareza (IDF).
    """
    
    def __init__(self):
        # Stopwords estándar para limpieza (compartidas con text_normalization)
        self.stop_words = STOP_WORDS
        
    def normalize(self, text: str) -> Set[str]:
        return tokenize(text)

    def calculate_match(
        self,
        name1: str,
        name2: str,
        ean1: Optional[str] = None,
        ean2: Optional[str] = None,
        penalize_extra: bool = True,
        db_context: Optional[str] = None,
        soft_qualifiers: bool = True,
    ) -> Tuple[bool, float, str]:
        """
        name1: nombre del catálogo. name2: título del anuncio.
        db_context: texto de contexto del candidato (p.ej. su sub_category). Sus tokens no
            cuentan como "variante" si aparecen en el anuncio (p.ej. "Turtles of Grayskull").
        soft_qualifiers: si es False, los tokens entre paréntesis se tratan como núcleo
            (comportamiento estricto clásico, usado por SmartMatcher para autoselección).
        """
        # R01: Prioridad absoluta EAN-13
        if ean1 and ean2:
            clean_ean1 = re.sub(r'[^0-9]', '', str(ean1))
            clean_ean2 = re.sub(r'[^0-9]', '', str(ean2))
            if clean_ean1 == clean_ean2 and len(clean_ean1) >= 8:
                return True, 1.0, "EAN Match"

        if soft_qualifiers:
            core, qualifiers = split_catalog_name(name1)  # DB Tokens
            if not core:
                core, qualifiers = qualifiers, set()
        else:
            core, qualifiers = self.normalize(name1), set()
        tokens1 = core | qualifiers
        tokens2 = self.normalize(name2) # Scraped Tokens
        
        if not tokens1 or not tokens2: return False, 0.0, "Empty tokens"

        # --- DINAMIC WEIGHTING (IDF) ---
        # Instantánea única de pesos por llamada (coherente aunque otro hilo refresque el catálogo)
        snapshot_weights, name_tokens = weights_manager.snapshot()

        def w_of(t: str) -> float:
            # Desconocido = ruido (1.0) para tokens del anuncio
            return snapshot_weights.get(t, 1.0)

        def db_weight(t: str) -> float:
            w = snapshot_weights.get(t, 10.0)
            return w * QUALIFIER_WEIGHT_FACTOR if t in qualifiers else w

        def is_identity(t: str) -> bool:
            return t in snapshot_weights and snapshot_weights[t] > IDENTITY_WEIGHT

        # --- RAPIDFUZZ CROSS-TOKEN MATCHING ---
        total_w_common = 0.0
        matched_tokens_db = set()
        
        for t1 in tokens1:
            best_score = 0
            for t2 in tokens2:
                # Usamos fuzz.ratio para tolerancia a erratas (ej: Univers -> Universe)
                s = fuzz.ratio(t1, t2)
                if s > best_score:
                    best_score = s
            
            if best_score >= FUZZY_THRESHOLD: # Umbral de tolerancia a erratas
                total_w_common += db_weight(t1)
                matched_tokens_db.add(t1)

        w_db_total = sum(db_weight(t) for t in tokens1)
        weighted_score = total_w_common / w_db_total if w_db_total > 0 else 0.0
        
        # --- LEYES DINÁMICAS (Algorithmic Guards) ---
        
        # Ley 1: Conflicto de Identidad (Rareza Alta)
        # Si un token NÚCLEO de la DB es una "Identidad" (peso > 5 según WeightEngine), DEBE coincidir.
        # Los calificadores entre paréntesis no vetan (solo restan cobertura).
        db_identities = {t for t in core if is_identity(t)}
        
        if db_identities:
            missing_identities = db_identities - matched_tokens_db
            if missing_identities:
                return False, 0.0, f"Identity Conflict (Rare tokens missing): {missing_identities}"

        # Ley 2: Conflicto de Series (Tokens Comunes)
        # Si tokens muy comunes (peso < 3.0, como 'origins', 'masters') NO coinciden, penalizar o fallar.
        db_series = {t for t in tokens1 if w_of(t) < 3.0}
        scr_series = {t for t in tokens2 if w_of(t) < 3.0}
        
        if db_series and scr_series:
            # Si ambos declaran serie, debe haber solapamiento
            common_series = db_series.intersection(scr_series)
            if not common_series:
                return False, 0.0, f"Series Dissonance: DB={db_series} vs Scraped={scr_series}"

        # Ley 3: Penalización de Variante
        # Si el anuncio contiene tokens conocidos del catálogo que este candidato NO tiene
        # (p.ej. "battle armor" frente al He-Man básico, o "thundercats" frente al He-Man Origins),
        # la puntuación baja (con suelo). No cuentan: números/años, series genéricas ni el
        # contexto (subcategoría) del propio candidato, comparado con tolerancia a erratas.
        variant_note = ""
        if penalize_extra and weighted_score > 0:
            context_tokens = self.normalize(db_context) if db_context else set()
            extra_tokens = {
                t2 for t2 in tokens2
                if t2 in snapshot_weights
                and not t2.isdigit()
                and t2 not in NEVER_VARIANT_TOKENS
                and w_of(t2) >= VARIANT_TOKEN_MIN_WEIGHT
                and not _fuzzy_in(t2, tokens1)
                and not _fuzzy_in(t2, context_tokens)
            }
            if extra_tokens:
                w_extra = sum(w_of(t) for t in extra_tokens)
                factor = max(VARIANT_PENALTY_FLOOR, w_db_total / (w_db_total + w_extra))
                weighted_score *= factor
                variant_note = f" · Variant penalty {sorted(extra_tokens)}"

        # Umbral Dinámico (0.7 para asegurar precisión)
        # Con la nueva fórmula (basada en DB), 0.7 es un umbral sólido.
        is_match = weighted_score >= 0.7
        reason = "Dynamic Weight Match" if is_match else f"Insufficient DB Coverage: {weighted_score:.2f}"
        
        return is_match, weighted_score, reason + variant_note

# Singleton instance
engine = PythonBrainEngine()
