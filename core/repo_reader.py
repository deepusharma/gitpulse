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
import asyncio
import httpx

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


async def _get_local_commits(days:int=7) -> list:
    """
    Get the commits from local configuration for the duration of days provided 
    """
    # Using run_in_executor to keep local git (sync) from blocking the loop
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _get_local_commits_sync, days)

def _get_local_commits_sync(days:int=7) -> list:
    config = load_config()
    repos = config.get("repos", {})
    logger.debug("Repos: %s", str(repos))

    since = datetime.now(timezone.utc) - timedelta(days=days)
    logger.debug("Since: %s", str(since))

    commits=[]
    
    for name, path in repos.items():
        try:
            logger.debug("Repo: %s", name)
            repo=Repo(path)

            for commit in repo.iter_commits(since=since): 
                commits.append({
                    "repo":name,
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


async def _get_github_commits(days: int = 7, username: str = None, repos: list = None) -> list:
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

    since = datetime.now(timezone.utc) - timedelta(days=days)
    since_iso = since.isoformat()

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Semaphore to prevent GitHub secondary rate limits (max 3 concurrent)
    semaphore = asyncio.Semaphore(3)

    async def fetch_repo_commits(client: httpx.AsyncClient, repo: str, retries: int = 3) -> list:
        url = f"https://api.github.com/repos/{username}/{repo}/commits"
        params = {"since": since_iso, "per_page": 100}
        
        async with semaphore:
            for attempt in range(retries):
                try:
                    response = await client.get(url, headers=headers, params=params, timeout=30.0)
                    
                    if response.status_code == 404:
                        logger.error("Repo '%s/%s' not found or is private", username, repo)
                        return []
                    elif response.status_code in [429, 403]:
                        if attempt < retries - 1:
                            wait_time = (attempt + 1) * 0.5
                            logger.warning("GitHub Rate Limit hit for %s. Retrying in %ss...", repo, wait_time)
                            await asyncio.sleep(wait_time)
                            continue
                        logger.error("GitHub API rate limit exceeded permanently for %s", repo)
                        return []
                    
                    response.raise_for_status()
                    data = response.json()
                    return [
                        {
                            "repo": repo,
                            "message": commit["commit"]["message"],
                            "author": commit["commit"]["author"]["name"],
                            "date": datetime.fromisoformat(commit["commit"]["author"]["date"].replace("Z", "+00:00")),
                            "hash": commit["sha"]
                        }
                        for commit in data
                    ]
                except (httpx.RequestError, httpx.HTTPStatusError) as e:
                    if attempt < retries - 1:
                        logger.warning("Fetch error for %s (%s). Retrying...", repo, str(e))
                        await asyncio.sleep((attempt + 1) * 0.5)
                        continue
                    logger.error("Failed to fetch commits for %s after %s retries: %s", repo, retries, e)
                    return []
        return []

    async with httpx.AsyncClient() as client:
        # TRIGGER ALL REPO FETCHES SIMULTANEOUSLY
        tasks = [fetch_repo_commits(client, repo) for repo in repos]
        results = await asyncio.gather(*tasks)
        
    # Flatten the list of lists
    return [commit for repo_commits in results for commit in repo_commits]

async def get_commits(source: str = "local", days: int = 7, **kwargs) -> list:
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
        return await _get_local_commits(days=days)
    elif source == "github":
        return await _get_github_commits(days=days, **kwargs)
    else:
        logger.error("Unknown source: %s", source)
        raise ValueError(f"Unknown source: {source}")