# Sprint 16 Execution Plan — Pro Features

**Sprint Goal:** Add support for private org repos via expanded OAuth scope, public shareable summary links, and comparison modes.
**Milestone:** v1.1 — Pro Features
**Branch:** `feature/sprint-16-pro`
**Status:** Approved — Ready to Execute

---

## Design Decisions (Pre-approved)

| Decision | Choice | Rationale |
|---|---|---|
| OAuth scope upgrade | Conditional `repo` scope via a toggle on the sign-in page | Always requesting `repo` scope would break users who only need public repos; opt-in keeps it safe |
| Token storage | NextAuth JWT callback stores GitHub access token in the session | Token never hits our backend at rest; only passes it in-flight per request |
| Token forwarding | Frontend passes token as `X-GitHub-Token` header to FastAPI on private-repo requests | Keeps FastAPI stateless — no session server needed |
| Public link storage | Add `is_public BOOLEAN` column to existing `summaries` table (migration in `db.py`) | Minimal DB change; re-uses existing UUID `id` as permalink |
| Unauthenticated public route | `GET /summary/public/{id}` — no auth required | Separate route keeps auth middleware clean |
| Comparison mode (S16.3) | Period comparison (current N days vs previous N days) computed server-side | Avoids complex client math; consistent with existing analytics patterns |

---

## Architecture

### OAuth Scope Upgrade

Current `route.ts` does not request any scopes explicitly — GitHub OAuth defaults to `read:user` + `user:email`. To access private repos we need the full `repo` scope.

The plan is to make the scope **conditional via a session param**:
- Default sign-in: `scope: "read:user user:email"` (unchanged, public repos only)
- Opt-in sign-in: `scope: "read:user user:email repo"` (private repos unlocked)
- A new `signIn({ callbackUrl, scope: "private" })` call is triggered from a UI toggle on the home page

NextAuth does not natively support per-call scope overrides on GitHub OAuth v4. We handle this by  registering a **second GitHub provider** with `id: "github-private"` and `scope: "read:user user:email repo"`. The user explicitly picks this via a UI prompt.

The access token must flow from NextAuth into the frontend session, then be forwarded to FastAPI via a request header. To do this:
- `jwt` callback: persist `account.access_token` into the token
- `session` callback: expose it as `session.accessToken`

FastAPI's `get_activity` already passes a `GITHUB_TOKEN` env var for server-level rate limiting. Private-repo requests forward the user's personal token as an override so our server token doesn't get contaminated.

### DB Schema Change — `is_public` flag

```sql
ALTER TABLE summaries ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE;
```

The `summaries` table already has:
```
id UUID, username TEXT, repos TEXT[], days INT, display TEXT, summary TEXT, generated_at TIMESTAMPTZ
```

No other table changes are needed.

### New API Endpoints

```python
PATCH /history/{summary_id}/public
    # Toggle is_public flag. Body: {"public": true|false}
    # Returns: {"id": str, "is_public": bool}

GET /summary/public/{summary_id}
    # Returns a summary record if is_public=true, 404 otherwise (no auth required)
    # Returns: {"id", "username", "repos", "days", "summary", "generated_at"}

GET /analytics/compare
    # Compare current period vs previous period for a user
    # Query params: username, days
    # Returns: {"current": {...}, "previous": {...}, "delta": {...}}
```

### Frontend New Routes / Components

```
/summary/[id]   — public summary view (no auth required, renders summary card)
```

New UI components alongside existing pages:
- **Permission toggle** on home page — "Include private repos" checkbox → triggers re-auth with `github-private` provider
- **Share button** on Results component → calls `PATCH /history/{id}/public`, copies permalink to clipboard
- **Comparison section** in `/insights` page → calls `GET /analytics/compare`

---

## Order of Execution

```
Stream 1 (Backend):
  DB Migration (is_public column)
    → PATCH /history/{id}/public endpoint
    → GET /summary/public/{id} endpoint
    → GET /analytics/compare endpoint
    → Extend POST /summarise to accept X-GitHub-Token header
    → Tests for all new endpoints

Stream 2 (Frontend):
  NextAuth: add github-private provider + expose accessToken in session
    → Home page: permission toggle UI
    → Results component: Share button
    → New /summary/[id] public page (no auth wrapper)
    → Insights page: comparison chart section
```

---

## Step-by-Step Technical Plan

### Stream 1 — Backend

#### Step 1.1: DB Migration — `is_public` column
- File: `api/db.py`
- Add `init_summaries_public_migration()` async function that runs `ALTER TABLE summaries ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE`.
- Call from `init_db()` after the existing pool init, after the existing `init_rosters_table()` call.
- Use `IF NOT EXISTS` inside `ADD COLUMN` to make it idempotent (Postgres 9.6+ supports this).

#### Step 1.2: `PATCH /history/{summary_id}/public` — Toggle public flag
- File: `api/api.py`
- New Pydantic model: `PublicToggleRequest(public: bool)`
- New Pydantic model: `PublicToggleResponse(id: str, is_public: bool)`
- `PATCH /history/{summary_id}/public` — receives `{public: true|false}`, runs `UPDATE summaries SET is_public=$1 WHERE id=$2`, returns `PublicToggleResponse`.
- Returns 404 if the id doesn't exist, 503 if DB is disabled.

#### Step 1.3: `GET /summary/public/{summary_id}` — Unauthenticated public view
- File: `api/api.py`
- No auth dependency required (fully open).
- Queries `SELECT * FROM summaries WHERE id=$1 AND is_public=TRUE`.
- Returns `{id, username, repos, days, summary, generated_at}` or 404.
- New response model: `PublicSummaryResponse`.

#### Step 1.4: Extend `POST /summarise` with user token forwarding
- File: `api/api.py`
- Add optional `Request` dependency to the route to read the `X-GitHub-Token` header.
- If present, pass the token value into `get_activity(... token=user_token)`.
- Update `gitpulse/core/repo_reader.py` → `_get_github_activity()` to accept an optional `token` parameter that overrides the env-var token when fetching from the GitHub API.
- This unlocks private repo access without touching the server-level `GITHUB_TOKEN`.

#### Step 1.5: `GET /analytics/compare` — Period comparison
- File: `api/api.py`
- Query params: `username: str`, `days: int = 30`.
- Fetches activity for `days` window (current period) AND for the `days` window immediately before that (previous period), via two `get_activity` calls.
- Computes per-period totals: `commits`, `prs`, `issues`, `active_days`.
- Computes `delta`: `{commits: +N%, prs: +N%, ...}` as percentage differences.
- Returns: `{"current": {...}, "previous": {...}, "delta": {...}, "days": N}`.
- Add to `analytics_cache` with 5-minute TTL.

#### Step 1.6: Tests
- File: `api/tests/test_api.py`
- `test_patch_summary_public` — mock DB, verify toggle sets `is_public=True`.
- `test_get_public_summary` — verify response when `is_public=True`; verify 404 when `is_public=False`.
- `test_get_public_summary_not_found` — verify 404 for nonexistent ID.
- `test_analytics_compare` — mock `get_activity`, verify delta calculation math.
- `test_summarise_with_user_token` — verify `X-GitHub-Token` header is picked up and forwarded.

---

### Stream 2 — Frontend

#### Step 2.1: NextAuth — `github-private` provider + expose `accessToken`
- File: `web/app/api/auth/[...nextauth]/route.ts`
- Add a second provider: `GithubProvider({ id: "github-private", clientId, clientSecret, authorization: { params: { scope: "read:user user:email repo" } } })`.
- Update `jwt` callback: `if (account?.access_token) token.accessToken = account.access_token;`
- Update `session` callback: `session.accessToken = token.accessToken as string;`
- File: `web/types/next-auth.d.ts` (**new** or update existing) — extend `Session` interface to include `accessToken: string`.

#### Step 2.2: Home page — Permission toggle UI
- File: `web/components/SummaryForm.tsx` (or a new `PrivateRepoToggle.tsx` component)
- Add a checkbox/toggle: "Include private repos (requires additional permissions)".
- When toggled ON and the user is not yet signed in with `github-private` scope: call `signIn("github-private")`.
- When toggled ON and already signed in with `github-private`: set a request flag `usePrivateToken=true`.
- When `usePrivateToken=true`, the form passes `X-GitHub-Token: session.accessToken` as a header in the `POST /summarise` fetch call.
- Visual indicator: badge on the form "🔒 Private Repos" when active.

#### Step 2.3: Results component — Share button
- File: `web/components/Results.tsx`
- Add a "Share" button (icon: `Share2` from lucide-react) next to the Copy button.
- On click: calls `PATCH {API_URL}/history/{summaryId}/public` with `{public: true}`.
- On success: constructs permalink `{window.location.origin}/summary/{summaryId}` and copies to clipboard.
- Show a toast: "Public link copied to clipboard!" (use existing shadcn toast pattern).
- The `summaryId` needs to come from the API response — ensure `POST /summarise` response includes `id` field (add to `SummariseResponse` model in both Python and TypeScript).

> [!IMPORTANT]
> `POST /summarise` must be updated to return the DB-inserted `id` field. This requires returning the `RETURNING id` value from the INSERT in `api.py` and exposing it in `SummariseResponse`.

#### Step 2.4: `/summary/[id]` — Public view page (no auth required)
- File: `web/app/summary/[id]/page.tsx` (**new**)
- Server component (no `"use client"`) — fetches `GET {API_URL}/summary/public/{id}` at render time.
- If 404 → renders a "Summary not found or is private" card.
- If found → renders the summary in a clean read-only layout (no Header form, just the summary card + GitPulse branding footer).
- No NextAuth session check — fully public.
- SEO: sets `<title>` and `<meta description>` from the summary content dynamically.

#### Step 2.5: Insights page — Comparison section
- File: `web/app/insights/page.tsx`
- Add a new section below the existing charts: "Period Comparison".
- Fetches `GET /analytics/compare?username=X&days=N` (uses same `days` value already on the page).
- Renders a side-by-side stat card table showing current vs previous period with colored delta arrows:
  - Green ▲ for positive change, Red ▼ for negative.
  - Metrics: Commits, PRs merged, Issues closed, Active days.
- Loading skeleton during fetch.

---

## File Change Summary

| File | Change | Stream |
|---|---|---|
| `api/db.py` | Add `init_summaries_public_migration()` | 1 |
| `api/api.py` | `PATCH /history/{id}/public`, `GET /summary/public/{id}`, `GET /analytics/compare`, extend `/summarise` with token header + return `id` | 1 |
| `gitpulse/core/repo_reader.py` | Optional `token` param override in `_get_github_activity()` | 1 |
| `api/tests/test_api.py` | 5 new test cases | 1 |
| `web/app/api/auth/[...nextauth]/route.ts` | Add `github-private` provider, expose `accessToken` | 2 |
| `web/types/next-auth.d.ts` | Extend `Session` type with `accessToken` | 2 |
| `web/components/SummaryForm.tsx` | Private repo toggle + token forwarding | 2 |
| `web/components/Results.tsx` | Share button + public link copy | 2 |
| `web/app/summary/[id]/page.tsx` | **NEW** — public summary view | 2 |
| `web/app/insights/page.tsx` | Add comparison section | 2 |

---

## Open Questions / Pre-work for Execution

> [!IMPORTANT]
> **S16.3 Comparison scope:** The brief mentions "comparison modes" broadly. This plan scopes it to a backend `GET /analytics/compare` endpoint + a read-only UI section in `/insights`. This is achievable within a single sprint. A full side-by-side interactive comparison across arbitrary date ranges is deferred to v1.2.

> [!WARNING]
> **`POST /summarise` must return `id`:** The Share feature depends on the summary DB id being returned in the `/summarise` response. This is a breaking shape change — the TypeScript `SummariseResponse` type must be updated. No existing consumer reads an `id` field today, so it is backward-compatible (additive), but tests must be updated to assert its presence.

> [!NOTE]
> **Private repo OAuth on Railway:** The `github-private` provider will require the same `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`. No new GitHub OAuth App is needed — just the `repo` scope addition. The Vercel env vars do not change.

---

## Definition of Done

- [ ] `ALTER TABLE summaries ADD COLUMN is_public` runs idempotently on startup
- [ ] `PATCH /history/{id}/public` toggles flag and returns updated state
- [ ] `GET /summary/public/{id}` returns summary without auth if `is_public=TRUE`; 404 otherwise
- [ ] `GET /analytics/compare` returns current vs previous period deltas correctly
- [ ] `POST /summarise` accepts `X-GitHub-Token` header and returns `id` in response
- [ ] `gitpulse/core/repo_reader.py` passes user token through to GitHub API when provided
- [ ] NextAuth session exposes `accessToken` when `github-private` provider used
- [ ] Home page toggles private repo mode; requests include user token when active
- [ ] Results component Share button creates shareable link and copies to clipboard
- [ ] `/summary/[id]` renders public summary without requiring sign-in
- [ ] Insights page shows period comparison section with delta indicators
- [ ] All new tests pass (`uv run pytest -v`)
- [ ] `npm run lint` passes in web/
- [ ] PR squash-merged to master

---

## Out of Scope (Deferred)

- Per-user authenticated roster isolation (v1.1+ when private repos land and user binding makes sense)
- Interactive date-range comparison picker (deferred to v1.2)
- S15.6 Smart Reminders (still deferred from Sprint 15)
