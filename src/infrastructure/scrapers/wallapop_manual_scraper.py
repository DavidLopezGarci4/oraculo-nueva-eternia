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
from typing import List

from curl_cffi.requests import AsyncSession

from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer
from src.infrastructure.scrapers.wallapop_signed_api import search_wallapop_v3_signed


class WallapopManualScraper(BaseScraper):
    """Scraper manual de Wallapop basado en API v3 firmada + proxy residencial opcional."""

    def __init__(self):
        super().__init__(shop_name="WallapopManual", base_url="https://es.wallapop.com")
        self.is_auction_source = True  # Peer-to-Peer -> Purgatorio

    async def _search_single(self, session: AsyncSession, query: str, proxy: str | None) -> List[ScrapedOffer]:
        result = await search_wallapop_v3_signed(
            session,
            query,
            proxy=proxy,
            max_items=40,
            log_callback=self._log,
            shop_name_override=self.shop_name,
        )
        if result.blocked:
            self.blocked = True
        return result.offers

    async def search(self, query: str = "auto") -> List[ScrapedOffer]:
        self._log("⚔️ WallapopManual: iniciando extracción alternativa (API v3 firmada).")

        proxy = os.environ.get("WALLAPOP_RESIDENTIAL_PROXY") or None
        if proxy:
            self._log("🛰️ Proxy residencial detectado (WALLAPOP_RESIDENTIAL_PROXY). Ruteando por IP no vetada.")
        else:
            self._log("ℹ️ Sin proxy residencial. Si la IP es de datacenter, se recomienda el Nexus Local Bridge.")

        if query == "auto":
            queries = [
                "masters del universo origins",
                "masters of the universe origins",
                "motu origins",
            ]
        else:
            queries = [query]

        all_offers: List[ScrapedOffer] = []
        async with AsyncSession() as session:
            for q in queries:
                all_offers.extend(await self._search_single(session, q, proxy))

        # Deduplicar por URL
        seen = set()
        unique: List[ScrapedOffer] = []
        for o in all_offers:
            if o.url not in seen:
                seen.add(o.url)
                unique.append(o)

        self.items_scraped = len(unique)
        self._log(f"✅ WallapopManual: {self.items_scraped} reliquias únicas hacia el Purgatorio.")
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
