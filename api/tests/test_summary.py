from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone
from api.api import app

client = TestClient(app)

def test_get_public_summary_success():
    with patch("api.dependencies.get_db_pool") as mock_pool_func:
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        
        mock_conn.fetchrow.return_value = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "dev",
            "repos": ["repo1"],
            "days": 7,
            "summary": "Public summary content",
            "generated_at": datetime(2026, 3, 21, 12, 0, tzinfo=timezone.utc)
        }
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_pool_func.return_value = mock_pool
        
        response = client.get("/summary/public/123e4567-e89b-12d3-a456-426614174000")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "123e4567-e89b-12d3-a456-426614174000"
        assert data["summary"] == "Public summary content"
        assert data["username"] == "dev"

def test_get_public_summary_not_found():
    with patch("api.dependencies.get_db_pool") as mock_pool_func:
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_conn.fetchrow.return_value = None
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_pool_func.return_value = mock_pool
        
        response = client.get("/summary/public/non-existent-id")
        assert response.status_code == 404

def test_get_public_summary_db_error():
    with patch("api.dependencies.get_db_pool") as mock_pool_func:
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_conn.fetchrow.side_effect = Exception("DB error")
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_pool_func.return_value = mock_pool
        
        response = client.get("/summary/public/123")
        assert response.status_code == 500
