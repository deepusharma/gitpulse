"""Unit tests for gitpulse.core.recommendations."""

import pytest
from unittest.mock import AsyncMock, patch

from gitpulse.core.recommendations import build_recommendations_prompt, get_recommendations


# ---------------------------------------------------------------------------
# build_recommendations_prompt
# ---------------------------------------------------------------------------


def test_build_recommendations_prompt_contains_metrics():
    """build_recommendations_prompt includes all metric values in the output."""
    metrics = {
        "commits": 15,
        "prs": 3,
        "issues": 2,
        "avg_cycle_time_hrs": 12.5,
        "stale_prs": 1,
        "commit_streak_days": 5,
        "prev_commits": 20,
    }
    prompt = build_recommendations_prompt(metrics)

    assert "15" in prompt
    assert "3" in prompt
    assert "12.5" in prompt
    assert "1" in prompt
    assert "5" in prompt
    assert "20" in prompt


def test_build_recommendations_prompt_delta_up():
    """build_recommendations_prompt includes a 'up' delta when commits increased."""
    metrics = {"commits": 20, "prev_commits": 10}
    prompt = build_recommendations_prompt(metrics)
    assert "up" in prompt


def test_build_recommendations_prompt_delta_down():
    """build_recommendations_prompt includes a 'down' delta when commits decreased."""
    metrics = {"commits": 5, "prev_commits": 10}
    prompt = build_recommendations_prompt(metrics)
    assert "down" in prompt


def test_build_recommendations_prompt_no_activity():
    """build_recommendations_prompt handles zero commits without error."""
    metrics = {"commits": 0, "prev_commits": 0}
    prompt = build_recommendations_prompt(metrics)
    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_build_recommendations_prompt_returns_string():
    """build_recommendations_prompt always returns a non-empty string."""
    prompt = build_recommendations_prompt({})
    assert isinstance(prompt, str)
    assert len(prompt) > 10


# ---------------------------------------------------------------------------
# get_recommendations
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_get_recommendations_returns_non_empty_string():
    """get_recommendations returns the LLM output string unchanged."""
    mock_summary = "1. Commit more regularly.\n2. Review stale PRs.\n3. Write tests."
    metrics = {
        "commits": 8,
        "prs": 1,
        "issues": 0,
        "avg_cycle_time_hrs": 24.0,
        "stale_prs": 2,
        "commit_streak_days": 3,
        "prev_commits": 12,
    }

    with patch(
        "gitpulse.core.recommendations.summarise",
        new=AsyncMock(return_value=mock_summary),
    ):
        result = await get_recommendations(metrics)

    assert result == mock_summary
    assert len(result) > 0


@pytest.mark.anyio
async def test_get_recommendations_calls_summarise_with_prompt():
    """get_recommendations passes a built prompt to summarise."""
    mock_summarise = AsyncMock(return_value="nudges")

    with patch(
        "gitpulse.core.recommendations.summarise",
        new=mock_summarise,
    ):
        await get_recommendations({"commits": 5})

    assert mock_summarise.called
    call_args = mock_summarise.call_args[0][0]
    # The prompt should reference the commit count
    assert "5" in call_args
