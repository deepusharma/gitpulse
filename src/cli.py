import logging
import argparse
import os

from repo_reader import get_commits
from summarise import format_commits, to_prompt_str, to_display_str, build_prompt, summarise
from utils import load_env


logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

# 1. import argparse, logging, and all functions from summarise, repo_reader, utils
# 2. parse --days and --debug args
# 3. set logging level based on --debug flag
# 4. load_env()
# 5. get_commits(days)
# 6. format_commits(commits)
# 7. to_display_str -> print
# 8. to_prompt_str -> build_prompt -> summarise -> print

if __name__ == "__main__":    
    
    parser = argparse.ArgumentParser(description="GitPulse — weekly standup generator")
    parser.add_argument("--days", type=int, default=7, help="Number of days to look back (default: 7)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--output", default="output/summary.md", help="Output file path")
    parser.add_argument("--repo", default=None, help="Repo name to filter")
    
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.WARNING
    logging.basicConfig(level=log_level)

    load_env()

    # 1. receives a FLAT LIST of commit dicts from repo_reader.get_commits
    commits = get_commits(args.days)
    #logger.debug("Commits: %s", str(commits))

    if args.repo:
        commits = [c for c in commits if c["repo"] == args.repo]
        logger.debug("Filtered commits for repo: %s", args.repo)
        if not commits:
            logger.warning("No commits found for repo: %s", args.repo)



    # 2. format_commits: groups by repo, cleans messages -> returns dict
    logger.debug("Formatted Commits: START")
    formatted_commits = format_commits(commits)
    #logger.debug("Formatted Commits:\n%s", json.dumps(formatted_commits, indent=2, default=str))

    # 3. to_prompt_str: converts dict -> compact string for LLM
    prompt_str = to_prompt_str(formatted_commits)
    logger.debug("Prompt String: %s", str(prompt_str))

    display_str = to_display_str(formatted_commits)
    logger.debug("Display String: %s", str(display_str))
    print("Display String: " + str(display_str))            # noqa: T201

    # 4. build_prompt: wraps string into full LLM prompt
    prompt = build_prompt(prompt_str)
    logger.debug("Prompt: %s", str(prompt))


    # 5. summarise: orchestrates 2-4, calls Groq, returns summary string
    summary = summarise(prompt)
    logger.debug("Summary: \n%s", str(summary))
    print("Summary: "+ str(summary))        # noqa: T201

    # 6. write summary to file
    os.makedirs(os.path.dirname(args.output) or "output", exist_ok=True)
    with open(args.output, "w") as f:
        f.write(summary)
    logger.debug("Summary written to %s", args.output)