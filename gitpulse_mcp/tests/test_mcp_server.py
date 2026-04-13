"""Unit tests for gitpulse_mcp/server.py tool handlers."""

import json
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

SAMPLE_ACTIVITY = {
    "commits": [
        {
            "repo": "gitpulse",
            "message": "feat: add mcp server",
            "author": "Test User",
            "date": datetime(2026, 4, 10, 10, 0, tzinfo=timezone.utc),
            "hash": "a1b2c3d4e5f6a1b2",
        }
    ],
    "prs": [
        {
            "repo": "gitpulse",
            "title": "Add MCP integration",
            "number": 42,
            "merged_at": datetime(2026, 4, 11, 12, 0, tzinfo=timezone.utc),
            "url": "https://github.com/deepusharma/gitpulse/pull/42",
        }
    ],
    "issues": [],
}


# ---------------------------------------------------------------------------
# handle_generate_standup
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_generate_standup_tool_returns_summary():
    """handle_generate_standup returns the summarise() output string."""
    mock_summary = "WHAT I DID\n* Implemented MCP server."
    arguments = {
        "username": "deepusharma",
        "repos": ["gitpulse"],
        "days": 7,
        "source": "github",
        "tone": "standup",
    }

    with patch(
        "gitpulse_mcp.server.get_activity",
        new=AsyncMock(return_value=(SAMPLE_ACTIVITY, [])),
    ), patch(
        "gitpulse_mcp.server.summarise",
        new=AsyncMock(return_value=mock_summary),
    ):
        from gitpulse_mcp.server import handle_generate_standup

        result = await handle_generate_standup(arguments)

    assert result == mock_summary
    assert len(result) > 0


@pytest.mark.anyio
async def test_generate_standup_tool_empty_activity():
    """handle_generate_standup returns a 'no activity' message when empty."""
    empty_activity = {"commits": [], "prs": [], "issues": []}
    arguments = {
        "username": "deepusharma",
        "repos": ["gitpulse"],
        "days": 7,
    }

    with patch(
        "gitpulse_mcp.server.get_activity",
        new=AsyncMock(return_value=(empty_activity, [])),
    ):
        from gitpulse_mcp.server import handle_generate_standup

        result = await handle_generate_standup(arguments)

    assert "No activity found" in result


@pytest.mark.anyio
async def test_generate_standup_tool_missing_username():
    """handle_generate_standup raises ValueError when username is missing."""
    from gitpulse_mcp.server import handle_generate_standup

    with pytest.raises(ValueError, match="username"):
        await handle_generate_standup({"repos": ["gitpulse"]})


@pytest.mark.anyio
async def test_generate_standup_tool_missing_repos():
    """handle_generate_standup raises ValueError when repos is empty."""
    from gitpulse_mcp.server import handle_generate_standup

    with pytest.raises(ValueError, match="repos"):
        await handle_generate_standup({"username": "deepusharma", "repos": []})


# ---------------------------------------------------------------------------
# handle_get_insights
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_get_insights_tool_returns_aggregated_counts():
    """handle_get_insights returns a dict with commit/PR/issue counts."""
    arguments = {
        "username": "deepusharma",
        "repos": ["gitpulse"],
        "days": 7,
    }

    with patch(
        "gitpulse_mcp.server.get_activity",
        new=AsyncMock(return_value=(SAMPLE_ACTIVITY, [])),
    ):
        from gitpulse_mcp.server import handle_get_insights

        result = await handle_get_insights(arguments)

    assert isinstance(result, dict)
    assert result["total_commits"] == 1
    assert result["total_prs_merged"] == 1
    assert result["total_issues_closed"] == 0
    assert result["username"] == "deepusharma"
    assert result["repos"] == ["gitpulse"]
    assert result["days"] == 7
    assert "generated_at" in result


@pytest.mark.anyio
async def test_get_insights_tool_per_repo_breakdown():
    """handle_get_insights correctly counts commits per repo."""
    activity = {
        "commits": [
            {
                "repo": "gitpulse",
                "message": "feat: a",
                "author": "user",
                "date": datetime(2026, 4, 10, tzinfo=timezone.utc),
                "hash": "abc1234",
            },
            {
                "repo": "dotfiles",
                "message": "chore: b",
                "author": "user",
                "date": datetime(2026, 4, 11, tzinfo=timezone.utc),
                "hash": "def5678",
            },
        ],
        "prs": [],
        "issues": [],
    }
    arguments = {"username": "deepusharma", "repos": ["gitpulse", "dotfiles"], "days": 7}

    with patch("gitpulse_mcp.server.get_activity", new=AsyncMock(return_value=(activity, []))):
        from gitpulse_mcp.server import handle_get_insights

        result = await handle_get_insights(arguments)

    assert result["commits_per_repo"]["gitpulse"] == 1
    assert result["commits_per_repo"]["dotfiles"] == 1


@pytest.mark.anyio
async def test_get_insights_tool_missing_username():
    """handle_get_insights raises ValueError when username is missing."""
    from gitpulse_mcp.server import handle_get_insights

    with pytest.raises(ValueError, match="username"):
        await handle_get_insights({"repos": ["gitpulse"]})


@pytest.mark.anyio
async def test_get_insights_tool_missing_repos():
    """handle_get_insights raises ValueError when repos is empty."""
    from gitpulse_mcp.server import handle_get_insights

    with pytest.raises(ValueError, match="repos"):
        await handle_get_insights({"username": "deepusharma", "repos": []})


# ---------------------------------------------------------------------------
# TOOLS schema validation
# ---------------------------------------------------------------------------


def test_tools_schema_structure():
    """TOOLS list contains exactly two tools with required fields."""
    from gitpulse_mcp.server import TOOLS

    assert len(TOOLS) == 2
    names = [t.name for t in TOOLS]
    assert "generate_standup" in names
    assert "get_insights" in names

    for tool in TOOLS:
        assert tool.description
        assert tool.inputSchema
        assert "required" in tool.inputSchema
