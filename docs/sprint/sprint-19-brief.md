# Sprint 19 — API Refactor & Code Health

**Sprint goal:** Break `api/api.py` from a 1,500-line monolith into focused routers, establish file-size guardrails in the coding standards, and eliminate the duplicate `/health/keys` route.
**Milestone:** v1.4 — Code Health
**Duration:** Day 13 (~3 hours)
**Status:** Not Started

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

## Order of Work

```text
S19.6 (standards doc) → S19.5 (dedup) → S19.1 (scaffold) →
S19.3 (dependencies) → S19.2 (migrate, domain-by-domain) → S19.4 (test split)
```

Standards first so the guardrail is documented before the refactor begins.

---

## Definition of Done

- [ ] `api/api.py` is ≤ 80 lines (app init + router registration only)
- [ ] Each router file is ≤ 300 lines
- [ ] No routes are duplicated
- [ ] `uv run pytest -v` passes (82+ tests, same coverage)
- [ ] `api/dependencies.py` contains `_get_user_repos` and DB pool guard
- [ ] `AGENTS.md` and `GEMINI.md` updated with the 300-line rule
- [ ] PR squash-merged to master

---

## Out of Scope

- Changing any route behaviour or response schema (pure structural refactor)
- Adding new routes
- Migrating `gitpulse/core/` files (they are within limits today — revisit if needed)
