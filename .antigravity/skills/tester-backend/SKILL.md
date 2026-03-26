# Backend Test Engineer — gitpulse

## Extends

Global tester-backend skill — see ~/.antigravity/skills/tester-backend/SKILL.md

## Project-specific additions

### gitpulse test locations

- core/tests/ — shared library tests
- api/tests/ — FastAPI endpoint tests
- cli/tests/ — CLI tests

### gitpulse mocking patterns

- Mock core.repo_reader.get_commits for API tests
- Mock core.summarise.summarise for API tests
- Mock core.utils.load_dotenv for utils tests
- Use respx for GitHub API httpx mocks
- Use pytest skipif for tests requiring ~/.gitpulse.toml

### gitpulse test commands

- Run all: pytest -v
- Run core only: pytest core/tests/ -v
- Run api only: pytest api/tests/ -v

### Before starting

- Read AGENTS.md
- Check testpaths in pyproject.toml
