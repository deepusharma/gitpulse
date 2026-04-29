# Sprint 21 Plan: Release Hardening & Packaging

## Overview
This plan outlines the technical steps to execute Sprint 21, focusing on automating PyPI publishing via GitHub Actions and improving CLI resilience through pre-flight environment checks.

## Phase 1: Automated PyPI Publishing (#103)

### Step 1.1: Create Publish Workflow
**File:** `.github/workflows/publish.yml`
- Define a GitHub Action triggered on `push: tags: ['v*']`.
- **Jobs:**
  1. `test`: Run `uv sync --extra dev` and `uv run pytest -v` to ensure the codebase is stable.
  2. `publish`: Depends on `test`. Requires the `pypi` environment.
- **Publish Steps:**
  - Checkout code.
  - Setup Python using `actions/setup-python@v5`.
  - Install `uv`.
  - Build the package: `uv build`.
  - Publish to PyPI: `pypa/gh-action-pypi-publish@release/v1`.

## Phase 2: CLI Resilience (#220)

### Step 2.1: Pre-flight Environment Checks
**File:** `gitpulse/cli/cli.py`
- Modify the `generate` function to validate the environment *before* invoking `get_activity`.
- **Check 1:** Verify `GROQ_API_KEY` exists. If not, use `rich.panel.Panel` to display a user-friendly, actionable error message explaining how to get a key and where to set it. Exit with code 1.
- **Check 2 (Warning):** If `source="github"` is implied (or if we later add CLI flags for remote generation) and `GITHUB_TOKEN` is missing, print a `rich` warning about potential rate limits, but continue execution.

### Step 2.2: Refine Configuration Loading
**File:** `gitpulse/core/repo_reader.py` (or `cli.py` where config is loaded)
- Ensure the `load_config` function (or its caller in `cli.py`) handles malformed TOML files gracefully.
- If `tomllib.TOMLDecodeError` (or equivalent) occurs, catch it and instruct the user to run `gitpulse init` or fix their `~/.gitpulse.toml` syntax.

### Step 2.3: Graceful Exit Formatting
**File:** `gitpulse/cli/cli.py`
- Review all `typer.Exit(1)` calls. Ensure they are preceded by a styled `rich` message rather than a raw Python traceback, especially for expected failure modes (e.g., no commits found, invalid repo path).

## Phase 3: Validation & Testing

### Step 3.1: Dry Run Validation
- Execute `uv run gitpulse generate` with an unset `GROQ_API_KEY` to verify the pre-flight check intercepts the execution cleanly.
- Verify the output formatting matches the standard GitPulse UI guidelines.

### Step 3.2: Config Initialization Test
- Run `uv run gitpulse init` and verify `~/.gitpulse.toml` is created with valid syntax.

### Step 3.3: Publish Action Linting
- Validate `.github/workflows/publish.yml` using `gh workflow lint` (if available) or manual syntax review.

## Final Review
- Ensure `AGENTS.md` and `docs/prd/PRD.md` are updated to reflect the completion of these tasks upon sprint closure.
