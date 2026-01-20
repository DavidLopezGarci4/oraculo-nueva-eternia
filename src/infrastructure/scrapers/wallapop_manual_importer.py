"""
WallapopManualImporter: Sistema de importación manual asistida para Wallapop.
Fase 10.3 - Solución alternativa ante bloqueos de CloudFront.

FLUJO DE USO:
1. El usuario navega a Wallapop y busca "motu origins" (u otro término).
2. Copia las URLs de los productos que le interesan a un archivo .txt (una por línea).
3. Ejecuta este script que procesa las URLs y las envía al Purgatorio.

ALTERNATIVA SIMPLE:
- El usuario puede pegar datos en formato CSV directamente.
"""
import asyncio
import logging
import re
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# Importaciones del proyecto
from src.infrastructure.scrapers.base import ScrapedOffer
from src.infrastructure.scrapers.pipeline import ScrapingPipeline
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import PendingMatchModel

logger = logging.getLogger(__name__)

class WallapopManualImporter:
    """
    Importador manual para datos de Wallapop.
    Soporta múltiples formatos de entrada.
    """
    
    def __init__(self):
        self.shop_name = "Wallapop"
        self.items_imported = 0
    
    def parse_simple_format(self, text: str) -> List[dict]:
        """
        Parsea texto en formato simple:
        Nombre del producto | Precio | URL
        
        Ejemplo:
        He-Man Origins | 25.00 | https://es.wallapop.com/item/he-man-123
        """
        offers = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3:
                try:
                    name = parts[0]
                    price = float(re.sub(r'[^\d.,]', '', parts[1]).replace(',', '.'))
                    url = parts[2]
                    
                    if 'wallapop.com' in url:
                        offers.append({
                            'product_name': f"[Wallapop] {name}",
                            'price': price,
                            'url': url
                        })
                except Exception as e:
                    logger.warning(f"Error parseando linea: {line} - {e}")
                    continue
        
        return offers
    
    def parse_url_list(self, text: str) -> List[str]:
        """
        Extrae URLs de Wallapop de un texto.
        """
        pattern = r'https?://(?:es\.)?wallapop\.com/item/[^\s\"\'\<\>]+'
        return list(set(re.findall(pattern, text)))
    
    async def import_from_file(self, filepath: str) -> int:
        """
        Importa datos desde un archivo .txt o .csv.
        """
        path = Path(filepath)
        if not path.exists():
            logger.error(f"Archivo no encontrado: {filepath}")
            return 0
        
        content = path.read_text(encoding='utf-8')
        
        # Detectar formato
        if '|' in content:
            offers_data = self.parse_simple_format(content)
        else:
            # Solo URLs, extraer y crear ofertas básicas
            urls = self.parse_url_list(content)
            offers_data = [{'url': url, 'product_name': '[Wallapop] Item', 'price': 0} for url in urls]
        
        return await self._save_to_purgatory(offers_data)
    
    async def import_from_text(self, text: str) -> int:
        """
        Importa datos desde texto directo (clipboard, etc).
        """
        if '|' in text:
            offers_data = self.parse_simple_format(text)
        else:
            urls = self.parse_url_list(text)
            offers_data = [{'url': url, 'product_name': '[Wallapop] Item', 'price': 0} for url in urls]
        
        return await self._save_to_purgatory(offers_data)
    
    async def _save_to_purgatory(self, offers_data: List[dict]) -> int:
        """
        Guarda las ofertas en la tabla de Purgatorio para revisión manual.
        """
        saved = 0
        
        with SessionCloud() as db:
            for offer in offers_data:
                # Verificar si ya existe en Purgatorio
                existing = db.query(PendingMatchModel).filter(
                    PendingMatchModel.url == offer['url']
                ).first()
                
                if existing:
                    logger.info(f"URL ya existe en Purgatorio: {offer['url'][:50]}...")
                    continue
                
                # Crear nuevo item en Purgatorio
                pending = PendingMatchModel(
                    scraped_name=offer['product_name'],
                    price=offer['price'],
                    currency="EUR",
                    url=offer['url'],
                    shop_name=self.shop_name,
                    image_url=None,
                    origin_category="auction",
                    found_at=datetime.utcnow()
                )
                db.add(pending)
                saved += 1
            
            db.commit()
        
        self.items_imported = saved
        logger.info(f"[WallapopManualImporter] Importados {saved} items al Purgatorio.")
        return saved


# === SCRIPT DE USO INTERACTIVO ===
if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("WALLAPOP MANUAL IMPORTER - EL ORACULO DE ETERNIA")
    print("=" * 60)
    print()
    print("INSTRUCCIONES:")
    print("1. Navega a Wallapop y busca 'motu origins'")
    print("2. Copia los datos de los productos que te interesen")
    print("3. Pega aqui en formato: Nombre | Precio | URL")
    print("   (Una linea por producto)")
    print()
    print("O simplemente pega las URLs (una por linea)")
    print()
    print("Escribe 'FIN' en una linea vacia para procesar.")
    print("-" * 60)
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'FIN':
                break
            lines.append(line)
        except EOFError:
            break
    
    text = '\n'.join(lines)
    
    if not text.strip():
        print("No se recibieron datos. Saliendo.")
        sys.exit(0)
    
    async def run_import():
        importer = WallapopManualImporter()
        count = await importer.import_from_text(text)
        print()
        print("=" * 60)
        print(f"RESULTADO: {count} items importados al Purgatorio.")
        print("Ahora puedes vincularlos desde la web del Oraculo.")
        print("=" * 60)
    
    asyncio.run(run_import())
