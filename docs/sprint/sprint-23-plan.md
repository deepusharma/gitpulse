# Sprint 23 Plan: Release Hardening & v1.5 Launch

## Phase 1: Code Health & Linting Sweep
1. **Backend Linting**: Run `uv run ruff check .` and fix any warnings or violations across `gitpulse/` and `api/`.
2. **Frontend Linting**: Run `npm run lint` and `npm run build` in the `web/` directory to ensure strict TypeScript and ESLint compliance.
3. **Test Validation**: Ensure `pytest -v` (backend) and `npm run test` (frontend) pass cleanly with high coverage and no deprecation warnings.

## Phase 2: CI/CD & Workflow Robustness
1. **`ci.yml` Review**: Ensure Node version compatibility and `uv` setup are robust. (Node 21 is currently used; evaluate if we should pin Node 20 LTS).
2. **`publish.yml` Review**: Verify the `pypi` environment block is correct. The test job in `publish.yml` uses `uv sync --extra dev` whereas `ci.yml` uses `uv pip install -e ".[dev]"`. Unify the `uv` dependency installation strategy to ensure consistency across CI workflows.
3. **TestPyPI Sandbox**: Set up a parallel `test-publish.yml` workflow or add a manual trigger (`workflow_dispatch`) to publish to TestPyPI before hitting the main PyPI.

## Phase 3: Documentation & Release Preparation
1. **README Update**: Double-check that environment variables (like `RESEND_API_KEY`, `GITHUB_TOKEN`), installation steps, and CLI references match the latest `v1.5` state.
2. **Version Bump Check**: Ensure `web/package.json`, `pyproject.toml`, and `AGENTS.md` are correctly bumped to `1.5.0` (or the intended release version).
3. **Changelog Construction**: Draft the release notes highlighting Sprint 19-22 features (Streaks, Team Standups, Delivery modals, CLI auth, etc.).

## Phase 4: Final Tag & Deployment
1. Open and merge the `feature/sprint-23-hardening` PR.
2. Draft a new GitHub Release with the `v1.5.0` tag.
3. Observe `.github/workflows/publish.yml` trigger and successfully push to PyPI.
