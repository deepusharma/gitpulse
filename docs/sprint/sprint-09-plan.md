# Sprint 09 Execution Plan — Packaging & PyPI

## 1. Context & Objectives
- **Goal**: Make `gitpulse` installable via pip, publish it to PyPI via GitHub Actions, and add an interactive `init` command.
- **Stories**: #102 (`pip install gitpulse`), #103 (PyPI publish workflow), #104 (`gitpulse init`).

## 2. Pre-requisites Review
- `pyproject.toml` needs updates to its `[project]` fields (version, metadata) and adding `[build-system]` to ensure pip cleanly builds it.
- `cli/cli.py` currently uses `argparse` with no subparsers; we need to add `init` as a command.
- The project has `uv` as the default package manager.

## 3. Step-by-Step Implementation Plan

### Step 1: #102 - Make gitpulse installable as pip package
1. **Update `pyproject.toml`**:
   - Update `version = "0.3.0"`.
   - Add `description`, `readme`, `license`, `urls` as specified in `sprint-09.md`.
   - Add explicit `[build-system]` block for setuptools:
     ```toml
     [build-system]
     requires = ["setuptools>=61.0.0", "wheel"]
     build-backend = "setuptools.build_meta"
     ```
   - Make sure `project.scripts` correctly points to `cli.cli:main` (already present).
2. **Test Installability**:
   - Run `uv pip install -e .` (or standard `pip install -e .`).
   - Run `gitpulse --help` and verify output.
   - Run `gitpulse --days 7 --dry-run` to ensure command functions normally.
3. **Update README.md**:
   - Add an "Installation" section explaining how to `pip install gitpulse`.

### Step 2: #103 - Publish to PyPI via GitHub Actions
1. **Create GitHub Actions Workflow**:
   - Create File: `.github/workflows/publish.yml`.
   - Trigger: `on: release: types: [published]` or manual `workflow_dispatch`.
   - Define job Steps:
     1. Checkout code (`actions/checkout@v4`).
     2. Setup Python (`actions/setup-python@v5`).
     3. Install build tools: `pip install build pytest uv pypa-build` etc.
     4. Run Tests: `pytest -v`.
     5. Build package: `python -m build`.
     6. Publish to TestPyPI: Use `pypa/gh-action-pypi-publish@release/v1` targeting `test.pypi.org/legacy/` with `TEST_PYPI_API_TOKEN`.
     7. Publish to PyPI: Only on successes of TestPyPI with `PYPI_API_TOKEN`.
2. **Update README.md**:
   - Add a PyPI version badge.

### Step 3: #104 - Add interactive `gitpulse init` command
1. **Modify `cli/cli.py`**:
   - Update `argparse` to use an optional positional argument or subparser `parser.add_argument("command", nargs="?", help="Command to run (e.g. init)")`.
   - If `args.command == "init"`:
     - Prompt for GitHub username (`input()`).
     - Prompt for repository configs in a loop (`input()` for name, path, y/n for more).
     - Prompt for default days (default 7) and output path (default `output/summary.md`).
     - Validate `GROQ_API_KEY` presence in `os.environ` or `.env`. If missing, output clear instructions on how to set it.
     - Persist the configuration to `~/.gitpulse.toml` using `tomllib`/manual formatting.
     - Exit cleanly.
   - If no command is provided, fall back to the default summary generation logic.

## 4. Testing & Verification
- Verify `gitpulse init` prompts properly and generates `~/.gitpulse.toml`.
- Run `pytest -v` to ensure testing suite still passes locally.
- Execute a dry run of summary generation to ensure standard operation remains functional.
