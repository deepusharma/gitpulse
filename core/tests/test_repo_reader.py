import pytest
import os
import respx
import httpx
from core.repo_reader import load_config, get_commits

local_integration = pytest.mark.skipif(
    not os.path.exists(os.path.expanduser("~/.gitpulse.toml")),
    reason="~/.gitpulse.toml not found — skipping integration tests"
)

# -----------------------------------------------------------------------------
# load_config
# -----------------------------------------------------------------------------

@local_integration
def test_load_config_returns_dict():
    """load_config returns a dict."""
    result = load_config()
    assert isinstance(result, dict)

@local_integration
def test_load_config_has_repos():
    """load_config returns at least one repo."""
    result = load_config()
    assert len(result) > 0


# -----------------------------------------------------------------------------
# get_commits
# -----------------------------------------------------------------------------

@pytest.mark.anyio
@local_integration
async def test_get_commits_returns_list():
    """get_commits returns a tuple (list, list)."""
    result, errors = await get_commits(days=1)
    assert isinstance(result, list)
    assert isinstance(errors, list)

@pytest.mark.anyio
@local_integration
async def test_get_commits_commit_has_required_keys():
    """Each commit dict has the required keys."""
    result, errors = await get_commits(days=15)
    if result:
        commit = result[0]
        assert "repo" in commit
        assert "message" in commit
        assert "author" in commit
        assert "date" in commit
        assert "hash" in commit

# -----------------------------------------------------------------------------
# Github API Adapter
# -----------------------------------------------------------------------------

@pytest.mark.anyio
@respx.mock
async def test_get_commits_github_returns_list():
    respx.get(
        url__regex=r"https://api\.github\.com/repos/deepusharma/gitpulse/commits.*"
    ).respond(
        json=[{
            "sha": "a1b2c3d",
            "commit": {
                "message": "test message",
                "author": {"name": "Test Author", "date": "2026-03-21T10:00:00Z"}
            }
        }]
    )
    result, errors = await get_commits(source="github", username="deepusharma", repos=["gitpulse"], days=7)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["repo"] == "gitpulse"
    assert result[0]["hash"] == "a1b2c3d"
    assert result[0]["author"] == "Test Author"
    assert result[0]["message"] == "test message"

@pytest.mark.anyio
async def test_get_commits_github_empty_repo():
    result, errors = await get_commits(source="github", username="deepusharma", repos=[])
    assert result == []
    assert errors == []

@pytest.mark.anyio
async def test_get_commits_github_invalid_source_raises():
    with pytest.raises(ValueError, match="Unknown source: unknown"):
        await get_commits(source="unknown")

@pytest.mark.anyio
@respx.mock
async def test_get_commits_github_404_returns_error():
    respx.get(
        url__regex=r"https://api\.github\.com/repos/deepusharma/nonexistent/commits.*"
    ).respond(status_code=404)
    result, errors = await get_commits(source="github", username="deepusharma", repos=["nonexistent"], days=7)
    assert len(errors) == 1
    assert "not found" in errors[0]

@pytest.mark.anyio
@respx.mock
async def test_get_commits_github_429_returns_error():
    respx.get(
        url__regex=r"https://api\.github\.com/repos/deepusharma/gitpulse/commits.*"
    ).respond(status_code=429)
    result, errors = await get_commits(source="github", username="deepusharma", repos=["gitpulse"], days=7)
    assert len(errors) == 1
    assert "rate limit" in errors[0].lower()