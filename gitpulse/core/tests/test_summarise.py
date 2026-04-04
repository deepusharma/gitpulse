from datetime import datetime, timezone
from gitpulse.core.summarise import format_commits, to_prompt_str, to_display_str, build_prompt


# -----------------------------------------------------------------------------
# format_commits
# -----------------------------------------------------------------------------

def test_format_commits_empty():
    """format_commits returns empty dict when given empty list."""
    result = format_commits([])
    assert result == {}


def test_format_commits_single():
    """format_commits correctly cleans hash, date and message for a single commit."""
    commits = [
        {
            "repo": "gitpulse",
            "message": "feat: add summariser\n\nFirst pass.\n",
            "author": "Deepak Sharma",
            "date": datetime(2026, 3, 20, 10, 0, tzinfo=timezone.utc),
            "hash": "a1b2c3d4e5f6a1b2c3d4e5f6",
        }
    ]
    result = format_commits(commits)

    assert "gitpulse" in result
    assert len(result["gitpulse"]) == 1
    assert result["gitpulse"][0]["hash"] == "a1b2c3d"
    assert result["gitpulse"][0]["date"] == "2026-03-20"
    assert result["gitpulse"][0]["message"] == "feat: add summariser | First pass."


def test_format_commits_multiple_repos():
    """format_commits groups commits from different repos into separate keys."""
    commits = [
        {
            "repo": "gitpulse",
            "message": "feat: add cli\n",
            "author": "Deepak Sharma",
            "date": datetime(2026, 3, 20, 10, 0, tzinfo=timezone.utc),
            "hash": "a1b2c3d4e5f6a1b2c3d4e5f6",
        },
        {
            "repo": "dotfiles",
            "message": "chore: add vscode settings\n",
            "author": "Deepak Sharma",
            "date": datetime(2026, 3, 20, 11, 0, tzinfo=timezone.utc),
            "hash": "b2c3d4e5f6a1b2c3d4e5f6a1",
        }
    ]
    result = format_commits(commits)

    assert "gitpulse" in result
    assert "dotfiles" in result
    assert len(result["gitpulse"]) == 1
    assert len(result["dotfiles"]) == 1


def test_format_commits_multiple_commits_same_repo():
    """format_commits groups multiple commits from the same repo into one key."""
    commits = [
        {
            "repo": "gitpulse",
            "message": "feat: add cli\n",
            "author": "Deepak Sharma",
            "date": datetime(2026, 3, 20, 10, 0, tzinfo=timezone.utc),
            "hash": "a1b2c3d4e5f6a1b2c3d4e5f6",
        },
        {
            "repo": "gitpulse",
            "message": "fix: handle empty commits\n",
            "author": "Deepak Sharma",
            "date": datetime(2026, 3, 20, 11, 0, tzinfo=timezone.utc),
            "hash": "b2c3d4e5f6a1b2c3d4e5f6a1",
        }
    ]
    result = format_commits(commits)

    assert "gitpulse" in result
    assert len(result["gitpulse"]) == 2


# -----------------------------------------------------------------------------
# to_prompt_str
# -----------------------------------------------------------------------------

def test_to_prompt_str_empty():
    """to_prompt_str returns empty string when given empty dict."""
    result = to_prompt_str({})
    assert result == ""


def test_to_prompt_str_contains_repo_and_commit():
    """to_prompt_str output contains repo header and commit details."""
    formatted = {
        "gitpulse": [
            {"hash": "a1b2c3d", "date": "2026-03-20", "message": "feat: add cli"}
        ]
    }
    result = to_prompt_str(formatted)

    assert "### gitpulse" in result
    assert "a1b2c3d" in result
    assert "2026-03-20" in result
    assert "feat: add cli" in result


# -----------------------------------------------------------------------------
# to_display_str
# -----------------------------------------------------------------------------

def test_to_display_str_empty():
    """to_display_str returns empty string when given empty dict."""
    result = to_display_str({})
    assert result == ""


def test_to_display_str_contains_repo_and_commit():
    """to_display_str output contains repo header, hash, date and message lines."""
    formatted = {
        "gitpulse": [
            {"hash": "a1b2c3d", "date": "2026-03-20", "message": "feat: add cli | First pass."}
        ]
    }
    result = to_display_str(formatted)

    assert "### gitpulse" in result
    assert "a1b2c3d" in result
    assert "2026-03-20" in result
    assert "feat: add cli" in result
    assert "First pass." in result


# -----------------------------------------------------------------------------
# build_prompt
# -----------------------------------------------------------------------------

def test_build_prompt_contains_commit_data():
    """build_prompt output contains the commit data passed in."""
    prompt_str = "### gitpulse\n  - a1b2c3d | 2026-03-20 | feat: add cli\n"
    result = build_prompt(prompt_str)

    assert "### gitpulse" in result
    assert "feat: add cli" in result


def test_build_prompt_contains_sections():
    """build_prompt output contains all four required standup sections."""
    prompt_str = "### gitpulse\n  - a1b2c3d | 2026-03-20 | feat: add cli\n"
    result = build_prompt(prompt_str)

    assert "WHAT I DID" in result
    assert "DETAILS" in result
    assert "WHATS NEXT" in result
    assert "BLOCKERS" in result