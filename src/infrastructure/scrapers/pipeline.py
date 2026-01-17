import asyncio
from typing import List
from datetime import datetime
from loguru import logger
from src.infrastructure.scrapers.base import BaseSpider, ScrapedOffer
from src.domain.schemas import ProductSchema
from src.infrastructure.repositories.product import ProductRepository
from sqlalchemy.orm import Session
from src.infrastructure.database_cloud import SessionCloud, init_cloud_db
from src.infrastructure.services.telegram_service import telegram_service

class ScrapingPipeline:
    def __init__(self, spiders: List[BaseSpider]):
        self.spiders = spiders

    async def run_product_search(self, product_name: str) -> List[dict]:
        """
        Runs all spiders in parallel and transforms results into 3OX Contract format.
        """
        logger.info(f"Pipeline: Searching for '{product_name}' across {len(self.spiders)} spiders.")
        
        tasks = [spider.search(product_name) for spider in self.spiders]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_legacy_offers = []
        for spider, res in zip(self.spiders, results):
            if isinstance(res, Exception):
                logger.error(f"Spider {spider.shop_name} failed for '{product_name}': {res}")
            else:
                logger.info(f"Spider {spider.shop_name} found {len(res)} offers.")
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

    def update_database(self, offers: List[dict]):
        """
        Persists found offers to the database using SmartMatcher.
        Includes Phase 18: Búnker & Circuit Breaker.
        REFACTOR 7.3: Bulk Pre-filtering Strategy (No more N+1 / Duplicate Errors).
        """
        if not offers:
            logger.warning("🛡️ Circuit Breaker: No offers found to process. Skipping DB update for this batch.")
            return

        # Ensure offers are dicts (Scrapers now return Pydantic objects)
        if hasattr(offers[0], 'model_dump'):
            offers = [o.model_dump() for o in offers]

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
        from src.domain.models import PendingMatchModel, BlackcludedItemModel, OfferModel
        
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
                    # logger.info(f"🔗 Update: {offer.get('product_name')}")
                    
                    # Update without committing yet
                    repo.add_offer(existing_offer.product, {
                        "shop_name": offer.get('shop_name'),
                        "price": offer.get('price'),
                        "currency": offer.get('currency'), 
                        "url": url_str,
                        "is_available": offer.get('is_available')
                    }, commit=False)
                    
                    # Sentinel/Audit logic omitted for speed in updates or can be added selectively
                    continue

                # d. Check Pending (Update price if changed)
                if url_str in existing_pending_urls:
                    pending_item = existing_pending[url_str]
                    new_price = offer.get('price', 0.0)
                    
                    if new_price > 0 and abs(pending_item.price - new_price) > 0.01:
                        # logger.info(f"📈 Purgatory Price Update: {pending_item.scraped_name} ({pending_item.price} -> {new_price})")
                        pending_item.price = new_price
                        pending_item.found_at = datetime.utcnow()
                        # Si quisiéramos alertas aquí (antes de vincular), se podrían añadir.
                    continue

                # --- IF HERE, IT IS A NEW CANDIDATE ---
                best_match_product = None
                best_match_score = 0.0
                
                # Iterate all DB products to find best match
                for p in all_products:
                    is_match, score, reason = matcher.match(
                        p.name, 
                        offer.get('product_name'), 
                        url_str,
                        db_ean=p.ean,
                        scraped_ean=offer.get('ean')
                    )
                    
                    if is_match and score > best_match_score:
                        best_match_score = score
                        best_match_product = p
                        if score >= 0.99: break
                
                # SmartMatch Logic
                if best_match_product and best_match_score >= 0.75:
                    logger.info(f"✅ SmartMatch (75%+): '{offer.get('product_name')}' -> '{best_match_product.name}'")
                    repo.add_offer(best_match_product, {
                        "shop_name": offer.get('shop_name'),
                        "price": offer.get('price'),
                        "currency": offer.get('currency'), 
                        "url": url_str,
                        "is_available": offer.get('is_available')
                    }, commit=False)
                    
                    # Audit new link
                    auditor.log_offer_event(
                        "SMART_MATCH", 
                        {"url": url_str, "name": best_match_product.name, "shop_name": offer.get('shop_name'), "price": offer.get('price')}, 
                        details=f"Match confidence: {best_match_score:.2f}"
                    )

                    # --- PHASE 8.5: THE EYE OF SAURON (TELEGRAM ALERT) ---
                    # Only alert for high-confidence matches to avoid noise
                    if best_match_score >= 0.90:
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
                        "receipt_id": offer.get('receipt_id'),
                        "found_at": datetime.utcnow()
                    }
                    
                    # --- REFACTOR 7.3: GRANULAR ATOMIC INSERT ---
                    try:
                        # Use nested transaction to prevent full rollback on error for this specific item
                        db.begin_nested()
                        
                        if 'postgresql' in db.bind.dialect.name.lower():
                            from sqlalchemy.dialects.postgresql import insert as pg_insert
                            stmt = pg_insert(PendingMatchModel).values(pending_data).on_conflict_do_nothing(index_elements=['url'])
                            db.execute(stmt)
                        else:
                            # Standard add for SQLite
                            if not db.query(PendingMatchModel).filter(PendingMatchModel.url == url_str).first():
                                pending = PendingMatchModel(**pending_data)
                                db.add(pending)
                        
                        db.commit() # Savepoint commit
                        new_items_count += 1
                    except Exception as e:
                        db.rollback() # Rollback to savepoint only
                        if "unique" in str(e).lower():
                            logger.debug(f"⏳ Duplicate URL skipped (SafeMode): {url_str}")
                        else:
                            logger.warning(f"⚠️ Item insertion error: {e}")
            
            db.commit()
            logger.success(f"⚡ Batch Complete: {new_items_count} new items added to Purgatory (Atomic Safe Mode).")

        except Exception as e:
            logger.error(f"❌ Pipeline Critical Error: {e}")
            db.rollback()
        finally:
            db.close()
