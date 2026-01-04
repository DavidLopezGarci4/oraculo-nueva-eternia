
import re
import math
import unicodedata
import threading
from typing import Dict, Set, Optional
from collections import Counter
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models import ProductModel

class WeightEngine:
    """
    Motor Dinámico de Pesos basado en IDF (Inverse Document Frequency).
    Analiza la base de datos matriz para determinar qué palabras son 'Identidades' 
    (raras y únicas) y cuáles son 'Series' (comunes y repetitivas).
    """
    
    def __init__(self, db_url: str = "sqlite:///oraculo.db"):
        self.db_url = db_url
        self.weights: Dict[str, float] = {}
        self.token_df: Counter = Counter()
        self.total_docs: int = 0
        self._lock = threading.Lock()
        
        # Cargar inicial
        self.refresh()

    def normalize(self, text: str) -> Set[str]:
        if not text: return set()
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        text = text.lower()
        text = re.sub(r'[^a-z0-9]', ' ', text)
        tokens = set(text.split())
        # Filtro básico: longitud > 1 para evitar ruido (ej: 'a', 'la')
        return {t for t in tokens if len(t) > 1 or t.isdigit()}

    def refresh(self):
        """Recalcula los pesos analizando todos los productos de la DB."""
        try:
            engine = create_engine(self.db_url)
            Session = sessionmaker(bind=engine)
            with Session() as session:
                products = session.query(ProductModel).all()
                new_total_docs = len(products)
                
                if new_total_docs == 0:
                    logger.warning("WeightEngine: Database is empty. Using default weights.")
                    return

                new_df = Counter()
                for p in products:
                    combined = f"{p.name} {p.sub_category or ''}"
                    tokens = self.normalize(combined)
                    for t in tokens:
                        new_df[t] += 1
                
                # Calcular Pesos Dinámicos
                new_weights = {}
                max_idf = math.log10(new_total_docs) if new_total_docs > 0 else 1
                
                for t, count in new_df.items():
                    # IDF = log10(Total / df)
                    idf = math.log10(new_total_docs / count)
                    # Escala [1.0, 10.0]
                    # Si aparece en todos (df=N), idf=0 -> peso=1.0
                    # Si aparece en 1 (df=1), idf=max -> peso=10.0
                    scale = 9 * (idf / max_idf) if max_idf > 0 else 0
                    new_weights[t] = round(1.0 + scale, 2)

                with self._lock:
                    self.weights = new_weights
                    self.token_df = new_df
                    self.total_docs = new_total_docs
                
                logger.success(f"WeightEngine: Refreshed weights for {len(self.weights)} tokens from {new_total_docs} products.")
                
        except Exception as e:
            logger.error(f"WeightEngine: Error refreshing weights: {e}")

    def get_weight(self, token: str) -> float:
        """
        Devuelve el peso de un token. 
        Si es conocido, se usa su IDF [1.0, 10.0].
        Si es DESCONOCIDO, se asume que es RUIDO (peso 1.0) para no penalizar el match.
        """
        with self._lock:
            # Si no conocemos el token, probablemente sea una palabra de la web que no está en la DB
            return self.weights.get(token, 1.0)

    def is_identity(self, token: str) -> bool:
        """Determina si un token es una Identidad Crítica (peso > 5.0)."""
        # Solo consideramos identidades palabras que SÍ están en nuestra DB
        with self._lock:
            if token not in self.weights:
                return False
            return self.weights[token] > 5.0

# Singleton global instance
weights_manager = WeightEngine()
