import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from api.api import app

client = TestClient(app)

def test_health_returns_200():
    """Verify that the health check endpoint returns 200 OK and correct version."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.6.0"}

def test_health_keys_returns_status():
    """Verify that health/keys returns status for github and groq."""
    with patch("httpx.AsyncClient.get") as mock_get:
        # Mock successful GitHub call
        mock_get.return_value = AsyncMock(status_code=200)
        
        # Mock groq availability (since it's a direct import in the route)
        with patch("os.getenv") as mock_env:
            mock_env.side_effect = lambda k: "dummy_key" if k in ["GITHUB_TOKEN", "GROQ_API_KEY"] else None
            
            response = client.get("/health/keys")
            assert response.status_code == 200
            data = response.json()
            assert "github" in data
            assert "groq" in data
            assert data["github"] == "valid"
