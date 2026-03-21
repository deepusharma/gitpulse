# Sprint 02 — Full Backend Execution Plan

## User Review Required

> [!IMPORTANT]
> **Gaps & Assumptions Detected:**
> 1. `httpx` is not currently installed. The [pyproject.toml](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/pyproject.toml) file under dependencies only lists `["typer", "groq", "gitpython", "rich", "python-dotenv"]`. I will add `httpx` during Stream 1, and later add `fastapi` and `uvicorn` for Stream 2.
> 2. [api-contract.md](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/docs/api/api-contract.md) mentions that GitHub returns date strings in ISO format. The [repo_reader.py](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/src/repo_reader.py) returns aware `datetime` objects for `date` currently (`commit.committed_datetime` from GitPython is an aware UTC timestamp). We must ensure that the GitHub `date` strings are parsed into aware `datetime` objects (`datetime.fromisoformat()`) to maintain seamless equivalence.
> 3. Stream 1 is a hard dependency for Stream 2: The FastAPI app will fail its core use-case if `source="github"` doesn't work correctly. We will execute and verify Stream 1 completely before looking at Stream 2.

## Stream 1 Execution Plan (GitHub API Adapter - #24, #25, #26, #27, #28)

We will modify [core/repo_reader.py](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/core/repo_reader.py) to use an adapter pattern, introducing GitHub scraping while keeping local evaluation behavior consistent.

### [MODIFY] [pyproject.toml](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/pyproject.toml)
- Add `httpx` to the list of `dependencies`. Run `uv pip install -e ".[dev]"` afterward.

### [MODIFY] [core/repo_reader.py](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/core/repo_reader.py)
1. Introduce the routing interface:
   ```python
   def get_commits(source: str = "local", days: int = 7, **kwargs) -> list:
       if source == "local":
           return _get_local_commits(days)
       elif source == "github":
           return _get_github_commits(days=days, **kwargs)
       else:
           raise ValueError(f"Unknown source: {source}")
   ```
2. Rename current [get_commits](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/core/repo_reader.py#37-83) function to `_get_local_commits(days: int = 7)`.
3. Create `_get_github_commits(days: int = 7, username: str = None, repos: list[str] = None) -> list`:
   - Calculate `since` using `datetime.now(timezone.utc) - timedelta(days=days)`.
   - Setup `httpx` loop for every repo in [repos](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/core/tests/test_repo_reader.py#19-23).
   - Setup Authorization headers to pass `GITHUB_TOKEN` from `os.environ` if accessible. Include `Accept: application/vnd.github+json` and `X-GitHub-Api-Version: 2022-11-28`.
   - Intercept error status codes to properly elevate:
     - 404: `ValueError("Repo 'username/repo' not found or is private")`
     - 429: `ValueError("GitHub API rate limit exceeded")`
     - 401: `ValueError("GitHub API unauthorised — check GITHUB_TOKEN")`
   - Iterate over commits returning flat objects of shape: `{"repo": repo_name, "message": commit["commit"]["message"], "author": commit["commit"]["author"]["name"], "date": datetime.fromisoformat(commit["commit"]["author"]["date"]), "hash": commit["sha"]}`.

### [MODIFY] [core/tests/test_repo_reader.py](file:///Users/shrutirastogi/Documents/GitProjects/public/gitpulse/core/tests/test_repo_reader.py)
- Add mocks for HTTP calls using `unittest.mock.patch("httpx.get")` to bypass live requests.
- Integrate the 5 test cases specified: returns list, empty repo, invalid source raises, 404 raises, 429 raises.

## Verification Plan
1. Validate `pytest -v` accurately runs all `repo_reader` tests. Tests should fully mock all `httpx` endpoints.
2. The CLI uses `source="local"` directly without explicit arguments currently. We will verify that running `python -m cli.cli --days 1` continues to function.
