import re
import unicodedata
from typing import Set, Tuple, Optional
from loguru import logger
from rapidfuzz import fuzz
from src.core.weight_engine import weights_manager

class PythonBrainEngine:
    """
    Motor de respaldo en Python optimizado.
    Utiliza WeightEngine para asignar pesos dinámicos basados en la rareza (IDF).
    """
    
    def __init__(self):
        # Stopwords estándar para limpieza
        self.stop_words = {
            "mattel", "figure", "figura", "action", "toy", "juguete", "cm", "inch",
            "wave", "deluxe", "collection", "collector", "edicion", "edition",
            "new", "nuevo", "caja", "box", "original", "authentic",
            "super7", "reaction", "pop", "funko", "vinyl", "of", "the", "del", "de", "y", "and",
            "comprar", "venta", "oferta", "precio", "barato", "envio", "gratis",
            "frikiverso", "articulada", "unidades", "unidad", "stock", "disponible", "entrega", "articulo"
        }
        
    def normalize(self, text: str) -> Set[str]:
        if not text: return set()
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        text = text.lower()
        text = re.sub(r'[^a-z0-9]', ' ', text)
        tokens = set(text.split())
        
        # Mapeo de Sinónimos common
        synonyms = {"tmnt": "turtles", "motu": "masters", "universe": "masters", "origenes": "origins"}
        normalized = set()
        for t in tokens:
            normalized.add(synonyms.get(t, t))
            
        # Filtrar significativos (Stopwords out)
        # Nota: Ya no dependemos de series_tokens para el filtro, el peso se encargará
        significant = normalized - self.stop_words
        return {t for t in significant if len(t) > 1 or t.isdigit()}

    def calculate_match(self, name1: str, name2: str, ean1: Optional[str] = None, ean2: Optional[str] = None) -> Tuple[bool, float, str]:
        # R01: Prioridad absoluta EAN-13
        if ean1 and ean2:
            clean_ean1 = re.sub(r'[^0-9]', '', str(ean1))
            clean_ean2 = re.sub(r'[^0-9]', '', str(ean2))
            if clean_ean1 == clean_ean2 and len(clean_ean1) >= 8:
                return True, 1.0, "EAN Match"

        tokens1 = self.normalize(name1) # DB Tokens
        tokens2 = self.normalize(name2) # Scraped Tokens
        
        if not tokens1 or not tokens2: return False, 0.0, "Empty tokens"

        # --- DINAMIC WEIGHTING (IDF) ---
        # Obtenemos pesos de WeightEngine (1.0 = Común, 10.0 = Raro)
        all_unique = tokens1 | tokens2
        weights = {t: weights_manager.get_weight(t) for t in all_unique}

        # --- RAPIDFUZZ CROSS-TOKEN MATCHING ---
        total_w_common = 0
        matched_tokens_db = set()
        
        for t1 in tokens1:
            best_score = 0
            for t2 in tokens2:
                # Usamos fuzz.ratio para tolerancia a erratas (ej: Univers -> Universe)
                s = fuzz.ratio(t1, t2)
                if s > best_score:
                    best_score = s
            
            if best_score >= 85: # Umbral de tolerancia a erratas
                total_w_common += weights.get(t1, 10.0)
                matched_tokens_db.add(t1)

        w_db_total = sum(weights.get(t, 10.0) for t in tokens1)
        weighted_score = total_w_common / w_db_total if w_db_total > 0 else 0.0
        
        # --- LEYES DINÁMICAS (Algorithmic Guards) ---
        
        # Ley 1: Conflicto de Identidad (Rareza Alta)
        # Si un token en la DB es una "Identidad" (peso > 5 según WeightEngine), DEBE coincidir.
        db_identities = {t for t in tokens1 if weights_manager.is_identity(t)}
        
        if db_identities:
            missing_identities = db_identities - matched_tokens_db
            if missing_identities:
                return False, 0.0, f"Identity Conflict (Rare tokens missing): {missing_identities}"

        # Ley 2: Conflicto de Series (Tokens Comunes)
        # Si tokens muy comunes (peso < 3.0, como 'origins', 'masters') NO coinciden, penalizar o fallar.
        db_series = {t for t in tokens1 if weights_manager.get_weight(t) < 3.0}
        scr_series = {t for t in tokens2 if weights_manager.get_weight(t) < 3.0}
        
        if db_series and scr_series:
            # Si ambos declaran serie, debe haber solapamiento
            common_series = db_series.intersection(scr_series)
            if not common_series:
                return False, 0.0, f"Series Dissonance: DB={db_series} vs Scraped={scr_series}"

        # Umbral Dinámico (0.7 para asegurar precisión)
        # Con la nueva fórmula (basada en DB), 0.7 es un umbral sólido.
        is_match = weighted_score >= 0.7
        reason = "Dynamic Weight Match" if is_match else f"Insufficient DB Coverage: {weighted_score:.2f}"
        
        return is_match, weighted_score, reason

# Singleton instance
engine = PythonBrainEngine()
