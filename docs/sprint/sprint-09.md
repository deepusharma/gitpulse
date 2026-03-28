# Sprint 09 — Packaging & PyPI

**Sprint goal:** Make gitpulse installable via pip and publish to PyPI.
**Milestone:** v0.7 — Packaging & DX
**Duration:** Day 5 (Weekday — ~1.5 hours)
**Status:** Not Started

---

## Pre-Sprint Manual Setup (Do before planning)

1. Create PyPI account at pypi.org
2. Create TestPyPI account at test.pypi.org
3. Generate API token on both (Settings → API tokens)
4. Add to GitHub secrets:
   - `PYPI_API_TOKEN`
   - `TEST_PYPI_API_TOKEN`

---

## Antigravity Prompts

### Planning Prompt (Gemini 3.1 Pro High — Planning Mode)
```
Read these files before responding:
- AGENTS.md
- docs/sprint/sprint-09.md
- pyproject.toml
- cli/cli.py
- core/__init__.py

We are planning Sprint 09 — Packaging and PyPI.

Before writing any code:
1. Review stories #102, #103, #104
2. Review current pyproject.toml structure
3. Check if package is already installable locally
4. Identify what needs to change for pip install gitpulse to work
5. Plan PyPI publish GitHub Actions workflow
6. Plan gitpulse init interactive onboarding
7. Propose step-by-step execution plan
8. Save plan to docs/sprint/sprint-09-execution-plan.md

Do not write any code yet. Planning only.
Use @backend-dev skill.
```

### Execution Prompt (Fast Mode)
```
Read these files before starting:
- AGENTS.md
- docs/sprint/sprint-09.md
- docs/sprint/sprint-09-execution-plan.md

Execute stories #102, #103, #104 in order.
Branch: feature/sprint-09-packaging

Use @backend-dev skill.

After #102 — test locally:
  pip install -e .
  gitpulse --help
  gitpulse --days 7 --dry-run

Run pytest -v before committing.
Commit: "feat: pip packaging, PyPI publish, gitpulse init (S#102-S#104)"
Push and create PR.
Closes #102
Closes #103
Closes #104
```

---

## Sprint Stories

| Issue | Story | Status | Priority |
|---|---|---|---|
| #102 | S9.1: make gitpulse installable as pip package | 🔵 This Sprint | High |
| #103 | S9.2: publish to PyPI via GitHub Actions | 🔵 This Sprint | High |
| #104 | S9.3: add interactive onboarding to CLI | 🔵 This Sprint | Medium |

---

## Story Details

### #102 — pip install gitpulse

**Goal:** `pip install gitpulse` → `gitpulse --days 7` works.

**pyproject.toml changes:**
```toml
[project]
name = "gitpulse"
version = "0.3.0"
description = "AI-powered standup summary generator"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.12"

[project.scripts]
gitpulse = "cli.cli:main"

[project.urls]
Homepage = "https://github.com/deepusharma/gitpulse"
Repository = "https://github.com/deepusharma/gitpulse"
```

**Done when:**
- [ ] pip install -e . works
- [ ] gitpulse --help works
- [ ] gitpulse --days 7 works
- [ ] gitpulse --dry-run works
- [ ] README updated with pip install instructions

---

### #103 — PyPI publish workflow

**File:** `.github/workflows/publish.yml`

**Trigger:** On new GitHub release

**Steps:**
1. Run tests
2. Build package — `python -m build`
3. Publish to TestPyPI first
4. If successful — publish to PyPI

**Done when:**
- [ ] Workflow file created
- [ ] Manual trigger publishes to TestPyPI
- [ ] Package installable from TestPyPI
- [ ] README has PyPI badge

---

### #104 — gitpulse init

**Goal:** Interactive first-run setup.

**Command:** `gitpulse init`

**Flow:**
```
Welcome to gitpulse setup

Enter your GitHub username: deepusharma
Enter repo paths (or press Enter to skip):
  Repo name: gitpulse
  Repo path: /Users/you/GitProjects/gitpulse
  Add another? (y/n): n

Set defaults:
  Default days [7]: 7
  Default output [output/summary.md]:

Setup complete. Config saved to ~/.gitpulse.toml
```

**Done when:**
- [ ] gitpulse init command works
- [ ] Creates ~/.gitpulse.toml
- [ ] Validates GROQ_API_KEY
- [ ] Clear instructions if key missing

---

## Order of Work
```
#102 → #103 → #104
```

## Definition of Done
- [ ] pip install gitpulse works
- [ ] gitpulse command available after install
- [ ] PyPI publish workflow created
- [ ] gitpulse init guides new users
- [ ] All tests pass
- [ ] PR merged
