import re
import unicodedata
from typing import Set, Tuple, List
from src.core.rust_bridge import kernel
from src.core.brain_engine import engine as python_engine

class SmartMatcher:
    """
    Orquestador de Matching.
    Prioridades:
    1. Rust Kernel (Rápido, estricto)
    2. EAN/GTIN Match (Exacto, si existe)
    3. Python Brain Engine (Semántico, dinámico, con pesos IDF)
    """
    def __init__(self):
        # La limpieza y stopwords ahora se centralizan en los motores
        pass

    def match(self, product_name: str, scraped_title: str, scraped_url: str, db_ean: str = None, scraped_ean: str = None) -> Tuple[bool, float, str]:
        """
        Punto de entrada único para el matching de productos.
        """
        # --- PRIORIDAD 1: RUST KERNEL (Aceleración) ---
        # El kernel de Rust es muy rápido pero puede ser estricto.
        is_match, score, engine_reason = kernel.match_items(product_name, scraped_title, db_ean, scraped_ean)
        
        # Si el Rust Kernel está SEGURO (> 0.95), lo aceptamos de inmediato
        if is_match and score >= 0.95:
            return True, score, f"3OX.Engine :: {engine_reason}"

        # --- PRIORIDAD 2: EAN MATCH (Si falló Rust o confianza media) ---
        if db_ean and scraped_ean:
            clean_db = re.sub(r'[^0-9]', '', str(db_ean))
            clean_scraped = re.sub(r'[^0-9]', '', str(scraped_ean))
            if clean_db == clean_scraped and len(clean_db) >= 8:
                return True, 1.0, f"Perfect EAN Match: {db_ean}"

        # --- PRIORIDAD 3: PYTHON SEMANTIC FALLBACK (El cerebro inteligente) ---
        # Combinamos título y URL para máxima información
        full_scraped_name = f"{scraped_title} {scraped_url}"
        
        py_match, py_score, py_reason = python_engine.calculate_match(
            product_name, 
            full_scraped_name, 
            db_ean, 
            scraped_ean
        )
        
        # Si Python tiene un score significativamente mejor o Rust dio False, usamos Python
        if is_match is False or py_score > score:
            return py_match, py_score, f"Python.Brain :: {py_reason}"
        
        return is_match, score, f"3OX.Engine :: {engine_reason}"
