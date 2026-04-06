# Sprint 11 Plan — Open Source Ready (v0.8.0)

**Sprint goal:** Make GitPulse ready to share publicly — comprehensive README, contributing guide, MkDocs docs site, automated release workflow, and CLI pre-flight auth.
**Milestone:** v0.8.0
**Branch:** `feature/sprint-11-open-source`
**Stories:** #108, #109, #110, #111, #220

---

## 0. Pre-Sprint State Assessment

### What already exists

| Asset | Status | Notes |
|---|---|---|
| `README.md` | ⚠️ Incomplete | Missing: demo GIF, architecture diagram, pip install instructions, .gitpulse.toml reference table, API quick-ref, contributor section. Version stale (v0.6.0). |
| `CHANGELOG.md` | ✅ Exists | Manually maintained, up to v0.6.0. Must be updated to v0.7.0 before tagging v0.8.0. |
| `LICENSE` | ✅ Exists | MIT license present. |
| `.github/workflows/ci.yml` | ✅ Exists | Runs pytest + Vitest on PRs and pushes to master. |
| `.github/workflows/publish.yml` | ⚠️ Partial | Publishes to PyPI on `v*` tag but does NOT create a GitHub Release or auto-generate a changelog. |
| `.github/workflows/hygiene.yml` | ✅ Exists | Stale branch hygiene. |
| `.github/` templates | ❌ Missing | No ISSUE_TEMPLATE, no PULL_REQUEST_TEMPLATE. |
| `CONTRIBUTING.md` | ❌ Missing | |
| `CODE_OF_CONDUCT.md` | ❌ Missing | |
| `mkdocs.yml` | ❌ Missing | |
| MkDocs content docs | ❌ Missing | |
| GitHub Pages workflow | ❌ Missing | |
| Release workflow | ⚠️ Partial | `publish.yml` handles PyPI but no GitHub Release creation. |
| CLI pre-flight auth (#220) | ❌ Missing | `groq.AuthenticationError` not caught in `summarise.py` or `cli.py`. |

### README Gap Analysis

The current `README.md` has these specific technical gaps for new users:

1. **Version stale** — says v0.6.0; package is at v0.7.0.
2. **No `pip install` section** — only shows how to install from source via `uv`. New users who installed via PyPI are left without guidance.
3. **No architecture diagram** — project structure section is a plain text tree with no mermaid diagram.
4. **No `.gitpulse.toml` reference table** — config section shows an example but no complete field reference.
5. **Missing PyPI badge** — `![PyPI](https://img.shields.io/pypi/v/gitpulse)` not present.
6. **No Contributing section** — no mention of how to contribute or link to `CONTRIBUTING.md`.
7. **No docs site link** — MkDocs site URL not referenced.
8. **Demo GIF placeholder** — section exists but content is absent.
9. **Roadmap is stale** — "Email & Slack (v0.7)" listed; actual v0.7 was Packaging & DX.
10. **No Web UI screenshot** — web section describes the flow but has no screenshot placeholder.

---

## 1. Story #108 — Comprehensive README

### Sections to write

| Section | Content |
|---|---|
| Hero + badges | One-line description. Badges: CI, PyPI version, license, Python version, Groq. |
| Demo | `[Demo GIF coming soon]` placeholder |
| Features list | Bullet list of top 6 features across CLI + Web |
| Installation | Two methods: `pip install gitpulse` (primary) and from-source with `uv` |
| Quick start | 3 commands: `pip install`, `gitpulse init`, `gitpulse generate` |
| `.gitpulse.toml` reference | Table of all keys with types, defaults, descriptions |
| Web UI | Screenshot placeholder + link to live demo |
| API | `POST /summarise` and `GET /health` quick-reference table |
| Architecture | Mermaid diagram (CLI -> core -> Groq; Web -> API -> core -> GitHub) |
| Contributing | Link to `CONTRIBUTING.md` |
| License | MIT with link |

### Badges to include
```markdown
![CI](https://github.com/deepusharma/gitpulse/actions/workflows/ci.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/gitpulse)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Groq](https://img.shields.io/badge/LLM-Groq%20%7C%20llama--3.3--70b-orange)
```

### Architecture diagram (mermaid, for README)
```
CLI (gitpulse generate) ──────────────────────────────┐
                                                        ▼
Web UI (Next.js/Vercel) ──► FastAPI (Railway) ──► gitpulse.core
                                                        │
                              ┌─────────────────────────┤
                              ▼                         ▼
                         Local .git / GitHub API    Groq API
```

### `.gitpulse.toml` reference table

| Key | Section | Type | Default | Description |
|---|---|---|---|---|
| `github_username` | root | string | — | Your GitHub username |
| `days` | `[defaults]` | int | 7 | Default lookback window in days |
| `output` | `[defaults]` | string | `"output/summary.md"` | Default output file path |
| `<repo-name>` | `[repos]` | string | — | Absolute path to a local git repository |

---

## 2. Story #109 — Contributing Guide & GitHub Templates

### Files to create

#### `CONTRIBUTING.md`
Sections:
1. Welcome
2. Setting up locally (prerequisites: python 3.12+, uv, node 21+; git clone; uv sync --extra dev; cp .env.example .env; cd web && npm ci)
3. Development workflow (branch naming, pytest, npm test, ruff)
4. Commit style (conventional commits table)
5. PR process (reference an issue, fill template, squash merge only)
6. Reporting bugs (link to bug report template)
7. Environment variables table

#### `CODE_OF_CONDUCT.md`
- Contributor Covenant v2.1 (standard)

#### `.github/ISSUE_TEMPLATE/bug_report.md`
Fields: Describe the bug, Steps to reproduce, Expected behavior, Actual behavior, Environment (OS, Python, gitpulse version), Logs/screenshots.

#### `.github/ISSUE_TEMPLATE/feature_request.md`
Fields: Is your feature related to a problem, Describe solution, Describe alternatives, Additional context.

#### `.github/PULL_REQUEST_TEMPLATE.md`
Sections:
- What does this PR do?
- Type of change (checkbox: feat/fix/docs/refactor/test/chore)
- Related issue: `Closes #`
- Checklist:
  - [ ] Tests added/updated
  - [ ] `uv run pytest -v` passes
  - [ ] `uv run ruff check .` passes
  - [ ] `cd web && npm run test` passes (if frontend changed)
  - [ ] CHANGELOG.md updated
  - [ ] Version bumped atomically (pyproject.toml, package.json, AGENTS.md, PRD.md)

---

## 3. Story #110 — MkDocs Documentation Site

### Tool decision
**MkDocs + Material theme** — free, GitHub Pages compatible, Python-native, Markdown-based. No licensing cost.

### Navigation structure (`mkdocs.yml`)

```yaml
site_name: GitPulse
site_url: https://deepusharma.github.io/gitpulse
repo_url: https://github.com/deepusharma/gitpulse
repo_name: deepusharma/gitpulse

theme:
  name: material
  palette:
    - scheme: slate       # dark mode default for developer tool
      primary: indigo
      accent: cyan
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.top
    - content.code.copy
    - search.suggest

nav:
  - Home: index.md
  - Getting Started:
    - Installation: installation.md
    - Quick Start: quickstart.md
    - Configuration: configuration.md
  - Reference:
    - CLI Reference: cli-reference.md
    - API Reference: api-reference.md
    - Web UI Guide: web-ui.md
  - Contributing:
    - How to Contribute: contributing.md
    - Code of Conduct: code-of-conduct.md
    - Architecture: architecture.md

plugins:
  - search
```

### MkDocs content pages

| File | Source | Notes |
|---|---|---|
| `docs/index.md` | New | Landing page — what GitPulse is, hero summary, links to Installation/Quick Start |
| `docs/installation.md` | New | `pip install`, from-source via `uv`, environment variables |
| `docs/quickstart.md` | New | `gitpulse init` -> `gitpulse generate` in 3 steps |
| `docs/configuration.md` | Extracted from README | `.gitpulse.toml` full reference; environment variables table |
| `docs/cli-reference.md` | New (from cli.py help) | All commands, all flags, examples |
| `docs/api-reference.md` | From `docs/api/api-contract.md` | `POST /summarise`, `GET /health`, schemas, error responses |
| `docs/web-ui.md` | New | Web UI tour, screenshots (placeholder), feature walkthrough |
| `docs/contributing.md` | Copy of `CONTRIBUTING.md` | |
| `docs/code-of-conduct.md` | Copy of `CODE_OF_CONDUCT.md` | |
| `docs/architecture.md` | From architecture/overview.md | Condense for public audience, include mermaid diagram |

**Note:** MkDocs content files will be added alongside existing internal docs/. The `mkdocs.yml` `nav:` section explicitly controls what gets published — internal sprint/PRD docs are not exposed.

### GitHub Actions workflow — `.github/workflows/docs.yml`

```yaml
name: Deploy Docs

on:
  push:
    branches: [master]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install mkdocs-material
      - run: mkdocs gh-deploy --force
```

Deploys to `gh-pages` branch -> GitHub Pages at `deepusharma.github.io/gitpulse`.

### Dependencies (dev only)
Add to `pyproject.toml` under `[project.optional-dependencies]`:
```toml
docs = ["mkdocs>=1.6", "mkdocs-material>=9.5"]
```
These are NOT runtime dependencies.

---

## 4. Story #111 — GitHub Release Workflow

### Current state
`publish.yml` triggers on `v*` tags and publishes to PyPI. It does NOT:
- Run tests before publishing (risk: broken package on PyPI)
- Create a GitHub Release
- Auto-generate a changelog

### New file: `.github/workflows/release.yml`

**Trigger:** push to tags matching `v*.*.*`

**Steps:**
1. `checkout` (full history for changelog generation — `fetch-depth: 0`)
2. `setup-python` -> install `uv`
3. `uv sync --extra dev` -> run `pytest -v` **(gate: fail fast if tests break)**
4. Build package: `python -m build`
5. Generate changelog via `git-cliff` (`orhun/git-cliff-action@v3`) from conventional commits since last tag
6. Create GitHub Release via `softprops/action-gh-release`:
   - Tag: the pushed tag (e.g. `v0.8.0`)
   - Body: auto-generated changelog from git-cliff
   - Attach wheel + sdist as release assets
7. Publish to PyPI via `pypa/gh-action-pypi-publish`

**Tool for changelog:** `git-cliff` — understands conventional commits, outputs clean markdown.

### New file: `cliff.toml` (at root)

```toml
[changelog]
header = ""
body = """
{% for group, commits in commits | group_by(attribute="group") %}
### {{ group | upper_first }}
{% for commit in commits %}
- {{ commit.message }}
{% endfor %}
{% endfor %}
"""
trim = true

[git]
conventional_commits = true
commit_parsers = [
  { message = "^feat", group = "Features" },
  { message = "^fix", group = "Bug Fixes" },
  { message = "^docs", group = "Documentation" },
  { message = "^refactor", group = "Refactoring" },
  { message = "^test", group = "Tests" },
  { message = "^chore", group = "Chores" },
]
```

**Decision:** Delete `publish.yml` — `release.yml` takes over the full release gate. This avoids double-publishing risk on the same tag.

**Required GitHub secrets:** `PYPI_API_TOKEN` (already set).

---

## 5. Story #220 — CLI Pre-flight Auth

### Problem
When `GROQ_API_KEY` is set but invalid (wrong/expired), `groq.AsyncGroq` raises `groq.AuthenticationError` (HTTP 401). The CLI currently has no specific handler — the error propagates as a raw Python traceback.

### Root cause
- `load_env(check_keys=not dry_run)` in `cli.py` line 119 only checks key *presence*, not *validity*.
- `summarise.py` line 141 catches `Exception` generically and re-raises.
- `cli.py` has no `groq.AuthenticationError`-specific except block.

### Changes

#### `gitpulse/core/summarise.py` — add specific catch
```python
async with groq.AsyncGroq(api_key=groq_api_key) as client:
    try:
        response = await client.chat.completions.create(...)
        return response.choices[0].message.content
    except groq.AuthenticationError:
        logger.error("Groq authentication failed — invalid or expired API key")
        raise  # Re-raise for CLI to catch
    except Exception as e:
        logger.error("Error during Groq summarization: %s", e, exc_info=True)
        raise
```

#### `gitpulse/cli/cli.py` — Rich error panel
Add `import groq` at top.

In `_run()` inside `generate()`, wrap `summarise(prompt)` call:

```python
try:
    summary = await summarise(prompt)
except groq.AuthenticationError:
    console.print(
        Panel(
            "[bold red]Authentication Failed[/bold red]\n\n"
            "Your GROQ_API_KEY was rejected by the Groq API.\n\n"
            "Resolution steps:\n"
            "1. Get a valid key from https://console.groq.com\n"
            "2. Run: export GROQ_API_KEY=your_key_here\n"
            "   — or add it to your .env file\n"
            "3. Re-run: gitpulse generate",
            title="Groq Error",
            border_style="red",
            expand=False,
        )
    )
    raise typer.Exit(1)
```

#### Tests
In relevant CLI test file, add:
- Mock `summarise` to raise `groq.AuthenticationError`
- Assert CLI exits with code 1
- Assert "Authentication Failed" appears in console output

---

## 6. Version Sync Requirements

Per AGENTS.md, all version changes must be applied atomically:

| File | Current | Target |
|---|---|---|
| `pyproject.toml` | `0.7.0` | `0.8.0` |
| `web/package.json` | verify current | `0.8.0` |
| `AGENTS.md` Milestone History | `v0.7 🔵 Active` | `v0.7 ✅ Complete`, `v0.8 🔵 Active` |
| `docs/prd/PRD.md` Release Table | update v0.6/v0.7/v0.8 status rows | `v0.7 ✅ Complete`, `v0.8 🔄 In Progress` |
| `README.md` hero line | `v0.6.0` | `v0.8.0` |
| `CHANGELOG.md` | entries up to `0.6.0` | Add `[0.7.0]` and `[0.8.0]` entries |

---

## 7. Execution Order

```
Step 1: Branch
  git checkout -b feature/sprint-11-open-source

Step 2: Story #220 — CLI Pre-flight Auth (code change first)
  ├── Edit gitpulse/core/summarise.py
  ├── Edit gitpulse/cli/cli.py
  └── Add test for auth failure path

Step 3: Story #108 — Comprehensive README
  └── Rewrite README.md (all sections)

Step 4: Story #109 — Contributing Guide & Templates
  ├── Create CONTRIBUTING.md
  ├── Create CODE_OF_CONDUCT.md
  ├── Create .github/ISSUE_TEMPLATE/bug_report.md
  ├── Create .github/ISSUE_TEMPLATE/feature_request.md
  └── Create .github/PULL_REQUEST_TEMPLATE.md

Step 5: Story #110 — MkDocs Site
  ├── Add [docs] optional dep to pyproject.toml
  ├── Create mkdocs.yml
  ├── Create docs/index.md
  ├── Create docs/installation.md
  ├── Create docs/quickstart.md
  ├── Create docs/configuration.md
  ├── Create docs/cli-reference.md
  ├── Create docs/api-reference.md
  ├── Create docs/web-ui.md
  ├── Create docs/contributing.md
  ├── Create docs/code-of-conduct.md
  ├── Create docs/architecture.md
  └── Create .github/workflows/docs.yml

Step 6: Story #111 — Release Workflow
  ├── Create cliff.toml
  ├── Create .github/workflows/release.yml
  └── Delete .github/workflows/publish.yml

Step 7: Version sync (atomic)
  ├── pyproject.toml -> 0.8.0
  ├── web/package.json -> 0.8.0
  ├── AGENTS.md milestone history
  ├── docs/prd/PRD.md release table
  ├── README.md hero
  └── CHANGELOG.md (add 0.7.0 and 0.8.0 entries)

Step 8: Verification
  ├── uv run pytest -v
  ├── uv run ruff check .
  ├── cd web && npm run test
  └── mkdocs build --strict

Step 9: Commit + Push
  git commit -m "feat: open source ready — README, Contributing, MkDocs, release workflow, CLI auth (#108 #109 #110 #111 #220)"
  git push origin feature/sprint-11-open-source

Step 10: PR -> merge -> tag
  Open PR, merge (squash), git tag v0.8.0, git push origin v0.8.0
```

---

## 8. Open Questions

**Q1 — GitHub Pages enabled?**
The `docs.yml` workflow deploys to GitHub Pages at `deepusharma.github.io/gitpulse`. GitHub Pages must be enabled in repo settings (Settings -> Pages -> Source: `gh-pages` branch) before the workflow runs. Action needed before Step 5.

**Q2 — Retire `publish.yml`?**
`release.yml` supersedes `publish.yml`. Recommend deleting `publish.yml` to avoid double-publishing on a `v*` tag. Confirm before Step 6.

**Q3 — Demo GIF / screenshots?**
README and `web-ui.md` call for a demo GIF and Web UI screenshot. Placeholder text for this sprint; defer actual recording to a post-launch pass unless you want to record now.

**Q4 — `git-cliff` vs manual CHANGELOG?**
Existing `CHANGELOG.md` is manually curated up to v0.6.0. Recommend: use `git-cliff` for auto-generation in `release.yml` (populates the GitHub Release body), while keeping the manual `CHANGELOG.md` for human-readable history. Both can coexist.

**Q5 — Story #220 scope**
Only `groq.AuthenticationError` (401) is in scope. Deferring GitHub token validation (optional token, low risk) to a future sprint.

---

## 9. Definition of Done

- [ ] #108: README is version-correct (v0.8.0), has all badges, mermaid diagram, pip install section, toml reference table, contributing link
- [ ] #109: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, all three GitHub templates created  
- [ ] #110: `mkdocs.yml` and all 10 content pages created; `docs.yml` workflow present; `mkdocs build --strict` passes
- [ ] #111: `release.yml` created with test gate + GitHub Release creation + PyPI publish; `cliff.toml` present; `publish.yml` deleted
- [ ] #220: `groq.AuthenticationError` caught in `summarise.py`; Rich panel displayed in CLI; test added  
- [ ] All version strings synced to `0.8.0` across 6 files
- [ ] `uv run pytest -v` passes
- [ ] `uv run ruff check .` passes
- [ ] `cd web && npm run test` passes
- [ ] `mkdocs build --strict` passes
- [ ] PR merged; `v0.8.0` tag created and pushed -> triggers `release.yml`
