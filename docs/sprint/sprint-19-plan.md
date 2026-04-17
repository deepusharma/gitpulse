# Sprint 19 Execution Plan — API Refactor & Code Health

**Sprint Goal:** Break `api/api.py` into focused APIRouter modules, extract nested functions from `repo_reader.py`, split `web/lib/api.ts` into types and HTTP layers, eliminate the duplicate `/health/keys` route, and resolve the duplicate API helpers in `web/app/templates/page.tsx`.
**Milestone:** v1.4 — Code Health
**Branch:** `feature/sprint-19-code-health`
**Status:** Approved — Ready to Execute

---

## Current State Audit (pre-refactor)

| File | Lines | Problem |
|---|---|---|
| `api/api.py` | **1,570** | 31 routes in one file; duplicate `GET /health/keys` at lines 168 and 205 |
| `web/lib/api.ts` | **309** | Mixed interfaces + HTTP functions; 9 interfaces + 17 functions interleaved |
| `gitpulse/core/repo_reader.py` | **274** | 3 nested async fetchers inside `_get_github_commits()` — untestable |
| `web/app/templates/page.tsx` | — | 3 local API helpers duplicate canonical versions in `lib/api.ts` |

---

## Design Decisions (Pre-approved)

| Decision | Choice | Rationale |
|---|---|---|
| Router decomposition strategy | One `APIRouter` per domain prefix | Matches FastAPI best practices; mirrors the existing test domain groupings |
| Shared models location | New `api/models.py` for cross-router types (e.g., `SummariseResponse`) | Avoids circular imports between routers |
| Shared dependencies location | New `api/dependencies.py` | Isolates FastAPI `Depends()` callables; importable by any router |
| Test split strategy | One test file per router; existing test IDs preserved | Prevents coverage gaps; minimal delta from current test structure |
| `web/lib/types.ts` | All `interface` + `type` exports; zero functions | Pure separation — any consumer imports types without loading HTTP code |
| `repo_reader.py` helper names | `_fetch_commits`, `_fetch_prs`, `_fetch_issues` (module-level, private) | Consistent naming; `_` prefix signals internal use |
| File size rule | 300-line max per file in `api/` and `gitpulse/core/` | Generous for docstrings + type hints but draws a clear line |

---

## Target File Structure

```
api/
├── api.py               ← ≤ 80 lines: app init, lifespan, CORS, router registration
├── models.py            ← NEW: shared Pydantic models (SummariseResponse, etc.)
├── dependencies.py      ← NEW: shared FastAPI Depends (get_user_repos, db_pool_guard)
├── db.py                ← unchanged
├── cache.py             ← unchanged
├── routers/
│   ├── __init__.py      ← NEW
│   ├── health.py        ← GET /health, GET /health/keys (deduplicated)
│   ├── summarise.py     ← POST /summarise, PATCH /history/:id/public, GET /summary/public/:id
│   ├── history.py       ← GET /history
│   ├── analytics.py     ← GET /analytics/*, GET /analytics/compare
│   ├── insights.py      ← GET /insights/metrics, GET /insights/health, GET /analytics/insights, POST /insights/recommendations
│   ├── github.py        ← GET /github/validate, GET /github/repos
│   ├── team.py          ← POST /team/roster, GET /team/rosters, GET /team/roster/:id, DELETE /team/roster/:id, POST /team/summarise
│   ├── mcp.py           ← GET /mcp/sse, POST /mcp/sse/call
│   ├── templates.py     ← POST/GET/DELETE /prompt-templates
│   ├── deliver.py       ← POST /deliver/slack
│   └── badges.py        ← GET /badges/*
└── tests/
    ├── test_health.py
    ├── test_summarise.py
    ├── test_history.py
    ├── test_analytics.py
    ├── test_insights.py
    ├── test_github.py
    ├── test_team.py
    ├── test_mcp_api.py
    ├── test_templates.py
    ├── test_deliver.py
    └── test_badges.py

web/lib/
├── types.ts             ← NEW: all interfaces and types (no functions)
└── api.ts               ← HTTP functions only; imports types from ./types
```

---

## Route → Router Mapping

| Route(s) | Target Router | Lines in api.py |
|---|---|---|
| `GET /health`, `GET /health/keys` (×2 → deduplicated to ×1) | `routers/health.py` | 157–240 |
| `POST /summarise`, `PATCH /history/:id/public`, `GET /summary/public/:id`, `GET /analytics/compare` | `routers/summarise.py` | 244–515 |
| `GET /history` | `routers/history.py` | 515–648 |
| `GET /analytics/commits-per-day`, `/analytics/repos-breakdown`, `/analytics/all` | `routers/analytics.py` | 649–876 |
| `GET /analytics/insights`, `GET /insights/metrics`, `GET /insights/health`, `POST /insights/recommendations` | `routers/insights.py` | 877–1159 |
| `GET /github/validate`, `GET /github/repos` | `routers/github.py` | 699–747 |
| `POST /team/roster`, `GET /team/rosters`, `GET /team/roster/:id`, `DELETE /team/roster/:id`, `POST /team/summarise` | `routers/team.py` | 1031–1159 |
| `POST /deliver/slack` | `routers/deliver.py` | 1160–1189 |
| `GET /badges/streak`, `/badges/commits`, `/badges/health` | `routers/badges.py` | 1190–1236 |
| `GET /mcp/sse`, `POST /mcp/sse/call` | `routers/mcp.py` | 1237–1357 |
| `POST/GET/DELETE /prompt-templates` | `routers/templates.py` | 1460–1570 |

> [!NOTE]
> `GET /analytics/compare` logically belongs to summarise (it compares summary periods), so it lands in `routers/summarise.py`. The `/analytics/all` bulk endpoint lives in `routers/analytics.py`.

---

## Order of Execution

```
S19.6  → Update AGENTS.md + GEMINI.md with 300-line rule
S19.5  → Dedup GET /health/keys (2-line fix, zero risk)
S19.7  → Extract repo_reader.py nested fetchers + 3 new unit tests
S19.8  → Split web/lib/api.ts + fix templates/page.tsx duplication
S19.1  → Scaffold api/routers/ + api/models.py + api/dependencies.py
S19.3  → Move shared deps into api/dependencies.py
S19.2  → Migrate routes domain-by-domain (pytest after EACH domain)
S19.4  → Split api/tests/test_api.py into per-router test files
```

Run `uv run pytest -v` after every domain migration. Run `npm run lint` after S19.8.

---

## Step-by-Step Technical Plan

### S19.6 — Coding Standard Update *(~10 min)*

**Files:** `AGENTS.md`, `GEMINI.md`

Add to `AGENTS.md` under **Coding Standards → Python**:

```markdown
- **File size limit:** 300 lines max per file in `api/` and `gitpulse/core/`. Files approaching this limit must be split before adding new features.
```

Add the equivalent rule to `GEMINI.md` under **Development Conventions → Core Mandates** (after item 5):

```markdown
6. **File Size**: No file in `api/` or `gitpulse/core/` shall exceed **300 lines**. Split into modules before adding features if at the limit.
```

---

### S19.5 — Dedup `GET /health/keys` *(~5 min)*

**File:** `api/api.py` line 205

`GET /health/keys` is registered **twice** — at lines 168 and 205 (confirmed in audit above). FastAPI silently uses the first and ignores the second. Simply **delete** the second registration (lines 205–240) and its associated handler function (they are identical copies).

Verification: `curl localhost:8000/health/keys` returns the same response as before.

---

### S19.7 — Extract `repo_reader.py` Nested Fetchers *(~45 min)*

**File:** `gitpulse/core/repo_reader.py`

**Problem:** `_get_github_commits()` contains three nested async functions that are ~160 lines total and cannot be unit tested independently.

**Fix:** Lift them to module-level private functions with explicit parameter signatures:

```python
# BEFORE (nested inside _get_github_commits — untestable)
async def fetch_repo_commits(client, repo, retries=3): ...
async def fetch_repo_prs(...): ...
async def fetch_repo_issues(...): ...

# AFTER (module-level — independently testable)
async def _fetch_commits(
    client: httpx.AsyncClient,
    repo: str,
    username: str,
    since_iso: str,
    headers: dict,
    semaphore: asyncio.Semaphore,
) -> list[dict]: ...

async def _fetch_prs(
    client: httpx.AsyncClient,
    repo: str,
    username: str,
    since: datetime,
    headers: dict,
    semaphore: asyncio.Semaphore,
) -> list[dict]: ...

async def _fetch_issues(
    client: httpx.AsyncClient,
    repo: str,
    username: str,
    since: datetime,
    headers: dict,
    semaphore: asyncio.Semaphore,
) -> list[dict]: ...
```

- `_get_github_commits()` calls each helper exactly as before — **zero behaviour change**.
- Google docstrings on each extracted function.
- File must remain ≤ 300 lines after the change.

**New tests** — `gitpulse/core/tests/test_repo_reader.py`:
- `test_fetch_commits_returns_list` — `respx` mock of GitHub API `/repos/{owner}/{repo}/commits`, assert list of dicts with `message`, `hash`, `date` keys.
- `test_fetch_prs_returns_list` — mock `/repos/{owner}/{repo}/pulls`, assert PR fields present.
- `test_fetch_issues_returns_list` — mock `/repos/{owner}/{repo}/issues`, assert issue fields present.

Use the existing `respx` + `httpx.AsyncClient` pattern already in the test file.

---

### S19.8 — Split `web/lib/api.ts` + Fix `templates/page.tsx` *(~45 min)*

#### Part A — Create `web/lib/types.ts`

Extract **all** `interface` and `type` declarations from `api.ts` into a new `web/lib/types.ts`. Based on current audit, these are:

```typescript
// web/lib/types.ts — interfaces only, zero HTTP code

export interface SummariseRequest { ... }
export interface SummariseResponse { ... }
export interface HistoryRecord { ... }
export interface HistoryResponse { ... }
export interface PublicSummaryResponse { ... }
export interface CompareRecord { ... }
export interface CompareResponse { ... }
export class ApiError extends Error { ... }  // keep here — shared error type
export interface RosterRequest { ... }
export interface RosterResponse { ... }
export interface TeamSummariseRequest { ... }
export interface TeamSummariseResponse { ... }
export interface RecommendationsRequest { ... }
export interface RecommendationsResponse { ... }
export interface PromptTemplate { ... }
export interface PromptTemplateCreate { ... }
```

#### Part B — Trim `web/lib/api.ts`

After moving interfaces to `types.ts`, `api.ts` becomes:

```typescript
// web/lib/api.ts — HTTP functions only
import type { SummariseRequest, SummariseResponse, ... } from "./types";
export { ApiError } from "./types";          // re-export for backward compat
export const API_URL = ...;

export async function generateSummary(...) { ... }
export async function togglePublicSummary(...) { ... }
// ... all 17 HTTP functions unchanged
```

Result: `api.ts` drops from 309 lines to ~220 lines (within 300-line limit).

> [!IMPORTANT]
> All existing component imports `from "@/lib/api"` continue to work unchanged — the HTTP functions stay in `api.ts`. Type-only imports in components should be updated to `from "@/lib/types"` where applicable, but this is not strictly required for correctness.

#### Part C — Fix `web/app/templates/page.tsx` duplication

Delete lines 34–55 (the three local helper functions: `listTemplates`, `createTemplate`, `deleteTemplate`) and replace usages:

| Before (local) | After (canonical from lib/api) |
|---|---|
| `listTemplates(username)` | `listPromptTemplates(username)` |
| `createTemplate({ name, content, username })` | `createPromptTemplate({ name, content, username })` |
| `deleteTemplate(id)` | `deletePromptTemplate(id)` |

Also add the import at the top:
```typescript
import { listPromptTemplates, createPromptTemplate, deletePromptTemplate } from "@/lib/api";
```

Run `npm run lint` after this step to verify no type errors.

---

### S19.1 — Scaffold Router Structure *(~20 min)*

**Create the following new files** (all empty stubs initially):

```
api/routers/__init__.py
api/routers/health.py
api/routers/summarise.py
api/routers/history.py
api/routers/analytics.py
api/routers/insights.py
api/routers/github.py
api/routers/team.py
api/routers/mcp.py
api/routers/templates.py
api/routers/deliver.py
api/routers/badges.py
api/models.py
api/dependencies.py
```

Each router stub follows this template:

```python
"""Router for [domain] endpoints."""
import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/[prefix]", tags=["[Domain]"])
```

`api/api.py` gets a new import block at the bottom (not yet wired up — just declared):

```python
from api.routers import health, summarise, history, analytics, insights, github, team, mcp, templates, deliver, badges
```

Run `uv run pytest -v` — all 82+ tests must still pass (nothing moved yet).

---

### S19.3 — Extract Shared Dependencies *(~20 min)*

**File:** `api/dependencies.py`

Move two reusable patterns from `api/api.py` into this file:

#### Dependency 1: `get_db_pool`

The "503 if DB disabled" guard that currently appears inline in ~12 routes:

```python
async def get_db_pool() -> asyncpg.Pool:
    """Return the active DB pool or raise 503 if DB is disabled.

    Args:
        None

    Returns:
        The active asyncpg connection pool.

    Raises:
        HTTPException: 503 if the database pool is not initialized.
    """
    if db.pool is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return db.pool
```

Usage in routers: `pool: asyncpg.Pool = Depends(get_db_pool)`

#### Dependency 2: `get_user_repos`

`_get_user_repos()` is a private helper currently called inline from 6 routes. Lift to `dependencies.py` as a proper async dependency:

```python
async def get_user_repos(username: str, repos: list[str] | None = None) -> list[str]:
    """Resolve the repo list for a user — use provided list or fetch all from GitHub.

    Args:
        username: GitHub username.
        repos: Optional explicit repo list. If None or empty, fetches all repos via API.

    Returns:
        List of repository name strings.
    """
```

#### Dependency 3: `get_token_override`

Reads `X-GitHub-Token` from the request header and returns it as an optional string:

```python
async def get_token_override(request: Request) -> str | None:
    """Extract optional user-supplied GitHub token from request headers.

    Args:
        request: The incoming FastAPI request.

    Returns:
        Token string if X-GitHub-Token header is present, else None.
    """
    return request.headers.get("X-GitHub-Token")
```

---

### S19.2 — Migrate Routes (Domain by Domain) *(~90 min)*

Migrate in this order. Run `uv run pytest -v` after **each domain**.

#### Domain 1: Health (`routers/health.py`) — ~10 lines

Move `GET /health` and the single (deduplicated) `GET /health/keys` handler. No model dependencies. Simplest migration — good confidence check.

```python
router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check(): ...

@router.get("/health/keys")
async def health_keys(): ...
```

Wire in `api.py`: `app.include_router(health.router)`.

#### Domain 2: GitHub (`routers/github.py`) — ~50 lines

Move `GET /github/validate` and `GET /github/repos`. These are read-only, no DB dependency.

#### Domain 3: History (`routers/history.py`) — ~135 lines

Move `GET /history`. Uses `get_db_pool` dependency from `dependencies.py`.

#### Domain 4: Summarise (`routers/summarise.py`) — ~270 lines

Move `POST /summarise`, `PATCH /history/{id}/public`, `GET /summary/public/{id}`, `GET /analytics/compare`. Imports `SummariseResponse` from `api/models.py`.

> [!IMPORTANT]
> `SummariseResponse` is shared — move it to `api/models.py` before this step to avoid circular imports.

#### Domain 5: Analytics (`routers/analytics.py`) — ~230 lines

Move `GET /analytics/commits-per-day`, `/analytics/repos-breakdown`, `/analytics/all`. These share the `analytics_cache` — import it from `api.cache`.

#### Domain 6: Insights (`routers/insights.py`) — ~280 lines

Move `GET /analytics/insights`, `GET /insights/metrics`, `GET /insights/health`, `POST /insights/recommendations`. Largest domain — check line count stays ≤ 300.

#### Domain 7: Team (`routers/team.py`) — ~130 lines

Move all 5 team routes. DB-heavy — uses `get_db_pool` dependency.

#### Domain 8: Deliver (`routers/deliver.py`) — ~30 lines

Move `POST /deliver/slack`.

#### Domain 9: Badges (`routers/badges.py`) — ~50 lines

Move `GET /badges/streak`, `/badges/commits`, `/badges/health`.

#### Domain 10: MCP (`routers/mcp.py`) — ~120 lines

Move `GET /mcp/sse` and `POST /mcp/sse/call`.

#### Domain 11: Templates (`routers/templates.py`) — ~110 lines

Move `POST/GET/DELETE /prompt-templates`. Uses `get_db_pool` dependency.

#### Final `api/api.py` target (~70 lines):

```python
"""GitPulse FastAPI application — entry point and router registration."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import db
from api.routers import (
    health, summarise, history, analytics, insights,
    github, team, mcp, templates, deliver, badges,
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db()
    yield
    await db.close_db()

app = FastAPI(title="GitPulse API", lifespan=lifespan)

app.add_middleware(CORSMiddleware, ...)

app.include_router(health.router)
app.include_router(github.router)
app.include_router(summarise.router)
app.include_router(history.router)
app.include_router(analytics.router)
app.include_router(insights.router)
app.include_router(team.router)
app.include_router(deliver.router)
app.include_router(badges.router)
app.include_router(mcp.router)
app.include_router(templates.router)
```

---

### S19.4 — Split Test File *(~60 min)*

**Current:** `api/tests/test_api.py` — single large file importing the whole app.

**Target:** One test file per router. Each imports only the app (FastAPI `TestClient`) — the split is logical (by test function grouping), not by import change, since `TestClient` always needs the full app.

Create these files (move corresponding test functions from `test_api.py`):

| New Test File | Test Functions to Move |
|---|---|
| `api/tests/test_health.py` | `test_health_*`, `test_health_keys_*` |
| `api/tests/test_summarise.py` | `test_summarise_*`, `test_patch_summary_*`, `test_get_public_*`, `test_analytics_compare_*` |
| `api/tests/test_history.py` | `test_history_*` |
| `api/tests/test_analytics.py` | `test_analytics_commits_*`, `test_analytics_repos_*`, `test_analytics_all_*` |
| `api/tests/test_insights.py` | `test_insights_*`, `test_recommendations_*` |
| `api/tests/test_github.py` | `test_github_validate_*`, `test_github_repos_*` |
| `api/tests/test_team.py` | `test_team_*` |
| `api/tests/test_deliver.py` | `test_deliver_*` |
| `api/tests/test_badges.py` | `test_badges_*` |
| `api/tests/test_mcp_api.py` | `test_mcp_*` |
| `api/tests/test_templates.py` | `test_prompt_template_*` |

Delete the original `api/tests/test_api.py` once all functions are migrated.

Run `uv run pytest -v` — test count must be ≥ the pre-sprint count.

---

## File Change Summary

| File | Change | Story |
|---|---|---|
| `AGENTS.md` | Add 300-line file size rule | S19.6 |
| `GEMINI.md` | Add 300-line file size rule | S19.6 |
| `api/api.py` | Reduce to ~70 lines (app init + router registration only) | S19.1, S19.2 |
| `api/models.py` | **NEW** — shared Pydantic models | S19.1 |
| `api/dependencies.py` | **NEW** — `get_db_pool`, `get_user_repos`, `get_token_override` | S19.3 |
| `api/routers/__init__.py` | **NEW** | S19.1 |
| `api/routers/health.py` | **NEW** | S19.2 |
| `api/routers/summarise.py` | **NEW** | S19.2 |
| `api/routers/history.py` | **NEW** | S19.2 |
| `api/routers/analytics.py` | **NEW** | S19.2 |
| `api/routers/insights.py` | **NEW** | S19.2 |
| `api/routers/github.py` | **NEW** | S19.2 |
| `api/routers/team.py` | **NEW** | S19.2 |
| `api/routers/mcp.py` | **NEW** | S19.2 |
| `api/routers/templates.py` | **NEW** | S19.2 |
| `api/routers/deliver.py` | **NEW** | S19.2 |
| `api/routers/badges.py` | **NEW** | S19.2 |
| `api/tests/test_api.py` | **DELETED** — split into per-router files | S19.4 |
| `api/tests/test_health.py` | **NEW** | S19.4 |
| `api/tests/test_summarise.py` | **NEW** | S19.4 |
| `api/tests/test_history.py` | **NEW** | S19.4 |
| `api/tests/test_analytics.py` | **NEW** | S19.4 |
| `api/tests/test_insights.py` | **NEW** | S19.4 |
| `api/tests/test_github.py` | **NEW** | S19.4 |
| `api/tests/test_team.py` | **NEW** | S19.4 |
| `api/tests/test_mcp_api.py` | **NEW** | S19.4 |
| `api/tests/test_templates.py` | **NEW** | S19.4 |
| `api/tests/test_deliver.py` | **NEW** | S19.4 |
| `api/tests/test_badges.py` | **NEW** | S19.4 |
| `gitpulse/core/repo_reader.py` | Extract 3 nested fetchers to module-level | S19.7 |
| `gitpulse/core/tests/test_repo_reader.py` | Add 3 new unit tests for extracted fetchers | S19.7 |
| `web/lib/types.ts` | **NEW** — all TypeScript interfaces | S19.8 |
| `web/lib/api.ts` | Remove interfaces; import from `./types`; HTTP functions only | S19.8 |
| `web/app/templates/page.tsx` | Remove 3 local helper functions; import from `@/lib/api` | S19.8 |

---

## Definition of Done

- [ ] `api/api.py` is ≤ 80 lines (app init + router registration only)
- [ ] Every router file is ≤ 300 lines
- [ ] `GET /health/keys` is registered exactly once (no duplicate)
- [ ] `api/dependencies.py` contains `get_db_pool`, `get_user_repos`, `get_token_override`
- [ ] `uv run pytest -v` passes — test count ≥ pre-sprint count (82+ tests)
- [ ] `repo_reader.py` has `_fetch_commits`, `_fetch_prs`, `_fetch_issues` at module level
- [ ] 3 new `test_repo_reader.py` unit tests pass for extracted fetchers
- [ ] `web/lib/types.ts` exists and exports all interfaces
- [ ] `web/lib/api.ts` is ≤ 300 lines and contains only HTTP functions
- [ ] `web/app/templates/page.tsx` uses `listPromptTemplates`, `createPromptTemplate`, `deletePromptTemplate` from `@/lib/api`
- [ ] `AGENTS.md` and `GEMINI.md` updated with the 300-line rule
- [ ] `npm run lint` passes in `web/`
- [ ] PR squash-merged to master

---

## Out of Scope

- Changing any route behaviour or response schema (pure structural refactor only)
- Adding new routes or features
- `web/components/SummaryForm.tsx` (302 lines but single-responsibility form — leave as-is)
- `gitpulse_mcp/server.py` (299 lines, within limit — no split needed yet)
- `web/app/insights/page.tsx` chart extraction (already done in Sprint 17 Stream 2)
- Sprint 18 gamification / VS Code extension (next sprint)

---

## Risk Notes

> [!WARNING]
> The `analytics_cache` object is imported by multiple routes. After migration it must be imported from `api.cache` in each router file — do not re-instantiate it per router or cache isolation will break.

> [!WARNING]
> `POST /summarise` returns `SummariseResponse` which is also referenced by `POST /team/summarise`. Move this model to `api/models.py` **before** migrating either router to avoid a circular import.

> [!NOTE]
> `uv run pytest -v` must be run after every single domain migration — not just at the end. A regression caught mid-migration is far cheaper to debug than one discovered after all 31 routes have moved.
