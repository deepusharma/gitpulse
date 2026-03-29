"""
Reads git repositories defined in ~/.gitpulse.toml and extracts
commit history for a given time period.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tomllib
import os

os.environ["GIT_PYTHON_REFRESH"] = "quiet"
from git import Repo, InvalidGitRepositoryError

import logging

logger = logging.getLogger(__name__)

import httpx
import os

def load_config() -> dict:

    """
    Load the repos from ~/.gitpulse.toml.  
    
    Returns:
        dict object containing the path to git repos definedin ~/.gitpulse.toml 

    Raises:
        FileNotFoundError: If the ~/.gitpulse.toml file is not found
    """
    
    config_path = Path.home() / ".gitpulse.toml"
    if not config_path.exists():
        logger.error("Config file not found at %s", config_path)
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(config_path,"rb") as f:
        config=tomllib.load(f)

    return config


def _get_local_commits(days:int=7) -> list:
    """
    Get the commits from local configuration for the duration of days provided 
    """
    config = load_config()
    repos = config.get("repos", {})
    logger.debug("Repos: %s", str(repos))

    since = datetime.now(timezone.utc) - timedelta(days=days)
    logger.debug("Since: %s", str(since))

    commits=[]
    
    for name, path in repos.items():
        try:
            logger.debug("Repo: %s", name)
            logger.debug("Path: %s", path)

            repo=Repo(path)

            for commit in repo.iter_commits(since=since): 
                logger.debug("Commits: %s", str(commit))

                commits.append({"repo":name,
                "message":commit.message, 
                "author":commit.author.name,
                "date":commit.committed_datetime,            
                "hash":commit.hexsha,
                })
        except (InvalidGitRepositoryError, FileNotFoundError) as e:
            logger.warning("Error loading repo. Skipping %s: %s", name, e, exc_info=True)
        except Exception as e:
            logger.error("msg: %s", e, exc_info=True)
    return commits


def _get_github_commits(days: int = 7, username: str = None, repos: list = None) -> list:
    """
    Get the commits from GitHub API for the duration of days provided.
    
    Args:
        days (int): Number of days to look back for commits. Defaults to 7.
        username (str): The GitHub username.
        repos (list): List of repository names.
        
    Returns:
        list: List of commit dicts from the given repositories.
    """
    if not username or not repos:
        return []

    commits = []
    since = datetime.now(timezone.utc) - timedelta(days=days)
    since_iso = since.isoformat()

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    with httpx.Client() as client:
        for repo in repos:
            url = f"https://api.github.com/repos/{username}/{repo}/commits"
            params = {
                "since": since_iso,
                "per_page": 100
            }
            try:
                response = client.get(url, headers=headers, params=params)

                if response.status_code == 404:
                    logger.error("Repo '%s/%s' not found or is private", username, repo)
                    raise ValueError(f"Repo '{username}/{repo}' not found or is private")
                elif response.status_code == 429:
                    logger.error("GitHub API rate limit exceeded")
                    raise ValueError("GitHub API rate limit exceeded")
                elif response.status_code == 401:
                    logger.error("GitHub API unauthorised — check GITHUB_TOKEN")
                    raise ValueError("GitHub API unauthorised — check GITHUB_TOKEN")

                response.raise_for_status()

                data = response.json()
                for commit in data:
                    commits.append({
                        "repo": repo,
                        "message": commit["commit"]["message"],
                        "author": commit["commit"]["author"]["name"],
                        "date": datetime.fromisoformat(commit["commit"]["author"]["date"]),
                        "hash": commit["sha"]
                    })
            except httpx.RequestError as e:
                logger.error("Network error while requesting %s: %s", url, e, exc_info=True)
                raise
            except httpx.HTTPStatusError as e:
                logger.error("HTTP error %s while requesting %s: %s", response.status_code, url, e, exc_info=True)
                raise

    return commits

def get_commits(source: str = "local", days: int = 7, **kwargs) -> list:
    """
    Get the commits for the duration of days provided 
    
    Args: 
        source (str): "local" or "github".
        days (int): Number of days to look back for commits. 7 by default

    Returns:
        list object containing the summaries of commit across each of these repos

    Raises:
        Exception: If Any errors found
    """
    if source == "local":
        return _get_local_commits(days=days)
    elif source == "github":
        return _get_github_commits(days=days, **kwargs)
    else:
        logger.error("Unknown source: %s", source)
        raise ValueError(f"Unknown source: {source}")