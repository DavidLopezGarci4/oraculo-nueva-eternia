import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.infrastructure.scrapers.pipeline import check_and_send_multiuser_alerts
from src.domain.models import UserModel, ProductModel, CollectionItemModel, PriceAlertModel

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.mark.anyio
async def test_check_and_send_multiuser_alerts_wishlist():
    db = MagicMock()
    
    mock_user = UserModel(
        id=1,
        username="guardian_test",
        telegram_chat_id="123456789",
        is_active=True
    )
    
    mock_product = ProductModel(
        id=10,
        name="He-Man Vintage Action Figure"
    )
    
    def mock_query(model):
        q = MagicMock()
        if model == UserModel:
            q.filter.return_value.all.return_value = [mock_user]
        elif model == ProductModel:
            q.join.return_value.filter.return_value.all.return_value = [mock_product]
        elif model == PriceAlertModel:
            q.join.return_value.filter.return_value.all.return_value = []
        return q
        
    db.query.side_effect = mock_query
    
    with patch("src.infrastructure.services.telegram_service.telegram_service.send_wishlist_alert", new_callable=AsyncMock) as mock_send_wishlist:
        with patch("src.infrastructure.services.telegram_service.telegram_service.send_price_alert", new_callable=AsyncMock) as mock_send_price:
            
            check_and_send_multiuser_alerts(
                db=db,
                scraped_name="Masters of the Universe He-Man Vintage Action Figure on card",
                price=25.0,
                shop_name="Wallapop",
                url="https://wallapop.com/item/1",
                is_vintage=True
            )
            
            await asyncio.sleep(0.1)
            
            mock_send_wishlist.assert_called_once_with(
                chat_id="123456789",
                product_name="He-Man Vintage Action Figure",
                price=25.0,
                shop_name="Wallapop",
                url="https://wallapop.com/item/1"
            )
            mock_send_price.assert_not_called()

@pytest.mark.anyio
async def test_check_and_send_multiuser_alerts_price_alert():
    db = MagicMock()
    
    mock_user = UserModel(
        id=1,
        username="guardian_test",
        telegram_chat_id="123456789",
        is_active=True
    )
    
    mock_product = ProductModel(
        id=10,
        name="Skeletor Vintage"
    )
    
    mock_price_alert = PriceAlertModel(
        id=200,
        product_id=10,
        user_id=1,
        target_price=30.0,
        is_active=True,
        product=mock_product
    )
    
    def mock_query(model):
        q = MagicMock()
        if model == UserModel:
            q.filter.return_value.all.return_value = [mock_user]
        elif model == ProductModel:
            q.join.return_value.filter.return_value.all.return_value = []
        elif model == PriceAlertModel:
            q.join.return_value.filter.return_value.all.return_value = [mock_price_alert]
        return q
        
    db.query.side_effect = mock_query
    
    with patch("src.infrastructure.services.telegram_service.telegram_service.send_wishlist_alert", new_callable=AsyncMock) as mock_send_wishlist:
        with patch("src.infrastructure.services.telegram_service.telegram_service.send_price_alert", new_callable=AsyncMock) as mock_send_price:
            
            check_and_send_multiuser_alerts(
                db=db,
                scraped_name="Skeletor Vintage figure loose 80s",
                price=22.0,
                shop_name="Ebay",
                url="https://ebay.es/itm/2",
                is_vintage=True
            )
            
            await asyncio.sleep(0.1)
            
            mock_send_price.assert_called_once_with(
                chat_id="123456789",
                product_name="Skeletor Vintage",
                price=22.0,
                target_price=30.0,
                shop_name="Ebay",
                url="https://ebay.es/itm/2"
            )
            mock_send_wishlist.assert_not_called()
