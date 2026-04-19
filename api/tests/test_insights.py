from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from api.api import app

client = TestClient(app)

def test_get_insights_metrics():
    with patch("api.dependencies.get_user_repos", new_callable=AsyncMock) as mock_get_repos:
        mock_get_repos.return_value = ["repo1"]
        with patch("api.routers.insights.get_activity", new_callable=AsyncMock) as mock_get_activity:
            mock_get_activity.return_value = ({"commits": [
                {"repo": "repo1", "hash": "abc", "author": "dev", "date": datetime.now(timezone.utc) - timedelta(days=1), "message": "msg1"},
            ], "prs": [
                {"repo": "repo1", "title": "pr1", "merged_at": datetime.now(timezone.utc) - timedelta(days=1)}
            ], "issues": [
                {"repo": "repo1", "title": "iss1", "closed_at": datetime.now(timezone.utc) - timedelta(days=2)}
            ]}, [])
            response = client.get("/insights/metrics?username=testuser&repos=repo1&days=3")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3
            # We just verify basic contents exist inside the returned array
            pr_day = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
            issue_day = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%d")
            
            pr_day_metric = next((m for m in data if m["date"] == pr_day), None)
            assert pr_day_metric is not None
            assert pr_day_metric["commits"] == 1
            assert pr_day_metric["prs"] == 1
            
            issue_day_metric = next((m for m in data if m["date"] == issue_day), None)
            assert issue_day_metric is not None
            assert issue_day_metric["issues"] == 1

def test_get_insights_health():
    with patch("api.dependencies.get_user_repos", new_callable=AsyncMock) as mock_get_repos:
        mock_get_repos.return_value = ["repo1"]
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_client_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "stargazers_count": 5,
                "forks_count": 2,
                "open_issues_count": 1
            }
            mock_client_get.return_value = mock_response
            
            response = client.get("/insights/health?username=testuser&repos=repo1")
            assert response.status_code == 200
            data = response.json()
            
            assert data["total_stars"] == 5
            assert data["total_forks"] == 2
            assert data["total_open_issues"] == 1
            assert "health_score" in data
