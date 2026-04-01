# Sprint 07 Execution Plan — Summary History

**Sprint Goal:** Store summaries in Neon PostgreSQL and show history in web UI.

---

## 1. State Assessment
- **Existing `db/` folder:** Contains outdated files (`ddl.sql`, `dml.sql`, `playground-1.mongodb.js`) likely from a previous iteration. We will override these with a new `schema.sql` containing the `summaries` table as per Story #93.
- **Environment:** No `DATABASE_URL` or Neon connection string is currently present in the `.env` or system environment. This needs to be manually added.
- **ORM Approach:** **Raw SQL with `asyncpg`** is recommended. The schema is dead simple (single table, flat inserts/reads), making SQLAlchemy overkill. `asyncpg` will interact natively with FastAPI's async event loop without blocking or adding excess overhead.
- **Neon / Railway Risks:**
  - **Connection Limits:** Railway connecting to an external serverless Neon DB could quickly exhaust active connections if not pooled. **Mitigation:** Use `asyncpg.create_pool(...)` in the FastAPI lifespan.
  - **SSL Requirement:** Neon requires SSL connections. **Mitigation:** Ensure the connection string or pool config explicitly enforces `ssl="require"`.

---

## 2. Step-by-step Execution Plan

### Stream 1: Backend and Database (Skill: @backend-dev)

**1. DB Scripts & Config (Story #93)**
- Add `asyncpg` to the backend dependencies in `requirements.txt`.
- Create `db/schema.sql` using the schema definition provided in `sprint-07.md`.
- Set up connection pooling using `asyncpg` in a new `api/db.py` helper or within `api/api.py`'s lifespan hook.

**2. Save Summary (Story #94)**
- Modify the `POST /summarise` endpoint in `api/api.py`.
- On successful summary generation, execute an `INSERT` statement via the `asyncpg` connection pool.
- Wrap this in a robust `try...except` block targeting DB exceptions. If saving fails, log the error using `logger.error` but allow the API to return the summary response intact without throwing a 500.

**3. Fetch History (Story #95)**
- Add the new `GET /history` endpoint to `api/api.py`.
- Extract query parameters: `username` and optional `limit` (defaulting to 10).
- Execute `SELECT * FROM summaries WHERE username = $1 ORDER BY generated_at DESC LIMIT $2`.
- Format the response to match the exact JSON structure defined in `sprint-07.md`.

**4. Backend Testing (Story #97)**
- Write/update tests in `api/tests/test_api.py`.
- Mock the database pool and test both `/summarise` data persistence (and failure fallback) and `/history` response mapping.
- Verify tests pass with `pytest -v`.

*Commit and push changes to `feature/sprint-07-history`. Do not PR yet.*

---

### Stream 2: Web UI (Skill: @frontend-dev)

**1. Create History Route (Story #96)**
- Create `web/src/app/history/page.tsx`.
- Retrieve the current logged-in user session via NextAuth.
- Perform a `fetch` directly from Next.js (server component if possible, or client via SWR/TanStack Query if interactive) to `GET /api/history?username=XYZ`.

**2. History UI Component (Story #96)**
- Implement an expandable list (Accordion style) showing past summaries.
- The summary row/header should display `generated_at` (formatted nicely), `repos`, and lookback `days`.
- Clicking expands to display the markdown summary (rendered appropriately, re-using existing markdown components if you have them).

**3. Frontend Checking & Delivery (Story #97)**
- Add required tests.
- Run `npm run build` targeting the web app to ensure no TS strict errors.
- Commit all changes and push.
- Create Pull Request referencing Closes #93, #94, #95, #96, #97.
