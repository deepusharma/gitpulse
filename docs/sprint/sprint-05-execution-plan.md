# Sprint 05 Execution Plan: CLI Polish & Config Defaults

## Overview
This document outlines the execution steps for Sprint 05 to implement `--dry-run`, config defaults, and enhanced error handling in the CLI.

## Step-by-Step Plan

### 1. Update Config Loading (`core/repo_reader.py`)
- Modify `load_config()` to return the entire `config` dictionary instead of just the `repos` section.
- Update `_get_local_commits()` so that it accesses `repos = load_config().get("repos", {})` instead.

### 2. Overhaul CLI Argument Parsing (`cli/cli.py`)
- Import `load_config` from `core.repo_reader` into `cli/cli.py`.
- Parse the `~/.gitpulse.toml` to extract `[defaults]`.
- Update `argparse.ArgumentParser` to default to `None` for arguments like `--days`, `--output`, and `--repo`.
- Merge argument prioritisation: 
  `CLI passed argument` > `config [defaults]` > `Hardcoded system default`.
- Add `--dry-run` flag (`action="store_true"`) to argparse.

### 3. Improve Error Messages (`cli/cli.py` & `core/utils.py`)
- **Missing Config**: Wrap `load_config()` in a `try/except FileNotFoundError` block in `cli.py`. On failure, exit with: `"~/.gitpulse.toml not found. Run gitpulse init to set up."`
- **Repo Not Found**: If a `--repo <name>` flag is used, verify it exists in `config.get('repos', {})`. If missing, exit with: `"Repo '<name>' not found in ~/.gitpulse.toml. Add it under [repos]."`
- **Missing API Key**: Ensure `GROQ_API_KEY` presence is checked before the LLM step (so `--dry-run` can still function without it). If missing during normal run, exit with: `"GROQ_API_KEY not set. Add it to .env or export it."`
- **No Commits**: After `commits = get_commits()`, check if the list is empty. If so, exit with: `"No commits found for the last N days. Try --days 30."`

### 4. Implement Dry Run Mode (`cli/cli.py`)
- Follow the normal execution flow to fetch and format commits.
- Print the `display_str`.
- If `args.dry_run` is True, output `"dry-run mode — skipping LLM call"`, bypass the LLM calls (`build_prompt` and `summarise`), skip file writing, and exit successfully.

### 5. Automated Tests (`cli/tests/test_cli.py`)
- Add a test that proves the CLI respects config defaults when flags are missing.
- Add a test that verifies CLI flags correctly override config default values.
- Add a test verifying `--dry-run` executes without attempting to call the Groq model.

## Risks & Dependencies
- Altering the return type of `load_config()` will impact `_get_local_commits()`. We must ensure we update its consumption correctly, while leaving `_get_github_commits()` unharmed.
- `argparse` can mask whether a default came from the command line or from instantiation. We must set defaults to `None` or use `set_defaults()` using the config so we correctly identify overrides.

This systematic approach secures full coverage of the sprint stories without regression.
