"""
Reads git repositories defined in ~/.gitpulse.toml and extracts
commit history for a given time period.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tomllib
from git import Repo, InvalidGitRepositoryError

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
    
    #OPTIMIZE Move to proper logger and get rid of print statements
    print("Repos" + str(repos))

    since = datetime.now(timezone.utc) - timedelta(days=days)
    print("Since: " + str(since))

    commits=[]
    
    for name, path in repos.items():
        try:
            print("Repo: " + name)
            print("Path: " + path)

            repo=Repo(path)

            for commit in repo.iter_commits(since=since): 
                print("Commits: " + str(commit))

                commits.append({"repo":name,
                "message":commit.message, 
                "author":commit.author.name,
                "date":commit.committed_datetime,            
                "hash":commit.hexsha,
                })
        except (InvalidGitRepositoryError, FileNotFoundError) as e:
            print(f"Error loading repo {name}: {e}")
        except Exception as e:
            #TODO narrow down exception types
            print(f"Error loading repo {name}: {e}")
    return commits
    
# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
#print(load_config())
#NOTE Need to review this later 
commits = get_commits(15)
print("(main) All Commits: " + str(commits))
