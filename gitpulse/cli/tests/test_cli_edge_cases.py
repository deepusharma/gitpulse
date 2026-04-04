import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from typer.testing import CliRunner
from gitpulse.cli.cli import app

runner = CliRunner()

def test_cli_config_not_found():
    """Verify CLI behavior when ~/.gitpulse.toml is missing."""
    with patch("gitpulse.cli.cli.load_config", side_effect=FileNotFoundError):
        result = runner.invoke(app, ["generate"])
        assert result.exit_code == 1
        assert "~/.gitpulse.toml not found" in result.stdout

def test_cli_missing_api_key():
    """Verify CLI behavior when GROQ_API_KEY is missing."""
    mock_config = {"repos": {"test": "/path/to/test"}}
    
    with patch("gitpulse.cli.cli.load_config", return_value=mock_config):
        with patch("gitpulse.cli.cli.load_env", side_effect=EnvironmentError("GROQ_API_KEY not set")):
            result = runner.invoke(app, ["generate"])
            assert result.exit_code == 1
            assert "GROQ_API_KEY not set" in result.stdout

def test_cli_repo_not_in_config():
    """Verify CLI behavior when requested repo is missing from config."""
    mock_config = {"repos": {"known": "/path/to/known"}}
    
    with patch("gitpulse.cli.cli.load_config", return_value=mock_config):
        with patch("gitpulse.cli.cli.load_env"):
            result = runner.invoke(app, ["generate", "--repo", "unknown"])
            assert result.exit_code == 1
            assert "Repo 'unknown' not found in ~/.gitpulse.toml" in result.stdout
