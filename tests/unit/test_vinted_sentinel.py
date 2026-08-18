import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from src.application.services.vinted_sentinel_service import VintedSentinelService

@pytest.mark.asyncio
async def test_sentinel_blackout_detection():
    sentinel = VintedSentinelService()
    
    # 02:05 UTC -> Blackout
    dt_blackout_night = datetime(2026, 8, 18, 2, 5, 0, tzinfo=timezone.utc)
    assert sentinel._is_daily_scan_blackout(dt_blackout_night) is True
    
    # 14:35 UTC -> Blackout
    dt_blackout_afternoon = datetime(2026, 8, 18, 14, 35, 0, tzinfo=timezone.utc)
    assert sentinel._is_daily_scan_blackout(dt_blackout_afternoon) is True
    
    # 10:15 UTC -> Normal execution allowed
    dt_allowed = datetime(2026, 8, 18, 10, 15, 0, tzinfo=timezone.utc)
    assert sentinel._is_daily_scan_blackout(dt_allowed) is False

@pytest.mark.asyncio
async def test_sentinel_status_and_lifecycle():
    sentinel = VintedSentinelService()
    sentinel.stop()
    
    status = sentinel.get_status()
    assert status["is_running"] is False
    
    sentinel.start()
    status_active = sentinel.get_status()
    assert status_active["is_running"] is True
    
    sentinel.stop()
    assert sentinel.is_running is False

@pytest.mark.asyncio
async def test_sentinel_dispatch_via_github():
    sentinel = VintedSentinelService()
    
    mock_resp = MagicMock()
    mock_resp.status_code = 204
    
    with patch("src.application.services.vinted_sentinel_service.settings.GITHUB_TOKEN", "ghp_mock_token_12345"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        
        res = await sentinel.dispatch_hunt(chat_id="12345")
        
        assert res["status"] == "dispatched_to_azure"
        assert res["mode"] == "github_actions"
        assert mock_post.called

@pytest.mark.asyncio
async def test_sentinel_dispatch_local_fallback():
    sentinel = VintedSentinelService()
    
    with patch("src.application.services.vinted_sentinel_service.settings.GITHUB_TOKEN", None), \
         patch("src.application.services.vinted_hunter_service.VintedHunterService.run_hunt", new_callable=AsyncMock) as mock_hunt:
        
        mock_hunt.return_value = {
            "total_scraped": 80,
            "bargains_found": 1,
            "bargains": [{"product_name": "He-Man"}],
            "status": "success"
        }
        
        res = await sentinel.dispatch_hunt(chat_id="12345")
        
        assert res["total_scraped"] == 80
        assert res["bargains_found"] == 1
        assert mock_hunt.called
