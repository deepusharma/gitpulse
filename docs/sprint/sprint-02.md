# Sprint 02 — Full Backend

**Sprint goal:** Build and deploy the FastAPI backend with GitHub API adapter.  
**Milestone:** v0.2 — Web UI  
**Duration:** 2026-03-21  
**Status:** In Progress

---

## Sprint Stories

| Issue | Story                                    | Status         | Session |
| ----- | ---------------------------------------- | -------------- | ------- |
| #24   | Add GitHub API adapter to repo_reader    | 🔵 This Sprint | Today   |
| #25   | Support source parameter local or github | 🔵 This Sprint | Today   |
| #26   | Accept github username and repo list     | 🔵 This Sprint | Today   |
| #27   | Write tests for GitHub API adapter       | 🔵 This Sprint | Today   |
| #28   | Handle rate limiting and API errors      | 🔵 This Sprint | Today   |
| #29   | Create FastAPI app skeleton in api/      | 🔵 This Sprint | Today   |
| #30   | Implement POST /summarise endpoint       | 🔵 This Sprint | Today   |
| #31   | Wire core modules into API endpoint      | 🔵 This Sprint | Today   |
| #32   | Add CORS support                         | 🔵 This Sprint | Today   |
| #33   | Add Pydantic request validation          | 🔵 This Sprint | Today   |
| #34   | Write tests for API endpoints            | 🔵 This Sprint | Today   |
| #35   | Deploy API to Railway                    | 🔵 This Sprint | Today   |

---

## Story Details

### #24, #25, #26 — GitHub API Adapter

**Goal:** Add GitHub API mode to `core/repo_reader.py`.

**Current state:**

```python
def get_commits(days: int = 7) -> list:
    # reads from ~/.gitpulse.toml and local git repos
```

**Target state:**

```python
def get_commits(source: str = "local", days: int = 7, **kwargs) -> list:
    if source == "local":
        return _get_local_commits(days)
    elif source == "github":
        return _get_github_commits(days=days, **kwargs)
    else:
        raise ValueError(f"Unknown source: {source}")
```

**GitHub API details:**

- Endpoint: `GET https://api.github.com/repos/{username}/{repo}/commits`
- Query params: `since={ISO datetime}`, `per_page=100`
- Auth header: `Authorization: Bearer {GITHUB_TOKEN}` (optional — raises rate limit)
- Response: list of commit objects

**Commit dict shape (must match local mode):**

```python
{
    "repo": repo_name,
    "message": commit["commit"]["message"],
    "author": commit["commit"]["author"]["name"],
    "date": datetime.fromisoformat(commit["commit"]["author"]["date"]),
    "hash": commit["sha"]
}
```

**Done when:**

- [ ] `get_commits(source="local")` works as before
- [ ] `get_commits(source="github", username="deepusharma", repos=["gitpulse"], days=7)` returns commits
- [ ] Returns same flat list shape as local mode
- [ ] `GITHUB_TOKEN` used if available in env

---

### #27, #28 — Tests + Error Handling

**Tests to write in `core/tests/test_repo_reader.py`:**

```python
# Mock httpx calls — no real GitHub API calls
def test_get_commits_github_returns_list()
def test_get_commits_github_empty_repo()
def test_get_commits_github_invalid_source_raises()
def test_get_commits_github_404_raises()
def test_get_commits_github_429_raises()
```

**Error handling:**

- 404 → raise `ValueError("Repo '{username}/{repo}' not found or is private")`
- 429 → raise `ValueError("GitHub API rate limit exceeded")`
- 401 → raise `ValueError("GitHub API unauthorised — check GITHUB_TOKEN")`
- Network error → log and raise

---

### #29, #30, #31, #32, #33 — FastAPI Backend

**File:** `api/api.py`

**Structure:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS
app.add_middleware(CORSMiddleware, ...)

# Models
class SummariseRequest(BaseModel):
    username: str
    repos: list[str]
    days: int = 7

class SummariseResponse(BaseModel):
    display: str
    summary: str
    repos: list[str]
    days: int
    generated_at: str

# Routes
@app.get("/health")
async def health(): ...

@app.post("/summarise")
async def summarise(request: SummariseRequest): ...
```

**See `docs/api/api-contract.md` for full request/response spec.**

**Dependencies to add to pyproject.toml:**

```
fastapi
uvicorn
httpx
python-dotenv (already installed)
```

---

### #34 — API Tests

**File:** `api/tests/test_api.py`

**Tests:**

```python
def test_health_returns_200()
def test_summarise_valid_request_returns_200()
def test_summarise_missing_username_returns_422()
def test_summarise_empty_repos_returns_422()
```

**Use `fastapi.testclient.TestClient` and mock `core.repo_reader.get_commits` and `core.summarise.summarise`.**

---

### #35 — Railway Deployment

**Steps:**

1. Create `Procfile` at project root:

```
   web: uvicorn api.api:app --host 0.0.0.0 --port $PORT
```

2. Sign up at railway.app with GitHub
3. New project → Deploy from GitHub repo
4. Set environment variables:
   - `GROQ_API_KEY`
   - `GITHUB_TOKEN` (optional)
5. Verify `GET /health` on live URL
6. Test `POST /summarise` with curl

---

## Order of Work

```
#24 → #25 → #26 → #27 → #28 → #29 → #30 → #31 → #32 → #33 → #34 → #35
```

---

## Agent Instructions

Use `@backend-dev` skill for all stories.

---

## Definition of Done

Sprint is complete when:

- [ ] GitHub API adapter working for public repos
- [ ] FastAPI backend running locally
- [ ] All tests passing
- [ ] API deployed to Railway
- [ ] `GET /health` returns 200 on live URL
- [ ] `POST /summarise` works end to end
