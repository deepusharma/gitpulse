from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from api.api import app

client = TestClient(app)

def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.5.0"}

def test_summarise_valid_request_returns_200():
    with patch("api.api.get_commits", new_callable=AsyncMock) as mock_get_commits:
        mock_get_commits.return_value = ([{"repo": "gitpulse", "hash": "abc", "author": "dev", "date": datetime(2026, 3, 21, tzinfo=timezone.utc), "message": "msg"}], [])
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
                assert data["username"] == "deepusharma"
                
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
    with patch("api.api.get_commits", new_callable=AsyncMock) as mock_get_commits:
        mock_get_commits.return_value = ([{"repo": "gitpulse", "hash": "abc", "author": "dev", "date": datetime(2026, 3, 21, tzinfo=timezone.utc), "message": "msg"}], [])
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

def test_get_history_filters_applied():
    with patch("api.api.get_db_pool") as mock_pool_func:
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

def test_github_validate_endpoint():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"login": "testuser", "avatar_url": "http://img"})
        response = client.get("/github/validate?username=testuser")
        assert response.status_code == 200
        assert response.json()["valid"] == True
        assert response.json()["avatar_url"] == "http://img"

def test_analytics_commits_per_day():
    with patch("api.api._get_user_repos", new_callable=AsyncMock) as mock_get_repos:
        mock_get_repos.return_value = ["gitpulse"]
        with patch("api.api.get_commits", new_callable=AsyncMock) as mock_get_commits:
            mock_get_commits.return_value = ([
                {"repo": "gitpulse", "hash": "abc", "author": "dev", "date": datetime(2026, 3, 21, tzinfo=timezone.utc), "message": "msg1"},
                {"repo": "gitpulse", "hash": "def", "author": "dev", "date": datetime(2026, 3, 21, tzinfo=timezone.utc), "message": "msg2"},
                {"repo": "gitpulse", "hash": "ghi", "author": "dev", "date": datetime(2026, 3, 22, tzinfo=timezone.utc), "message": "msg3"},
            ], [])
            response = client.get("/analytics/commits-per-day?username=deepusharma&days=30")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["date"] == "2026-03-21"
            assert data[0]["count"] == 2
            assert data[1]["date"] == "2026-03-22"
            assert data[1]["count"] == 1

def test_analytics_repos_breakdown():
    with patch("api.api._get_user_repos", new_callable=AsyncMock) as mock_get_repos:
        mock_get_repos.return_value = ["repo1", "repo2"]
        with patch("api.api.get_commits", new_callable=AsyncMock) as mock_get_commits:
            mock_get_commits.return_value = ([
                {"repo": "repo1", "hash": "abc", "author": "dev", "date": datetime(2026, 3, 21, tzinfo=timezone.utc), "message": "msg1"},
                {"repo": "repo1", "hash": "def", "author": "dev", "date": datetime(2026, 3, 21, tzinfo=timezone.utc), "message": "msg2"},
                {"repo": "repo2", "hash": "ghi", "author": "dev", "date": datetime(2026, 3, 22, tzinfo=timezone.utc), "message": "msg3"},
            ], [])
            response = client.get("/analytics/repos-breakdown?username=deepusharma&days=30")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["repo"] == "repo1"
            assert data[0]["count"] == 2
            assert data[0]["percentage"] == 66.7
            assert data[1]["repo"] == "repo2"
            assert data[1]["count"] == 1
            assert data[1]["percentage"] == 33.3

def test_analytics_all_returns_consolidated_data():
    with patch("api.api._get_user_repos", new_callable=AsyncMock) as mock_get_repos:
        mock_get_repos.return_value = ["repo1"]
        with patch("api.api.get_commits", new_callable=AsyncMock) as mock_get_commits:
            mock_get_commits.return_value = ([
                {"repo": "repo1", "hash": "abc", "author": "dev", "date": datetime.now(timezone.utc) - timedelta(days=1), "message": "msg1"},
            ], [])
            with patch("api.api.get_db_pool") as mock_pool_func:
                mock_pool = MagicMock()
                mock_conn = AsyncMock()
                mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
                mock_conn.fetchval.return_value = 10
                mock_pool_func.return_value = mock_pool
                
                response = client.get("/analytics/all?username=deepusharma&days=30")
                assert response.status_code == 200
                data = response.json()
                
                assert "commits_per_day" in data
                assert "repos_breakdown" in data
                assert "insights" in data
                assert data["insights"]["total_summaries"] == 10
                assert data["insights"]["top_repo"] == "repo1"
