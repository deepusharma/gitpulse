"""
Reads git repositories defined in ~/.gitpulse.toml and extracts
commit history for a given time period.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tomllib
from git import Repo, InvalidGitRepositoryError

import logging

logger = logging.getLogger(__name__)

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
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(config_path,"rb") as f:
        config=tomllib.load(f)

    return config.get("repos",{})


def get_commits(days:int=7) -> list:
    """
    Get the commits for the duration of days provided 
    
    Args: 
        days (int): Number of days to look back for commits. 7 by default

    Returns:
        list object containing the summaries of commit across each of these repos

    Raises:
        Exception: If Any errors found
    """
    #TODO Need to add the exception type in above comment
    
    repos = load_config()
    
    logger.debug ("Repos: %s", str(repos))

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
            logger.warning ("Error loading repo. Skipping %s: %s", name, e)
        except Exception as e:
            #TODO narrow down exception types
            logger.error ("Unexpected Error in loading repo %s: %s", name, e)
    return commits