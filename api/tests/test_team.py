from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from api.api import app

client = TestClient(app)

def test_create_roster():
    with patch("api.routers.team.get_db_pool") as mock_pool_func:
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
    with patch("api.routers.team.get_activity", new_callable=AsyncMock) as mock_get_activity:
        mock_get_activity.side_effect = [
            ({"commits": [{"repo": "repo1", "hash": "1", "author": "u1", "date": datetime.now(timezone.utc), "message": "msg1"}], "prs": [], "issues": []}, []),
            ({"commits": [{"repo": "repo1", "hash": "2", "author": "u2", "date": datetime.now(timezone.utc), "message": "msg2"}], "prs": [], "issues": []}, [])
        ]
        with patch("api.routers.team.summarise", new_callable=AsyncMock) as mock_summarise:
            mock_summarise.return_value = "Team Summary"
            
            response = client.post("/team/summarise", json={"usernames": ["u1", "u2"], "repos": ["repo1"]})
            assert response.status_code == 200
            data = response.json()
            assert data["summary"] == "Team Summary"
            assert "u1" in data["contributors"]
            assert "u2" in data["contributors"]
