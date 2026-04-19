from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from api.api import app

client = TestClient(app)

def test_get_history_returns_data():
    with patch("api.dependencies.get_db_pool") as mock_pool_func:
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        mock_record = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "deepusharma",
            "repos": ["gitpulse"],
            "days": 7,
            "summary": "Historical summary",
            "generated_at": datetime(2026, 3, 21, tzinfo=timezone.utc)
        }
        mock_conn.fetch.return_value = [mock_record]
        mock_conn.fetchval.return_value = 1
        
        mock_pool_func.return_value = mock_pool
        
        response = client.get("/history?username=deepusharma&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["summaries"]) == 1
        assert data["summaries"][0]["summary"] == "Historical summary"

def test_get_history_filters_applied():
    with patch("api.dependencies.get_db_pool") as mock_pool_func:
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = []
        mock_conn.fetchval.return_value = 0
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_pool_func.return_value = mock_pool
        
        response = client.get("/history?username=dev&search=test&start_date=2026-01-01")
        assert response.status_code == 200
        # Check if sql contains filters
        call_args = mock_conn.fetch.call_args[0]
        sql = call_args[0]
        assert "AND (repos::text ILIKE $2 OR summary ILIKE $2)" in sql
        assert "AND generated_at >= $3" in sql
