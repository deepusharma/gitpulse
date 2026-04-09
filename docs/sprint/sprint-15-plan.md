# Sprint 15 Execution Plan — Team & Reach

**Sprint Goal:** Enable multi-username team standups, Slack team delivery, team roster save/load, README badge generation, and presentation mode.
**Milestone:** v1.0 — Team & Reach
**Branch:** `feature/sprint-15-team`
**Status:** Approved — Ready to Execute

---

## Design Decisions (Pre-approved)

| Decision | Choice | Rationale |
|---|---|---|
| Slack Webhook URL storage | Client sends per request (stateless) | Security — secrets don't persist in DB |
| Team Roster persistence | Neon DB `rosters` table | Cross-device roster sharing; clean separation |
| Presentation mode | Standalone `/present` route (no Header/Footer) | True full-screen; route-level layout isolation in Next.js |
| Smart Reminders (S15.6) | Deferred to Sprint 16 | Scope risk — service workers + push scheduling is its own sprint |

---

## Architecture

### New DB Table

```sql
CREATE TABLE IF NOT EXISTS rosters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    usernames TEXT[] NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

No user authentication binding — rosters are global (like current summaries). Scoped auth can come in v1.1.

### New API Endpoints

```
POST   /team/roster               — Create/update a named team roster
GET    /team/rosters              — List all saved rosters
GET    /team/roster/{id}          — Get a specific roster by ID
DELETE /team/roster/{id}          — Delete a roster

POST   /team/summarise            — Generate aggregated standup for multiple usernames
POST   /deliver/slack             — POST standup summary to a Slack webhook URL

GET    /badges/streak?username=X  — Return SVG streak badge
GET    /badges/commits?username=X&days=N  — Return SVG commit count badge
GET    /badges/health?username=X  — Return SVG health score badge
```

### Frontend New Routes

```
/present?username=X&repos=Y&days=N   — Full-screen presentation mode (no layout shell)
```

`/present` gets its own `web/app/present/layout.tsx` that renders only `{children}` — no Header/Footer/Providers wrapping.

---

## Order of Execution

```
Pre-work: Fix Vercel deployment branch (gh-pages → master) [#227]

Stream 1 (Backend):
  DB Migration (rosters table)
    → Roster CRUD endpoints (/team/roster)
    → Multi-user /team/summarise aggregator
    → Slack delivery endpoint (/deliver/slack)
    → Badges endpoints (/badges/streak, /badges/commits, /badges/health)
    → Tests for all new endpoints

Stream 2 (Frontend):
  Team standup UI (multi-username input + roster save/load panel)
    → /present page (standalone layout, carousel, large typography)
    → Navigation updates (add Insights + Present links to Header)
```

---

## Step-by-Step Technical Plan

### Stream 1 — Backend

#### Step 1.1: DB Migration — `rosters` table
- File: `api/db.py`
- Add `init_rosters_table()` async function that runs `CREATE TABLE IF NOT EXISTS rosters(...)` on startup.
- Call from `api/api.py` startup event alongside existing DB init.

#### Step 1.2: Roster CRUD endpoints
- File: `api/api.py`
- `POST /team/roster` — body: `{name: str, usernames: list[str]}` → upserts to DB, returns roster with ID.
- `GET /team/rosters` — returns list of all rosters `[{id, name, usernames, created_at}]`.
- `GET /team/roster/{id}` — returns single roster or 404.
- `DELETE /team/roster/{id}` — deletes, returns 200.
- Pydantic models: `RosterRequest`, `RosterResponse`.

#### Step 1.3: Multi-user standup aggregator
- File: `api/api.py`
- `POST /team/summarise` — body: `{usernames: list[str], repos: list[str], days: int}`.
- Calls `get_activity(source="github", username=u, repos=repos, days=days)` concurrently via `asyncio.gather` for each username.
- Merges all activity dicts, builds a composite prompt using `format_activity` and `build_prompt`.
- Returns same `SummariseResponse` shape + adds `contributors: list[str]` field.
- Cache key: `(sorted usernames, sorted repos, days)`.

#### Step 1.4: Slack delivery endpoint
- File: `api/api.py`
- `POST /deliver/slack` — body: `{summary: str, webhook_url: str, channel: str | None}`.
- Sends an `httpx.AsyncClient.post` to the webhook URL with a Slack Block Kit payload:
  ```json
  {"blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": "<summary>"}}]}
  ```
- Returns `{ok: true}` on success or raises HTTPException on Slack error.
- Validates `webhook_url` starts with `https://hooks.slack.com/` for security.

#### Step 1.5: Badges API
- File: `api/api.py`
- `GET /badges/streak?username=X` — calls `/analytics/insights` internally, extracts `streak`, proxies to `https://img.shields.io/badge/streak-{N}-brightgreen` with a redirect (`RedirectResponse`).
- `GET /badges/commits?username=X&days=N` — proxies to shields.io for commit count badge.
- `GET /badges/health?username=X` — proxies to shields.io for health score badge.
- All three return `RedirectResponse(url=shields_url, status_code=302)` — no SVG generation needed, shields.io handles rendering.

#### Step 1.6: Tests
- File: `api/tests/test_api.py`
- `test_create_roster` — mocks DB, verifies roster creation.
- `test_list_rosters` — verifies GET /team/rosters.
- `test_team_summarise` — mocks `get_activity` for 2 usernames, verifies aggregation.
- `test_deliver_slack` — mocks `httpx.AsyncClient.post`, verifies payload shape.
- `test_badges_streak_redirect` — verifies 302 redirect to shields.io.

---

### Stream 2 — Frontend

#### Step 2.1: Team Standup UI (update main summary page or create `/team` page)
- File: `web/app/team/page.tsx` (**new page**)
- Multi-username input: comma-separated field (or add/remove chips UI).
- "Load Roster" dropdown: fetches `GET /team/rosters`, lets user pick a saved roster to populate usernames.
- "Save Roster" button: modal prompting for a roster name → calls `POST /team/roster`.
- Days input + Generate button → calls `POST /team/summarise`.
- Results section: renders per-contributor activity cards + AI summary beneath.
- "Send to Slack" button: text input for webhook URL → calls `POST /deliver/slack` with the rendered summary.

#### Step 2.2: `/present` page — Standalone presentation mode
- File: `web/app/present/layout.tsx` (**new layout**)
  - Renders only `{children}` — no `<Header>`, `<Footer>`, or `<Providers>` wrapper.
  - `className="min-h-screen bg-black text-white"` for clean full-screen.
- File: `web/app/present/page.tsx` (**new page**)
  - Reads `username`, `repos`, `days` from search params.
  - Fetches `POST /team/summarise` (or `POST /summarise` for single user).
  - Renders the summary in a large-typography carousel using Shadcn `Tabs` or a simple slide counter.
  - Each section (`WHAT I DID`, `DETAILS`, `WHATS NEXT`, `BLOCKERS`) gets its own "slide" with `text-5xl` font.
  - Navigation: left/right arrow keys or on-screen buttons to advance slides.
  - "Exit" button in corner → `router.back()`.

#### Step 2.3: Navigation updates
- File: `web/components/Header.tsx`
- Add "Team" nav link → `/team`.
- Add "Present" icon button (🖥) to summary results area that deep-links to `/present?username=...`.

---

## File Change Summary

| File | Change | Stream |
|---|---|---|
| `api/db.py` | Add `init_rosters_table()` | 1 |
| `api/api.py` | Add 8 new endpoints (roster CRUD, /team/summarise, /deliver/slack, /badges/*) | 1 |
| `api/tests/test_api.py` | Add 5 new test cases | 1 |
| `web/app/team/page.tsx` | New team standup page | 2 |
| `web/app/present/layout.tsx` | Stripped layout (no Header/Footer) | 2 |
| `web/app/present/page.tsx` | Carousel presentation view | 2 |
| `web/components/Header.tsx` | Add Team nav link + Present button | 2 |

---

## Definition of Done

- [ ] `POST /team/roster` creates and persists a named roster to Neon DB
- [ ] `GET /team/rosters` returns all saved rosters
- [ ] `POST /team/summarise` aggregates activity across multiple usernames concurrently
- [ ] `POST /deliver/slack` correctly delivers formatted standup to Slack webhook
- [ ] `GET /badges/streak` returns a 302 redirect to shields.io badge
- [ ] `/team` page supports multi-username input, roster save/load, Slack delivery
- [ ] `/present` renders full-screen carousel with no Header/Footer, large typography
- [ ] All new tests pass
- [ ] PR squash-merged to master

---

## Out of Scope (Deferred)

- **S15.6 Smart Reminders** — deferred to Sprint 16 (requires service worker + push subscription infra)
- Per-user authenticated roster isolation — deferred to v1.1 when private repo OAuth lands
