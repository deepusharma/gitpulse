# Sprint 09 Execution Plan — Packaging & PyPI (v0.7.0 Professional)

## 1. Context & Objectives
- **Goal**: Transition GitPulse into a professional, namespace-isolated Python package installable via `pip`.
- **Milestone**: **v0.7.0 Packaging & DX**.
- **Stories**: #102 (`pip install gitpulse`), #103 (PyPI publish workflow), #104 (`gitpulse init`).

## 2. Professional Refactor Strategy
To ensure GitPulse is "production ready" for PyPI, we are moving away from the "flat" structure to a **Namespace Layout**.

**Proposed Structure:**
```none
gitpulse/
├── __init__.py
├── core/
├── cli/
└── api/
```

**Why Namespace Layout?**
- Prevents collisions (no more global `import core`).
- Professional distribution standards.
- Cleaner import pathways (`from gitpulse.core...`).

---

## 3. Step-by-Step Implementation Plan

### Step 1: #102 - Professional Namespace Restructure
1. **Directory Refactor**:
   - Create the `gitpulse/` top-level directory.
   - Move `core/` and `cli/` inside `gitpulse/`.
2. **Update `pyproject.toml`**:
   - Upgrade `version = "0.7.0"`.
   - Update `project.scripts`: `gitpulse = "gitpulse.cli.cli:app"`.
   - Update `packages.find`: `include = ["gitpulse*"]`.
3. **Synchronize Imports**:
   - Update all `from core...` to `from gitpulse.core...`.
   - Update all `from cli...` to `from gitpulse.cli...`.
   - Apply to: `api/api.py`, `gitpulse/cli/cli.py`, and all test suites.

### Step 2: #104 - Interactive `gitpulse init` (Typer)
1. **Refactor `cli.py` to Typer**:
   - Benefit from better subcommand handling and built-in interactive help.
2. **Implement `init` Command**:
   - Use `typer.prompt` for Interactive Flow:
     - `GitHub Username`
     - `Repo Configs (Loop)`
     - `Default Days`
   - Persist to `~/.gitpulse.toml`.
   - Validate `GROQ_API_KEY` presence and print clear setup instructions if missing.

### Step 3: #103 - CI/CD & Distribution
1. **PyPI Publish Workflow**:
   - Create `.github/workflows/publish.yml`.
   - Automate `python -m build` and `pypa/gh-action-pypi-publish`.
2. **Release Documentation**:
   - Update `RELEASE_NOTES.md` and `AGENTS.md` milestone history.
   - Add "Installation" and "CLI Quickstart" sections to `README.md`.

---

## 4. Testing & Verification
- `uv run pytest -v`: Ensure all 59+ tests pass with new imports.
- `pip install -e .`: Verify the `gitpulse` binary is available in the shell.
- `gitpulse init`: Confirm configuration creation in home directory.
- `gitpulse --dry-run`: End-to-end logic check post-refactor.
