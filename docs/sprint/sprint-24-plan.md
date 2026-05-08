# Sprint 24 Plan: v1.6 — Observability & Growth

**Version:** v1.6.0  
**Sprint:** 24  
**Status:** Awaiting Approval

---

## Overview

Four epics, executed in dependency order:

| Phase | Epic | Risk | Est. Complexity |
|-------|------|------|-----------------|
| 1 | Epic C — API Observability | Low | Medium |
| 2 | Epic D — CLI Polish | Low | Low |
| 3 | Epic B — Public Profile Pages | Medium | Medium |
| 4 | Epic A — Scheduled Digests | High | High |

**Rationale for ordering:** Observability first (pure additive middleware, zero risk to existing routes). CLI second (self-contained). Public profiles third (read-only, no new DB writes). Scheduled digests last (new DB tables + async worker = highest blast radius).

---

## Phase 1 — Epic C: API Observability

### 1.1 Goals
- Structured request/response logging on every route
- Sentry error capture (optional, env-gated)
- `GET /admin/stats` internal summary endpoint

### 1.2 New Dependencies
Add to `pyproject.toml`:
```toml
sentry-sdk = { version = ">=2.0", extras = ["fastapi"], optional = true }
structlog = ">=24.0"
```
Both are optional — Sentry is a no-op when `SENTRY_DSN` is unset.

### 1.3 New Files

#### `api/middleware.py`
Purpose: FastAPI middleware for structured request logging.

Logs: method, path, status_code, latency_ms, username (from X-Username header).
Uses structlog bound logger. Must not raise — catches all exceptions internally.

#### `api/observability.py`
Purpose: Sentry initialization helper + structlog configuration.

```python
def configure_observability() -> None:
    """Initialize structlog and conditionally Sentry.
    
    structlog: JSON renderer in prod, console renderer in dev (LOG_FORMAT env).
    Sentry: only if SENTRY_DSN is set. No PII capture.
    """
```

#### `api/routers/admin.py`
New router — prefix `/admin`, tag `admin`.

**Endpoint: `GET /admin/stats`**

Auth: Header `X-Admin-Token` must match `ADMIN_TOKEN` env var (returns 403 otherwise).

Request: Query params `?days=30`

Response schema:
```json
{
  "total_summaries": 1024,
  "unique_users": 87,
  "summaries_last_n_days": 42,
  "top_repos": [{"repo": "gitpulse", "count": 15}],
  "error_rate_pct": 0.5,
  "generated_at": "2026-05-08T07:00:00Z"
}
```

Pydantic model to add to `api/models.py`:
```python
class AdminStatsResponse(BaseModel):
    total_summaries: int
    unique_users: int
    summaries_last_n_days: int
    top_repos: list[dict]
    error_rate_pct: float
    generated_at: str
```

DB queries (read-only against `summaries` table):
- `SELECT COUNT(*) FROM summaries;`
- `SELECT COUNT(DISTINCT username) FROM summaries;`
- `SELECT COUNT(*) FROM summaries WHERE generated_at >= NOW() - INTERVAL '$1 days';`
- Top repos via `UNNEST(repos)` grouped by count, LIMIT 10.

### 1.4 Changes to Existing Files

**`api/api.py`**
- Import and call `configure_observability()` before app creation
- Add `RequestLoggingMiddleware` via `app.add_middleware(...)`
- Import and register `admin.router`
- Bump version string to `1.6.0`

**`api/db.py`**
- Add `init_request_log_table()` — creates `request_logs` table (only when `ENABLE_DB_LOG=true`)

`request_logs` table schema:
```sql
CREATE TABLE IF NOT EXISTS request_logs (
    id          BIGSERIAL PRIMARY KEY,
    path        TEXT NOT NULL,
    method      TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    latency_ms  INTEGER NOT NULL,
    username    TEXT,
    logged_at   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_request_logs_logged_at ON request_logs(logged_at);
```

> Note: `ENABLE_DB_LOG` defaults to `false`. Stdout structured logs are always on. DB log table is opt-in to avoid write amplification.

### 1.5 Environment Variables Added

| Var | Required | Default | Purpose |
|-----|----------|---------|---------|
| `SENTRY_DSN` | No | unset | Enables Sentry if set |
| `ADMIN_TOKEN` | No | unset | Auth for `/admin/stats` |
| `LOG_FORMAT` | No | `json` | `json` or `console` |
| `ENABLE_DB_LOG` | No | `false` | Write request logs to DB |

### 1.6 Tests Required

File: `api/tests/test_middleware.py`
- `test_request_log_emitted` — assert structlog output contains path/status/latency
- `test_admin_stats_no_token_returns_403`
- `test_admin_stats_valid_token_returns_200`
- `test_sentry_not_initialized_when_dsn_unset`

---

## Phase 2 — Epic D: CLI Polish

### 2.1 Goals
- Shell completion via Typer built-in
- `--format json` flag on `gitpulse generate`
- New `gitpulse status` command

### 2.2 Changes to `gitpulse/cli/cli.py`

**Shell Completion**

Typer exposes `--install-completion` automatically when `app = typer.Typer(...)`. No code change needed beyond verification. Document in README.

**`--format` flag on `generate`**

Add param:
```python
format: str = typer.Option("pretty", "--format", "-f",
    help="Output format: 'pretty' (default) or 'json'")
```

When `format == "json"`, skip Rich panels and print a JSON object to stdout:
```json
{
  "username": "deepusharma",
  "repos": ["gitpulse"],
  "days": 7,
  "summary": "...",
  "generated_at": "2026-05-08T07:00:00Z"
}
```
Use `import json; print(json.dumps({...}))` — no Rich output. Enables: `gitpulse generate --format json | jq .summary`.

**New `gitpulse status` command**

```python
@app.command(name="status")
def status():
    """Show current config, API connectivity, and key health."""
```

Outputs a Rich table with:

| Check | Status |
|-------|--------|
| Config file `~/.gitpulse.toml` | Found / Missing |
| `GROQ_API_KEY` | Set / Missing |
| `GITHUB_TOKEN` | Set / Not set (rate limits apply) |
| API reachability (`NEXT_PUBLIC_API_URL/health`) | OK (200) / Unreachable |
| Config: repos | Lists repo names from config |
| Config: defaults | days, tone, language |

API check is a best-effort `httpx.get` with 3s timeout — prints warning if `NEXT_PUBLIC_API_URL` not set, skips gracefully.

### 2.3 Tests Required

File: `gitpulse/cli/tests/test_cli_status.py`
- `test_status_missing_config` — config absent → shows Missing
- `test_status_all_ok` — mocked config + env vars → all green
- `test_generate_format_json` — `--format json` → stdout is valid JSON, no Rich output
- `test_generate_format_pretty_default` — default still prints Rich panel

---

## Phase 3 — Epic B: Public Profile Pages

### 3.1 Goals
- `GET /profile/{username}` API endpoint (public, no auth)
- Next.js `app/u/[username]/page.tsx` — public profile page
- Dynamic OG meta tags
- "Share my profile" button in existing web UI

### 3.2 New API Endpoint

File: `api/routers/profile.py` (new)

**`GET /profile/{username}`**

No auth required. Aggregates public data only.

Request: path param `username`, query `?days=30`

Response (new `PublicProfileResponse` model in `api/models.py`):
```python
class PublicProfileResponse(BaseModel):
    username: str
    avatar_url: str
    bio: Optional[str]
    recent_summary: Optional[str]   # latest public summary text only
    current_streak: int
    longest_streak: int
    top_repos: list[str]            # max 5, public repos only
    health_score: int               # 0-100
    total_summaries: int
    generated_at: str
```

Implementation steps:
1. Fetch GitHub user profile (`avatar_url`, `bio`) via `GET https://api.github.com/users/{username}`
2. Fetch public repos via existing `get_user_repos(username)` (already public-only)
3. Fetch activity via `get_activity(source="github", ...)` — derive top 5 repos by commit count
4. Fetch latest **public** summary from DB: `SELECT summary FROM summaries WHERE username=$1 AND is_public=TRUE ORDER BY generated_at DESC LIMIT 1`
5. Calculate streak via `calculate_streak()` (imported from `api.utils` after refactor — see 3.3)
6. Fetch health score via `get_insights_health()`

**Private repo protection:** `get_user_repos()` already fetches only `type=public` repos. DB query filters `is_public=TRUE`.

**Cache:** 5-minute TTL using existing `analytics_cache`.

### 3.3 Refactor: Move `calculate_streak` to `api/utils.py`

Currently in `api/routers/analytics.py`. Move to a new `api/utils.py` to be importable from `profile.py` without circular import. Update `analytics.py` to import from `api.utils`.

### 3.4 Frontend: `app/u/[username]/page.tsx`

Route `/u/[username]` — public, server component, no `useSession`.

**OG meta tags via `generateMetadata`:**
```tsx
export async function generateMetadata({ params }) {
  const profile = await fetchProfile(params.username);
  return {
    title: `${params.username} on GitPulse`,
    description: `${params.username}'s dev activity — ${profile.current_streak} day streak.`,
    openGraph: {
      title: `${params.username} on GitPulse`,
      description: `Current streak: ${profile.current_streak} days | Health: ${profile.health_score}/100`,
      images: [profile.avatar_url],
      url: `https://gitpulse.dev/u/${params.username}`,
    },
    twitter: { card: "summary" },
  };
}
```

**Page sections:**
1. Header card — avatar, username, bio, streak badge
2. Stats grid — streak, longest streak, health score, total summaries (4-column)
3. Top repos list — up to 5 repo chips
4. Recent summary card — latest public standup text (Markdown rendered)
5. Footer CTA — "Generate your own standup at gitpulse.dev"

**New components** (`web/components/profile/`):
- `ProfileHeader.tsx`
- `ProfileStats.tsx`
- `TopReposList.tsx`
- `RecentSummaryCard.tsx`

**"Share my profile" button**

New `web/components/ShareProfileButton.tsx`:
- One-click copies `https://gitpulse.dev/u/{username}` to clipboard via `navigator.clipboard.writeText()`
- Placed in dashboard header (`web/app/page.tsx` or top nav)
- Uses `useSession().data?.user?.name` to construct URL

### 3.5 Tests Required

File: `api/tests/test_profile.py`
- `test_profile_returns_200_for_valid_user` — mock GitHub API + DB
- `test_profile_hides_private_summaries` — `is_public=FALSE` rows excluded
- `test_profile_404_for_unknown_user` — GitHub 404 → API 404
- `test_profile_cached` — second call hits cache, no duplicate GitHub fetch

File: `web/tests/profile.test.tsx`
- `test_profile_page_renders_username`
- `test_profile_page_shows_streak`
- `test_share_button_copies_url`

---

## Phase 4 — Epic A: Scheduled Digests

### 4.1 Goals
- Users configure a daily/weekly digest schedule (channel: email or Slack)
- Async worker reads the schedule and fires deliveries automatically
- Web UI "Schedule" settings panel

### 4.2 DB Schema Addition

New table via `api/db.py` → `init_schedules_table()`:

```sql
CREATE TABLE IF NOT EXISTS digest_schedules (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username      TEXT NOT NULL UNIQUE,
    enabled       BOOLEAN NOT NULL DEFAULT TRUE,
    frequency     TEXT NOT NULL CHECK (frequency IN ('daily', 'weekly')),
    hour_utc      INTEGER NOT NULL CHECK (hour_utc BETWEEN 0 AND 23),
    day_of_week   INTEGER CHECK (day_of_week BETWEEN 0 AND 6),  -- NULL for daily
    channel       TEXT NOT NULL CHECK (channel IN ('email', 'slack')),
    email_to      TEXT,
    slack_webhook TEXT,
    repos         TEXT[] NOT NULL,
    days          INTEGER NOT NULL DEFAULT 7,
    tone          TEXT NOT NULL DEFAULT 'professional',
    language      TEXT NOT NULL DEFAULT 'English',
    last_sent_at  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_digest_schedules_username ON digest_schedules(username);
```

App-layer constraints:
- `email_to` required when `channel = 'email'`
- `slack_webhook` required when `channel = 'slack'`
- `day_of_week` required when `frequency = 'weekly'`

### 4.3 New API Router: `api/routers/schedule.py`

Prefix: `/schedule`, tag: `schedule`

**`POST /schedule`** — Upsert schedule by username

Request (`DigestScheduleRequest` in `api/models.py`):
```python
class DigestScheduleRequest(BaseModel):
    username: str
    enabled: bool = True
    frequency: Literal["daily", "weekly"]
    hour_utc: int           # 0-23
    day_of_week: Optional[int] = None   # 0=Mon, 6=Sun; required if weekly
    channel: Literal["email", "slack"]
    email_to: Optional[str] = None
    slack_webhook: Optional[str] = None
    repos: list[str]
    days: int = 7
    tone: str = "professional"
    language: str = "English"
```

Response (`DigestScheduleResponse`):
```python
class DigestScheduleResponse(BaseModel):
    id: str
    username: str
    enabled: bool
    frequency: str
    hour_utc: int
    day_of_week: Optional[int]
    channel: str
    repos: list[str]
    days: int
    last_sent_at: Optional[str]
    created_at: str
```

**`GET /schedule/{username}`** — Fetch existing schedule (404 if none)

**`DELETE /schedule/{username}`** — Remove schedule, returns `{"ok": True}`

### 4.4 Digest Worker: `api/worker.py`

Standalone async worker — runs as a separate process or GitHub Actions cron job.

Entry point: `uv run python -m api.worker`

Logic:
1. Connect to DB
2. Query `digest_schedules WHERE enabled=TRUE`
3. For each schedule: check if it's time to fire (compare `hour_utc`, `day_of_week`, `last_sent_at`)
4. If due: call `get_activity()` + `summarise()` → deliver via email or Slack → `UPDATE last_sent_at = NOW()`

Graceful degradation:
- `RESEND_API_KEY` not set → log warning, skip email schedules
- `GROQ_API_KEY` not set → log error, skip all schedules
- Individual schedule failure → logged, remaining schedules continue

**GitHub Actions cron** (`.github/workflows/digest-worker.yml`):
```yaml
on:
  schedule:
    - cron: '0 * * * *'   # Every hour
jobs:
  run-worker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install uv && uv sync
      - run: uv run python -m api.worker
    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
      GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
      RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 4.5 Frontend: Schedule Settings Panel

**Route:** `app/settings/page.tsx` (new, or extend existing settings area)

**Components** (`web/components/schedule/`):
- `ScheduleForm.tsx` — controlled form with:
  - Frequency toggle: Daily / Weekly
  - Hour (UTC) picker with local time hint
  - Day of week selector (Weekly only)
  - Channel selector: Email / Slack
  - Email input (Email channel only)
  - Slack webhook input (Slack channel only)
  - Repo multi-select (from user's GitHub repos)
  - Days lookback (number input, default 7)
  - Tone selector (reuse existing options)
  - Enable/Disable toggle
  - Save button

- `ScheduleStatus.tsx` — shows current schedule summary + last sent time

**API helpers** in `web/lib/api.ts`:
```typescript
export async function getSchedule(username: string): Promise<DigestSchedule | null>
export async function saveSchedule(data: DigestScheduleRequest): Promise<DigestSchedule>
export async function deleteSchedule(username: string): Promise<void>
```

**TypeScript interface** (add to `web/types/`):
```typescript
interface DigestSchedule {
  id: string;
  username: string;
  enabled: boolean;
  frequency: "daily" | "weekly";
  hour_utc: number;
  day_of_week?: number;
  channel: "email" | "slack";
  email_to?: string;
  slack_webhook?: string;
  repos: string[];
  days: number;
  last_sent_at?: string;
  created_at: string;
}
```

### 4.6 Tests Required

File: `api/tests/test_schedule.py`
- `test_create_schedule_returns_201`
- `test_get_schedule_returns_existing`
- `test_get_schedule_404_unknown_user`
- `test_delete_schedule_removes_row`
- `test_create_schedule_email_requires_email_to`
- `test_create_schedule_slack_requires_webhook`

File: `api/tests/test_worker.py`
- `test_worker_skips_when_no_groq_key`
- `test_worker_fires_email_for_due_schedule` — mock time, DB, deliver_email
- `test_worker_skips_not_yet_due_schedule`
- `test_worker_updates_last_sent_at_after_delivery`

File: `web/tests/schedule.test.tsx`
- `test_schedule_form_renders`
- `test_weekly_day_selector_hidden_when_daily`
- `test_slack_input_hidden_when_email_selected`
- `test_save_calls_api_with_correct_payload`

---

## Cross-Cutting Changes

### `api/api.py` — All Additions
```python
from api.routers import admin, profile, schedule
from api.observability import configure_observability
from api.middleware import RequestLoggingMiddleware

configure_observability()

app = FastAPI(title="gitpulse API", version="1.6.0", lifespan=lifespan)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(admin.router)
app.include_router(profile.router)
app.include_router(schedule.router)
```

### Version Sync (atomic, all at once)

| File | Field | New Value |
|------|-------|-----------|
| `pyproject.toml` | `version` | `1.6.0` |
| `web/package.json` | `version` | `1.6.0` |
| `api/api.py` | FastAPI `version=` + lifespan log | `1.6.0` |
| `gitpulse/cli/cli.py` | version string in `main()` | `1.6.0` |
| `AGENTS.md` | Milestone History | v1.6 In Progress |
| `docs/prd/PRD.md` | Release Table | v1.6.0 row |

---

## Complete File Map

### New Files
```
api/middleware.py
api/observability.py
api/utils.py                              (calculate_streak moved here)
api/worker.py
api/routers/admin.py
api/routers/profile.py
api/routers/schedule.py
api/tests/test_middleware.py
api/tests/test_profile.py
api/tests/test_schedule.py
api/tests/test_worker.py
web/app/u/[username]/page.tsx
web/app/settings/page.tsx
web/components/profile/ProfileHeader.tsx
web/components/profile/ProfileStats.tsx
web/components/profile/TopReposList.tsx
web/components/profile/RecentSummaryCard.tsx
web/components/schedule/ScheduleForm.tsx
web/components/schedule/ScheduleStatus.tsx
web/components/ShareProfileButton.tsx
web/tests/profile.test.tsx
web/tests/schedule.test.tsx
.github/workflows/digest-worker.yml
```

### Modified Files
```
api/api.py                    (middleware, new routers, version bump)
api/db.py                     (init_request_log_table, init_schedules_table)
api/models.py                 (AdminStatsResponse, PublicProfileResponse, DigestScheduleRequest/Response)
api/routers/analytics.py      (import calculate_streak from api.utils)
gitpulse/cli/cli.py           (--format flag, status command, version bump)
pyproject.toml                (version bump, optional sentry dep)
web/package.json              (version bump)
web/lib/api.ts                (schedule API helpers)
web/types/index.ts            (DigestSchedule interface)
web/app/page.tsx              (add ShareProfileButton)
AGENTS.md                     (milestone history)
docs/prd/PRD.md               (release table)
```

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Sentry SDK import overhead | Import lazily inside `configure_observability()` |
| Worker double-fires if cron overlaps | Guard: skip if `last_sent_at` within 50 min |
| Profile page slow cold-load | 5-min cache on `/profile/{username}`; skeleton UI on frontend |
| `calculate_streak` move breaks analytics | Moved + import updated in one commit; existing tests cover it |
| Slack webhook stored in DB plain text | Known limitation; document; encrypt in v1.7 |

---

*Awaiting approval before execution begins.*
