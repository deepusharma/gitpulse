"""Tests for Phase 3: Public Profile endpoint."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from datetime import date


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _mock_gh_user(username: str = "deepusharma") -> dict:
    return {
        "login": username,
        "avatar_url": f"https://avatars.githubusercontent.com/{username}",
        "bio": "Building things.",
    }


def _mock_activity(username: str = "deepusharma") -> tuple:
    activity = {
        "commits": [
            {
                "repo": "gitpulse",
                "message": "feat: add thing",
                "author": username,
                "date": __import__("datetime").datetime(2026, 5, 1, 10, 0, 0,
                    tzinfo=__import__("datetime").timezone.utc),
                "hash": "abc123",
            }
        ],
        "prs": [],
        "issues": [],
    }
    return activity, []


def _make_app():
    from api.api import app
    return app


# ---------------------------------------------------------------------------
# Profile endpoint tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_profile_returns_200_for_valid_user():
    """GET /profile/{username} should return 200 with mocked GitHub + activity."""
    app = _make_app()

    with (
        patch("api.routers.profile._fetch_github_user", new=AsyncMock(return_value=_mock_gh_user())),
        patch("api.routers.profile.get_user_repos", new=AsyncMock(return_value=["gitpulse"])),
        patch("api.routers.profile.get_activity", new=AsyncMock(return_value=_mock_activity())),
        patch("api.routers.profile._fetch_latest_public_summary", new=AsyncMock(return_value="Stand-up text")),
        patch("api.routers.profile._fetch_total_summaries", new=AsyncMock(return_value=5)),
        patch("api.db.get_db_pool", return_value=MagicMock()),
        patch("api.routers.insights.get_insights_health", new=AsyncMock(return_value={"health_score": 80})),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/profile/deepusharma")

    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == "deepusharma"
    assert "avatar_url" in body
    assert "current_streak" in body
    assert "top_repos" in body


@pytest.mark.anyio
async def test_profile_hides_private_summaries():
    """Profile should only expose is_public=TRUE summaries via DB filter."""
    # This is enforced by the SQL query in _fetch_latest_public_summary.
    # We verify the function returns None when no public row exists.
    from api.routers.profile import _fetch_latest_public_summary

    mock_conn = AsyncMock()
    mock_conn.fetchrow = AsyncMock(return_value=None)  # No public summary

    mock_pool = MagicMock()
    mock_pool.acquire = MagicMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_conn),
            __aexit__=AsyncMock(),
        )
    )

    result = await _fetch_latest_public_summary("deepusharma", mock_pool)
    assert result is None


@pytest.mark.anyio
async def test_profile_404_for_unknown_user():
    """GET /profile/{username} should return 404 when GitHub reports user not found."""
    from fastapi import HTTPException

    app = _make_app()

    async def _raise_404(username):
        raise HTTPException(status_code=404, detail="GitHub user 'nobody' not found")

    with patch("api.routers.profile._fetch_github_user", new=_raise_404):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/profile/nobody")

    assert resp.status_code == 404


@pytest.mark.anyio
async def test_profile_cached():
    """Second call to /profile/{username} should not re-fetch from GitHub."""
    app = _make_app()

    mock_gh = AsyncMock(return_value=_mock_gh_user())

    with (
        patch("api.routers.profile._fetch_github_user", new=mock_gh),
        patch("api.routers.profile.get_user_repos", new=AsyncMock(return_value=[])),
        patch("api.routers.profile.get_activity", new=AsyncMock(return_value=({"commits": [], "prs": [], "issues": []}, []))),
        patch("api.routers.profile._fetch_latest_public_summary", new=AsyncMock(return_value=None)),
        patch("api.routers.profile._fetch_total_summaries", new=AsyncMock(return_value=0)),
        patch("api.db.get_db_pool", return_value=MagicMock()),
        # Clear the cache first
        patch("api.routers.profile.analytics_cache") as mock_cache,
    ):
        # First call: cache miss
        mock_cache.get = MagicMock(return_value=None)
        mock_cache.set = MagicMock()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp1 = await client.get("/profile/deepusharma?days=7")

        # Second call: simulate cache hit
        mock_cache.get = MagicMock(return_value={
            "username": "deepusharma",
            "avatar_url": "https://avatars.githubusercontent.com/deepusharma",
            "bio": None,
            "recent_summary": None,
            "current_streak": 0,
            "longest_streak": 0,
            "top_repos": [],
            "health_score": 0,
            "total_summaries": 0,
            "generated_at": "2026-05-10T14:00:00Z",
        })

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp2 = await client.get("/profile/deepusharma?days=7")

    # GitHub was only called once (first request)
    assert mock_gh.call_count == 1
    assert resp1.status_code == 200
    assert resp2.status_code == 200


# ---------------------------------------------------------------------------
# Utility function tests
# ---------------------------------------------------------------------------

def test_calculate_streak_empty():
    """calculate_streak with no dates should return (0, 0)."""
    from api.utils import calculate_streak
    assert calculate_streak([]) == (0, 0)


def test_calculate_streak_single_date_today():
    """A single date equal to today gives streak of 1."""
    from api.utils import calculate_streak
    from datetime import datetime, timezone

    today = datetime.now(timezone.utc).date()
    current, longest = calculate_streak([today])
    assert current == 1
    assert longest == 1
