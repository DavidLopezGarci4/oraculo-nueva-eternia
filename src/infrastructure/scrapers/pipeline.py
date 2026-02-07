import asyncio
import json
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

class ScrapingPipeline:
    def __init__(self, scrapers: List[BaseScraper]):
        self.scrapers = scrapers

    async def run_product_search(self, product_name: str) -> List[dict]:
        """
        Runs all spiders in parallel and transforms results into 3OX Contract format.
        """
        logger.info(f"Pipeline: Searching for '{product_name}' across {len(self.scrapers)} scrapers.")
        
        tasks = [scraper.search(product_name) for scraper in self.scrapers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_legacy_offers = []
        for scraper, res in zip(self.scrapers, results):
            if isinstance(res, Exception):
                logger.error(f"Scraper {scraper.shop_name} failed for '{product_name}': {res}")
            else:
                logger.info(f"Scraper {scraper.shop_name} found {len(res)} offers.")
                # DNA Segregation (Phase 14 & 16): Inject source type based on scraper type
                source = "Peer-to-Peer" if getattr(scraper, 'is_auction_source', False) else "Retail"
                for offer in res:
                    if isinstance(offer, ScrapedOffer):
                        offer.source_type = source
                all_legacy_offers.extend(res)
        
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
        from src.domain.models import PendingMatchModel, BlackcludedItemModel, OfferModel, LogisticRuleModel
        
        auditor = AuditorService(repo)
        sentinel = SentinelService(repo)
        
        try:
            # --- PHASE 7.3: BULK PRE-FETCHING ---
            logger.info("🛡️ Pipeline: Initiating Bulk Pre-filtering...")
            
            # A. Extract URLs from incoming batch
            incoming_urls = [str(o.get('url', '')) for o in offers if o.get('url')]
            
            if not incoming_urls:
                logger.warning("No valid URLs in batch. Aborting.")
                return

            # B. Bulk Check against Database (3 Queries instead of N)
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
            
            # Pre-fetch all products for matching (only if needed)
            all_products = repo.get_all(limit=5000)

            # --- PHASE 34: LOGISTICS PRE-CACHE (Eliminate N+1) ---
            rules = db.query(LogisticRuleModel).all()
            rules_map = {f"{r.shop_name}_{r.country_code}": r for r in rules}
            user_location = "ES" # Default

            logger.info(f"📊 Stats: {len(offers)} incoming | {len(existing_offers)} active links | {len(existing_pending_urls)} in Purgatory | {len(blocked_urls)} blocked")

            processed_urls_in_batch = set()
            new_items_count = 0
            
            for offer in offers:
                url_str = str(offer.get('url', ''))
                
                # a. Dedup within batch
                if url_str in processed_urls_in_batch:
                    continue
                processed_urls_in_batch.add(url_str)
                
                # b. Check Blacklist
                if url_str in blocked_urls:
                    # logger.debug(f"🛑 Blocked: {offer.get('product_name')}")
                    continue
                    
                # c. Check Active Links (Update Logic)
                if url_str in existing_offers:
                    existing_offer = existing_offers[url_str]
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
                        # Si quisiéramos alertas aquí (antes de vincular), se podrían añadir.
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
                            score=opp_score,
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
                else:
                    # To Purgatory
                    # logger.info(f"🆕 To Purgatory: '{offer.get('product_name')}'")
                    
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
                        "found_at": datetime.utcnow()
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
                        
                    except Exception as e:
                        # db.begin_nested() context manager handles rollback of the savepoint automatically
                        if "unique" in str(e).lower():
                            logger.debug(f"⏳ Duplicate URL skipped (SaveMode): {url_str}")
                        else:
                            logger.warning(f"⚠️ Item insertion error ({url_str}): {e}")
            
            db.commit()
            logger.success(f"⚡ Batch Complete: {new_items_count} new items added to Purgatory (Atomic Safe Mode).")

            # --- PHASE 44: AVAILABILITY SYNC ---
            if shop_names:
                incoming_urls = [str(o.get('url', '')) for o in offers if o.get('url')]
                self.sync_availability(incoming_urls, shop_names)
            
            return new_items_count

        except Exception as e:
            logger.error(f"❌ Pipeline Critical Error: {e}")
            db.rollback()
        finally:
            db.close()
