from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone
from api.api import app

client = TestClient(app)

def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.2.0"}

def test_summarise_valid_request_returns_200():
    with patch("api.api.get_commits") as mock_get_commits:
        mock_get_commits.return_value = [{"repo": "gitpulse", "hash": "abc", "author": "dev", "date": datetime(2026, 3, 21, tzinfo=timezone.utc), "message": "msg"}]
        with patch("api.api.summarise") as mock_summarise:
            mock_summarise.return_value = "Test summary"
            with patch("api.api.get_db_pool") as mock_pool_func:
                mock_pool = MagicMock()
                mock_conn = AsyncMock()
                mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
                mock_pool_func.return_value = mock_pool
                
                response = client.post("/summarise", json={"username": "deepusharma", "repos": ["gitpulse"], "days": 7})
                assert response.status_code == 200
                data = response.json()
                assert "display" in data
                assert data["summary"] == "Test summary"
                assert data["repos"] == ["gitpulse"]
                
                # Check DB interaction
                mock_conn.execute.assert_called_once()
                args = mock_conn.execute.call_args[0]
                assert "INSERT INTO summaries" in args[0]
                assert args[1] == "deepusharma"

def test_summarise_missing_username_returns_422():
    response = client.post("/summarise", json={"repos": ["gitpulse"]})
    assert response.status_code == 422

def test_summarise_empty_repos_returns_422():
    response = client.post("/summarise", json={"username": "deepusharma", "repos": []})
    assert response.status_code == 422

def test_summarise_db_failure_does_not_break_response():
    with patch("api.api.get_commits") as mock_get_commits:
        mock_get_commits.return_value = [{"repo": "gitpulse", "hash": "abc", "author": "dev", "date": datetime(2026, 3, 21, tzinfo=timezone.utc), "message": "msg"}]
        with patch("api.api.summarise") as mock_summarise:
            mock_summarise.return_value = "Test summary"
            with patch("api.api.get_db_pool") as mock_pool_func:
                mock_pool = MagicMock()
                mock_conn = AsyncMock()
                mock_conn.execute.side_effect = Exception("DB failure")
                mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
                mock_pool_func.return_value = mock_pool
                
                response = client.post("/summarise", json={"username": "deepusharma", "repos": ["gitpulse"], "days": 7})
                assert response.status_code == 200
                data = response.json()
                assert data["summary"] == "Test summary"

def test_get_history_returns_data():
    with patch("api.api.get_db_pool") as mock_pool_func:
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

def test_get_history_no_pool_returns_empty():
    with patch("api.api.get_db_pool") as mock_pool_func:
        mock_pool_func.return_value = None
        response = client.get("/history?username=deepusharma")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["summaries"] == []

