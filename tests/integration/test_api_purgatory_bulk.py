import pytest
import json
from datetime import datetime, timezone
from src.domain.models import PendingMatchModel, ProductModel, OfferModel, UserModel
from tests.conftest import ADMIN_HEADERS

def test_api_purgatory_bulk_match(client):
    from src.interfaces.api.routers.purgatory import SessionCloud
    
    # 1. Prepare database records
    with SessionCloud() as db:
        # Ensure a test user with ID 1 exists so logistics / scoring can run
        user = db.query(UserModel).filter(UserModel.id == 1).first()
        if not user:
            user = UserModel(id=1, username="admin", email="admin@test.com", hashed_password="hash", location="ES")
            db.add(user)
            db.commit()

        # Create two pending matches (purgatory relics)
        p1 = PendingMatchModel(
            id=101,
            scraped_name="Skeletor Origins Figure",
            price=24.99,
            currency="EUR",
            url="https://example.com/skeletor",
            shop_name="ToyStore",
            source_type="Retail",
            found_at=datetime.now(timezone.utc)
        )
        p2 = PendingMatchModel(
            id=102,
            scraped_name="He-Man Origins Figure",
            price=29.99,
            currency="EUR",
            url="https://example.com/heman",
            shop_name="ToyStore",
            source_type="Retail",
            found_at=datetime.now(timezone.utc)
        )
        db.add(p1)
        db.add(p2)

        # Create two products in the catalog
        prod1 = ProductModel(
            id=1001,
            name="Skeletor",
            category="Masters of the Universe",
            sub_category="Origins",
            figure_id="SKE01",
            is_vintage=False
        )
        prod2 = ProductModel(
            id=1002,
            name="He-Man",
            category="Masters of the Universe",
            sub_category="Origins",
            figure_id="HEM01",
            is_vintage=False
        )
        db.add(prod1)
        db.add(prod2)
        db.commit()

    # 2. Call the bulk match endpoint
    payload = {
        "matches": [
            {"pending_id": 101, "product_id": 1001},
            {"pending_id": 102, "product_id": 1002}
        ]
    }
    resp = client.post("/api/purgatory/match/bulk", json=payload, headers=ADMIN_HEADERS)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "success"
    assert "2 vinculaciones programadas" in data["message"]

    # 3. Verify that background task has executed and elements are synced
    with SessionCloud() as db:
        # The pending match models should have been deleted from purgatory
        remaining_p1 = db.query(PendingMatchModel).filter(PendingMatchModel.id == 101).first()
        remaining_p2 = db.query(PendingMatchModel).filter(PendingMatchModel.id == 102).first()
        assert remaining_p1 is None
        assert remaining_p2 is None

        # Offers should be created for each product
        o1 = db.query(OfferModel).filter(OfferModel.product_id == 1001).first()
        o2 = db.query(OfferModel).filter(OfferModel.product_id == 1002).first()
        assert o1 is not None
        assert o2 is not None
        assert o1.price == 24.99
        assert o2.price == 29.99
        assert o1.shop_name == "ToyStore"
        assert o2.shop_name == "ToyStore"
