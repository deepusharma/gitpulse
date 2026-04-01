# Sprint 11 Execution Plan — Open Source Ready

**Goal:** Make gitpulse ready to share publicly — comprehensive README, contributing guide, docs site, and automated releases.
**Milestone:** v0.8 — Open Source Ready

---

## 1. Analysis & Pre-Work Responses

1. **Review stories #108, #109, #110, #111:** 
   Reviewed. The sprint covers an overhaul of the `README.md`, contribution guidelines/templates, establishing a formal documentation site via MkDocs, and wrapping up with a GitHub release workflow tailored for PyPI publishing.
2. **Review current `README.md`:** 
   The current README features a good baseline but lacks structural maturity. Missing elements include an explicitly stated Hero section, a Demo GIF placeholder, a well-defined Architecture section with a mermaid diagram placeholder, clear separation of CLI/Web/API usage instructions, Web UI screenshots, and proper contributor links per #108.
3. **Review existing docs structure:** 
   Currently, `docs/` is split into `api/`, `architecture/`, `prd/`, and `sprint/`. We need to expand this structure significantly to build the frontend navigation content needed by MkDocs (e.g. `installation.md`, `cli-reference.md`).
4. **Decide between MkDocs vs Mintlify:** 
   **MkDocs** (with the `mkdocs-material` theme) is the chosen documentation solution. It is explicitly prioritized in `sprint-11.md` (Story #110), fully open-source, integrates perfectly with GitHub Pages via GitHub Actions, and supports an extensive markdown ecosystem.
5. **Plan GitHub Issue and PR Templates:** 
   Standardized `.github` templates will be used. This will include two Markdown issue templates (`bug_report.md` and `feature_request.md`) equipped with yaml frontmatter config, and a `PULL_REQUEST_TEMPLATE.md` mapped to project conventions.
6. **Plan release workflow:** 
   A `.github/workflows/release.yml` file will be created. It will trigger on tags matching `v*` (e.g., `v0.8.0`). Steps will include: running `pytest`, building the package with `uv`, auto-generating changelogs based on Conventional Commits, creating a GitHub Release, and finally publishing to PyPI using PyPI trusted publishers or an API token.

---

## 2. Step-by-Step Execution Plan

### Step 1: Initialize Workspace
- Checkout new branch: `feature/sprint-11-open-source`
- Ensure local tests pass before proceeding.

### Step 2: Expand and Rewrite `README.md` (Story #108)
- Modify `README.md` to be comprehensive and compelling. 
- **Include**:
  - Improved One-sentence Hero.
  - Badges: `CI`, `PyPI version`, `License`, `Coverage`.
  - Placeholder for a demo GIF (`![Demo](doc/assets/demo.gif)`).
  - Explicit Feature List.
  - **Installation**: Details for installing via `pip install gitpulse` vs source.
  - **Quick Start**: Minimum commands to the first functional summary.
  - **Configuration**: Specific details on `~/.gitpulse.toml`.
  - **Architecture**: A dedicated section featuring a block diagram (using `mermaid` codeblocks).
  - Link to `CONTRIBUTING.md`.

### Step 3: Setup Contribution Conventions (Story #109)
- **Create `CONTRIBUTING.md`**: Add instructions for environment setup (`uv`), development workflow, testing, and branch/commit conventions matching `AGENTS.md`.
- **Create `CODE_OF_CONDUCT.md`**: Add standard Contributor Covenant language.
- **Create Issue & PR Templates**:
  - `.github/ISSUE_TEMPLATE/bug_report.md`
  - `.github/ISSUE_TEMPLATE/feature_request.md`
  - `.github/PULL_REQUEST_TEMPLATE.md`
- **Commit Stream 1**: `docs: comprehensive README and contributing guide (S#108-S#109)`
- **Action**: Do **not** create the PR yet. Store commits locally.

### Step 4: Configure MkDocs Site (Story #110)
- **Create `mkdocs.yml`**: Configure site metadata, navigation structure, and apply the `material` theme. Include extensions if necessary (like `pymdownx.superfences` for mermaid support).
- **Structure the `docs/` content**:
  - `docs/index.md` (Getting Started)
  - `docs/installation.md`
  - `docs/configuration.md`
  - `docs/cli-reference.md`
  - `docs/api-reference.md`
  - `docs/web-ui.md`
  - `docs/contributing.md`
- **Create `.github/workflows/docs.yml`**: Setup a GitHub Action to install `mkdocs-material` and trigger `mkdocs gh-deploy --force` upon pushes to the `master` branch.

### Step 5: Setup GitHub Release Workflow (Story #111)
- **Create `.github/workflows/release.yml`**: Setup the release action.
  - **Triggers**: `push` on `tags` matching `v*`.
  - **Jobs**:
    - **Test & Lint**: Execute `pytest -v` and structure checks.
    - **Build**: Use `uv build` to construct wheel and sdist.
    - **Release**: Leverage `softprops/action-gh-release` for GitHub release generation. Generate changelog dynamically utilizing release-drafter or conventional-changelog methodologies.
    - **Publish to PyPI**: Upload built artifacts.
- **Commit Stream 2**: `docs: add MkDocs site and release workflow (S#110-S#111)`
- **Action**: Push branch to origin and open a Pull Request resolving S#108, S#109, S#110, and S#111.

### Step 6: Post-Sprint Tasks
- Merge Pull Request into `master`.
- Pull changes locally, execute deployment verification.
- Tag commit with `v0.8.0` and `git push --tags` to initialize the newly created release pipeline natively.
