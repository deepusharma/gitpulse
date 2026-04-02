import logging
import argparse
import sys
import os

from core.repo_reader import get_commits, load_config
from core.summarise import format_commits, to_prompt_str, to_display_str, build_prompt, summarise
from core.utils import load_env


import asyncio

logger = logging.getLogger(__name__)

async def main():
    parser = argparse.ArgumentParser(description="GitPulse — weekly standup generator")
    parser.add_argument("--days", type=int, default=None, help="Number of days to look back")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--output", default=None, help="Output file path")
    parser.add_argument("--repo", default=None, help="Repo name to filter")
    parser.add_argument("--dry-run", action="store_true", help="Show commits without calling Groq API")
    
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.WARNING
    logging.basicConfig(level=log_level)

    try:
        config = load_config()
    except FileNotFoundError:
        print("~/.gitpulse.toml not found. Run gitpulse init to set up.")
        sys.exit(1)

    defaults = config.get("defaults", {})
    
    # Priority: args > defaults > hardcoded
    days = args.days if args.days is not None else defaults.get("days", 7)
    output = args.output if args.output is not None else defaults.get("output", "output/summary.md")
    repo = args.repo if args.repo is not None else defaults.get("repo")
    
    if repo:
        repos = config.get("repos", {})
        if repo not in repos:
            print(f"Repo '{repo}' not found in ~/.gitpulse.toml. Add it under [repos].")
            sys.exit(1)

    # load env, check keys only if not dry-run
    try:
        load_env(check_keys=not args.dry_run)
    except EnvironmentError:
        print("GROQ_API_KEY not set. Add it to .env or export it.")
        sys.exit(1)

    commits, errors = await get_commits(source="local", days=days)
    if errors:
        for error in errors:
            print(f"Error: {error}")
    
    if repo:
        commits = [c for c in commits if c["repo"] == repo]

    if not commits:
        print(f"No commits found for the last {days} days. Try --days 30.")
        sys.exit(1)

    logger.debug("Formatted Commits: START")
    formatted_commits = format_commits(commits)

    display_str = to_display_str(formatted_commits)
    print("Display String:\n" + str(display_str))

    if args.dry_run:
        print("dry-run mode — skipping LLM call")
        sys.exit(0)

    prompt_str = to_prompt_str(formatted_commits)
    prompt = build_prompt(prompt_str)

    summary = await summarise(prompt)
    print("Summary:\n"+ str(summary))

    os.makedirs(os.path.dirname(output) or "output", exist_ok=True)
    with open(output, "w") as f:
        f.write(summary)
    logger.debug("Summary written to %s", output)

if __name__ == "__main__":    
    asyncio.run(main())