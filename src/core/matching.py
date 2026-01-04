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

    def match(self, product_name: str, scraped_title: str, scraped_url: str, db_ean: str = None, scraped_ean: str = None, sub_category: str = None) -> Tuple[bool, float, str]:
        """
        Punto de entrada único y centralizado para el matching.
        Aplica la política de Veto: Python siempre tiene la última palabra sobre identidades.
        """
        # --- PRIORIDAD 1: EAN/GTIN (Innegable) ---
        if db_ean and scraped_ean:
            clean_db = re.sub(r'[^0-9]', '', str(db_ean))
            clean_scraped = re.sub(r'[^0-9]', '', str(scraped_ean))
            if clean_db == clean_scraped and len(clean_db) >= 8:
                return True, 1.0, f"Perfect EAN Match: {db_ean}"

        # Preparación de datos DB (Unificamos Nombre + Subcategoría para máxima precisión)
        db_full_name = f"{product_name} {sub_category or ''}".strip()
        
        # --- PRIORIDAD 2: RUST KERNEL (Fast Pass) ---
        rust_match, rust_score, rust_reason = kernel.match_items(db_full_name, scraped_title, db_ean, scraped_ean)
        
        # --- PRIORIDAD 3: PYTHON BRAIN (Deep Semantic + VETO) ---
        # Combinamos título y URL para capturar info extra de la web
        web_full_content = f"{scraped_title} {scraped_url}"
        
        py_match, py_score, py_reason = python_engine.calculate_match(
            db_full_name, 
            web_full_content, 
            db_ean, 
            scraped_ean
        )
        
        # --- LÓGICA DE DECISIÓN UNIFICADA (The Law of the Oracle) ---
        
        # 1. VETO: Si Python detecta conflicto de IDENTIDAD (ej: Panthor != Roboto), 
        # rechazamos el match sin importar lo que diga Rust (siempre que Rust sea confianza media/baja).
        # Si Rust es > 0.95 y Python veta, hay una discrepancia grave: priorizamos el Veto por seguridad.
        if "Conflict" in py_reason or "Dissonance" in py_reason:
            return False, 0.0, f"VETO :: {py_reason}"

        # 2. CONFIANZA EXTREMA: Si Rust está muy seguro (>0.95) y Python no veta, aceptamos.
        if rust_match and rust_score >= 0.95:
            return True, rust_score, f"3OX.Rust :: {rust_reason}"

        # 3. REFUERZO SEMÁNTICO: En zonas de duda (score < 0.95), mandan los pesos del Cerebro.
        return py_match, py_score, f"3OX.Brain :: {py_reason}"
