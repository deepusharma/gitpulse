import pytest
from unittest.mock import patch, MagicMock
from core.repo_reader import _get_local_commits_sync, load_config
from git import InvalidGitRepositoryError

def test_get_local_commits_invalid_repo(tmp_path):
    """Verify core logic handles non-git directories gracefully."""
    # Create a non-git directory
    non_git_dir = tmp_path / "not-a-repo"
    non_git_dir.mkdir()
    
    mock_config = {"repos": {"bad-repo": str(non_git_dir)}}
    
    with patch("core.repo_reader.load_config", return_value=mock_config):
        # Should not raise exception, but return empty list (logging the warning)
        commits = _get_local_commits_sync(days=7)
        assert commits == []

def test_get_local_commits_empty_period(tmp_path):
    """Verify core logic handles repositories with no commits in the last N days."""
    import git
    repo_dir = tmp_path / "empty-repo"
    repo = git.Repo.init(repo_dir)
    
    # No commits yet
    mock_config = {"repos": {"empty": str(repo_dir)}}
    
    with patch("core.repo_reader.load_config", return_value=mock_config):
        # Should return empty list gracefully
        commits = _get_local_commits_sync(days=7)
        assert commits == []

def test_load_config_malformed_toml(tmp_path):
    """Verify behavior with a malformed .gitpulse.toml file."""
    config_file = tmp_path / ".gitpulse.toml"
    config_file.write_text("[repos\ninvalid-toml")
    
    with patch("pathlib.Path.home", return_value=tmp_path):
        with pytest.raises(Exception): # tomllib.TOMLDecodeError or similar
            load_config()
