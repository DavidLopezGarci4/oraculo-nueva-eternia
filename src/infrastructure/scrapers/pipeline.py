import asyncio
import json
import threading
from typing import List
from datetime import datetime
from loguru import logger
from src.infrastructure.scrapers.base import BaseScraper, ScrapedOffer
from src.domain.schemas import ProductSchema
from src.infrastructure.repositories.product import ProductRepository
from sqlalchemy.orm import Session
from src.infrastructure.database_cloud import SessionCloud, init_cloud_db
from src.infrastructure.services.telegram_service import telegram_service
from src.application.services.deal_scorer import DealScorer
from src.application.services.logistics_service import LogisticsService
def clean_purgatory_globally(db: Session):
    """
    Elimina de forma proactiva y global del Purgatorio cualquier oferta 
    cuya URL ya esté guardada en offers, blackcluded_items o vintage_miscellaneous.
    """
    from src.domain.models import PendingMatchModel, OfferModel, BlackcludedItemModel, VintageMiscellaneousModel
    
    try:
        q_offers = db.query(OfferModel.url).subquery()
        q_black = db.query(BlackcludedItemModel.url).subquery()
        q_misc = db.query(VintageMiscellaneousModel.url).subquery()
        
        deleted_offers = db.query(PendingMatchModel).filter(PendingMatchModel.url.in_(q_offers)).delete(synchronize_session=False)
        deleted_black = db.query(PendingMatchModel).filter(PendingMatchModel.url.in_(q_black)).delete(synchronize_session=False)
        deleted_misc = db.query(PendingMatchModel).filter(PendingMatchModel.url.in_(q_misc)).delete(synchronize_session=False)
        
        total_deleted = deleted_offers + deleted_black + deleted_misc
        if total_deleted > 0:
            logger.info(f"🧹 Purgatory Cleanup: Removed {total_deleted} redundant items ({deleted_offers} linked, {deleted_black} blacklisted, {deleted_misc} misc)")
    except Exception as e:
        logger.error(f"⚠️ Error running global purgatory cleanup: {e}")

def check_and_send_multiuser_alerts(db: Session, scraped_name: str, price: float, shop_name: str, url: str, is_vintage: bool):
    """
    Cruza una nueva oferta con las listas de deseos y alertas de precio de todos los usuarios
    que tengan registrado un telegram_chat_id, disparando las alertas correspondientes.
    """
    from src.domain.models import UserModel, CollectionItemModel, ProductModel, PriceAlertModel
    from src.infrastructure.services.telegram_service import telegram_service
    import re
    
    try:
        users_with_tg = db.query(UserModel).filter(UserModel.telegram_chat_id != None, UserModel.is_active == True).all()
        if not users_with_tg:
            return
            
        name_lower = scraped_name.lower()
        
        for u in users_with_tg:
            # 1. Alertas de Lista de Deseos (Wishlist)
            wishlist_items = db.query(ProductModel).join(CollectionItemModel).filter(
                CollectionItemModel.owner_id == u.id,
                CollectionItemModel.acquired == False
            ).all()
            
            for p in wishlist_items:
                p_clean = p.name.lower().replace("-", " ")
                p_words = [w for w in re.sub(r'[^a-z0-9\s]', '', p_clean).split() if len(w) > 2]
                if p_words and all(w in name_lower for w in p_words):
                    # Coincidencia! Enviar alerta
                    asyncio.create_task(telegram_service.send_wishlist_alert(
                        chat_id=u.telegram_chat_id,
                        product_name=p.name,
                        price=price,
                        shop_name=shop_name,
                        url=url
                    ))
                    break # Evitar duplicados por oferta
            
            # 2. Alertas de Precio Objetivo (El Centinela)
            price_alerts = db.query(PriceAlertModel).join(ProductModel).filter(
                PriceAlertModel.user_id == u.id,
                PriceAlertModel.is_active == True,
                PriceAlertModel.target_price >= price
            ).all()
            
            for pa in price_alerts:
                p_clean = pa.product.name.lower().replace("-", " ")
                p_words = [w for w in re.sub(r'[^a-z0-9\s]', '', p_clean).split() if len(w) > 2]
                if p_words and all(w in name_lower for w in p_words):
                    asyncio.create_task(telegram_service.send_price_alert(
                        chat_id=u.telegram_chat_id,
                        product_name=pa.product.name,
                        price=price,
                        target_price=pa.target_price,
                        shop_name=shop_name,
                        url=url
                    ))
                    break
    except Exception as e:
        logger.error(f"⚠️ Error en check_and_send_multiuser_alerts: {e}")

class ScrapingPipeline:
    def __init__(self, scrapers: List[BaseScraper], cancel_event: threading.Event | None = None):
        self.scrapers = scrapers
        self.cancel_event = cancel_event
        self.log_callback = None

    def _log(self, msg: str):
        if self.log_callback:
            try:
                self.log_callback(msg)
            except:
                pass

    async def run_product_search(self, product_name: str) -> List[dict]:
        """
        Runs all spiders with cancellation support.
        If cancel_event is set, aborts remaining scrapers.
        """
        logger.info(f"Pipeline: Searching for '{product_name}' across {len(self.scrapers)} scrapers.")
        
        all_legacy_offers = []
        
        for scraper in self.scrapers:
            # 🛡️ Check cancellation before each scraper
            if self.cancel_event and self.cancel_event.is_set():
                logger.warning(f"🛑 Pipeline ABORTADO: Señal de cancelación recibida antes de {scraper.shop_name}.")
                break
            
            try:
                res = await asyncio.wait_for(scraper.search(product_name), timeout=300)  # 5 min per scraper max
                logger.info(f"Scraper {scraper.shop_name} found {len(res)} offers.")
                source = "Peer-to-Peer" if getattr(scraper, 'is_auction_source', False) else "Retail"
                for offer in res:
                    if isinstance(offer, ScrapedOffer):
                        offer.source_type = source
                all_legacy_offers.extend(res)
            except asyncio.TimeoutError:
                logger.warning(f"⏳ Scraper {scraper.shop_name} TIMEOUT (5 min). Saltando.")
            except asyncio.CancelledError:
                logger.warning(f"🛑 Scraper {scraper.shop_name} CANCELADO.")
                break
            except Exception as e:
                logger.error(f"Scraper {scraper.shop_name} failed for '{product_name}': {e}")
        
        if self.cancel_event and self.cancel_event.is_set():
            logger.warning(f"🛑 Pipeline cancelado. Devolviendo {len(all_legacy_offers)} ofertas parciales recolectadas.")
        
        # 3OX.Bridge :: Transformación al Contrato dev/contract.ref
        from src.infrastructure.scrapers.adapter import adapter
        transformed_offers = adapter.transform(all_legacy_offers)
        
        return transformed_offers

    def clean_product_name(self, name: str) -> str:
        """
        Normalizes product names for better fuzzy matching.
        """
        import re
        n = name.lower()
        # Specific fix for "Sun-Man" -> "Sun Man" to handle hyphenated names
        n = n.replace("-", " ")
        
        remove_list = [
            "masters of the universe", "motu", "origins", 
            "figura", "figure", "action", "mattel", "14 cm", "14cm"
        ]
        for w in remove_list:
            n = n.replace(w, "")
        
        # Remove special chars but keep spaces
        n = re.sub(r'[^a-zA-Z0-9\s]', '', n)
        return " ".join(n.split())

    def sync_availability(self, found_urls: List[str], shop_names: List[str]):
        """
        Fase 44: Sincroniza la disponibilidad de las ofertas.
        Si una oferta activa de una de las tiendas escaneadas no está en found_urls,
        se marca como no disponible (is_available = False).
        """
        from src.domain.models import OfferModel
        from datetime import datetime, timedelta
        
        db: Session = SessionCloud()
        try:
            # Buscamos ofertas que estaban marcadas como disponibles pero no se han encontrado ahora
            query = db.query(OfferModel).filter(
                OfferModel.shop_name.in_(shop_names),
                OfferModel.is_available == True,
                ~OfferModel.url.in_(found_urls)
            )
            
            missing_offers = query.all()
            if not missing_offers:
                # logger.debug(f"📊 Sync: No se encontraron items para desactivar en {shop_names}")
                return

            for offer in missing_offers:
                # Regla eBay: 48h de gracia para evitar falsos negativos por micro-bloqueos
                if offer.shop_name == "Ebay.es":
                    if datetime.utcnow() - offer.last_seen < timedelta(hours=48):
                        continue
                
                # Regla General (Vinted/Otros): Si desaparece de la búsqueda, ya no está disponible
                offer.is_available = False
                logger.info(f"🌑 Sync: Oferta marcada como no disponible: {offer.url} ({offer.shop_name})")
                
                # Regla de Historial: Registrar que el ítem se vendió o no está disponible
                from src.domain.models import OfferHistoryModel
                action = "SOLD_OR_UNAVAILABLE_VINTAGE" if offer.is_vintage else "SOLD_OR_UNAVAILABLE"
                history = OfferHistoryModel(
                    offer_url=offer.url,
                    product_name=offer.product.name if offer.product else "Desconocido",
                    shop_name=offer.shop_name,
                    price=offer.price,
                    action_type=action,
                    details=json.dumps({
                        "last_seen": offer.last_seen.isoformat() if offer.last_seen else None,
                        "is_vintage": offer.is_vintage
                    }),
                )
                db.add(history)
            
            db.commit()
            logger.success(f"✔️ Sync: Finalizada sincronización de disponibilidad para {shop_names}.")
        except Exception as e:
            logger.error(f"❌ Error en sync_availability: {e}")
            db.rollback()
        finally:
            db.close()

    def update_database(self, offers: List[dict], shop_names: List[str] = None):
        """
        Persists found offers to the database using SmartMatcher.
        Includes Phase 18: Búnker & Circuit Breaker.
        REFACTOR 7.3: Bulk Pre-filtering Strategy (No more N+1 / Duplicate Errors).
        Fase 44: Integración de sync_availability.
        """
        if not offers and not shop_names:
            logger.warning("🛡️ Circuit Breaker: No offers found to process. Skipping DB update for this batch.")
            return

        # Ensure offers are dicts (Standardize objects from different Pydantic versions)
        standardized_offers = []
        for o in offers:
            if hasattr(o, 'model_dump'):
                standardized_offers.append(o.model_dump())
            elif hasattr(o, 'dict'):
                standardized_offers.append(o.dict())
            elif isinstance(o, dict):
                standardized_offers.append(o)
            else:
                # Fallback for generic objects with __dict__
                try:
                    standardized_offers.append(vars(o))
                except:
                    standardized_offers.append(o)
        offers = standardized_offers

        # --- UNIVERSAL URL NORMALIZATION LAYER ---
        from src.core.url_utils import normalize_url
        for o in offers:
            if o.get('url'):
                o['url'] = normalize_url(o['url'])

        # --- SQLITE DATE TIME COMPATIBILITY KAIZEN ---
        from dateutil.parser import parse as parse_date
        
        def secure_date(val):
            if not val:
                return None
            if isinstance(val, datetime):
                return val
            from datetime import date
            if isinstance(val, date):
                return datetime(val.year, val.month, val.day)
            if isinstance(val, str):
                try:
                    return parse_date(val)
                except Exception:
                    return None
            return None

        for o in offers:
            if 'first_seen_at' in o:
                o['first_seen_at'] = secure_date(o['first_seen_at'])
            if 'expiry_at' in o:
                o['expiry_at'] = secure_date(o['expiry_at'])
            if 'sold_at' in o:
                o['sold_at'] = secure_date(o['sold_at'])
            if 'original_listing_date' in o:
                o['original_listing_date'] = secure_date(o['original_listing_date'])
            if 'found_at' in o:
                o['found_at'] = secure_date(o['found_at'])
            if 'last_price_update' in o:
                o['last_price_update'] = secure_date(o['last_price_update'])

        # 1. Save Raw Snapshot (Black Box)
        try:
            from src.core.backup_manager import BackupManager
            bm = BackupManager()
            shop_name = offers[0].get('shop_name', 'unknown') if offers else "unknown"
            bm.save_raw_snapshot(shop_name, offers)
        except Exception as e:
            logger.error(f"⚠️ Failed to save safety snapshot: {e}")

        from src.infrastructure.database_cloud import SessionCloud
        db: Session = SessionCloud()
        from src.core.matching import SmartMatcher
        
        matcher = SmartMatcher()
        repo = ProductRepository(db)
        from src.application.services.auditor import AuditorService
        from src.application.services.sentinel import SentinelService
        from src.domain.models import PendingMatchModel, BlackcludedItemModel, OfferModel, LogisticRuleModel, VintageMiscellaneousModel
        
        auditor = AuditorService(repo)
        sentinel = SentinelService(repo)
        
        try:
            # Limpieza global proactiva del purgatorio al inicio del lote
            clean_purgatory_globally(db)
            
            # --- PHASE 7.3: BULK PRE-FETCHING ---
            self._log("🛡️ [Filtro] Iniciando pre-filtrado y cruce de datos en base de datos...")
            logger.info("🛡️ Pipeline: Initiating Bulk Pre-filtering...")
            
            # A. Extract URLs from incoming batch
            incoming_urls = [str(o.get('url', '')) for o in offers if o.get('url')]
            
            if not incoming_urls:
                logger.warning("No valid URLs in batch. Aborting.")
                return

            # B. Bulk Check against Database (4 Queries instead of N)
            # 1. Blocked Items
            blocked_urls = set(
                x[0] for x in db.query(BlackcludedItemModel.url).filter(BlackcludedItemModel.url.in_(incoming_urls)).all()
            )
            # 2. Pending Items (Purgatory) - Fetch full objects for price updates
            existing_pending = {
                p.url: p for p in db.query(PendingMatchModel).filter(PendingMatchModel.url.in_(incoming_urls)).all()
            }
            existing_pending_urls = set(existing_pending.keys())
            # 3. Active Offers (Linked) - Fetch full objects for updates
            existing_offers = {
                o.url: o for o in db.query(OfferModel).filter(OfferModel.url.in_(incoming_urls)).all()
            }
            # 4. Miscellaneous Items - Fetch full objects for updates
            existing_misc = {
                m.url: m for m in db.query(VintageMiscellaneousModel).filter(VintageMiscellaneousModel.url.in_(incoming_urls)).all()
            }

            # C. Clean up redundant items in Purgatory (already matched/discarded/miscellaneous)
            redundant_pending_urls = existing_pending_urls.intersection(
                blocked_urls.union(existing_offers.keys()).union(existing_misc.keys())
            )
            if redundant_pending_urls:
                logger.info(f"🧹 Pipeline Cleanup: Removing {len(redundant_pending_urls)} redundant items from Purgatory (already matched/discarded/miscellaneous)")
                db.query(PendingMatchModel).filter(PendingMatchModel.url.in_(redundant_pending_urls)).delete(synchronize_session=False)
                for url in redundant_pending_urls:
                    existing_pending_urls.discard(url)
                    existing_pending.pop(url, None)
            
            # Pre-fetch all products for matching (only if needed)
            all_products = repo.get_all(limit=5000)

            # --- PHASE 34: LOGISTICS PRE-CACHE (Eliminate N+1) ---
            rules = db.query(LogisticRuleModel).all()
            rules_map = {f"{r.shop_name}_{r.country_code}": r for r in rules}
            user_location = "ES" # Default

            self._log(f"📊 [Stats] {len(offers)} ofertas recibidas | {len(existing_offers)} activas en catálogo | {len(existing_pending_urls)} en Purgatorio | {len(blocked_urls)} en Lista Negra")
            logger.info(f"📊 Stats: {len(offers)} incoming | {len(existing_offers)} active links | {len(existing_pending_urls)} in Purgatory | {len(blocked_urls)} blocked")

            processed_urls_in_batch = set()
            new_items_count = 0
            price_updates_count = 0
            unchanged_count = 0
            discarded_count = 0
            
            for offer in offers:
                url_str = str(offer.get('url', ''))
                
                # a. Dedup within batch
                if url_str in processed_urls_in_batch:
                    discarded_count += 1
                    continue
                processed_urls_in_batch.add(url_str)
                
                # b. Check Blacklist
                if url_str in blocked_urls:
                    discarded_count += 1
                    # logger.debug(f"🛑 Blocked: {offer.get('product_name')}")
                    continue
                    
                # c. Check Active Links (Update Logic)
                if url_str in existing_offers:
                    existing_offer = existing_offers[url_str]
                    # Track price updates vs unchanged
                    old_price = existing_offer.price
                    new_price = offer.get('price')
                    if old_price is not None and new_price is not None and abs(old_price - new_price) > 0.01:
                        price_updates_count += 1
                    else:
                        unchanged_count += 1

                    # --- PHASE 18: DEAL SCORER (UPDATE SCORE) ---
                    # We assume user_id 2 for location/wishlist check
                    landed_price = LogisticsService.optimized_get_landing_price(offer.get('price'), offer.get('shop_name'), user_location, rules_map)
                    is_wish = any(ci.owner_id == 2 and not ci.acquired for ci in existing_offer.product.collection_items)
                    opp_score = DealScorer.calculate_score(existing_offer.product, landed_price, is_wish)

                    # Update without committing yet
                    repo.add_offer(existing_offer.product, {
                        "shop_name": offer.get('shop_name'),
                        "price": offer.get('price'),
                        "currency": offer.get('currency'), 
                        "url": url_str,
                        "is_available": offer.get('is_available') if offer.get('is_available') is not None else True,
                        "source_type": offer.get('source_type', 'Retail'),
                        "opportunity_score": opp_score,
                        "sale_type": offer.get('sale_type', 'Retail'),
                        "expiry_at": offer.get('expiry_at'),
                        "bids_count": offer.get('bids_count', 0),
                        "time_left_raw": offer.get('time_left_raw'),
                        "sold_at": offer.get('sold_at'),
                        "is_sold": offer.get('is_sold', False),
                        "original_listing_date": offer.get('original_listing_date'),
                        "last_price_update": datetime.utcnow()
                    }, commit=False)
                    continue

                # c2. Check Miscellaneous Items (Update Logic)
                if url_str in existing_misc:
                    misc_item = existing_misc[url_str]
                    new_price = offer.get('price', 0.0)
                    if new_price > 0 and abs(misc_item.price - new_price) > 0.01:
                        misc_item.price = new_price
                        misc_item.added_at = datetime.utcnow()
                        price_updates_count += 1
                    else:
                        unchanged_count += 1
                    continue

                # d2. Relevance check for MOTU (Brand exclusion & keyword check)
                if url_str not in existing_offers and url_str not in existing_misc and url_str not in existing_pending_urls:
                    from src.core.vintage_utils import validate_motu_relevance
                    from src.domain.models import OfferHistoryModel
                    is_relevant, reason = validate_motu_relevance(offer.get('product_name', ''))
                    if not is_relevant:
                        # Auto-blacklist the item to prevent future scraping attempts
                        bl = BlackcludedItemModel(
                            url=url_str,
                            scraped_name=offer.get('product_name', 'Desconocido'),
                            reason=f"Descarte automático: {reason}",
                            source_type=offer.get('source_type', 'Retail')
                        )
                        db.add(bl)
                        # Add history log for auditability
                        history = OfferHistoryModel(
                            offer_url=url_str,
                            product_name=offer.get('product_name', 'Desconocido'),
                            shop_name=offer.get('shop_name', 'Unknown'),
                            price=offer.get('price', 0.0),
                            action_type="AUTO_DISCARDED_RELEVANCE",
                            details=json.dumps({"reason": reason})
                        )
                        db.add(history)
                        blocked_urls.add(url_str)
                        discarded_count += 1
                        logger.info(f"🚫 Auto-Discarded: {offer.get('product_name')} ({reason})")
                        continue

                # d. Check Pending (Update price if changed)
                if url_str in existing_pending_urls:
                    pending_item = existing_pending[url_str]
                    new_price = offer.get('price', 0.0)
                    
                    if new_price > 0 and abs(pending_item.price - new_price) > 0.01:
                        # logger.info(f"📈 Purgatory Price Update: {pending_item.scraped_name} ({pending_item.price} -> {new_price})")
                        pending_item.price = new_price
                        pending_item.found_at = datetime.utcnow()
                        # Update source_type if it was missing or different
                        if "source_type" in offer:
                            pending_item.source_type = offer["source_type"]
                        if "sale_type" in offer:
                            pending_item.sale_type = offer["sale_type"]
                        if "expiry_at" in offer:
                            pending_item.expiry_at = offer["expiry_at"]
                        if "bids_count" in offer:
                            pending_item.bids_count = offer["bids_count"]
                        if "time_left_raw" in offer:
                            pending_item.time_left_raw = offer["time_left_raw"]
                        
                        # Phase 41: Market Intelligence updates
                        if "sold_at" in offer:
                            pending_item.sold_at = offer["sold_at"]
                        if "is_sold" in offer:
                            pending_item.is_sold = offer["is_sold"]
                        if "original_listing_date" in offer:
                            pending_item.original_listing_date = offer["original_listing_date"]
                        
                        pending_item.last_price_update = datetime.utcnow()
                        price_updates_count += 1
                        # Si quisiéramos alertas aquí (antes de vincular), se podrían añadir.
                    else:
                        unchanged_count += 1
                    continue

                # --- IF HERE, IT IS A NEW CANDIDATE ---
                best_match_product = None
                best_match_score = 0.0
                best_match_reason = "Bypassed (Purgatory-First Policy)"
                
                # REFACTOR: Purgatory-First Policy. Manual review is more reliable for new items.
                # The following SmartMatch logic is disabled to prevent false positives (e.g. Dragstor -> Despara).
                # To re-enable, uncomment the matching loop below.
                
                # for p in all_products:
                #     is_match, score, reason = matcher.match(
                #         p.name, 
                #         offer.get('product_name'), 
                #         url_str,
                #         db_ean=p.ean,
                #         scraped_ean=offer.get('ean')
                #     )
                #     
                #     if is_match and score > best_match_score:
                #         best_match_score = score
                #         best_match_product = p
                #         best_match_reason = reason
                #         if score >= 0.99: break
                
                # SmartMatch Logic (Will always be false now for new items)
                if best_match_product and best_match_score >= 0.75:
                    # --- PHASE 17: CROSS-VALIDATION SENTINEL ---
                    is_blocked, status, flags = sentinel.validate_cross_reference(
                        best_match_product, 
                        offer.get('price'), 
                        offer.get('image_url')
                    )
                    
                    if is_blocked:
                        logger.warning(f"⚠️ ANOMALY DETECTED: '{offer.get('product_name')}' -> '{best_match_product.name}'. Blocking and moving to Purgatory.")
                        # Auditor Event
                        auditor.log_offer_event(
                            "BLOCKED_BY_SENTINEL", 
                            {"url": url_str, "name": best_match_product.name, "shop_name": offer.get('shop_name'), "price": offer.get('price')}, 
                            details=f"Anomalies: {', '.join(flags)}"
                        )
                        
                        # --- PHASE 18: DEAL SCORER (OPPORTUNITY SCORE) ---
                        landed_price = LogisticsService.optimized_get_landing_price(offer.get('price'), offer.get('shop_name'), user_location, rules_map)
                        is_wish = any(ci.owner_id == 2 and not ci.acquired for ci in best_match_product.collection_items)
                        opp_score = DealScorer.calculate_score(best_match_product, landed_price, is_wish)

                        # Move to Purgatory (Already matched but blocked)
                        pending_data = {
                            "scraped_name": offer.get('product_name'),
                            "price": offer.get('price'),
                            "currency": offer.get('currency', 'EUR'),
                            "url": url_str,
                            "shop_name": offer.get('shop_name'),
                            "image_url": offer.get('image_url'),
                            "ean": offer.get('ean'),
                            "source_type": offer.get('source_type', 'Retail'),
                            "receipt_id": offer.get('receipt_id'),
                            "validation_status": status,
                            "is_blocked": True,
                            "anomaly_flags": json.dumps(flags),
                            "opportunity_score": opp_score,
                            "sale_type": offer.get('sale_type', 'Retail'),
                            "expiry_at": offer.get('expiry_at'),
                            "bids_count": offer.get('bids_count', 0),
                            "time_left_raw": offer.get('time_left_raw'),
                            "found_at": datetime.utcnow()
                        }
                        
                        # Atomic Upsert to Purgatory (Reusing same logic as below)
                        try:
                            with db.begin_nested():
                                if 'postgresql' in db.bind.dialect.name.lower():
                                    from sqlalchemy.dialects.postgresql import insert as pg_insert
                                    stmt = pg_insert(PendingMatchModel).values(pending_data)
                                    stmt = stmt.on_conflict_do_update(
                                        index_elements=['url'],
                                        set_={
                                            "price": stmt.excluded.price,
                                            "is_blocked": stmt.excluded.is_blocked,
                                            "anomaly_flags": stmt.excluded.anomaly_flags,
                                            "validation_status": stmt.excluded.validation_status
                                        }
                                    )
                                    db.execute(stmt)
                                else:
                                    existing = db.query(PendingMatchModel).filter(PendingMatchModel.url == url_str).first()
                                    if existing:
                                        existing.price = pending_data["price"]
                                        existing.is_blocked = True
                                        existing.anomaly_flags = json.dumps(flags)
                                        existing.validation_status = status
                                    else:
                                        db.add(PendingMatchModel(**pending_data))
                            new_items_count += 1
                        except Exception as e:
                            logger.error(f"Failed to move blocked item to Purgatory: {e}")
                            
                        continue # Skip adding as active offer
                    
                    # --- PHASE 18: DEAL SCORER ---
                    landed_price = LogisticsService.optimized_get_landing_price(offer.get('price'), offer.get('shop_name'), user_location, rules_map)
                    is_wish = any(ci.owner_id == 2 and not ci.acquired for ci in best_match_product.collection_items)
                    opp_score = DealScorer.calculate_score(best_match_product, landed_price, is_wish)

                    # Normal SmartMatch flow if no anomalies
                    self._log(f"✅ [SmartMatch] Auto-vinculado: '{offer.get('product_name')}' ➔ '{best_match_product.name}' ({offer.get('price')}€)")
                    logger.info(f"✅ SmartMatch: '{offer.get('product_name')}' -> '{best_match_product.name}' (Match: {best_match_score:.2f} | Reason: {best_match_reason} | Deal: {opp_score})")
                    repo.add_offer(best_match_product, {
                        "shop_name": offer.get('shop_name'),
                        "price": offer.get('price'),
                        "currency": offer.get('currency'), 
                        "url": url_str,
                        "is_available": offer.get('is_available') if offer.get('is_available') is not None else True,
                        "source_type": offer.get('source_type', 'Retail'),
                        "opportunity_score": opp_score
                    }, commit=False)
                    
                    # Audit new link
                    auditor.log_offer_event(
                        "SMART_MATCH", 
                        {"url": url_str, "name": best_match_product.name, "shop_name": offer.get('shop_name'), "price": offer.get('price')}, 
                        details=f"Match confidence: {best_match_score:.2f}"
                    )

                    # --- PHASE 8.5 & 18: NOTIFICATIONS ---
                    if DealScorer.is_mandatory_buy(best_match_product, landed_price, opp_score):
                        asyncio.create_task(telegram_service.send_mandatory_buy_alert(
                            product_name=best_match_product.name,
                            price=offer.get('price'),
                            landed_price=landed_price,
                            shop_name=offer.get('shop_name'),
                            url=url_str
                        ))
                    elif best_match_score >= 0.90:
                        asyncio.create_task(telegram_service.send_deal_alert(
                            product_name=best_match_product.name,
                            price=offer.get('price'),
                            shop_name=offer.get('shop_name'),
                            url=url_str
                        ))
                    
                    # Alertas multi-usuario (Wishlist / Price Alerts) para items auto-vinculados
                    check_and_send_multiuser_alerts(
                        db,
                        scraped_name=best_match_product.name,
                        price=offer.get('price'),
                        shop_name=offer.get('shop_name'),
                        url=url_str,
                        is_vintage=best_match_product.is_vintage
                    )
                else:
                    # Regla Vintage: Si es vintage (muñeco de los 80 o contiene 'vintage'), marcamos el flag para ir al Purgatorio
                    from src.core.vintage_utils import check_is_vintage
                    product_name = offer.get('product_name')
                    is_v = check_is_vintage(product_name) or bool(offer.get('is_vintage'))
                    
                    # Para evitar errores y mantener el control absoluto del usuario (David), 
                    # NINGÚN artículo vintage se asocia o crea de forma automática en el catálogo de Eternia.
                    # En su lugar, todos se envían al Purgatorio con el flag `is_vintage = is_v` para que el usuario 
                    # los pueda emparejar y vincular manualmente con total precisión.

                    # To Purgatory
                    pending_data = {
                        "scraped_name": offer.get('product_name'),
                        "price": offer.get('price'),
                        "currency": offer.get('currency', 'EUR'),
                        "url": url_str,
                        "shop_name": offer.get('shop_name'),
                        "image_url": offer.get('image_url'),
                        "ean": offer.get('ean'),
                        "source_type": offer.get('source_type', 'Retail'),
                        "receipt_id": offer.get('receipt_id'),
                        "time_left_raw": offer.get('time_left_raw'),
                        "first_seen_at": offer.get('first_seen_at') or datetime.utcnow(),
                        "sold_at": offer.get('sold_at'),
                        "is_sold": offer.get('is_sold', False),
                        "original_listing_date": offer.get('original_listing_date'),
                        "last_price_update": datetime.utcnow(),
                        "found_at": datetime.utcnow(),
                        "is_vintage": is_v
                    }
                    
                    # --- REFACTOR 7.3: DEFINITIVE ATOMIC UPSERT ---
                    try:
                        # Use a nested transaction (SAVEPOINT) to isolate this operation
                        with db.begin_nested():
                            if 'postgresql' in db.bind.dialect.name.lower():
                                from sqlalchemy.dialects.postgresql import insert as pg_insert
                                
                                # Use ON CONFLICT DO UPDATE to handle latent duplicates and price updates atomically
                                stmt = pg_insert(PendingMatchModel).values(pending_data)
                                stmt = stmt.on_conflict_do_update(
                                    index_elements=['url'],
                                    set_={
                                        "price": stmt.excluded.price,
                                        "found_at": stmt.excluded.found_at,
                                        "scraped_name": stmt.excluded.scraped_name,
                                        "last_price_update": stmt.excluded.last_price_update,
                                        "is_sold": stmt.excluded.is_sold,
                                        "sold_at": stmt.excluded.sold_at
                                    }
                                )
                                db.execute(stmt)
                            else:
                                # SQLite / Fallback
                                existing = db.query(PendingMatchModel).filter(PendingMatchModel.url == url_str).first()
                                if existing:
                                    existing.price = pending_data["price"]
                                    existing.found_at = pending_data["found_at"]
                                    existing.last_price_update = pending_data["last_price_update"]
                                    existing.is_sold = pending_data["is_sold"]
                                    existing.sold_at = pending_data["sold_at"]
                                else:
                                    pending = PendingMatchModel(**pending_data)
                                    db.add(pending)
                        # No db.commit() here! We commit the whole batch at the end.
                        new_items_count += 1
                        
                        # Disparar alertas para nuevos candidatos en Purgatorio
                        if url_str not in existing_pending_urls:
                            if is_v:
                                asyncio.create_task(telegram_service.send_new_purgatory_vintage_alert(
                                    scraped_name=pending_data["scraped_name"],
                                    price=pending_data["price"],
                                    shop_name=pending_data["shop_name"],
                                    url=url_str
                                ))
                            
                            check_and_send_multiuser_alerts(
                                db,
                                scraped_name=pending_data["scraped_name"],
                                price=pending_data["price"],
                                shop_name=pending_data["shop_name"],
                                url=url_str,
                                is_vintage=is_v
                            )
                        
                    except Exception as e:
                        # db.begin_nested() context manager handles rollback of the savepoint automatically
                        if "unique" in str(e).lower():
                            logger.debug(f"⏳ Duplicate URL skipped (SaveMode): {url_str}")
                        else:
                            logger.warning(f"⚠️ Item insertion error ({url_str}): {e}")
            
            # Limpieza global proactiva del purgatorio al finalizar la actualización
            clean_purgatory_globally(db)
            db.commit()
            
            # --- RESUMEN DE MÉTRICAS COMPLETO (COMPATIBLE CON PARSER FRONTEND) ---
            stats_msg = f"📊 [Resumen] Nuevas en Purgatorio: {new_items_count} | Precios actualizados: {price_updates_count} | Sin cambios: {unchanged_count} | Descartadas: {discarded_count}"
            self._log(stats_msg)
            self._log(f"⚡ [Fin] Proceso de persistencia completado. {new_items_count} nuevas ofertas enviadas al Purgatorio.")
            logger.success(f"⚡ Batch Complete: {stats_msg}")

            # --- PHASE 44: AVAILABILITY SYNC ---
            if shop_names:
                incoming_urls = [str(o.get('url', '')) for o in offers if o.get('url')]
                self.sync_availability(incoming_urls, shop_names)
            
            return new_items_count

        except Exception as e:
            error_msg = f"❌ Pipeline Critical Error: {e}"
            self._log(error_msg)
            logger.error(error_msg)
            db.rollback()
            return 0
        finally:
            db.close()
