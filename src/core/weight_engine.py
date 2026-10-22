
import math
import threading
from typing import Dict, Set, Optional, Iterable
from collections import Counter
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from src.domain.models import ProductModel
from src.core.text_normalization import tokenize

# Peso a partir del cual un token es una "Identidad" (palabra rara que debe coincidir)
IDENTITY_WEIGHT = 5.0

class WeightEngine:
    """
    Motor Dinámico de Pesos basado en IDF (Inverse Document Frequency).
    Analiza la base de datos matriz para determinar qué palabras son 'Identidades' 
    (raras y únicas) y cuáles son 'Series' (comunes y repetitivas).
    """
    
    def __init__(self, db_url: Optional[str] = None):
        # Usar la base de datos de configuración por defecto
        self.db_url = db_url or settings.DATABASE_URL
        self.weights: Dict[str, float] = {}
        self.token_df: Counter = Counter()
        self.total_docs: int = 0
        # Tokens que aparecen en algún NOMBRE de producto (no solo en subcategorías)
        self.name_tokens: frozenset = frozenset()
        self._signature: Optional[tuple] = None
        self._lock = threading.Lock()
        
        # Cargar inicial
        self.refresh()

    def normalize(self, text: str) -> Set[str]:
        # Normalización compartida con brain_engine y el índice del Purgatorio
        return tokenize(text)

    @staticmethod
    def _catalog_signature(products: list) -> tuple:
        names_hash = hash(tuple(sorted(f"{p.id}:{p.name}:{p.sub_category or ''}" for p in products)))
        return (len(products), max((p.id or 0) for p in products), names_hash)

    def _compute(self, products: Iterable) -> None:
        products = list(products)
        new_total_docs = len(products)
        if new_total_docs == 0:
            logger.warning("WeightEngine: Database is empty. Using default weights.")
            return

        new_df = Counter()
        new_name_tokens = set()
        for p in products:
            name_tokens = self.normalize(p.name or "")
            new_name_tokens |= name_tokens
            tokens = name_tokens | self.normalize(p.sub_category or "")
            for t in tokens:
                new_df[t] += 1
        
        # Calcular Pesos Dinámicos
        new_weights = {}
        max_idf = math.log10(new_total_docs) if new_total_docs > 1 else 1
        
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
            self.name_tokens = frozenset(new_name_tokens)
            self._signature = self._catalog_signature(products)

    def refresh(self):
        """Recalcula los pesos analizando todos los productos de la DB configurada (arranque)."""
        try:
            engine = create_engine(self.db_url)
            Session = sessionmaker(bind=engine)
            with Session() as session:
                products = session.query(ProductModel).all()
                self._compute(products)
                if self.total_docs:
                    logger.success(f"WeightEngine: Refreshed weights for {len(self.weights)} tokens from {self.total_docs} products.")
        except Exception as e:
            logger.error(f"WeightEngine: Error refreshing weights: {e}")

    def refresh_from_products(self, products: list) -> bool:
        """
        Recalcula los pesos con el catálogo real que usa la petición (p.ej. Supabase).
        Solo recalcula si el catálogo ha cambiado (firma por nº, id máximo y nombres).
        Devuelve True si ha recalculado.
        """
        if not products:
            return False
        try:
            signature = self._catalog_signature(products)
            if signature == self._signature:
                return False
            self._compute(products)
            return True
        except Exception as e:
            logger.error(f"WeightEngine: Error refreshing weights from products: {e}")
            return False

    def get_weight(self, token: str) -> float:
        """
        Devuelve el peso de un token. 
        Si es conocido, se usa su IDF [1.0, 10.0].
        Si es DESCONOCIDO, se asume que es RUIDO (peso 1.0) para no penalizar el match.
        """
        with self._lock:
            # Si no conocemos el token, probablemente sea una palabra de la web que no está en la DB
            return self.weights.get(token, 1.0)

    def snapshot(self) -> tuple:
        """(pesos, tokens_de_nombres) actuales. Los dicts se sustituyen atómicamente al refrescar."""
        with self._lock:
            return self.weights, self.name_tokens

    def is_known(self, token: str) -> bool:
        with self._lock:
            return token in self.weights

    def is_identity(self, token: str) -> bool:
        """Determina si un token es una Identidad Crítica (peso > 5.0)."""
        # Solo consideramos identidades palabras que SÍ están en nuestra DB
        with self._lock:
            if token not in self.weights:
                return False
            return self.weights[token] > IDENTITY_WEIGHT

# Singleton global instance
weights_manager = WeightEngine()
