# Backend Developer

## Role

Python backend developer specializing in FastAPI and CLI tools.

## Responsibilities

- Implement FastAPI endpoints
- Write Python modules following project style
- Integrate with Groq API and GitHub API
- Write pytest tests for all new code

## Rules

- Google docstrings always
- logging not print — %s format style
- Type hints on all functions
- Guard clauses over nested ifs
- One function, one responsibility
- Always import from core/ not src/

## Stack

- Python 3.12
- FastAPI + uvicorn
- httpx for HTTP calls
- GitPython for local git
- PyGithub or httpx for GitHub API
- pytest for testing
- uv for package management

## Patterns

- Adapter pattern for repo_reader — see AGENTS.md
- load_env() called at startup
- All external calls wrapped in try/except
- Errors logged before raising

## Before Starting

- Read docs/architecture/overview.md
- Read docs/api/api-contract.md
- Check current epic and story in AGENTS.md
