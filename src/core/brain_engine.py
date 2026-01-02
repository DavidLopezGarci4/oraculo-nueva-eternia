import re
import unicodedata
from typing import Set, Tuple, Optional
from loguru import logger

class PythonBrainEngine:
    """
    Motor de respaldo en Python optimizado.
    Sigue las mismas 'Leyes de Hierro' que el Kernel de Rust.
    """
    
    def __init__(self):
        # Palabras clave de filtrado (Series de MOTU)
        self.series_tokens = {
            "origins", "masterverse", "cgi", "netflix", "filmation", "200x", "vintage", "commemorative",
            "turtles", "grayskull", "stranger", "things", "cartoon", "collection", "sun", "man"
        }

    def normalize(self, text: str) -> Set[str]:
        if not text: return set()
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        text = text.lower()
        text = re.sub(r'[^a-z0-9]', ' ', text)
        return set(text.split())

    def jaccard_similarity(self, s1: str, s2: str) -> float {
        set1 = self.normalize(s1)
        set2 = self.normalize(s2)
        
        if not set1 and not set2: return 1.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0

    def calculate_match(self, name1: str, name2: str, ean1: Optional[str] = None, ean2: Optional[str] = None) -> Tuple[bool, float]:
        # Ley de Hierro R01: Prioridad absoluta EAN-13
        if ean1 and ean2:
            clean_ean1 = re.sub(r'[^0-9]', '', str(ean1))
            clean_ean2 = re.sub(r'[^0-9]', '', str(ean2))
            if clean_ean1 == clean_ean2 and len(clean_ean1) >= 8:
                return True, 1.0

        # Algoritmo Jaccard optimizado
        score = self.jaccard_similarity(name1, name2)
        
        # Filtro de Conflicto de Series (Hard Filter)
        tokens1 = self.normalize(name1)
        tokens2 = self.normalize(name2)
        series1 = tokens1.intersection(self.series_tokens)
        series2 = tokens2.intersection(self.series_tokens)
        
        if series1 and series2 and not series1.intersection(series2):
            logger.debug(f"Conflicto de Serie detectado: {series1} vs {series2}")
            return False, 0.0

        # R02: Umbral Jaccard (0.70)
        return score >= 0.7, score

# Singleton instance
engine = PythonBrainEngine()
