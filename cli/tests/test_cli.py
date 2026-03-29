import pytest
import sys
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from cli.cli import main

@patch("cli.cli.load_config")
@patch("cli.cli.load_env")
@patch("cli.cli.get_commits")
@patch("cli.cli.summarise")
def test_dry_run_skips_llm(mock_summarise, mock_get_commits, mock_load_env, mock_load_config, capsys):
    mock_load_config.return_value = {"repos": {"r1": "/path"}}
    mock_get_commits.return_value = [{"repo": "r1", "message": "msg", "author": "a", "date": datetime.now(timezone.utc), "hash": "hash"}]
    
    with patch.object(sys, "argv", ["gitpulse", "--dry-run"]):
        with pytest.raises(SystemExit) as excinfo:
            main()
    
    assert excinfo.value.code == 0
    mock_summarise.assert_not_called()
    out, err = capsys.readouterr()
    assert "dry-run mode — skipping LLM call" in out


@patch("cli.cli.load_config")
@patch("cli.cli.load_env")
@patch("cli.cli.get_commits")
@patch("cli.cli.summarise")
@patch("cli.cli.format_commits")
@patch("cli.cli.to_prompt_str")
@patch("cli.cli.build_prompt")
@patch("cli.cli.os.makedirs")
@patch("builtins.open")
def test_config_defaults_loaded(mock_open, mock_makedirs, mock_build_prompt, mock_to_prompt, mock_format, mock_summarise, mock_get_commits, mock_load_env, mock_load_config):
    mock_load_config.return_value = {
        "repos": {"r1": "/path"},
        "defaults": {"days": 14, "output": "custom_output.md", "repo": "r1"}
    }
    mock_get_commits.return_value = [{"repo": "r1", "message": "msg", "author": "a", "date": datetime.now(timezone.utc), "hash": "hash"}]
    mock_summarise.return_value = "summary"
    
    with patch.object(sys, "argv", ["gitpulse"]):
        main()
        
    mock_get_commits.assert_called_once_with(14)
    mock_open.assert_called_once_with("custom_output.md", "w")


@patch("cli.cli.load_config")
@patch("cli.cli.load_env")
@patch("cli.cli.get_commits")
@patch("cli.cli.summarise")
@patch("cli.cli.format_commits")
@patch("cli.cli.to_prompt_str")
@patch("cli.cli.build_prompt")
@patch("cli.cli.os.makedirs")
@patch("builtins.open")
def test_cli_flags_override_defaults(mock_open, mock_makedirs, mock_build_prompt, mock_to_prompt, mock_format, mock_summarise, mock_get_commits, mock_load_env, mock_load_config):
    mock_load_config.return_value = {
        "repos": {"r1": "/path"},
        "defaults": {"days": 14, "output": "custom_output.md", "repo": "r1"}
    }
    mock_get_commits.return_value = [{"repo": "r1", "message": "msg", "author": "a", "date": datetime.now(timezone.utc), "hash": "hash"}]
    mock_summarise.return_value = "summary"
    
    with patch.object(sys, "argv", ["gitpulse", "--days", "5", "--output", "flag_output.md", "--repo", "r1"]):
        main()
        
    mock_get_commits.assert_called_once_with(5)
    mock_open.assert_called_once_with("flag_output.md", "w")
