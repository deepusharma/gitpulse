# Contributing to gitpulse

Thank you for your interest in contributing! gitpulse is a community project and all contributions — bug reports, feature ideas, documentation improvements, and code — are very welcome.

---

## Table of Contents

- [Setting up locally](#setting-up-locally)
- [Development workflow](#development-workflow)
- [Commit style](#commit-style)
- [PR process](#pr-process)
- [Reporting bugs](#reporting-bugs)
- [Environment variables](#environment-variables)

---

## Setting up locally

### Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.12+ | [python.org](https://www.python.org) |
| uv | latest | `pip install uv` or [astral.sh/uv](https://astral.sh/uv) |
| Node.js | 21+ | [nodejs.org](https://nodejs.org) |
| Git | any | — |

### Steps

```bash
# 1. Fork and clone
git clone https://github.com/<your-username>/gitpulse.git
cd gitpulse

# 2. Install Python dependencies (including test extras)
uv venv && source .venv/bin/activate
uv sync --extra dev

# 3. Configure environment
cp .env.example .env
# Edit .env and add: GROQ_API_KEY=gsk_...
# Get a free key at https://console.groq.com

# 4. Install frontend dependencies
cd web && npm ci && cd ..

# 5. Verify everything works
uv run pytest -v
cd web && npm run test && cd ..
```

You're ready to contribute!

---

## Development workflow

### Branching

```
feature/your-description    # new feature
fix/your-description        # bug fix
docs/your-description       # documentation only
test/your-description       # tests only
```

Always branch from `master`:
```bash
git checkout master && git pull
git checkout -b feature/my-feature
```

### Running the app locally

```bash
# CLI
uv run gitpulse generate --dry-run

# API server
uv run uvicorn api.api:app --reload

# Web (in a separate terminal)
cd web && npm run dev
```

### Linting & testing

```bash
# Python lint (must pass — blocks print statements via T20 rule)
uv run ruff check .

# Python tests
uv run pytest -v

# Single test
uv run pytest -k "test_name" -v

# Frontend tests
cd web && npm run test
```

All tests must pass before opening a PR.

---

## Commit style

gitpulse uses [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Use for |
|---|---|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation changes only |
| `refactor:` | Code change that is neither a feature nor a fix |
| `test:` | Adding or updating tests |
| `chore:` | Build, config, tooling, dependency updates |

**Examples:**
```
feat: add --repo flag to filter by repository name
fix: catch groq.AuthenticationError and show Rich panel
docs: add .gitpulse.toml reference table to README
test: add CLI auth failure test
chore: bump groq to 1.1.2
```

---

## PR process

1. **Reference an issue** — every PR must close or relate to an issue (`Closes #XX`)
2. **Fill the PR template** — be clear about what changed and why
3. **Pass all checks** — CI runs pytest + Vitest automatically on every PR
4. **One commit per logical change** — squash locally before pushing if needed
5. **Squash merge only** — maintainers will squash merge your PR

---

## Reporting bugs

Please use the [Bug Report template](https://github.com/deepusharma/gitpulse/issues/new?template=bug_report.md).

Include:
- gitpulse version (`gitpulse --version`)
- OS and Python version
- Steps to reproduce
- Expected vs actual behaviour
- Any relevant logs (run with `--debug` to capture them)

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Required | Your Groq API key — get one at [console.groq.com](https://console.groq.com) |
| `GITHUB_TOKEN` | Optional | Raises GitHub API rate limit from 60 to 5,000 req/hr |
| `NEXT_PUBLIC_API_URL` | Web only | FastAPI backend URL for the Next.js frontend |
| `DATABASE_URL` | API only | PostgreSQL connection string for history persistence |

Copy `.env.example` to `.env` and fill in the required values.

---

## Code standards

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

Thank you for making gitpulse better! 🎉
