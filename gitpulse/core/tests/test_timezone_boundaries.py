import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from gitpulse.core.repo_reader import _get_local_commits_sync

def test_get_local_commits_boundary_utc():
    """Verify that 'since' date is correctly calculated in UTC."""
    # Mock datetime.now to a fixed point in time
    fixed_now = datetime(2026, 4, 2, 10, 0, 0, tzinfo=timezone.utc)
    
    with patch("gitpulse.core.repo_reader.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_now
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        mock_config = {"repos": {"r1": "/tmp/repo"}}
        
        with patch("gitpulse.core.repo_reader.load_config", return_value=mock_config):
            with patch("gitpulse.core.repo_reader.Repo") as mock_repo_class:
                mock_repo = MagicMock()
                mock_repo_class.return_value = mock_repo
                mock_repo.iter_commits.return_value = []
                
                _get_local_commits_sync(days=7)
                
                # Expected 'since' is fixed_now - 7 days
                expected_since = fixed_now - timedelta(days=7)
                
                # Check call to iter_commits
                mock_repo.iter_commits.assert_called_once()
                actual_since = mock_repo.iter_commits.call_args[1]["since"]
                
                assert actual_since == expected_since
                assert actual_since.tzinfo == timezone.utc

def test_get_local_commits_boundary_midnight():
    """Verify logic at midnight UTC boundary."""
    # 00:00:05 UTC
    midnight_now = datetime(2026, 4, 3, 0, 0, 5, tzinfo=timezone.utc)
    
    with patch("gitpulse.core.repo_reader.datetime") as mock_datetime:
        mock_datetime.now.return_value = midnight_now
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        mock_config = {"repos": {"r1": "/tmp/repo"}}
        
        with patch("gitpulse.core.repo_reader.load_config", return_value=mock_config):
            with patch("gitpulse.core.repo_reader.Repo") as mock_repo_class:
                mock_repo = MagicMock()
                mock_repo_class.return_value = mock_repo
                mock_repo.iter_commits.return_value = []
                
                _get_local_commits_sync(days=1)
                
                # Should be 00:00:05 on the previous day
                expected_since = datetime(2026, 4, 2, 0, 0, 5, tzinfo=timezone.utc)
                actual_since = mock_repo.iter_commits.call_args[1]["since"]
                
                assert actual_since == expected_since
