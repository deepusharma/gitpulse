import pytest
import sys
import os
from unittest.mock import patch, AsyncMock, MagicMock
from cli.cli import main
from datetime import datetime, timezone

@pytest.mark.anyio
async def test_cli_repo_filtering(capsys):
    """Verify that --repo flag correctly filters the commit list."""
    mock_config = {
        "repos": {"repo1": "/path/1", "repo2": "/path/2"}
    }
    mock_commits = [
        {"repo": "repo1", "hash": "abc", "author": "dev", "date": datetime.now(timezone.utc), "message": "msg1"},
        {"repo": "repo2", "hash": "def", "author": "dev", "date": datetime.now(timezone.utc), "message": "msg2"},
    ]
    
    with patch("cli.cli.load_config", return_value=mock_config):
        with patch("cli.cli.load_env"):
            with patch("cli.cli.get_commits", new_callable=AsyncMock) as mock_get:
                mock_get.return_value = (mock_commits, [])
                # Mock dry-run to avoid summarization
                with patch("sys.argv", ["gitpulse", "--repo", "repo1", "--dry-run"]):
                    with pytest.raises(SystemExit) as cm:
                        await main()
                    assert cm.value.code == 0
                    captured = capsys.readouterr()
                    # Should only show repo1 in display
                    assert "### repo1" in captured.out
                    assert "### repo2" not in captured.out

@pytest.mark.anyio
async def test_cli_output_auto_mkdir(tmp_path):
    """Verify that CLI creates parent directories for output files."""
    output_dir = tmp_path / "deep" / "nested" / "dir"
    output_file = output_dir / "summary.md"
    
    mock_config = {"repos": {"r1": "/path"}}
    mock_commits = [{"repo": "r1", "hash": "a", "author": "d", "date": datetime.now(timezone.utc), "message": "m"}]
    
    with patch("cli.cli.load_config", return_value=mock_config):
        with patch("cli.cli.load_env"):
            with patch("cli.cli.get_commits", new_callable=AsyncMock) as mock_get:
                mock_get.return_value = (mock_commits, [])
                with patch("cli.cli.summarise", new_callable=AsyncMock) as mock_sum:
                    mock_sum.return_value = "Summary content"
                    with patch("sys.argv", ["gitpulse", "--output", str(output_file)]):
                        # We don't raise SystemExit because 0 is success
                        await main()
                        
    assert output_file.exists()
    assert output_file.read_text() == "Summary content"

@pytest.mark.anyio
async def test_cli_days_calculation():
    """Verify that --days flag is passed correctly to get_commits."""
    mock_config = {"repos": {"r1": "/path"}}
    
    with patch("cli.cli.load_config", return_value=mock_config):
        with patch("cli.cli.load_env"):
            with patch("cli.cli.get_commits", new_callable=AsyncMock) as mock_get:
                mock_get.return_value = ([], ["No commits"]) # Trigger error to exit
                with patch("sys.argv", ["gitpulse", "--days", "14"]):
                    with pytest.raises(SystemExit):
                        await main()
                # Verify get_commits was called with days=14
                mock_get.assert_called_with(source="local", days=14)
