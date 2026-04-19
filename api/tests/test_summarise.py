from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from api.api import app

client = TestClient(app)

def test_summarise_cache_hit():
    from api.api import commit_cache
    commit_cache.clear()
    
    with patch("api.routers.summarise.get_activity", new_callable=AsyncMock) as mock_get_activity:
        mock_get_activity.return_value = ({"commits": [{"repo": "gitpulse", "hash": "abc", "author": "dev", "date": datetime(2026, 3, 21, tzinfo=timezone.utc), "message": "msg"}], "prs": [], "issues": []}, [])
        with patch("api.routers.summarise.summarise", new_callable=AsyncMock) as mock_summarise:
            mock_summarise.return_value = "Test summary"
            with patch("api.db.get_db_pool") as mock_pool_func:
                mock_pool = MagicMock()
                mock_conn = AsyncMock()
                mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
                mock_pool_func.return_value = mock_pool
                
                payload = {"username": "deepusharma", "repos": ["gitpulse"], "days": 7}
                
                # 1. First call (Cache Miss)
                resp1 = client.post("/summarise", json=payload)
                assert resp1.status_code == 200
                assert mock_get_activity.call_count == 1
                
                # 2. Second call (Cache Hit)
                resp2 = client.post("/summarise", json=payload)
                assert resp2.status_code == 200
                assert mock_get_activity.call_count == 1  # Should NOT increase
                assert resp2.json()["summary"] == "Test summary"

def test_summarise_cache_refresh():
    from api.api import commit_cache
    commit_cache.clear()
    
    with patch("api.routers.summarise.get_activity", new_callable=AsyncMock) as mock_get_activity:
        # First call: return empty
        mock_get_activity.return_value = ({"commits": [], "prs": [], "issues": []}, [])
        with patch("api.routers.summarise.summarise", new_callable=AsyncMock) as mock_summarise:
            mock_summarise.return_value = "Test"
            with patch("api.db.get_db_pool"):
                payload = {"username": "user", "repos": ["repo"], "days": 7}
                
                # Populate cache
                client.post("/summarise", json=payload)
                assert mock_get_activity.call_count == 1
                
                # Call with refresh=True
                client.post("/summarise?refresh=true", json=payload)
                assert mock_get_activity.call_count == 2 # Should increase because refresh bypasses cache

def test_summarise_valid_request_returns_200():
    with patch("api.routers.summarise.get_activity", new_callable=AsyncMock) as mock_get_activity:
        mock_get_activity.return_value = ({"commits": [{"repo": "gitpulse", "hash": "abc", "author": "dev", "date": datetime(2026, 3, 21, tzinfo=timezone.utc), "message": "msg"}], "prs": [], "issues": []}, [])
        with patch("api.routers.summarise.summarise") as mock_summarise:
            mock_summarise.return_value = "Test summary"
            with patch("api.db.get_db_pool") as mock_pool_func:
                mock_pool = MagicMock()
                mock_conn = AsyncMock()
                mock_conn.fetchrow.return_value = {"id": "123e4567-e89b-12d3-a456-426614174000"}
                mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
                mock_pool_func.return_value = mock_pool

                
                response = client.post("/summarise", json={"username": "deepusharma", "repos": ["gitpulse"], "days": 7})
                assert response.status_code == 200
                data = response.json()
                assert "id" in data
                assert data["id"] == "123e4567-e89b-12d3-a456-426614174000"
                assert "display" in data
                assert data["summary"] == "Test summary"
                assert data["repos"] == ["gitpulse"]
                assert data["username"] == "deepusharma"
                
                # Check DB interaction
                mock_conn.fetchrow.assert_called_once()
                args = mock_conn.fetchrow.call_args[0]
                assert "INSERT INTO summaries" in args[0]
                assert args[1] == "deepusharma"

def test_summarise_missing_username_returns_422():
    response = client.post("/summarise", json={"repos": ["gitpulse"]})
    assert response.status_code == 422

def test_summarise_empty_repos_returns_422():
    response = client.post("/summarise", json={"username": "deepusharma", "repos": []})
    assert response.status_code == 422

def test_summarise_db_failure_does_not_break_response():
    with patch("api.routers.summarise.get_activity", new_callable=AsyncMock) as mock_get_activity:
        mock_get_activity.return_value = ({"commits": [{"repo": "gitpulse", "hash": "abc", "author": "dev", "date": datetime(2026, 3, 21, tzinfo=timezone.utc), "message": "msg"}], "prs": [], "issues": []}, [])
        with patch("api.routers.summarise.summarise") as mock_summarise:
            mock_summarise.return_value = "Test summary"
            with patch("api.db.get_db_pool") as mock_pool_func:
                mock_pool = MagicMock()
                mock_conn = AsyncMock()
                mock_conn.fetchrow.side_effect = Exception("DB failure")
                mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
                mock_pool_func.return_value = mock_pool
                
                response = client.post("/summarise", json={"username": "deepusharma", "repos": ["gitpulse"], "days": 7})
                assert response.status_code == 200
                data = response.json()
                assert data["summary"] == "Test summary"
