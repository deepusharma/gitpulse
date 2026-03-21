# AGENTS.md — gitpulse

This file provides shared context for all AI agents working on this project.
Read this before starting any task.

---

## Project Overview

gitpulse is a multi-client tool that reads git commit history and generates
AI-powered standup summaries. It has two clients — a CLI for local use and
a web interface for browser access — both sharing a common Python core library.

---

## Docs — Read Before Implementing

| Doc          | Path                            | When to read                    |
| ------------ | ------------------------------- | ------------------------------- |
| PRD          | `docs/prd/prd-web.md`           | Before any v0.2 feature         |
| Architecture | `docs/architecture/overview.md` | Before any implementation       |
| API Contract | `docs/api/api-contract.md`      | Before backend or frontend work |

---

## Codebase Structure

```
gitpulse/
├── core/
│   ├── __init__.py
│   ├── repo_reader.py
│   ├── summarise.py
│   ├── utils.py
│   ├── tests/
│   │   ├── test_repo_reader.py
│   │   ├── test_summarise.py
│   │   └── test_utils.py
│   └── docs/
│       └── core-guide.md
├── cli/
│   ├── __init__.py
│   ├── cli.py
│   ├── tests/
│   │   └── test_cli.py
│   └── docs/
│       └── cli-guide.md
├── api/
│   ├── __init__.py
│   ├── api.py
│   ├── tests/
│   │   └── test_api.py
│   └── docs/
│       └── api-guide.md
├── web/
│   ├── src/
│   │   └── app/
│   │       └── page.tsx
│   ├── tests/
│   └── docs/
│       └── web-guide.md
├── docs/
│   ├── prd/
│   │   └── prd-web.md
│   ├── architecture/
│   │   └── overview.md
│   ├── api/
│   │   └── api-contract.md
│   ├── decisions/
│   └── sphinx/
├── AGENTS.md
├── .antigravity/
│   ├── rules/
│   │   └── project-rules.md
│   └── skills/
│       ├── backend-dev/
│       │   └── SKILL.md
│       ├── frontend-dev/
│       │   └── SKILL.md
│       ├── reviewer/
│       │   └── SKILL.md
│       ├── tester-backend/
│       │   └── SKILL.md
│       └── tester-frontend/
│           └── SKILL.md
├── pyproject.toml
└── package.json
```

---

## Tech Stack

### Python (core + cli + api)

- Python 3.12+
- uv for package management
- FastAPI + uvicorn for API
- httpx for GitHub API calls
- GitPython for local git
- Groq API — llama-3.3-70b-versatile
- pytest for testing

### TypeScript (web)

- Next.js 14 App Router
- TypeScript strict mode
- Tailwind CSS
- shadcn/ui components
- fetch for API calls

---

## Coding Standards

### Python

- Google docstrings on all functions
- `logging` module — never `print`
- `%s` format style for logger calls: `logger.debug("msg: %s", var)`
- Type hints on all function signatures
- Guard clauses over nested ifs
- One function, one responsibility

### TypeScript

- Strict mode always
- No `any` types
- Interfaces over types for objects
- Named exports preferred

---

## Git Workflow

- Never commit directly to master — branch protection is enforced
- Branch naming: `feature/description`, `fix/description`, `test/description`
- Conventional commits always:
  - `feat:` new feature
  - `fix:` bug fix
  - `docs:` documentation
  - `refactor:` code change no feature/fix
  - `test:` adding tests
  - `chore:` build, config, tooling
- Every PR must reference an issue: `Closes #XX`
- Squash merge only

---

## Key Patterns

### repo_reader adapter pattern

```python
# CLI uses local source
get_commits(source="local", days=7)

# API uses github source
get_commits(source="github", username="deepusharma", repos=["gitpulse"], days=7)

# Both return same flat list shape:
# [{"repo": str, "message": str, "author": str, "date": datetime, "hash": str}]
```

### Import pattern

```python
# Always import from core — never from src
from core.repo_reader import get_commits
from core.summarise import format_commits, summarise
from core.utils import load_env
```

---

## Environment Variables

```
GROQ_API_KEY=          # Required for all Python components
GITHUB_TOKEN=          # Optional — raises GitHub API rate limit
NEXT_PUBLIC_API_URL=   # Required for web — FastAPI backend URL
```

---

## Testing Rules

- Tests required for all new functions
- Mock all external API calls — Groq, GitHub API
- One test file per module
- Run tests before every PR: `pytest -v`
- CI runs automatically on every PR

---

## Current Milestone

- Sprint 01 ✅ Complete
- Sprint 02 ✅ Complete  
- Sprint 03 🔵 Active — Next.js frontend (#36-#42)
- Active branch: feature/nextjs-frontend

Active epics:

- #15 — codebase restructure (✅ Complete)
- #16 — GitHub API adapter (✅ Complete)
- #17 — FastAPI backend (✅ Complete)
- #18 — Next.js frontend (🔵 Active)

Currently working on Epic #18 stories #36-#42.

---

## Sprint Workflow
- Sprint plans: docs/sprint/sprint-XX.md
- Execution plans: docs/sprint/sprint-XX-execution-plan.md
- Always read both before starting a sprint
- Save execution plan to file before closing planning chat
- Open new execution chat per sprint for clean context

---

## Skills Available

Specialized agent skills are in `.antigravity/skills/`:

| Skill             | Use for                            |
| ----------------- | ---------------------------------- |
| `backend-dev`     | Python, FastAPI, core library work. Use for all core/ api/ work. |
| `frontend-dev`    | Next.js, TypeScript, Tailwind work. Use for all web/ work. |
| `reviewer`        | Code review and quality checks. |
| `tester-backend`  | pytest, Python test writing. Use for Python tests. |
| `tester-frontend` | Vitest, React Testing Library. Use for TypeScript tests. |
