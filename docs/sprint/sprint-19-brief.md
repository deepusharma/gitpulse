# Sprint 19 — API Refactor & Code Health

**Sprint goal:** Break `api/api.py` into focused routers, extract nested functions from `repo_reader.py`, split `web/lib/api.ts` into types and HTTP layers, eliminate the duplicate `/health/keys` route, and resolve the duplicate API helper functions introduced in `web/app/templates/page.tsx` during Sprint 17.
**Milestone:** v1.4 — Code Health
**Duration:** Day 13 (~4 hours)
**Status:** Not Started — brief updated after Sprint 17 post-merge review (2026-04-15)

---

## Why This Sprint Exists

`api/api.py` has grown organically across 17 sprints. As of Sprint 17 it stands at **1,570 lines** and **31 routes** — all in a single file. This creates four concrete problems:

1. **Merge conflicts** — parallel work on different domain areas collides in the same file.
2. **Discoverability** — finding the right route requires scrolling through unrelated domains.
3. **Test coupling** — `api/tests/test_api.py` imports the entire app, slowing changes.
4. **Cognitive load** — new contributors must understand the whole module to change one endpoint.

FastAPI's `APIRouter` was designed exactly for this decomposition. This sprint applies it.

---

## Proposed File Structure (after refactor)

```
api/
├── api.py            ← FastAPI app init, lifespan, CORS, router registration only (~80 lines)
├── db.py             ← unchanged
├── cache.py          ← unchanged
├── routers/
│   ├── __init__.py
│   ├── summarise.py  ← POST /summarise, PATCH /history/:id/public, GET /summary/public/:id
│   ├── history.py    ← GET /history
│   ├── analytics.py  ← GET /analytics/*, GET /insights/*, GET /analytics/compare
│   ├── github.py     ← GET /github/validate, GET /github/repos
│   ├── team.py       ← POST /team/roster, GET /team/rosters, GET /team/roster/:id,
│   │                    DELETE /team/roster/:id, POST /team/summarise
│   ├── mcp.py        ← GET /mcp/sse, POST /mcp/sse/call
│   ├── recommendations.py ← POST /insights/recommendations
│   ├── templates.py  ← POST/GET/DELETE /prompt-templates
│   ├── deliver.py    ← POST /deliver/slack
│   ├── badges.py     ← GET /badges/*
│   └── health.py     ← GET /health, GET /health/keys (deduplicated)
├── dependencies.py   ← shared FastAPI dependencies (_get_user_repos, get_db_pool guard)
└── tests/
    ├── test_summarise.py
    ├── test_analytics.py
    ├── test_team.py
    ├── test_mcp_api.py
    ├── test_templates.py
    ├── test_recommendations_api.py
    └── ...              ← one test file per router
```

---

## File Size Guideline (new coding standard)

> **Rule:** No Python module in `api/` or `gitpulse/core/` shall exceed **300 lines**. If adding a feature would push a file past this limit, the feature goes into a new module first.

This limit is deliberately generous — it accommodates large docstrings and type annotations — but draws a clear line. The rule will be added to `AGENTS.md` and `GEMINI.md`.

---

## Sprint Stories

| Issue | Story | Status | Priority |
|---|---|---|---|
| TBD | S19.1: Create `api/routers/` structure + `APIRouter` per domain | 🔵 This Sprint | High |
| TBD | S19.2: Migrate all 31 routes into respective router files | 🔵 This Sprint | High |
| TBD | S19.3: Extract shared dependencies into `api/dependencies.py` | 🔵 This Sprint | High |
| TBD | S19.4: Split `api/tests/test_api.py` into per-router test files | 🔵 This Sprint | Medium |
| TBD | S19.5: Fix duplicate `GET /health/keys` route (currently registered twice) | 🔵 This Sprint | Medium |
| TBD | S19.6: Add 300-line file size rule to `AGENTS.md` and `GEMINI.md` | 🔵 This Sprint | Low |
| TBD | S19.7: Extract nested fetchers in `repo_reader.py` to module-level + tests | 🔵 This Sprint | Low |
| TBD | S19.8: Split `web/lib/api.ts` into `lib/types.ts` + `lib/api.ts` | 🔵 This Sprint | Low |

---

## Story Details

### S19.1 — Router Structure

- Create `api/routers/__init__.py`.
- Create one file per domain (see file map above) — each file instantiates `APIRouter` with a `prefix` and `tags`.
- `api/api.py` becomes the thin orchestrator: it only creates the `FastAPI` app, registers the lifespan, adds CORS, and calls `app.include_router(...)` for each router.

### S19.2 — Route Migration

- Move routes **domain by domain**, running `uv run pytest -v` after each domain to catch regressions immediately.
- The Pydantic models for each domain move into their respective router file.
- Shared models (e.g., `SummariseResponse`) used across routers stay in a new `api/models.py`.

### S19.3 — Shared Dependencies

- `_get_user_repos()` is currently a private helper called from 6 different routes. Move it to `api/dependencies.py` as a FastAPI dependency:
  ```python
  async def get_user_repos(username: str) -> list[str]:
      ...
  ```
- `get_db_pool()` guard (the 503 pattern) extracted as a reusable dependency.

### S19.4 — Test Split

- Mirror the router structure: one test file per router.
- Each test file imports only its router's app slice, not the entire `api.py`.
- Existing test coverage must be preserved at 100%.

### S19.5 — Dedup `/health/keys`

- `GET /health/keys` is registered **twice** in the current `api.py` (lines 146 and 183) — a copy-paste artifact. FastAPI silently uses the first registration and ignores the second. Remove the duplicate.

### S19.6 — Coding Standard Update

Add to `AGENTS.md` under **Coding Standards → Python**:

> **File size limit:** 300 lines max per file in `api/` and `gitpulse/core/`. Files approaching the limit must be split before adding new features.

Add the same rule to `GEMINI.md` under **Development Conventions → Core Mandates**.

---

### S19.7 — `repo_reader.py` — Extract nested fetchers (274 lines)

**Problem:** `_get_github_commits()` contains three nested async functions
(`fetch_repo_commits`, `fetch_repo_prs`, `fetch_repo_issues`) totalling ~160 lines.
Nested functions cannot be individually unit-tested and force the entire 274-line file
to be loaded to understand any single fetcher.

**Fix:** Lift the three nested helpers to module-level private functions:

```python
# Before — nested inside _get_github_commits(), untestable
async def fetch_repo_commits(client, repo, retries=3): ...

# After — module-level, independently testable
async def _fetch_commits(client, repo, username, since_iso, headers, semaphore): ...
async def _fetch_prs(client, repo, username, since, headers, semaphore): ...
async def _fetch_issues(client, repo, username, since, headers, semaphore): ...
```

- Zero behaviour change — `_get_github_commits` calls the same logic, now via module-level helpers.
- Add three new unit tests (one per fetcher) using `respx` mocks, matching existing test patterns.
- File stays within the 300-line limit.

**Estimate:** ~45 min.

---

### S19.8 — `web/lib/api.ts` — Split types from HTTP client + fix template duplication

**Problem A — file size already breached:** As of Sprint 17 Stream 2, `api.ts` stands at **309 lines** — already past the 300-line guardrail. The file now does two unrelated jobs:
1. Defines all TypeScript interfaces (`SummariseRequest`, `HistoryRecord`, `RosterResponse`, `PromptTemplate`, `RecommendationsResponse`, etc.)
2. Implements all HTTP client functions (`generateSummary`, `fetchHistory`, `createPromptTemplate`, etc.)

Any agent loading the file for a single HTTP function must parse all type definitions too.

**Problem B — duplicate API helpers in `templates/page.tsx`:** Sprint 17 Stream 2 shipped `web/app/templates/page.tsx` with three locally-defined API helper functions:

```typescript
// In web/app/templates/page.tsx (lines 34–55) — LOCAL duplicates
async function listTemplates(username: string): Promise<PromptTemplate[]> {...}
async function createTemplate(payload: CreateTemplatePayload): Promise<PromptTemplate> {...}
async function deleteTemplate(id: string): Promise<void> {...}
```

Identical logic already lives in `web/lib/api.ts` as the canonical versions:
```typescript
export async function listPromptTemplates(username: string): Promise<PromptTemplate[]> {...}
export async function createPromptTemplate(req: PromptTemplateCreate): Promise<PromptTemplate> {...}
export async function deletePromptTemplate(id: string): Promise<void> {...}
```

**Fix:**
1. Create `web/lib/types.ts` — all `interface` and `type` exports, no functions.
2. `web/lib/api.ts` — HTTP functions only; imports types from `./types`.
3. Refactor `web/app/templates/page.tsx` to delete the three local helpers and import `listPromptTemplates`, `createPromptTemplate`, `deletePromptTemplate` from `@/lib/api` instead.
4. Update all component imports: `from "@/lib/api"` stays valid for functions; type-only imports switch to `from "@/lib/types"`.

**Estimate:** ~45 min. No component logic changes; pure import cleanup.

---

## Order of Work

```text
S19.6 (standards doc)
  → S19.5 (dedup /health/keys)
  → S19.7 (repo_reader.py cleanup)  ← independent, do while warming up
  → S19.8 (api.ts split)            ← independent, do while warming up
  → S19.1 (router scaffold)
  → S19.3 (dependencies.py)
  → S19.2 (migrate routes, domain-by-domain, pytest after each)
  → S19.4 (test split)
```

S19.6 first so the guardrail is documented before the refactor begins.
S19.7 and S19.8 are independent and low-risk — good warm-up tasks before the
larger API migration.

---

## Definition of Done

- [ ] `api/api.py` is ≤ 80 lines (app init + router registration only)
- [ ] Each router file is ≤ 300 lines
- [ ] No routes are duplicated (`/health/keys` deduped)
- [ ] `uv run pytest -v` passes (82+ tests, same coverage)
- [ ] `api/dependencies.py` contains `_get_user_repos` and DB pool guard
- [ ] `repo_reader.py` nested fetchers extracted to module-level + 3 new unit tests
- [ ] `web/lib/types.ts` exists; `web/lib/api.ts` contains only HTTP functions
- [ ] `AGENTS.md` and `GEMINI.md` updated with the 300-line rule
- [ ] `npm run lint` passes in `web/`
- [ ] PR squash-merged to master

---

## Out of Scope

- Changing any route behaviour or response schema (pure structural refactor)
- Adding new routes
- `web/app/insights/page.tsx` chart extraction — ✅ already completed in Sprint 17 Stream 2 (`MetricCard` and `ComparisonChart` extracted to `web/components/insights/`)
- `web/components/SummaryForm.tsx` — 302 lines but a single-responsibility form; leave as-is
- `gitpulse_mcp/server.py` — 299 lines, within limit, no split needed yet
