import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta
import os

import asyncio
from api.worker import process_schedules

@patch.dict(os.environ, {"GROQ_API_KEY": ""}, clear=True)
def test_worker_skips_when_no_groq_key():
    with patch("api.worker.get_db_pool") as mock_get_pool:
        asyncio.run(process_schedules())
        mock_get_pool.assert_not_called()

@patch.dict(os.environ, {"GROQ_API_KEY": "test", "RESEND_API_KEY": "test"})
def test_worker_fires_email_for_due_schedule():
    with patch("api.worker.get_db_pool") as mock_get_pool, \
         patch("api.worker.get_activity", new_callable=AsyncMock) as mock_get_activity, \
         patch("api.worker.summarise", new_callable=AsyncMock) as mock_summarise, \
         patch("api.worker.deliver_email", new_callable=AsyncMock) as mock_deliver:
        
        now = datetime.now(timezone.utc)
        
        mock_get_activity.return_value = ({"commits": [{"repo": "repo1", "hash": "abc", "author": "dev", "date": now, "message": "test"}], "prs": [], "issues": []}, [])
        mock_summarise.return_value = "Test Summary"
        
        class MockConnection:
            async def __aenter__(self): return self
            async def __aexit__(self, exc_type, exc_val, exc_tb): pass
            async def fetch(self, query):
                return [{
                    "id": "test-id",
                    "username": "testuser",
                    "enabled": True,
                    "frequency": "daily",
                    "hour_utc": now.hour,
                    "day_of_week": now.weekday(),
                    "channel": "email",
                    "email_to": "test@test.com",
                    "slack_webhook": None,
                    "repos": ["repo1"],
                    "days": 7,
                    "tone": "professional",
                    "language": "English",
                    "last_sent_at": None
                }]
            async def execute(self, query, *args):
                pass
                
        class MockPool:
            def acquire(self): return MockConnection()
            
        mock_get_pool.return_value = MockPool()
        
        asyncio.run(process_schedules())
        
        mock_get_activity.assert_called_once()
        mock_summarise.assert_called_once()
        mock_deliver.assert_called_once()

@patch.dict(os.environ, {"GROQ_API_KEY": "test"})
def test_worker_skips_not_yet_due_schedule():
    with patch("api.worker.get_db_pool") as mock_get_pool, \
         patch("api.worker.get_activity", new_callable=AsyncMock) as mock_get_activity:
        
        now = datetime.now(timezone.utc)
        not_due_hour = (now.hour + 1) % 24
        
        class MockConnection:
            async def __aenter__(self): return self
            async def __aexit__(self, exc_type, exc_val, exc_tb): pass
            async def fetch(self, query):
                return [{
                    "id": "test-id",
                    "username": "testuser",
                    "enabled": True,
                    "frequency": "daily",
                    "hour_utc": not_due_hour,
                    "day_of_week": now.weekday(),
                    "channel": "email",
                    "email_to": "test@test.com",
                    "slack_webhook": None,
                    "repos": ["repo1"],
                    "days": 7,
                    "tone": "professional",
                    "language": "English",
                    "last_sent_at": None
                }]
                
        class MockPool:
            def acquire(self): return MockConnection()
            
        mock_get_pool.return_value = MockPool()
        
        asyncio.run(process_schedules())
        
        mock_get_activity.assert_not_called()

@patch.dict(os.environ, {"GROQ_API_KEY": "test", "RESEND_API_KEY": "test"})
def test_worker_updates_last_sent_at_after_delivery():
    with patch("api.worker.get_db_pool") as mock_get_pool, \
         patch("api.worker.get_activity", new_callable=AsyncMock) as mock_get_activity, \
         patch("api.worker.summarise", new_callable=AsyncMock) as mock_summarise, \
         patch("api.worker.deliver_email", new_callable=AsyncMock):
        
        now = datetime.now(timezone.utc)
        
        mock_get_activity.return_value = ({"commits": [{"repo": "repo1", "hash": "abc", "author": "dev", "date": now, "message": "test"}], "prs": [], "issues": []}, [])
        mock_summarise.return_value = "Test Summary"
        
        execute_mock = AsyncMock()
        
        class MockConnection:
            async def __aenter__(self): return self
            async def __aexit__(self, exc_type, exc_val, exc_tb): pass
            async def fetch(self, query):
                return [{
                    "id": "test-id",
                    "username": "testuser",
                    "enabled": True,
                    "frequency": "daily",
                    "hour_utc": now.hour,
                    "day_of_week": now.weekday(),
                    "channel": "email",
                    "email_to": "test@test.com",
                    "slack_webhook": None,
                    "repos": ["repo1"],
                    "days": 7,
                    "tone": "professional",
                    "language": "English",
                    "last_sent_at": None
                }]
            async def execute(self, query, *args):
                await execute_mock(query, *args)
                
        class MockPool:
            def acquire(self): return MockConnection()
            
        mock_get_pool.return_value = MockPool()
        
        asyncio.run(process_schedules())
        
        execute_mock.assert_called_once()
        assert "UPDATE digest_schedules SET last_sent_at = NOW()" in execute_mock.call_args[0][0]
