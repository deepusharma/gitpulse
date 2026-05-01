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

@patch.dict("os.environ", {"RESEND_API_KEY": "re_test"})
def test_deliver_email():
    with patch("resend.Emails.send") as mock_send:
        mock_send.return_value = {"id": "email_123"}
        response = client.post("/deliver/email", json={"to": "test@example.com", "summary": "hello"})
        assert response.status_code == 200
        assert response.json() == {"ok": True, "id": "email_123"}
        mock_send.assert_called_once()

def test_deliver_gist():
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"html_url": "https://gist.github.com/123"}
        mock_post.return_value = mock_response
        
        response = client.post(
            "/deliver/gist", 
            json={"summary": "hello", "is_public": False},
            headers={"X-GitHub-Token": "gho_test"}
        )
        assert response.status_code == 200
        assert response.json() == {"url": "https://gist.github.com/123"}
        mock_post.assert_called_once()

def test_deliver_gist_no_token():
    response = client.post("/deliver/gist", json={"summary": "hello", "is_public": False})
    assert response.status_code == 401
