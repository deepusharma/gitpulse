from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from api.api import app

client = TestClient(app)

def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.6.0"}

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

def test_github_validate_endpoint():
    from api.api import repo_cache
    repo_cache.clear()
    
    with patch("httpx.AsyncClient.get") as mock_get:
        # Mock 1: User profile fetch
        # Mock 2: Repos fetch
        mock_res_profile = MagicMock(status_code=200, json=lambda: {"login": "testuser", "avatar_url": "http://img"})
        mock_res_repos = MagicMock(status_code=200, json=lambda: [{"name": "repo1"}])
        
        mock_get.side_effect = [mock_res_profile, mock_res_repos, mock_res_profile, mock_res_repos]
        
        # 1. First call (Miss for repos)
        response = client.get("/github/validate?username=testuser")
        assert response.status_code == 200
        # Should have called profile then repos
        assert mock_get.call_count == 2
        
        # 2. Second call (Hit for repos)
        response = client.get("/github/validate?username=testuser")
        assert response.status_code == 200
        # Should have called profile, but SKIPPED repos call because of cache
        assert mock_get.call_count == 3

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

def test_get_insights_metrics():
    with patch("api.dependencies.get_user_repos", new_callable=AsyncMock) as mock_get_repos:
        mock_get_repos.return_value = ["repo1"]
        with patch("api.api.get_activity", new_callable=AsyncMock) as mock_get_activity:
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

def test_create_roster():
    from api.api import get_db_pool
    with patch("api.api.get_db_pool") as mock_pool_func:
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        mock_conn.fetchrow.return_value = {"id": "123", "name": "Team A", "usernames": ["u1"], "created_at": datetime.now(timezone.utc)}
        mock_pool_func.return_value = mock_pool
        
        response = client.post("/team/roster", json={"name": "Team A", "usernames": ["u1"]})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Team A"

def test_team_summarise():
    with patch("api.api.get_activity", new_callable=AsyncMock) as mock_get_activity:
        mock_get_activity.side_effect = [
            ({"commits": [{"repo": "repo1", "hash": "1", "author": "u1", "date": datetime.now(timezone.utc), "message": "msg1"}], "prs": [], "issues": []}, []),
            ({"commits": [{"repo": "repo1", "hash": "2", "author": "u2", "date": datetime.now(timezone.utc), "message": "msg2"}], "prs": [], "issues": []}, [])
        ]
        with patch("api.api.summarise", new_callable=AsyncMock) as mock_summarise:
            mock_summarise.return_value = "Team Summary"
            
            response = client.post("/team/summarise", json={"usernames": ["u1", "u2"], "repos": ["repo1"]})
            assert response.status_code == 200
            data = response.json()
            assert data["summary"] == "Team Summary"
            assert "u1" in data["contributors"]
            assert "u2" in data["contributors"]
            
def test_deliver_slack():
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        response = client.post("/deliver/slack", json={"summary": "hello", "webhook_url": "https://hooks.slack.com/T000"})
        assert response.status_code == 200
        assert mock_post.called

def test_badges_streak_redirect():
    with patch("api.routers.analytics.get_insights", new_callable=AsyncMock) as mock_insights:
        mock_insights.return_value = {"streak": 42}
        response = client.get("/badges/streak?username=deepusharma", follow_redirects=False)
        assert response.status_code == 307
        assert "streak-42-brightgreen" in response.headers["location"]
