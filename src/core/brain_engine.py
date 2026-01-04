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
            "turtles", "grayskull", "stranger", "things", "cartoon", "collection", "sun", "man",
            "engineering", "art", "classics", "revelation", "revolution", "mondo", "super7", "tmnt", "motu",
            "masters", "universe"
        }
        self.identity_tokens = {
            "skeletor", "teela", "heman", "manatarms", "beastman", "trapjaw", "evillyn", "fisto", "ramman",
            "orko", "stratos", "merman", "jitsu", "triklops", "hordak", "she-ra", "man-at-arms", "he-man"
        }
    def normalize(self, text: str) -> Set[str]:
        if not text: return set()
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        text = text.lower()
        text = re.sub(r'[^a-z0-9]', ' ', text)
        tokens = set(text.split())
        
        # Mapeo de Sinónimos
        synonyms = {"tmnt": "turtles", "motu": "masters", "universe": "masters"}
        normalized = set()
        for t in tokens:
            normalized.add(synonyms.get(t, t))
        return normalized
    

    def jaccard_similarity(self, s1: str, s2: str) -> float:
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

        # Algoritmo de Pesos Dinámicos
        tokens1 = self.normalize(name1)
        tokens2 = self.normalize(name2)
        
        if not tokens1 or not tokens2: return False, 0.0

        common = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        # Pesos: Serie (x10), Identidad (x5), Otros (x1)
        weights = {}
        for t in union:
            if t in self.series_tokens: weights[t] = 10.0
            elif t in self.identity_tokens: weights[t] = 5.0
            else: weights[t] = 1.0
            
        w_intersection = sum(weights[t] for t in common)
        w_union = sum(weights[t] for t in union)
        score = w_intersection / w_union if w_union > 0 else 0.0
        
        # Ley de Hierro 1: Conflicto de Identidad
        id1 = tokens1.intersection(self.identity_tokens)
        id2 = tokens2.intersection(self.identity_tokens)
        if id1 and id2 and not id1.intersection(id2):
            return False, 0.0
            
        # Ley de Hierro 2: Si el producto (1) declara una serie o identidad, la web (2) DEBE tenerla
        if id1 and not id1.intersection(id2): return False, 0.0
        
        # Ley de Hierro 2: Si el producto (1) declara una serie o identidad, la web (2) DEBE tenerla
        if id1 and not id1.intersection(id2): return False, 0.0
        
        series1 = tokens1.intersection(self.series_tokens)
        series2 = tokens2.intersection(self.series_tokens)
        
        if series1 and not series1.intersection(series2):
            return False, 0.0

        # R02: Umbral Jaccard Pesado (0.65)
        return score >= 0.65, score

# Singleton instance
engine = PythonBrainEngine()
