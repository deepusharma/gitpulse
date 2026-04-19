from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from api.api import app

client = TestClient(app)

def test_badges_streak_redirect():
    with patch("api.routers.analytics.get_insights", new_callable=AsyncMock) as mock_insights:
        mock_insights.return_value = {"streak": 42}
        response = client.get("/badges/streak?username=deepusharma", follow_redirects=False)
        assert response.status_code == 307
        assert "streak-42-brightgreen" in response.headers["location"]
