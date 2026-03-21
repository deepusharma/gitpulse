# Sprint 01 — Codebase Restructure Execution Plan

## Goal Description
Restructure the legacy flat script codebase into clearly delineated modules (`core`, `cli`, `api`, `web`) to support the multi-client v0.2 milestone without modifying any existing business logic. Set up the agent infrastructure and testing protocols for the new structure.

## Executed Changes

### Move Shared Logic to `core/` (#19)
- Relocated `src/repo_reader.py`, `src/summarise.py`, and `src/utils.py` to `core/`.
- Moved associated unit tests into `core/tests/`.
- Generated empty placeholder documentation in `core/docs/core-guide.md`.
- Ensure all logic remains completely identical.

### Move CLI Code to `cli/` (#20)
- Isolated the command-line interface logic to `cli/cli.py`.
- Encapsulated the module-level execution block within a formal `main()` function.
- Created `cli/tests/` and an empty `cli/docs/cli-guide.md`.
- Registered `gitpulse = "cli.cli:main"` as the central entry point macro in `pyproject.toml`.

### Abstract Imports and Test Paths (#21, #22)
- Replaced all explicit `src.*` imports globally with the newly qualified `core.*`.
- Explicitly specified `testpaths = ["core/tests", "cli/tests"]` in `pyproject.toml` so Pytest natively discovers all modularized test suites.
- Validated that the GitHub Actions CI automatically recognized the new testing framework without modifying the runner configuration.

## Verification
- Validated `pytest -v` accurately detected and ran all 16 pre-existing tests securely natively without `src/` conflicts.
- Verified manual local test runs using the standard CLI parameters `python -m cli.cli --days 7` executed functionally over the new directory map.
