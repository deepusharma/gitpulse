# Sprint 07 — Summary History

**Sprint goal:** Store summaries in Neon PostgreSQL and show history in web UI.
**Milestone:** v0.5 — History & Analytics
**Duration:** Day 3 (Weekday — ~1.5 hours)
**Status:** ✅ Complete — Merged via PR #132

---

## AI Planning Prompt

### Planning Prompt (Gemini 3.1 Pro High — Planning Mode)
```
Read these files before responding:
- AGENTS.md
- docs/sprint/sprint-07-brief.md
- docs/architecture/overview.md
- docs/api/api-contract.md
- api/api.py

We are planning Sprint 07 — Summary History.

Before writing any code:
1. Review stories #93, #94, #95, #96, #97
2. Check if db/ folder exists and what's in it
3. Confirm Neon connection string is available in environment
4. Identify best ORM approach — raw SQL vs SQLAlchemy vs asyncpg
5. Identify risks around DB connection in Railway
6. Propose step-by-step execution plan
7. Save plan to docs/sprint/sprint-07-plan.md

Do not write any code yet. Planning only.
Use @backend-dev skill for API/DB work.
Use @frontend-dev skill for history page.
```

### Execution Prompt — Stream 1: Backend (Fast Mode)
```
Read these files before starting:
- AGENTS.md
- docs/sprint/sprint-07-brief.md
- docs/sprint/sprint-07-plan.md
- docs/api/api-contract.md

Execute stories #93, #94, #95 — database and API.
Branch: feature/sprint-07-history

Use @backend-dev skill.
Run pytest -v before committing — all tests must pass.
Commit: "feat: add Neon DB schema and history API (S#93-S#95)"
Push — do NOT create PR yet, Stream 2 follows.
```

### Execution Prompt — Stream 2: Frontend (Fast Mode)
```
Stream 1 is complete. Now execute stories #96, #97 — history page and tests.
Still on branch: feature/sprint-07-history

Use @frontend-dev skill for #96.
Use @tester-backend skill for #97.
Run npm run build and pytest -v before committing.
Commit: "feat: add history page and tests (S#96-S#97)"
Push and create PR.
Closes #93
Closes #94
Closes #95
Closes #96
Closes #97
```

---

## Sprint Stories

| Issue | Story | Status | Priority |
|---|---|---|---|
| #93 | S7.1: set up Neon PostgreSQL schema | ✅ Done | High |
| #94 | S7.2: save summary to DB after generation | ✅ Done | High |
| #95 | S7.3: add GET /history API endpoint | ✅ Done | High |
| #96 | S7.4: add history page to web UI | ✅ Done | High |
| #97 | S7.5: write tests for history endpoints | ✅ Done | High |

---

## Story Details

### #93 — Neon PostgreSQL schema

**Schema:**
```sql
CREATE TABLE summaries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username TEXT NOT NULL,
  repos TEXT[] NOT NULL,
  days INTEGER NOT NULL,
  display TEXT NOT NULL,
  summary TEXT NOT NULL,
  generated_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_summaries_username ON summaries(username);
CREATE INDEX idx_summaries_generated_at ON summaries(generated_at DESC);
```

**Environment variables:**
```
DATABASE_URL=postgresql://user:pass@host/dbname
```

**Done when:**
- [x] Neon connection working from API
- [x] summaries table created
- [x] db/schema.sql committed
- [x] DATABASE_URL in Railway environment

---

### #94 — Save summary to DB

**Implementation:**
- After successful summarise call — insert to DB
- Save failure must NOT break the API response
- Log save errors but return summary normally

**Done when:**
- [x] POST /summarise saves to DB
- [x] DB failure doesn't break response
- [x] username, repos, summary, generated_at stored

---

### #95 — GET /history endpoint

**Request:** `GET /history?username=deepusharma&limit=10`

**Response:**
```json
{
  "summaries": [
    {
      "id": "uuid",
      "username": "deepusharma",
      "repos": ["gitpulse"],
      "days": 7,
      "summary": "...",
      "generated_at": "2026-03-28T10:00:00Z"
    }
  ],
  "total": 10
}
```

**Done when:**
- [x] GET /history returns list
- [x] Supports ?username= filter
- [x] Supports ?limit= parameter (default 10)
- [x] Returns most recent first

---

### #96 — History page

**Route:** `/history` in Next.js App Router

**UI:**
- List of past summaries
- Date, repos, days shown per item
- Click to expand full summary
- Filtered to logged-in user

**Done when:**
- [x] /history route works
- [x] Lists past summaries
- [x] Expandable items
- [x] Auth protected

---

### #97 — Tests

**Done when:**
- [x] Test POST /summarise saves to DB (mock DB)
- [x] Test GET /history returns data
- [x] Test DB failure doesn't break summarise

---

## Order of Work
```
#93 → #94 → #95 → #96 → #97
```

## Definition of Done
- [x] Neon DB connected and schema created
- [x] Summaries saved on generation
- [x] GET /history returns past summaries
- [x] History page shows in web UI
- [x] All tests pass
- [x] PR #132 merged
