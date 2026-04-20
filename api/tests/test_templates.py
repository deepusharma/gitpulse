import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime
from api.api import app

client = TestClient(app)

@pytest.fixture
def mock_db_pool():
    with patch("api.routers.prompt_templates.get_db_pool") as mock:
        pool = MagicMock()
        mock.return_value = pool
        yield pool

def test_list_prompt_templates(mock_db_pool):
    """Test listing prompt templates for a user."""
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [
        {
            "id": "uuid-1",
            "username": "testuser",
            "name": "Template 1",
            "content": "Content 1",
            "created_at": datetime(2026, 3, 21)
        }
    ]
    mock_db_pool.acquire.return_value.__aenter__.return_value = mock_conn
    
    response = client.get("/prompt-templates?username=testuser")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Template 1"
    assert data[0]["content"] == "Content 1"

def test_create_prompt_template(mock_db_pool):
    """Test creating a new prompt template."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {
        "id": "uuid-2",
        "username": "testuser",
        "name": "New Template",
        "content": "New Content",
        "created_at": datetime(2026, 3, 21)
    }
    mock_db_pool.acquire.return_value.__aenter__.return_value = mock_conn
    
    response = client.post("/prompt-templates", json={
        "username": "testuser",
        "name": "New Template",
        "content": "New Content"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Template"
    assert data["id"] == "uuid-2"

def test_delete_prompt_template(mock_db_pool):
    """Test deleting a prompt template."""
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "DELETE 1"
    mock_db_pool.acquire.return_value.__aenter__.return_value = mock_conn
    
    response = client.delete("/prompt-templates/uuid-1")
    assert response.status_code == 204

def test_delete_prompt_template_not_found(mock_db_pool):
    """Test deleting a non-existent prompt template."""
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "DELETE 0"
    mock_db_pool.acquire.return_value.__aenter__.return_value = mock_conn
    
    response = client.delete("/prompt-templates/non-existent")
    assert response.status_code == 404
