import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Set

from src.infrastructure.scrapers.vinted_scraper import VintedScraper
from src.infrastructure.scrapers.pipeline import ScrapingPipeline
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import (
    ProductModel,
    LogisticRuleModel,
    BlackcludedItemModel,
    PendingMatchModel,
    HunterAlertLogModel,
    ScraperExecutionLogModel
)
from src.application.services.logistics_service import LogisticsService
from src.infrastructure.services.telegram_service import telegram_service
from src.core.matching import SmartMatcher

logger = logging.getLogger(__name__)

class VintedHunterService:
    """
    Servicio de Incursión y Caza para Vinted.
    Rastrea el cuarteto oficial de búsquedas MOTU (o término personalizado),
    inyecta las ofertas en el Purgatorio y envía alertas push inmediatas a Telegram
    cuando una oferta tiene un Landed Price inferior al precio medio de mercado (P25 / MSRP),
    omitiendo ofertas descartadas por el usuario o ya notificadas en el mismo día natural.
    """

    @staticmethod
    async def run_hunt(
        query: str = "auto",
        chat_id: Optional[str] = None,
        notify_summary: bool = True,
        next_eta_mins: Optional[int] = None
    ) -> Dict[str, Any]:
        start_time = datetime.now(timezone.utc)
        logger.info(f"🏹 VintedHunter: Iniciando caza para query='{query}'...")
        
        # 1. Ejecutar scraper de Vinted
        scraper = VintedScraper()
        offers = await scraper.search(query)
        total_scraped = len(offers)
        logger.info(f"🏹 VintedHunter: Extraídas {total_scraped} ofertas de Vinted.")
        
        if not offers:
            if notify_summary and chat_id:
                try:
                    await telegram_service.send_message(
                        "🏹 <b>[Centinela de Vinted]</b> Incursión finalizada.\n\n"
                        "• 📦 <b>Ofertas analizadas:</b> 0\n"
                        "• 🛡️ <i>Sin actividad reciente en este ciclo.</i>",
                        chat_id=int(chat_id) if str(chat_id).isdigit() else None
                    )
                except Exception:
                    pass
            return {
                "total_scraped": 0,
                "new_purgatory": 0,
                "bargains_found": 0,
                "status": "empty"
            }

        # 2. Inyectar en base de datos / Purgatorio mediante ScrapingPipeline
        pipeline = ScrapingPipeline([])
        pipeline.update_database(offers, shop_names=["Vinted"])
        
        # 3. Detectar y evaluar gangas respecto al precio medio de mercado (P25)
        new_bargains_to_alert = []
        recurring_bargains_count = 0
        matcher = SmartMatcher()
        
        with SessionCloud() as db:
            # A) Precargar URLs descartadas o bloqueadas por el usuario
            blackcluded_urls: Set[str] = {b.url for b in db.query(BlackcludedItemModel.url).all()}
            rejected_matches = db.query(PendingMatchModel.url).filter(
                (PendingMatchModel.validation_status == "REJECTED") | 
                (PendingMatchModel.is_blocked == True)
            ).all()
            rejected_urls: Set[str] = {p[0] for p in rejected_matches}
            discarded_urls: Set[str] = blackcluded_urls.union(rejected_urls)

            # B) Precargar URLs ya notificadas hoy (día natural UTC actual)
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            today_alerted_urls: Set[str] = {
                a[0] for a in db.query(HunterAlertLogModel.url).filter(
                    HunterAlertLogModel.sent_at >= today_start
                ).all()
            }

            # C) Precargar reglas logísticas y catálogo activo
            rules = db.query(LogisticRuleModel).all()
            rules_map = {f"{r.shop_name}_{r.country_code}": r for r in rules}
            products = db.query(ProductModel).filter(ProductModel.is_vintage == False).all()
            
            for offer in offers:
                if offer.price <= 0:
                    continue
                
                # Descartar si el usuario la ha bloqueado o rechazado previamente
                if offer.url in discarded_urls:
                    continue
                    
                # Calcular Landed Price optimizado (Base + 5€ envío + 2% seguro Vinted)
                landed_price = LogisticsService.optimized_get_landing_price(
                    price=offer.price,
                    shop_name="Vinted",
                    user_location="ES",
                    rules_map=rules_map
                )
                
                # Buscar matching contra el catálogo
                best_match_product = None
                best_score = 0.0
                
                for p in products:
                    is_match, score, _ = matcher.match(
                        product_name=p.name,
                        scraped_title=offer.product_name,
                        scraped_url=offer.url,
                        db_ean=p.sku if hasattr(p, "sku") else p.ean,
                        scraped_ean=offer.ean,
                        sub_category=p.sub_category
                    )
                    if is_match and score > best_score:
                        best_score = score
                        best_match_product = p
                
                if not best_match_product or best_score < 0.60:
                    continue
                
                # Determinar el precio de referencia de mercado (P25 o MSRP)
                p25 = best_match_product.p25_price or 0.0
                retail = best_match_product.retail_price or 0.0
                benchmark = p25 if p25 > 0 else (retail if retail > 0 else 0.0)
                
                if benchmark > 0 and landed_price < benchmark:
                    savings_pct = ((benchmark - landed_price) / benchmark) * 100
                    # Alertar si el ahorro es de al menos un 10% respecto al suelo medio
                    if savings_pct >= 10:
                        bargain_data = {
                            "product_name": best_match_product.name,
                            "item_title": offer.product_name,
                            "price": offer.price,
                            "landed_price": landed_price,
                            "benchmark_price": benchmark,
                            "savings_pct": savings_pct,
                            "url": offer.url,
                            "image_url": offer.image_url,
                            "shop_name": "Vinted"
                        }

                        # Comprobar si ya fue alertada hoy
                        if offer.url in today_alerted_urls:
                            recurring_bargains_count += 1
                        else:
                            new_bargains_to_alert.append(bargain_data)
                            # Registrar en la base de datos para deduplicación diaria
                            db.add(HunterAlertLogModel(
                                url=offer.url,
                                product_name=best_match_product.name,
                                price=offer.price,
                                sent_at=datetime.now(timezone.utc)
                            ))
                            today_alerted_urls.add(offer.url)

            db.commit()

        logger.info(
            f"🏹 VintedHunter: {len(new_bargains_to_alert)} nuevas gangas para alertar "
            f"({recurring_bargains_count} omitidas por haber sido alertadas ya hoy)."
        )
        
        # 4. Despachar alertas push individuales para ofertas NUEVAS no alertadas hoy
        for b in new_bargains_to_alert:
            try:
                await telegram_service.send_bargain_hunt_alert(
                    product_name=b["product_name"],
                    item_title=b["item_title"],
                    price=b["price"],
                    landed_price=b["landed_price"],
                    benchmark_price=b["benchmark_price"],
                    savings_pct=b["savings_pct"],
                    shop_name=b["shop_name"],
                    url=b["url"],
                    image_url=b.get("image_url"),
                    chat_id=chat_id
                )
                await asyncio.sleep(0.5)
            except Exception as ex:
                logger.error(f"Error enviando alerta de ganga Vinted: {ex}")

        # 5. Despachar reporte consolidado del ciclo si está activado
        if notify_summary:
            if new_bargains_to_alert:
                bargains_list = "\n".join([
                    f"  ↳ <b>{b['product_name']}</b> a <b>{b['price']:.2f}€</b> (Landed: {b['landed_price']:.2f}€ vs Ref: {b['benchmark_price']:.2f}€ | 💰 <b>-{b['savings_pct']:.0f}%</b>) — <a href=\"{b['url']}\">Ver Oferta</a>"
                    for b in new_bargains_to_alert[:5]
                ])
                opportunities_block = f"🔥 <b>¡Nuevas Oportunidades Detectadas! ({len(new_bargains_to_alert)})</b>\n{bargains_list}\n\n"
            else:
                if recurring_bargains_count > 0:
                    opportunities_block = f"🛡️ <i>{recurring_bargains_count} chollos activos ya fueron notificados hoy (silenciados para evitar repetición).</i>\n\n"
                else:
                    opportunities_block = "🛡️ <i>Sin chollos por debajo del precio medio en este ciclo. Todo bajo control.</i>\n\n"

            eta_text = f"⏱️ <i>Próxima incursión aleatoria en ~{next_eta_mins} min (IP Azure rotatoria).</i>" if next_eta_mins else "⏱️ <i>Incursión completada con éxito.</i>"

            summary_msg = (
                f"🏹 <b>[Centinela de Vinted: Incursión Completada]</b>\n\n"
                f"• 📦 <b>Ofertas analizadas:</b> {total_scraped}\n"
                f"• ⚖️ <b>Purgatorio:</b> Registradas en base de datos\n\n"
                f"{opportunities_block}"
                f"{eta_text}"
            ).strip()

            try:
                target_chat_int = int(chat_id) if chat_id and str(chat_id).isdigit() else None
                await telegram_service.send_message(summary_msg, chat_id=target_chat_int)
            except Exception as ex:
                logger.error(f"Error enviando resumen de centinela a Telegram: {ex}")

        # 6. Guardar log forense de ejecución y minutos en la base de datos
        try:
            with SessionCloud() as db_log:
                db_log.add(ScraperExecutionLogModel(
                    spider_name="VintedHunter",
                    status="success",
                    items_found=total_scraped,
                    new_items=len(new_bargains_to_alert),
                    errors=0,
                    start_time=start_time.replace(tzinfo=None),
                    end_time=datetime.now(timezone.utc).replace(tzinfo=None),
                    trigger_type="sentinel" if query == "auto" else "manual",
                    logs=f"Incursión '{query}': {total_scraped} analizadas, {len(new_bargains_to_alert)} gangas nuevas, {recurring_bargains_count} recurrentes."
                ))
                db_log.commit()
        except Exception as log_ex:
            logger.error(f"Error guardando ScraperExecutionLogModel en VintedHunter: {log_ex}")

        return {
            "total_scraped": total_scraped,
            "bargains_found": len(new_bargains_to_alert),
            "recurring_bargains": recurring_bargains_count,
            "bargains": new_bargains_to_alert,
            "status": "success"
        }
