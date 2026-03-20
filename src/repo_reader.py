from datetime import datetime, timedelta, timezone
from pathlib import Path
import tomllib;
from git import Repo, InvalidGitRepositoryError


# -----------------------------------------------------------------------------
# load_config
# -----------------------------------------------------------------------------
def load_config() -> dict:
    """Load the repos from TOML File"""
    config_path = Path.home() / ".gitpulse.toml"
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(config_path,"rb") as f:
        config=tomllib.load(f)

    return config.get("repos",{})


# -----------------------------------------------------------------------------
# get_commits
# -----------------------------------------------------------------------------
def get_commits(days:int=7) -> dict:
    
    repos = load_config()
    print("Repos" + str(repos))

    since = datetime.now() - timedelta(days=5)
    print("Since: " + str(since))

    commits=[]
    #return commits

    for name, path in repos.items():
        try:
            repo=Repo(path)
            print("Repo: " + name)
            print("Path: " + path)
            print("Commits: " + str(repo.iter_commits(since=since)))
            
            commits.extend(repo.iter_commits(since=since))

        except Exception as e:
            print(f"Error loading repo {name}: {e}")
    return commits
    
# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
#print(load_config())
get_commits(15)
