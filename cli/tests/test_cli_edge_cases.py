import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from cli.cli import main
import sys
import os

@pytest.mark.anyio
async def test_cli_config_not_found(capsys):
    """Verify CLI behavior when ~/.gitpulse.toml is missing."""
    with patch("cli.cli.load_config", side_effect=FileNotFoundError):
        # Mock sys.argv to avoid argparse picking up pytest arguments
        with patch("sys.argv", ["gitpulse"]):
            with pytest.raises(SystemExit) as cm:
                await main()
            assert cm.value.code == 1
            captured = capsys.readouterr()
            assert "~/.gitpulse.toml not found" in captured.out

@pytest.mark.anyio
async def test_cli_missing_api_key(capsys):
    """Verify CLI behavior when GROQ_API_KEY is missing."""
    mock_config = {"repos": {"test": "/path/to/test"}}
    
    with patch("cli.cli.load_config", return_value=mock_config):
        with patch("cli.cli.load_env", side_effect=EnvironmentError("GROQ_API_KEY not set")):
            with patch("sys.argv", ["gitpulse"]):
                with pytest.raises(SystemExit) as cm:
                    await main()
                assert cm.value.code == 1
                captured = capsys.readouterr()
                assert "GROQ_API_KEY not set" in captured.out

@pytest.mark.anyio
async def test_cli_repo_not_in_config(capsys):
    """Verify CLI behavior when requested repo is missing from config."""
    mock_config = {"repos": {"known": "/path/to/known"}}
    
    with patch("cli.cli.load_config", return_value=mock_config):
        # Must also mock load_env and get_commits to avoid further errors
        with patch("cli.cli.load_env"):
            with patch("sys.argv", ["gitpulse", "--repo", "unknown"]):
                with pytest.raises(SystemExit) as cm:
                    await main()
                assert cm.value.code == 1
                captured = capsys.readouterr()
                assert "Repo 'unknown' not found in ~/.gitpulse.toml" in captured.out
                assert "Add it under [repos]" in captured.out
