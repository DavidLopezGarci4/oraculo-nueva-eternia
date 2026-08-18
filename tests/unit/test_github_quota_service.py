import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from src.application.services.github_quota_service import GitHubQuotaService
from src.domain.models import ScraperExecutionLogModel
from tests.conftest import _TestSession

@pytest.mark.asyncio
async def test_quota_service_with_github_api():
    mock_runs = [
        {
            "name": "Scrapers Oraculo (Daily Scan)",
            "run_started_at": "2026-08-18T02:00:00Z",
            "updated_at": "2026-08-18T02:03:30Z", # 210s -> 4 billed mins
            "status": "completed",
            "conclusion": "success"
        },
        {
            "name": "Vinted Hunter (On-Demand Cloud Scan)",
            "run_started_at": "2026-08-18T05:00:00Z",
            "updated_at": "2026-08-18T05:00:25Z", # 25s -> 1 billed min
            "status": "completed",
            "conclusion": "success"
        }
    ]

    with patch("src.application.services.github_quota_service.GitHubQuotaService._fetch_github_runs_this_month", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {
            "total_billed_minutes": 5,
            "total_runs": 2,
            "breakdown": {
                "daily_scan": {"minutes": 4, "runs": 1},
                "vinted_sentinel": {"minutes": 1, "runs": 1},
                "ci_tests": {"minutes": 0, "runs": 0},
                "others": {"minutes": 0, "runs": 0}
            }
        }

        quota = await GitHubQuotaService.get_quota_status()
        
        assert quota["source"] == "github_api_live"
        assert quota["total_quota_minutes"] == 2000
        assert quota["used_minutes"] == 5
        assert quota["remaining_minutes"] == 1995
        assert quota["percentage_used"] == 0.2
        assert quota["cadence_status"] == "optimal"
        assert "00:00 UTC" in quota["reset_date"]
        assert quota["breakdown"]["daily_scan"]["minutes"] == 4
        assert quota["breakdown"]["vinted_sentinel"]["minutes"] == 1

@pytest.mark.asyncio
async def test_quota_service_db_fallback(client):
    # 1. Poblar la base de datos con un log de DailyScan y un log de VintedHunter
    with _TestSession() as db:
        db.add(ScraperExecutionLogModel(
            spider_name="DailyScan",
            status="success",
            start_time=datetime.now(timezone.utc).replace(tzinfo=None),
            end_time=datetime.now(timezone.utc).replace(tzinfo=None),
            trigger_type="scheduled",
            items_found=150,
            new_items=10
        ))
        db.add(ScraperExecutionLogModel(
            spider_name="VintedHunter",
            status="success",
            start_time=datetime.now(timezone.utc).replace(tzinfo=None),
            end_time=datetime.now(timezone.utc).replace(tzinfo=None),
            trigger_type="sentinel",
            items_found=400,
            new_items=3
        ))
        db.commit()

    with patch("src.application.services.github_quota_service.GitHubQuotaService._fetch_github_runs_this_month", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = None # Simular API no disponible

        quota = await GitHubQuotaService.get_quota_status()
        
        assert quota["source"] == "database_fallback"
        assert quota["used_minutes"] >= 2
        assert quota["remaining_minutes"] <= 1998

def test_generate_logs_csv(client):
    with _TestSession() as db:
        db.add(ScraperExecutionLogModel(
            spider_name="VintedHunter",
            status="success",
            start_time=datetime.now(timezone.utc).replace(tzinfo=None),
            end_time=datetime.now(timezone.utc).replace(tzinfo=None),
            trigger_type="sentinel",
            items_found=20,
            new_items=2,
            errors=0
        ))
        db.commit()

        csv_content = GitHubQuotaService.generate_logs_csv(db_session=db)
        assert "ID;Proceso / Spider;Estado;Disparador" in csv_content
        assert "VintedHunter" in csv_content
