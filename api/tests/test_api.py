from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime, timezone
from api.api import app

client = TestClient(app)

def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.2.0"}

def test_summarise_valid_request_returns_200():
    with patch("api.api.get_commits") as mock_get_commits:
        mock_get_commits.return_value = [{"repo": "gitpulse", "hash": "abc", "author": "dev", "date": datetime(2026, 3, 21, tzinfo=timezone.utc), "message": "msg"}]
        with patch("api.api.summarise") as mock_summarise:
            mock_summarise.return_value = "Test summary"
            
            response = client.post("/summarise", json={"username": "deepusharma", "repos": ["gitpulse"], "days": 7})
            assert response.status_code == 200
            data = response.json()
            assert "display" in data
            assert data["summary"] == "Test summary"
            assert data["repos"] == ["gitpulse"]

def test_summarise_missing_username_returns_422():
    response = client.post("/summarise", json={"repos": ["gitpulse"]})
    assert response.status_code == 422

def test_summarise_empty_repos_returns_422():
    response = client.post("/summarise", json={"username": "deepusharma", "repos": []})
    assert response.status_code == 422
