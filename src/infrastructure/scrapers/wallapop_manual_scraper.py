"""
WallapopManualScraper — Estrategia ALTERNATIVA de extracción de Wallapop.

Objetivo: resolver los bloqueos WAF de CloudFront que sufre el scraper automático
(`WallapopScraper`) cuando se ejecuta desde la IP de datacenter del servidor (OCI).

Diferencias clave frente al scraper clásico:

  1. FIRMA REAL DE LA API v3 (X-Signature): reproduce la firma HMAC que exige
     `api.wallapop.com/api/v3/search` mediante `WallapopSigner`. La llamada "directa"
     del scraper clásico NO firmaba, y CloudFront/Wallapop la penalizaba de inmediato.

  2. IMPERSONACIÓN TLS (curl_cffi chrome): huella TLS/JA3 de Chrome real, no de Python.

  3. PROXY RESIDENCIAL "BYO" (Bring Your Own): si se define la variable de entorno
     `WALLAPOP_RESIDENTIAL_PROXY` (p. ej. una IP residencial/móvil de España, o el túnel
     de la máquina local del usuario), la petición sale por una IP no vetada → bypass real.
     Sin proxy, desde el datacenter, seguirá bloqueado: en ese caso el sistema recomienda
     usar el "Nexus Local Bridge" (ver docs/technical/PLAN_WALLAPOP_NEXUS_LOCAL.md).

Se registra en el orquestador como spider "WallapopManual" y se dispara manualmente
desde el panel de Configuración (endpoint /api/scrapers/run).
"""
from __future__ import annotations

import os
import asyncio
import os
import random
from typing import List, Optional

from curl_cffi.requests import AsyncSession

from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer
from src.infrastructure.scrapers.wallapop_signed_api import search_wallapop_v3_signed


class WallapopManualScraper(BaseScraper):
    """
    Scraper manual de Wallapop basado en API v3 firmada + proxy residencial/local.
    Soporta modo básico (tríada core) y modo completo escalonado (5 familias con paginación profunda).
    """

    CORE_QUERIES = [
        "masters del universo origins",
        "masters of the universe origins",
        "motu origins",
    ]

    FULL_FAMILIES = {
        "1. Tríada Canónica": [
            "masters del universo origins",
            "masters of the universe origins",
            "motu origins",
        ],
        "2. Vendedores Casuales / Chollos": [
            "he-man origins",
            "skeletor origins",
            "figura he-man mattel",
            "muñecos masters del universo",
            "muñeco heman",
        ],
        "3. Sub-líneas y Exclusivas": [
            "cartoon collection motu",
            "turtles of grayskull",
            "mattel creations motu",
            "snakemen origins",
            "fan favorites motu",
        ],
        "4. Vehículos y Playsets": [
            "castillo grayskull origins",
            "snake mountain origins",
            "battle cat origins",
            "point dread motu",
        ],
        "5. Lotes y Liquidaciones": [
            "lote origins",
            "lote motu",
            "lote masters del universo",
        ],
    }

    def __init__(self):
        super().__init__(shop_name="Wallapop", base_url="https://es.wallapop.com")
        self.is_auction_source = True  # Peer-to-Peer -> Purgatorio

    async def _search_single(
        self, session: AsyncSession, query: str, proxy: str | None, start: int = 0
    ) -> List[ScrapedOffer]:
        result = await search_wallapop_v3_signed(
            session,
            query,
            proxy=proxy,
            max_items=40,
            start=start,
            log_callback=self._log,
            shop_name_override=self.shop_name,
        )
        if result.blocked:
            self.blocked = True
        return result.offers

    async def search(self, query: str = "auto") -> List[ScrapedOffer]:
        self._log("⚔️ WallapopManual: iniciando extracción (API v3 firmada).")

        proxy = os.environ.get("WALLAPOP_RESIDENTIAL_PROXY") or None
        if proxy:
            self._log("🛰️ Proxy residencial detectado. Ruteando por IP no vetada.")
        else:
            self._log("ℹ️ Conexión directa residencial.")

        q_clean = (query or "").strip().lower()
        is_deep_mode = q_clean in ["completo", "full", "deep", "exhaustivo"]

        all_offers: List[ScrapedOffer] = []

        if is_deep_mode:
            self._log("🌟 [NEXUS COMPLETO] Iniciando Incursión Profunda Escalonada (5 Familias con Paginación Segura)...")
            async with AsyncSession() as session:
                for family_name, terms in self.FULL_FAMILIES.items():
                    self._log(f"📂 Procesando Familia: {family_name}...")
                    for t in terms:
                        # Página 1 (start=0)
                        p1_offers = await self._search_single(session, t, proxy, start=0)
                        all_offers.extend(p1_offers)
                        
                        # Pausa humana aleatoria entre páginas (1.2s - 2.0s)
                        await asyncio.sleep(random.uniform(1.2, 2.0))
                        
                        # Página 2 (start=40)
                        p2_offers = await self._search_single(session, t, proxy, start=40)
                        all_offers.extend(p2_offers)
                        
                        # Pausa de seguridad entre términos (1.8s - 3.0s)
                        await asyncio.sleep(random.uniform(1.8, 3.0))
                        
                    # Pausa extra entre familias (2.5s - 4.0s)
                    await asyncio.sleep(random.uniform(2.5, 4.0))
        else:
            # Modo básico o consultas personalizadas
            if q_clean in ["auto", "basico", "basic", ""]:
                queries = self.CORE_QUERIES
            elif "," in query:
                queries = [q.strip() for q in query.split(",") if q.strip()]
            else:
                queries = [query.strip()]

            async with AsyncSession() as session:
                for idx, q in enumerate(queries):
                    all_offers.extend(await self._search_single(session, q, proxy, start=0))
                    if idx < len(queries) - 1:
                        await asyncio.sleep(random.uniform(1.0, 2.0))

        # Deduplicar por URL
        seen = set()
        unique: List[ScrapedOffer] = []
        for o in all_offers:
            if o.url not in seen:
                seen.add(o.url)
                unique.append(o)

        self.items_scraped = len(unique)
        if self.blocked and not unique:
            self._log(
                "🛡️ WallapopManual: bloqueado por WAF en todas las búsquedas. "
                "Verifica que el Nexus Local Bridge (.\\run_nexus_bridge.ps1) esté corriendo con IP residencial.",
                level="warning",
            )
        else:
            self._log(f"✅ WallapopManual: {self.items_scraped} reliquias únicas enviadas al Purgatorio.")
        return unique


if __name__ == "__main__":
    import asyncio
    import logging
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    async def _test():
        s = WallapopManualScraper()
        res = await s.search("masters of the universe origins")
        print(f"\nTotal: {len(res)} (blocked={s.blocked})")
        for r in res[:10]:
            print(f"- {r.product_name}: {r.price}€ -> {r.url}")

    asyncio.run(_test())
