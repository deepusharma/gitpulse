# Sprint 01 — Codebase Restructure Plan

The goal of this sprint is to restructure the codebase to support both the CLI and a new web frontend, setting the stage for v0.2.

## User Review Required

> [!IMPORTANT]
> **Gaps & Inconsistencies Detected:**
> 1. [pyproject.toml](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/pyproject.toml) currently defines the entry point as `gitpulse = "src.cli:app"`. However, inspecting [src/cli.py](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/src/cli.py) shows it utilizes standard `argparse`, not Typer, and has no `app` object. We will update the entry point to `gitpulse = "cli.cli:main"` and correctly wrap the script execution in a [main()](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/main.py#1-3) function as proposed in Story #20.
> 2. [main.py](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/main.py) at the root currently just prints "Hello from gitpulse!". We will ignore this file and let it be, unless you want it deleted.
> 3. Story #20 mentions creating `test_cli.py` inside `cli/tests/` when there is currently no `test_cli.py` in `tests/`. This naturally works out since there were no CLI tests to move to begin with.
> 4. We will completely replace `pythonpath = ["src"]` in [pyproject.toml](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/pyproject.toml) with `pythonpath = ["."]` and set `testpaths = ["core/tests", "cli/tests"]` since `src/` will no longer exist.

Please confirm the plan below is acceptable to proceed with execution.

## Proposed Changes

### Story #19 — Move Shared Logic to `core/`
We will create the `core` structure (`core/`, `core/tests/`, `core/docs/`) and use `git mv` to preserve git history.
#### [NEW] `core/__init__.py`
#### [NEW] `core/docs/core-guide.md`
#### [MODIFY] `core/repo_reader.py` (Moved from [src/repo_reader.py](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/src/repo_reader.py))
#### [MODIFY] `core/summarise.py` (Moved from [src/summarise.py](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/src/summarise.py))
#### [MODIFY] `core/utils.py` (Moved from [src/utils.py](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/src/utils.py))
#### [MODIFY] `core/tests/test_repo_reader.py` (Moved from [tests/test_repo_reader.py](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/tests/test_repo_reader.py))
#### [MODIFY] `core/tests/test_summarise.py` (Moved from [tests/test_summarise.py](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/tests/test_summarise.py))
#### [MODIFY] `core/tests/test_utils.py` (Moved from [tests/test_utils.py](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/tests/test_utils.py))

---

### Story #20 — Move CLI Code to `cli/`
We will create the `cli` structure (`cli/`, `cli/tests/`, `cli/docs/`) and use `git mv` for [src/cli.py](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/src/cli.py).
#### [NEW] `cli/__init__.py`
#### [NEW] `cli/tests/test_cli.py` 
#### [NEW] `cli/docs/cli-guide.md`
#### [MODIFY] `cli/cli.py` (Moved from [src/cli.py](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/src/cli.py))
- We will indent the execution block under `if __name__ == "__main__":` into a `def main():` function.

---

### Story #21 & #22 — Update Imports, Tests, and CI
We will update references to point to the new package paths.
#### [MODIFY] `cli/cli.py`
- Update imports from `from repo_reader import ...` to `from core.repo_reader import ...`.
#### [MODIFY] `core/tests/*`
- Update imports from `from repo_reader import ...` to `from core.repo_reader import ...` as well.
#### [MODIFY] [pyproject.toml](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/pyproject.toml)
- Adjust the `[project.scripts]` to run `gitpulse = "cli.cli:main"`.
- Adjust the `[tool.pytest.ini_options]` to use `pythonpath = ["."]` instead of `["src"]` and configure `testpaths`.
#### [DELETE] `src/` (Folder will be empty)
#### [DELETE] `tests/` (Folder will be empty)

## Verification Plan

### Automated Tests
- Run `pytest -v` from the project root. We expect exactly 16 passing tests.

### Manual Verification
- Run the CLI from the command line: `python -m cli.cli --days 7`. Ensure it successfully parses standard arguments without crashing.
