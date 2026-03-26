# Backend Developer — gitpulse

## Extends

Global backend-dev skill — see ~/.antigravity/skills/backend-dev/SKILL.md

## Project-specific additions

### gitpulse stack

- Groq API — llama-3.3-70b-versatile
- GitPython for local git
- httpx for GitHub API calls

### gitpulse patterns

- Adapter pattern — get_commits(source="local"|"github")
- Always import from core/ not src/
- load_env() called at startup in cli.py and api.py

### gitpulse structure

- core/ — shared library
- cli/ — CLI client
- api/ — FastAPI backend
- web/ — Next.js frontend

### Before starting

- Read AGENTS.md
- Read docs/architecture/overview.md
- Read docs/api/api-contract.md
- Check current sprint in docs/sprint/
