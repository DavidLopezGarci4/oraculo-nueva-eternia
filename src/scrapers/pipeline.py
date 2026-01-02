import asyncio
from typing import List
from loguru import logger
from src.scrapers.base import BaseSpider, ScrapedOffer
from src.domain.schemas import Product
from src.infrastructure.repositories.product import ProductRepository
from sqlalchemy.orm import Session
from src.infrastructure.database import SessionLocal

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
        from src.scrapers.adapter import adapter
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
        """
        if not offers:
            logger.warning("🛡️ Circuit Breaker: No offers found to process. Skipping DB update for this batch.")
            return

        # 1. Save Raw Snapshot (Black Box)
        try:
            from src.core.backup_manager import BackupManager
            bm = BackupManager()
            shop_name = offers[0].get('shop_name', 'unknown') if offers else "unknown"
            bm.save_raw_snapshot(shop_name, offers)
        except Exception as e:
            logger.error(f"⚠️ Failed to save safety snapshot: {e}")

        db: Session = SessionLocal()
        from src.core.matching import SmartMatcher
        
        matcher = SmartMatcher()
        repo = ProductRepository(db)
        
        try:
            # Pre-fetch all product names/IDs
            all_products = repo.get_all(limit=5000)
            
            for offer in offers:
                best_match_product = None
                best_match_score = 0.0
                
                # Check 1: Does this offer satisfy "Already Linked" logic?
                url_str = str(offer.get('url', ''))
                existing_offer = repo.get_offer_by_url(url_str)
                
                if existing_offer:
                    logger.info(f"🔗 Known Link: '{offer.get('product_name')}' -> '{existing_offer.product.name}' (Price Update)")
                    saved_o, _ = repo.add_offer(existing_offer.product, {
                        "shop_name": offer.get('shop_name'),
                        "price": offer.get('price'),
                        "currency": offer.get('currency'), 
                        "url": url_str,
                        "is_available": offer.get('is_available')
                    }, commit=False)
                    
                    from src.core.notifier import NotifierService
                    NotifierService().check_price_alerts_sync(db, existing_offer.product, saved_o)
                    continue

                # Iterate all DB products to find best
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
                        
                        if score >= 0.99:
                             break
                
                if best_match_product and best_match_score >= 0.7:
                    logger.info(f"✅ SmartMatch: '{offer.get('product_name')}' -> '{best_match_product.name}' (Score: {best_match_score:.2f})")
                    
                    saved_offer, alert_discount = repo.add_offer(best_match_product, {
                        "shop_name": offer.get('shop_name'),
                        "price": offer.get('price'),
                        "currency": offer.get('currency'), 
                        "url": url_str,
                        "is_available": offer.get('is_available')
                    }, commit=False)
                    
                    if alert_discount:
                        from src.core.notifier import NotifierService
                        notifier = NotifierService()
                        notifier.send_deal_alert_sync(best_match_product, saved_offer, alert_discount)
                    
                    from src.core.notifier import NotifierService
                    NotifierService().check_price_alerts_sync(db, best_match_product, saved_offer)
                else:
                    logger.info(f"⏳ No Match Found: '{offer.get('product_name')}' (Top Score: {best_match_score:.2f}) -> Routing to Purgatory")
                    
                    from src.domain.models import BlackcludedItemModel
                    is_blacklisted = db.query(BlackcludedItemModel).filter(BlackcludedItemModel.url == url_str).first()
                    if is_blacklisted:
                        logger.warning(f"🚫 Ignored (Blacklist): {offer.get('product_name')}")
                        continue
                        
                    from src.domain.models import PendingMatchModel
                    try:
                        existing = db.query(PendingMatchModel).filter(PendingMatchModel.url == url_str).first()
                    except Exception as e:
                        logger.warning(f"⚠️ Query for existing Pending item failed: {e}")
                        db.rollback()
                        existing = None
                    if not existing:
                        all_data = {
                            "scraped_name": offer.get('product_name'),
                            "price": offer.get('price'),
                            "currency": offer.get('currency', 'EUR'),
                            "url": url_str,
                            "shop_name": offer.get('shop_name'),
                            "image_url": offer.get('image_url'),
                            "ean": offer.get('ean'),
                            "receipt_id": offer.get('receipt_id') # --- 3OX Audit ---
                        }
                        
                        from sqlalchemy import inspect
                        try:
                            mapper = inspect(PendingMatchModel)
                            allowed_keys = {c.key for c in mapper.attrs}
                            pending_data = {k: v for k, v in all_data.items() if k in allowed_keys}
                        except:
                            pending_data = {k: v for k, v in all_data.items() if hasattr(PendingMatchModel, k)}

                        try:
                            pending = PendingMatchModel(**pending_data)
                            db.add(pending)
                        except TypeError as e:
                            logger.warning(f"⚠️ Model instantiation failed: {e}. Retrying with safe subset.")
                            db.rollback()
                            safe_data = {k: v for k, v in pending_data.items() if k not in ['ean', 'image_url']}
                            pending = PendingMatchModel(**safe_data)
                            db.add(pending)
                        except Exception as e:
                            logger.error(f"❌ Critical DB failure in Purgatory routing: {e}")
                            db.rollback()
                        
                        try:
                            from src.domain.models import OfferHistoryModel
                            history = OfferHistoryModel(
                                offer_url=url_str,
                                product_name=offer.get('product_name'),
                                shop_name=offer.get('shop_name'),
                                price=offer.get('price'),
                                action_type="PURGATORY",
                                details=f"Match score too low ({best_match_score:.2f}). Moved to Purgatory."
                            )
                            db.add(history)
                        except: pass
            
            db.commit()
            logger.info("⚡ Batch Commit Complete: All offers persisted in a single spark.")

        finally:
            db.close()
