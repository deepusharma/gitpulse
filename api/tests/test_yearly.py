from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from api.api import app

client = TestClient(app)

def test_get_year_in_review_success():
    with patch("api.dependencies.get_db_pool") as mock_pool_func:
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        
        # Mock DB response for 2 summaries
        mock_conn.fetch.return_value = [
            {
                "generated_at": datetime(2026, 1, 15, tzinfo=timezone.utc),
                "summary": "Summary 1",
                "repos": ["repo1"]
            },
            {
                "generated_at": datetime(2026, 2, 20, tzinfo=timezone.utc),
                "summary": "Summary 2",
                "repos": ["repo1", "repo2"]
            }
        ]
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_pool_func.return_value = mock_pool
        
        with patch("api.routers.yearly.summarise", new_callable=AsyncMock) as mock_summarise:
            mock_summarise.return_value = "Yearly AI summary"
            
            response = client.get("/analytics/year-in-review?username=dev&year=2026")
            
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "dev"
            assert data["year"] == 2026
            assert data["total_stats"]["summaries"] == 2
            assert data["total_stats"]["unique_repos"] == 2
            assert len(data["top_repos"]) == 2
            assert data["top_repos"][0]["name"] == "repo1"
            assert data["top_repos"][0]["count"] == 2
            assert data["ai_wrap_up"] == "Yearly AI summary"
            assert data["busiest_day"]["count"] == 1

def test_get_year_in_review_no_data():
    with patch("api.dependencies.get_db_pool") as mock_pool_func:
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = []
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_pool_func.return_value = mock_pool
        
        response = client.get("/analytics/year-in-review?username=dev&year=2026")
        assert response.status_code == 404
        assert "No activity found" in response.json()["detail"]

def test_get_year_in_review_db_error():
    with patch("api.dependencies.get_db_pool") as mock_pool_func:
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_conn.fetch.side_effect = Exception("DB Fail")
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_pool_func.return_value = mock_pool
        
        response = client.get("/analytics/year-in-review?username=dev&year=2026")
        assert response.status_code == 500
