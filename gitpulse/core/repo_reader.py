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


async def _get_local_commits(days:int=7) -> tuple[list, list]:
    """
    Get the commits from local configuration for the duration of days provided.
    Returns (commits, errors).
    """
    # Using run_in_executor to keep local git (sync) from blocking the loop
    loop = asyncio.get_running_loop()
    commits = await loop.run_in_executor(None, _get_local_commits_sync, days)
    return commits, []

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


async def _fetch_commits(
    client: httpx.AsyncClient,
    repo: str,
    username: str,
    since_iso: str,
    headers: dict,
    semaphore: asyncio.Semaphore,
) -> tuple[list, str | None]:
    """Fetch commits for a repo from GitHub."""
    retries = 3
    url = f"https://api.github.com/repos/{username}/{repo}/commits"
    params = {"since": since_iso, "per_page": 100}
    
    async with semaphore:
        for attempt in range(retries):
            try:
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
                
                if response.status_code == 404:
                    error_msg = f"Repo '{username}/{repo}' not found or is private"
                    logger.error(error_msg)
                    return [], error_msg
                elif response.status_code in [429, 403]:
                    if attempt < retries - 1:
                        wait_time = (attempt + 1) * 0.5
                        logger.warning("GitHub Rate Limit hit for %s. Retrying in %ss...", repo, wait_time)
                        await asyncio.sleep(wait_time)
                        continue
                    error_msg = "GitHub API rate limit exceeded permanently"
                    logger.error("%s for %s", error_msg, repo)
                    return [], error_msg
                
                response.raise_for_status()
                data = response.json()
                commits = [
                    {
                        "repo": repo,
                        "message": commit["commit"]["message"],
                        "author": commit["commit"]["author"]["name"],
                        "date": datetime.fromisoformat(commit["commit"]["author"]["date"].replace("Z", "+00:00")),
                        "hash": commit["sha"]
                    }
                    for commit in data
                ]
                return commits, None
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if attempt < retries - 1:
                    logger.warning("Fetch error for %s (%s). Retrying...", repo, str(e))
                    await asyncio.sleep((attempt + 1) * 0.5)
                    continue
                error_msg = f"Failed to fetch commits for {repo}: {str(e)}"
                logger.error(error_msg)
                return [], error_msg
    return [], "Unknown error"

async def _fetch_prs(
    client: httpx.AsyncClient,
    repo: str,
    username: str,
    since: datetime,
    headers: dict,
    semaphore: asyncio.Semaphore,
) -> tuple[list, str | None]:
    """Fetch closed pull requests for a repo from GitHub."""
    retries = 3
    url = f"https://api.github.com/repos/{username}/{repo}/pulls"
    params = {"state": "closed", "sort": "updated", "direction": "desc", "per_page": 50}
    
    async with semaphore:
        for attempt in range(retries):
            try:
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
                if response.status_code in [404, 429, 403]: return [], None
                response.raise_for_status()
                data = response.json()
                prs = []
                for pr in data:
                    if pr.get("merged_at"):
                        merged_at = datetime.fromisoformat(pr["merged_at"].replace("Z", "+00:00"))
                        if merged_at >= since:
                            prs.append({
                                "repo": repo,
                                "title": pr["title"],
                                "number": pr["number"],
                                "merged_at": merged_at,
                                "url": pr["html_url"]
                            })
                return prs, None
            except Exception:
                return [], None
    return [], None

async def _fetch_issues(
    client: httpx.AsyncClient,
    repo: str,
    username: str,
    since: datetime,
    headers: dict,
    semaphore: asyncio.Semaphore,
) -> tuple[list, str | None]:
    """Fetch closed issues for a repo from GitHub."""
    retries = 3
    url = f"https://api.github.com/repos/{username}/{repo}/issues"
    params = {"state": "closed", "sort": "updated", "direction": "desc", "per_page": 50}
    
    async with semaphore:
        for attempt in range(retries):
            try:
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
                if response.status_code in [404, 429, 403]: return [], None
                response.raise_for_status()
                data = response.json()
                issues = []
                for issue in data:
                    # Skip if it's a PR masquerading as an issue
                    if "pull_request" not in issue and issue.get("closed_at"):
                        closed_at = datetime.fromisoformat(issue["closed_at"].replace("Z", "+00:00"))
                        if closed_at >= since:
                            issues.append({
                                "repo": repo,
                                "title": issue["title"],
                                "number": issue["number"],
                                "closed_at": closed_at,
                                "url": issue["html_url"]
                            })
                return issues, None
            except Exception:
                return [], None
    return [], None


async def _get_github_commits(days: int = 7, username: str = None, repos: list = None, token: str = None) -> tuple[dict, list]:
    """
    Get the commits from GitHub API for the duration of days provided.
    
    Args:
        days (int): Number of days to look back for commits. Defaults to 7.
        username (str): The GitHub username.
        repos (list): List of repository names.
        token (str): Optional GitHub access token to override default.
        
    Returns:
        tuple[dict, list]: (dict of activity lists, list of error strings).
    """
    if not username or not repos:
        return {"commits": [], "prs": [], "issues": []}, []

    since = datetime.now(timezone.utc) - timedelta(days=days)
    since_iso = since.isoformat()

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    # Use provided token or fall back to GITHUB_TOKEN env var
    auth_token = token or os.getenv("GITHUB_TOKEN")
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    # Semaphore to prevent GitHub secondary rate limits (max 3 concurrent)
    semaphore = asyncio.Semaphore(3)

    async with httpx.AsyncClient() as client:
        # TRIGGER ALL REPO FETCHES SIMULTANEOUSLY
        commit_tasks = [_fetch_commits(client, repo, username, since_iso, headers, semaphore) for repo in repos]
        pr_tasks = [_fetch_prs(client, repo, username, since, headers, semaphore) for repo in repos]
        issue_tasks = [_fetch_issues(client, repo, username, since, headers, semaphore) for repo in repos]
        
        commit_results = await asyncio.gather(*commit_tasks)
        pr_results = await asyncio.gather(*pr_tasks)
        issue_results = await asyncio.gather(*issue_tasks)
        
    all_commits = []
    all_prs = []
    all_issues = []
    all_errors = []
    
    for res_commits, error in commit_results:
        all_commits.extend(res_commits)
        if error:
            all_errors.append(error)
            
    for res_prs, _ in pr_results:
        all_prs.extend(res_prs)
        
    for res_issues, _ in issue_results:
        all_issues.extend(res_issues)
            
    return {"commits": all_commits, "prs": all_prs, "issues": all_issues}, all_errors
async def get_activity(source: str = "local", days: int = 7, username: str = None, repos: list[str] = None, **kwargs) -> tuple[dict, list]:
    """
    Get the activity (commits, PRs, issues) for the duration of days provided 
    
    Args: 
        source (str): "local" or "github".
        days (int): Number of days to look back. 7 by default
        username (str): The GitHub username
        repos (list[str]): The repositories to fetch

    Returns:
        tuple[dict, list]: (dict of activity lists, list of error strings).

    Raises:
        Exception: If Any errors found
    """
    if repos is not None and not repos:
        return {"commits": [], "prs": [], "issues": []}, []

    if source == "local":
        commits, err = await _get_local_commits(days=days)
        return {"commits": commits, "prs": [], "issues": []}, err
    elif source == "github":
        return await _get_github_commits(days=days, username=username, repos=repos, **kwargs)
    else:
        logger.error("Unknown source: %s", source)
        raise ValueError(f"Unknown source: {source}")