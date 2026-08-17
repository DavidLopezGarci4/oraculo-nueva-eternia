import json
import pytest
from src.infrastructure.database_cloud import SessionCloud
from src.domain.models import (
    PendingMatchModel,
    OfferHistoryModel,
    BlackcludedItemModel,
    OfferModel,
    ProductModel,
    VintageMiscellaneousModel,
    VintageProductModel,
    ProductAliasModel,
)
from src.infrastructure.scrapers.pipeline import clean_purgatory_globally
from src.interfaces.api.routers.dashboard import revert_action
import asyncio

@pytest.mark.asyncio
async def test_revert_discarded_manual_returns_to_purgatory_and_survives_cleanup():
    test_url = "https://www.test-shop.com/test-discard-item-12345"
    
    with SessionCloud() as db:
        # Cleanup any previous test artifacts
        db.query(PendingMatchModel).filter(PendingMatchModel.url == test_url).delete()
        db.query(BlackcludedItemModel).filter(BlackcludedItemModel.url == test_url).delete()
        db.query(OfferHistoryModel).filter(OfferHistoryModel.offer_url == test_url).delete()
        
        # 1. Simulate a manual discard in Purgatory
        bl = BlackcludedItemModel(
            url=test_url,
            scraped_name="He-Man Test Figure",
            reason="manual_discard",
            source_type="Retail"
        )
        db.add(bl)
        
        history = OfferHistoryModel(
            offer_url=test_url,
            product_name="He-Man Test Figure",
            shop_name="TestShop",
            price=25.50,
            action_type="DISCARDED_MANUAL",
            details=json.dumps({
                "reason": "manual_discard",
                "original_item": {
                    "scraped_name": "He-Man Test Figure Scraped",
                    "ean": "1234567890",
                    "price": 25.50,
                    "currency": "EUR",
                    "url": test_url,
                    "shop_name": "TestShop",
                    "image_url": "https://test.com/img.jpg",
                    "condition": "MOC",
                    "grading": 9.0,
                    "is_vintage": False,
                    "source_type": "Retail",
                    "receipt_id": "REC-TEST-1"
                }
            })
        )
        db.add(history)
        db.commit()
        
        history_id = history.id

    # 2. Call revert_action
    result = await revert_action({"history_id": history_id})
    assert result["status"] == "success"

    # 3. Check DB state
    with SessionCloud() as db:
        # Check blacklist is clean
        bl_after = db.query(BlackcludedItemModel).filter(BlackcludedItemModel.url == test_url).first()
        assert bl_after is None, "Blacklist item should be deleted on revert"
        
        # Check PendingMatchModel has the item with full rich metadata
        purg_item = db.query(PendingMatchModel).filter(PendingMatchModel.url == test_url).first()
        assert purg_item is not None, "Pending item should be created in Purgatorio"
        assert purg_item.scraped_name == "He-Man Test Figure Scraped"
        assert purg_item.image_url == "https://test.com/img.jpg"
        assert purg_item.condition == "MOC"
        assert purg_item.grading == 9.0
        assert purg_item.receipt_id == "REC-TEST-1"
        
        # 4. RUN GLOBAL CLEANUP - verify it does NOT delete it
        clean_purgatory_globally(db)
        db.commit()
        
        purg_item_after_clean = db.query(PendingMatchModel).filter(PendingMatchModel.url == test_url).first()
        assert purg_item_after_clean is not None, "Item in Purgatorio must NOT be deleted by clean_purgatory_globally after revert"
        
        # Cleanup
        db.query(PendingMatchModel).filter(PendingMatchModel.url == test_url).delete()
        db.commit()


@pytest.mark.asyncio
async def test_revert_linked_vintage_returns_to_purgatory_and_survives_cleanup():
    test_url = "https://www.test-shop.com/test-vintage-item-99999"
    
    with SessionCloud() as db:
        # Create a test product
        prod = ProductModel(
            name="Vintage Test Product",
            category="Masters of the Universe",
            sub_category="Vintage",
            is_vintage=True,
            figure_id="TEST-VINT-1"
        )
        db.add(prod)
        db.flush()
        prod_id = prod.id

        offer = OfferModel(
            product_id=prod_id,
            shop_name="TestShop",
            price=80.0,
            currency="EUR",
            url=test_url,
            is_available=True,
            is_vintage=True,
            condition="Loose",
            grading=8.0,
            image_url="https://test.com/vintage.jpg"
        )
        db.add(offer)
        
        history = OfferHistoryModel(
            offer_url=test_url,
            product_name=prod.name,
            shop_name="TestShop",
            price=80.0,
            action_type="LINKED_VINTAGE",
            details=json.dumps({
                "product_id": prod_id,
                "original_item": {
                    "scraped_name": "Vintage Skeletor Taiwan 1982",
                    "price": 80.0,
                    "currency": "EUR",
                    "url": test_url,
                    "shop_name": "TestShop",
                    "image_url": "https://test.com/vintage.jpg",
                    "condition": "Loose",
                    "grading": 8.0,
                    "is_vintage": True
                }
            })
        )
        db.add(history)
        
        alias = ProductAliasModel(product_id=prod_id, source_url=test_url, confirmed=True)
        db.add(alias)
        db.commit()
        history_id = history.id

    # Call revert
    result = await revert_action({"history_id": history_id})
    assert result["status"] == "success"

    with SessionCloud() as db:
        # Check Offer is deleted
        offer_after = db.query(OfferModel).filter(OfferModel.url == test_url).first()
        assert offer_after is None, "Offer must be deleted"
        
        # Check Alias is deleted
        alias_after = db.query(ProductAliasModel).filter(ProductAliasModel.source_url == test_url).first()
        assert alias_after is None, "Alias must be deleted"
        
        # Check Purgatory item exists
        purg_item = db.query(PendingMatchModel).filter(PendingMatchModel.url == test_url).first()
        assert purg_item is not None
        assert purg_item.scraped_name == "Vintage Skeletor Taiwan 1982"
        assert purg_item.is_vintage is True
        
        # Run clean_purgatory_globally
        clean_purgatory_globally(db)
        db.commit()
        
        purg_item_after_clean = db.query(PendingMatchModel).filter(PendingMatchModel.url == test_url).first()
        assert purg_item_after_clean is not None, "Pending match must survive global cleanup"
        
        # Cleanup test entities
        db.query(PendingMatchModel).filter(PendingMatchModel.url == test_url).delete()
        db.query(ProductModel).filter(ProductModel.id == prod_id).delete()
        db.commit()
