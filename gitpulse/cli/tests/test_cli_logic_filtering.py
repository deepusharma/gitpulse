import pytest
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock, MagicMock
from typer.testing import CliRunner
from gitpulse.cli.cli import app

runner = CliRunner()

def test_cli_repo_filtering():
    """Verify that --repo flag correctly filters the commit list."""
    mock_config = {
        "repos": {"repo1": "/path/1", "repo2": "/path/2"}
    }
    mock_commits = [
        {"repo": "repo1", "hash": "abc", "author": "dev", "date": datetime.now(timezone.utc), "message": "msg1"},
        {"repo": "repo2", "hash": "def", "author": "dev", "date": datetime.now(timezone.utc), "message": "msg2"},
    ]
    
    with patch("gitpulse.cli.cli.load_config", return_value=mock_config):
        with patch("gitpulse.cli.cli.load_env"):
            with patch("gitpulse.cli.cli.get_commits", new_callable=AsyncMock) as mock_get:
                mock_get.return_value = (mock_commits, [])
                result = runner.invoke(app, ["generate", "--repo", "repo1", "--dry-run"])
                
                assert result.exit_code == 0
                # Should only show repo1 in display
                assert "Local Git History" in result.stdout
                assert "repo1" in result.stdout

def test_cli_output_auto_mkdir(tmp_path):
    """Verify that CLI creates parent directories for output files."""
    output_dir = tmp_path / "deep" / "nested" / "dir"
    output_file = output_dir / "summary.md"
    
    mock_config = {"repos": {"r1": "/path"}}
    mock_commits = [{"repo": "r1", "hash": "a", "author": "d", "date": datetime.now(timezone.utc), "message": "m"}]
    
    with patch("gitpulse.cli.cli.load_config", return_value=mock_config):
        with patch("gitpulse.cli.cli.load_env"):
            with patch("gitpulse.cli.cli.get_commits", new_callable=AsyncMock) as mock_get:
                mock_get.return_value = (mock_commits, [])
                with patch("gitpulse.cli.cli.summarise", new_callable=AsyncMock) as mock_sum:
                    mock_sum.return_value = "Summary content"
                    result = runner.invoke(app, ["generate", "--output", str(output_file)])
                        
    assert result.exit_code == 0
    assert output_file.exists()
    assert output_file.read_text() == "Summary content"

def test_cli_days_calculation():
    """Verify that --days flag is passed correctly to get_commits."""
    mock_config = {"repos": {"r1": "/path"}}
    
    with patch("gitpulse.cli.cli.load_config", return_value=mock_config):
        with patch("gitpulse.cli.cli.load_env"):
            with patch("gitpulse.cli.cli.get_commits", new_callable=AsyncMock) as mock_get:
                mock_get.return_value = ([], ["No commits"]) # Trigger error to exit
                result = runner.invoke(app, ["generate", "--days", "14"])
                
                assert result.exit_code == 0
                # Verify get_commits was called with days=14
                args, kwargs = mock_get.call_args
                assert kwargs["days"] == 14
