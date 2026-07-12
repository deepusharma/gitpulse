import pytest
from fastapi.testclient import TestClient
from api.api import app
from datetime import datetime, timezone
import json

client = TestClient(app)

def test_create_schedule_returns_201(monkeypatch):
    class MockPool:
        def acquire(self):
            class MockConnection:
                async def __aenter__(self): return self
                async def __aexit__(self, exc_type, exc_val, exc_tb): pass
                async def fetchrow(self, query, *args):
                    return {
                        "id": "test-id",
                        "username": args[0],
                        "enabled": args[1],
                        "frequency": args[2],
                        "hour_utc": args[3],
                        "day_of_week": args[4],
                        "channel": args[5],
                        "repos": args[8],
                        "days": args[9],
                        "last_sent_at": None,
                        "created_at": datetime.now(timezone.utc)
                    }
            return MockConnection()
            
    monkeypatch.setattr("api.routers.schedule.get_db_pool", lambda: MockPool())
    
    payload = {
        "username": "testuser",
        "frequency": "daily",
        "hour_utc": 10,
        "channel": "slack",
        "slack_webhook": "https://hooks.slack.com/test",
        "repos": ["repo1"],
        "days": 7
    }
    
    resp = client.post("/schedule", json=payload)
    assert resp.status_code == 201
    assert resp.json()["username"] == "testuser"

def test_get_schedule_returns_existing(monkeypatch):
    class MockPool:
        def acquire(self):
            class MockConnection:
                async def __aenter__(self): return self
                async def __aexit__(self, exc_type, exc_val, exc_tb): pass
                async def fetchrow(self, query, *args):
                    return {
                        "id": "test-id",
                        "username": args[0],
                        "enabled": True,
                        "frequency": "daily",
                        "hour_utc": 10,
                        "day_of_week": None,
                        "channel": "email",
                        "repos": ["repo1"],
                        "days": 7,
                        "last_sent_at": None,
                        "created_at": datetime.now(timezone.utc)
                    }
            return MockConnection()
            
    monkeypatch.setattr("api.routers.schedule.get_db_pool", lambda: MockPool())
    
    resp = client.get("/schedule/testuser")
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"

def test_get_schedule_404_unknown_user(monkeypatch):
    class MockPool:
        def acquire(self):
            class MockConnection:
                async def __aenter__(self): return self
                async def __aexit__(self, exc_type, exc_val, exc_tb): pass
                async def fetchrow(self, query, *args):
                    return None
            return MockConnection()
            
    monkeypatch.setattr("api.routers.schedule.get_db_pool", lambda: MockPool())
    
    resp = client.get("/schedule/unknownuser")
    assert resp.status_code == 404

def test_delete_schedule_removes_row(monkeypatch):
    class MockPool:
        def acquire(self):
            class MockConnection:
                async def __aenter__(self): return self
                async def __aexit__(self, exc_type, exc_val, exc_tb): pass
                async def execute(self, query, *args):
                    pass
            return MockConnection()
            
    monkeypatch.setattr("api.routers.schedule.get_db_pool", lambda: MockPool())
    
    resp = client.delete("/schedule/testuser")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

def test_create_schedule_email_requires_email_to():
    payload = {
        "username": "testuser",
        "frequency": "daily",
        "hour_utc": 10,
        "channel": "email",
        "repos": ["repo1"]
    }
    resp = client.post("/schedule", json=payload)
    assert resp.status_code == 400
    assert "email_to is required" in resp.text

def test_create_schedule_slack_requires_webhook():
    payload = {
        "username": "testuser",
        "frequency": "daily",
        "hour_utc": 10,
        "channel": "slack",
        "repos": ["repo1"]
    }
    resp = client.post("/schedule", json=payload)
    assert resp.status_code == 400
    assert "slack_webhook is required" in resp.text
