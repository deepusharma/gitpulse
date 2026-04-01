# Sprint 10 Execution Plan — Analytics Dashboard

**Sprint Goal:** Add commit frequency charts, repo activity breakdown, and productivity insights.

---

## 1. State Assessment
- **DB History Data:** The DB currently stores generated summaries (the `summaries` table from Sprint 07), which lacks raw commit granularity. Thus, raw commit metrics will need to be calculated dynamically from `core.repo_reader.get_commits(source="github")`.
- **Finding Repositories:** The analytics endpoints (`/analytics/...`) only accept `username` and `days`. To get the list of repositories to query, we must either query the `summaries` DB table to get previously summarized repos or call the GitHub API `GET /users/{username}/repos` to find their public repos.
- **Dependencies:** `recharts` is **not** currently installed in the Next.js `web/` project and needs to be added.
- **Risks & Mitigations:**
  - **Performance / External API Limits:** Fetching up to 30 days of commits across multiple repositories via the GitHub API on every page load will be slow and risk hitting rate limits. 
  - **Mitigation:** Execute aggregations concurrently on the backend. Ensure `GITHUB_TOKEN` is used for higher rate limits. Consider caching results if performance becomes a bottleneck.

---

## 2. API Endpoints Plan (Stream 1) → @backend-dev

**File to modify:** `api/api.py` (Add new routes)

**Helper Requirement:** 
Create a helper function `_get_user_repos(username: str) -> list[str]` which queries the GitHub API (`/users/{username}/repos`) for public repositories.

**Endpoint 1: `GET /analytics/commits-per-day`**
- **Query Params:** `username` (str), `days` (int, default=30)
- **Logic:** 
  1. Resolve repos for the username via `_get_user_repos`.
  2. Call `get_commits(source="github", username=username, repos=repos, days=days)`.
  3. Group returned commits by `commit['date']` (truncated to Day).
  4. Return formatted response `[{"date": "YYYY-MM-DD", "count": 5}, ...]`.

**Endpoint 2: `GET /analytics/repos-breakdown`**
- **Query Params:** `username` (str), `days` (int, default=30)
- **Logic:** 
  1. Resolve repos and fetch commits similarly.
  2. Map out a dictionary to count commits per repo.
  3. Calculate percentages `(count / total_commits) * 100`.
  4. Return: `[{"repo": "gitpulse", "count": 45, "percentage": 78.5}, ...]`.

**Endpoint 3: `GET /analytics/insights`**
- **Query Params:** `username` (str), `days` (int, default=30)
- **Logic:**
  1. **Total Summaries:** Execute DB query using the `asyncpg` connection pool: `SELECT count(*) FROM summaries WHERE username = $1`.
  2. Fetch user's raw commits via `get_commits()`.
  3. Iterate and calculate:
     - `most_active_day`: Map by `%A` (e.g. "Monday") and find the mode.
     - `streak`: Reverse-iterate from the max commit date to count consecutive days.
     - `top_repo`: Repo with highest count.
     - `average_commits`: `Total commits / days`.
  4. Return aggregated JSON: `{"most_active_day": "Monday", "streak": 5, "top_repo": "gitpulse", "total_summaries": 12, "average_commits_per_day": 3.4}`

**Testing:** 
- Add tests to `api/tests/test_api.py`.
- Mock GitHub API HTTP responses using `unittest.mock.patch`.
- Mock DB pool responses for the summaries count.

---

## 3. Web UI Plan (Stream 2) → @frontend-dev

**Directory:** `web/src/app/analytics/` & `web/src/components/`

**1. Setup**
- Inside the `web/` directory, run: `npm install recharts`

**2. Analytics Components (`web/src/components/analytics/` or similar)**
- `CommitFrequencyChart.tsx`: A `recharts` `BarChart` using the XAxis (date) and Tooltip.
- `RepoActivityChart.tsx`: A `recharts` `PieChart` or vertical bar, parsing the `percentage` for its legend.
- `InsightsPanel.tsx`: A robust grid using `shadcn/ui` Card components and `lucide-react` icons (e.g., `Flame` for Streaks, `Trophy` for top repo, `Calendar` for active day).

**3. Analytics Page Layout (`web/src/app/analytics/page.tsx`)**
- Header titled: **"Analytics Dashboard"**
- Global Filter controls: "Lookback window" Dropdown/Input (Default: 30 days) that refetches data.
- Layout:
  - Top full-width row: `CommitFrequencyChart`
  - Bottom split row (2 columns): `RepoActivityChart` & `InsightsPanel`

**4. Data Fetching**
- Utilize standard Next.js architecture (Client components fetching natively via `useEffect` + `fetch()` pointing to `/analytics/*`, or using React Server Components pointing natively internally avoiding standard fetch waterfalls where possible). Wait states natively handled via skeletons.

---

## 4. Execution Steps

1. **Stream 1 (Backend):** Implement all 3 API endpoints + Github repo helper inside `api/api.py`. Run tests.
2. **Commit:** Ensure `pytest -v` passes. Commit: `"feat: add analytics API endpoints (S#105-S#107 stream 1)"`. Push.
3. **Stream 2 (Frontend):** Install `recharts`. Build Next.js page `/analytics` and its dependent charts.
4. **Integration:** Connect UI fetchers to the new APIs. Provide robust load handling (Spinners) given the GitHub API latency.
5. **Final Review:** Validate the page on mobile/desktop. Compile using `npm run build`. 
6. **PR:** Create PR: `"feat: add analytics dashboard with charts (S#105-S#107 stream 2)"`. Fixes 105, 106, 107.
