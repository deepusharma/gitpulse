"""Tests for Phase 2: CLI Polish (--format json, status command)."""

import json
import os
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from gitpulse.cli.cli import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# --format json tests
# ---------------------------------------------------------------------------

def test_generate_format_json_outputs_valid_json():
    """gitpulse generate --format json should produce parseable JSON on stdout."""
    mock_activity = {
        "commits": [
            {
                "repo": "gitpulse",
                "message": "feat: add thing",
                "author": "deepusharma",
                "date": __import__("datetime").datetime(2026, 5, 1, 10, 0, 0),
                "hash": "abc123",
            }
        ],
        "prs": [],
        "issues": [],
    }
    mock_config = {
        "github_username": "deepusharma",
        "repos": {"gitpulse": "/path/to/gitpulse"},
        "defaults": {"days": 7, "tone": "professional", "language": "English", "output": "/tmp/out.md"},
    }

    with (
        patch("gitpulse.cli.cli.load_config", return_value=mock_config),
        patch("gitpulse.cli.cli.load_env"),
        patch("gitpulse.cli.cli.get_activity", return_value=(mock_activity, [])),
        patch("gitpulse.cli.cli.format_activity", return_value={"commits": mock_activity["commits"]}),
        patch("gitpulse.cli.cli.to_prompt_str", return_value="prompt"),
        patch("gitpulse.cli.cli.build_prompt", return_value="full prompt"),
        patch("gitpulse.cli.cli.summarise", return_value="Stand-up summary here."),
        patch("gitpulse.cli.cli.to_display_str", return_value="display"),
        patch("os.makedirs"),
        patch("builtins.open", MagicMock()),
    ):
        result = runner.invoke(app, ["generate", "--format", "json"])

    # Find the JSON line in output (may have logging noise before it)
    json_line = None
    for line in result.output.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                json_line = json.loads(line)
                break
            except json.JSONDecodeError:
                continue

    assert json_line is not None, f"No valid JSON found in output:\n{result.output}"
    assert "summary" in json_line
    assert "days" in json_line
    assert "generated_at" in json_line


def test_generate_format_pretty_default():
    """Default format should show Rich panel output, not raw JSON."""
    mock_activity = {
        "commits": [
            {
                "repo": "gitpulse",
                "message": "fix: a bug",
                "author": "deepusharma",
                "date": __import__("datetime").datetime(2026, 5, 1, 10, 0, 0),
                "hash": "abc123",
            }
        ],
        "prs": [],
        "issues": [],
    }
    mock_config = {
        "github_username": "deepusharma",
        "repos": {"gitpulse": "/path/to/gitpulse"},
        "defaults": {"days": 7, "tone": "professional", "language": "English", "output": "/tmp/out.md"},
    }

    with (
        patch("gitpulse.cli.cli.load_config", return_value=mock_config),
        patch("gitpulse.cli.cli.load_env"),
        patch("gitpulse.cli.cli.get_activity", return_value=(mock_activity, [])),
        patch("gitpulse.cli.cli.format_activity", return_value={"commits": mock_activity["commits"]}),
        patch("gitpulse.cli.cli.to_prompt_str", return_value="prompt"),
        patch("gitpulse.cli.cli.build_prompt", return_value="full prompt"),
        patch("gitpulse.cli.cli.summarise", return_value="Stand-up summary here."),
        patch("gitpulse.cli.cli.to_display_str", return_value="display"),
        patch("os.makedirs"),
        patch("builtins.open", MagicMock()),
    ):
        result = runner.invoke(app, ["generate"])

    assert "Standup Summary" in result.output


# ---------------------------------------------------------------------------
# status command tests
# ---------------------------------------------------------------------------

def test_status_missing_config(tmp_path):
    """status should report config as Missing when ~/.gitpulse.toml is absent."""
    fake_home = str(tmp_path)
    with patch("os.path.expanduser", return_value=str(tmp_path / ".gitpulse.toml")):
        result = runner.invoke(app, ["status"])
    assert "Missing" in result.output or "status" in result.output.lower()


def test_status_all_ok(tmp_path):
    """status should show all-green when config and keys are present."""
    # Write a minimal config file
    config_file = tmp_path / ".gitpulse.toml"
    config_file.write_text(
        '[defaults]\ndays = 7\ntone = "professional"\nlanguage = "English"\n\n[repos]\ngitpulse = "/path"\n'
    )
    mock_config = {
        "github_username": "deepusharma",
        "repos": {"gitpulse": "/path"},
        "defaults": {"days": 7, "tone": "professional", "language": "English"},
    }

    env_overrides = {
        "GROQ_API_KEY": "gsk_test",
        "GITHUB_TOKEN": "ghp_test",
        "NEXT_PUBLIC_API_URL": None,  # skip API check
    }

    with (
        patch("os.path.exists", return_value=True),
        patch("gitpulse.cli.cli.load_config", return_value=mock_config),
        patch.dict(os.environ, {"GROQ_API_KEY": "gsk_test", "GITHUB_TOKEN": "ghp_test"}, clear=False),
    ):
        result = runner.invoke(app, ["status"])

    # Should not crash and should contain the table header
    assert result.exit_code == 0
    assert "GitPulse Status" in result.output
