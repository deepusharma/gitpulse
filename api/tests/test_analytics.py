from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from api.api import app

client = TestClient(app)

def test_analytics_commits_per_day():
    with patch("api.dependencies.get_user_repos", new_callable=AsyncMock) as mock_get_repos:
        mock_get_repos.return_value = ["repo1"]
        with patch("api.routers.analytics.get_activity", new_callable=AsyncMock) as mock_get_activity:
            mock_get_activity.return_value = ({"commits": [
                {"repo": "gitpulse", "hash": "111", "author": "dev", "date": datetime(2026, 3, 21, tzinfo=timezone.utc), "message": "m1"},
                {"repo": "gitpulse", "hash": "222", "author": "dev", "date": datetime(2026, 3, 21, tzinfo=timezone.utc), "message": "m2"},
                {"repo": "gitpulse", "hash": "333", "author": "dev", "date": datetime(2026, 3, 22, tzinfo=timezone.utc), "message": "m3"}
            ], "prs": [], "issues": []}, [])
            response = client.get("/analytics/commits-per-day?username=deepusharma&days=30")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["date"] == "2026-03-21"
            assert data[0]["count"] == 2
            assert data[1]["date"] == "2026-03-22"
            assert data[1]["count"] == 1

def test_analytics_repos_breakdown():
    with patch("api.dependencies.get_user_repos", new_callable=AsyncMock) as mock_get_repos:
        mock_get_repos.return_value = ["repo1", "repo2"]
        with patch("api.routers.analytics.get_activity", new_callable=AsyncMock) as mock_get_activity:
            mock_get_activity.return_value = ({"commits": [
                {"repo": "repo1", "hash": "111", "author": "dev", "date": datetime(2026, 3, 1, tzinfo=timezone.utc), "message": "m1"},
                {"repo": "repo2", "hash": "222", "author": "dev", "date": datetime(2026, 3, 2, tzinfo=timezone.utc), "message": "m2"},
                {"repo": "repo2", "hash": "333", "author": "dev", "date": datetime(2026, 3, 2, tzinfo=timezone.utc), "message": "m3"}
            ], "prs": [], "issues": []}, [])
            response = client.get("/analytics/repos-breakdown?username=deepusharma&days=30")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["repo"] == "repo2"
            assert data[0]["count"] == 2
            assert data[0]["percentage"] == 66.7
            assert data[1]["repo"] == "repo1"
            assert data[1]["count"] == 1
            assert data[1]["percentage"] == 33.3

def test_analytics_all_returns_consolidated_data():
    with patch("api.dependencies.get_user_repos", new_callable=AsyncMock) as mock_get_repos:
        mock_get_repos.return_value = ["repo1"]
        with patch("api.routers.analytics.get_activity", new_callable=AsyncMock) as mock_get_activity:
            mock_get_activity.return_value = ({"commits": [
                {"repo": "repo1", "hash": "abc", "author": "dev", "date": datetime.now(timezone.utc) - timedelta(days=1), "message": "msg1"},
            ], "prs": [], "issues": []}, [])
            with patch("api.dependencies.get_db_pool") as mock_pool_func:
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
