from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from api.api import app

client = TestClient(app)

def test_deliver_slack():
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        response = client.post("/deliver/slack", json={"summary": "hello", "webhook_url": "https://hooks.slack.com/T000"})
        assert response.status_code == 200
        assert mock_post.called
