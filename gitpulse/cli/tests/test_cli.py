import pytest
import sys
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock, AsyncMock
from typer.testing import CliRunner
from gitpulse.cli.cli import app

runner = CliRunner()

@patch("gitpulse.cli.cli.load_config")
@patch("gitpulse.cli.cli.load_env")
@patch("gitpulse.cli.cli.get_commits", new_callable=AsyncMock)
@patch("gitpulse.cli.cli.summarise", new_callable=AsyncMock)
def test_dry_run_skips_llm(mock_summarise, mock_get_commits, mock_load_env, mock_load_config):
    mock_load_config.return_value = {"repos": {"r1": "/path"}}
    mock_get_commits.return_value = ([{"repo": "r1", "message": "msg", "author": "a", "date": datetime.now(timezone.utc), "hash": "hash"}], [])
    
    # Use CliRunner to call the command
    result = runner.invoke(app, ["generate", "--dry-run"])
    
    assert result.exit_code == 0
    mock_summarise.assert_not_called()
    assert "Dry-run mode" in result.stdout


@patch("gitpulse.cli.cli.load_config")
@patch("gitpulse.cli.cli.load_env")
@patch("gitpulse.cli.cli.get_commits", new_callable=AsyncMock)
@patch("gitpulse.cli.cli.summarise", new_callable=AsyncMock)
@patch("gitpulse.cli.cli.format_commits")
@patch("gitpulse.cli.cli.to_prompt_str")
@patch("gitpulse.cli.cli.build_prompt")
@patch("gitpulse.cli.cli.os.makedirs")
@patch("builtins.open")
def test_config_defaults_loaded(mock_open, mock_makedirs, mock_build_prompt, mock_to_prompt, mock_format, mock_summarise, mock_get_commits, mock_load_env, mock_load_config):
    mock_load_config.return_value = {
        "repos": {"r1": "/path"},
        "defaults": {"days": 14, "output": "custom_output.md", "repo": "r1"}
    }
    mock_get_commits.return_value = ([{"repo": "r1", "message": "msg", "author": "a", "date": datetime.now(timezone.utc), "hash": "hash"}], [])
    mock_summarise.return_value = "summary"
    
    result = runner.invoke(app, ["generate"])
    
    assert result.exit_code == 0
    mock_get_commits.assert_called_once()
    # Check that it picked up the default days=14
    args, kwargs = mock_get_commits.call_args
    assert kwargs["days"] == 14
    mock_open.assert_called_once_with("custom_output.md", "w")


@patch("gitpulse.cli.cli.load_config")
@patch("gitpulse.cli.cli.load_env")
@patch("gitpulse.cli.cli.get_commits", new_callable=AsyncMock)
@patch("gitpulse.cli.cli.summarise", new_callable=AsyncMock)
@patch("gitpulse.cli.cli.format_commits")
@patch("gitpulse.cli.cli.to_prompt_str")
@patch("gitpulse.cli.cli.build_prompt")
@patch("gitpulse.cli.cli.os.makedirs")
@patch("builtins.open")
def test_cli_flags_override_defaults(mock_open, mock_makedirs, mock_build_prompt, mock_to_prompt, mock_format, mock_summarise, mock_get_commits, mock_load_env, mock_load_config):
    mock_load_config.return_value = {
        "repos": {"r1": "/path"},
        "defaults": {"days": 14, "output": "custom_output.md", "repo": "r1"}
    }
    mock_get_commits.return_value = ([{"repo": "r1", "message": "msg", "author": "a", "date": datetime.now(timezone.utc), "hash": "hash"}], [])
    mock_summarise.return_value = "summary"
    
    result = runner.invoke(app, ["generate", "--days", "5", "--output", "flag_output.md", "--repo", "r1"])
    
    assert result.exit_code == 0
    args, kwargs = mock_get_commits.call_args
    assert kwargs["days"] == 5
    mock_open.assert_called_once_with("flag_output.md", "w")
