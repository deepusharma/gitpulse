from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from api.api import app

client = TestClient(app)

def test_github_validate_endpoint():
    from api.cache import repo_cache
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
