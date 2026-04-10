# GEMINI.md — gitpulse

This file provides the foundational context and mandates for all AI agent interactions within the `gitpulse` project.

## Project Overview

**gitpulse** is an AI-powered standup summary generator that synthesizes git history (local or remote) into structured, professional updates using the Groq LLM (`llama-3.3-70b-versatile`).

### Architecture
- **`gitpulse.core`**: Shared Python library for repository analysis and AI summarization. Uses the Adapter pattern to support both local `.git` (GitPython) and remote GitHub API (httpx) sources.
- **`gitpulse.cli`**: Typer-based CLI tool for local standup generation.
- **`api/`**: FastAPI backend exposing summarization logic, history persistence (PostgreSQL), and analytics.
- **`web/`**: Next.js (App Router) frontend with GitHub OAuth, analytics dashboards (Recharts), and standup history.

### Tech Stack
- **Backend**: Python 3.12+, FastAPI, Typer, GitPython, Groq, Asyncpg, Pydantic.
- **Frontend**: Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, NextAuth.js, Recharts.
- **Tooling**: `uv` (Python package manager), `ruff` (Linter/Formatter), `vitest` (Frontend testing), `pytest` (Backend testing).

---

## Building and Running

### Prerequisites
- Python 3.12+
- Node.js 20+
- `uv` (recommended)
- API Keys: `GROQ_API_KEY`, `GITHUB_TOKEN` (optional but recommended)

### Backend (Core, CLI, API)
```bash
# Install dependencies and setup venv
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run CLI
gitpulse generate

# Run API (Dev)
uvicorn api.api:app --reload

# Run Tests
uv run pytest -v
```

### Frontend (Web)
```bash
cd web
npm install

# Run Dev Server
npm run dev

# Run Tests
npm run test

# Run Linting
npm run lint
```

---

## Development Conventions

### Core Mandates (from `.antigravity/rules/project-rules.md`)
1.  **Code Quality**: Prioritize clarity over cleverness. Functions should be <30 lines and have a single responsibility. Use guard clauses to fail fast.
2.  **Logic Separation**: Never put business logic in `cli.py` or `api.py`. Always implement it in `gitpulse.core`.
3.  **Logging**: Use the standard `logging` module in Python. Never use `print`. Use `%s` style formatting and always include `exc_info=True` for errors.
4.  **No Hardcoding**: All configurations (URLs, Model names, API keys) must come from environment variables or config files (`~/.gitpulse.toml`).
5.  **Testing**: Tests are **mandatory** for all new functions. Mock all external calls (Groq, GitHub API).
6.  **UI Standards**: Use **shadcn/ui** and **Tailwind CSS**. Monochrome/neutral palette with a single accent color. Mobile-first responsive design.
7.  **Documentation**: Use Google-style docstrings for Python and JSDoc for TypeScript.
8.  **Versioning**: Version strings must be synced across `pyproject.toml`, `web/package.json`, and `AGENTS.md`.

### Git Workflow
- **Branching**: `feature/description`, `fix/description`, `test/description`.
- **Commits**: Conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`).
- **PRs**: Squash merge only. Must pass `pytest` and linting before merging.

### Naming
- **Python**: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants.
- **TypeScript**: `camelCase` for functions/variables, `PascalCase` for components/interfaces. Do NOT prefix interfaces with `I`.

---

## Key Files & Directories
- `gitpulse/core/`: The "Brain" of the project (repo reading, AI prompt building).
- `api/api.py`: FastAPI entry point and route definitions.
- `web/app/`: Next.js App Router structure.
- `.antigravity/rules/project-rules.md`: Deep-dive development rules (MUST READ for agents).
- `AGENTS.md`: Strategic orchestration and milestone tracking.
- `pyproject.toml`: Python dependencies and scripts.
- `web/package.json`: Frontend dependencies and scripts.
