import pytest
import os
from core.repo_reader import load_config, get_commits

pytestmark = pytest.mark.skipif(
    not os.path.exists(os.path.expanduser("~/.gitpulse.toml")),
    reason="~/.gitpulse.toml not found — skipping integration tests"
)
# -----------------------------------------------------------------------------
# load_config
# -----------------------------------------------------------------------------

def test_load_config_returns_dict():
    """load_config returns a dict."""
    result = load_config()
    assert isinstance(result, dict)


def test_load_config_has_repos():
    """load_config returns at least one repo."""
    result = load_config()
    assert len(result) > 0


# -----------------------------------------------------------------------------
# get_commits
# -----------------------------------------------------------------------------

def test_get_commits_returns_list():
    """get_commits returns a list."""
    result = get_commits(days=1)
    assert isinstance(result, list)


def test_get_commits_commit_has_required_keys():
    """Each commit dict has the required keys."""
    result = get_commits(days=15)
    if result:
        commit = result[0]
        assert "repo" in commit
        assert "message" in commit
        assert "author" in commit
        assert "date" in commit
        assert "hash" in commit