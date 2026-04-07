# Sprint 14 Execution Plan — Depth & Intelligence

## 1. Goal Overview
Implement rich PR and Issue tracking within standups, and establish an `/insights` analytical dashboard displaying activity metrics, health scores, and Recharts-based visualisations.

## 2. Architectural Design

### API & Core (Fetching & Aggregation)
Currently, `core/repo_reader` only queries GitHub for commits. We will add:
1. **Pulls API Fetcher:** `GET /repos/{owner}/{repo}/pulls?state=closed&sort=updated`. We will filter for `merged_at` existing inside our `days` lookback period.
2. **Issues API Fetcher:** `GET /repos/{owner}/{repo}/issues?state=closed&sort=updated` inside the lookback period.
3. **Data Shape Update:** `get_commits()` changes to `get_activity()` returning a composite object:
   ```python
   {
       "commits": [...],
       "prs": [{"title": "...", "merged_at": "...", "url": "..."}],
       "issues": [{"title": "...", "closed_at": "...", "url": "..."}]
   }
   ```
4. **LLM Prompt Updates:** `core/summarise` will inject these new arrays natively into the Groq prompt block.

### Insights Endpoints (`api/api.py`)
Add two core analytical endpoints that do NOT call LLM, but just aggregate GitHub data for the frontend:
1. `GET /insights/metrics?username={user}&repos={...}&days={N}`
   - Returns a daily timeseries array for Recharts: `[{ date: '...', commits: 5, prs: 2, issues: 1 }]`.
2. `GET /insights/health?username={user}&repos={...}`
   - Calls `/repos/:owner/:repo` to fetch stars, forks, open PRs/Issues. Computes a health score (0-100) based on ratio formulas defined in the brainstorm doc.

### React Dashboard (`web/app/insights/page.tsx`)
1. **Metric Cards:** Use Shadcn UI `<Card>` for 4 key metrics (Commits, Merged PRs, Closed Issues, Health).
2. **Tooltips:** Implemented as Radix UI / Shadcn `<HoverCard>` or `<Popover>`, showing up to 8 recent specific PRs/Issues conditionally when a user hovers the metric cards.
3. **Charts:** A `<BarChart>` or `<AreaChart>` from `recharts` for the daily velocity.
4. **Stats for Nerds Panel:** Collapsible table computing averages (like avg stats per day).

---

## 3. Step-by-Step Execution

### Stream 1: PR/Issue Enrichment & Backend Caching (Backend Phase)
1. **Update `repo_reader.py`:** Create `fetch_prs` and `fetch_issues` mimicking the concurrency logic of the newest master branch.
2. **Modify `summarise.py`:** Update prompt structures to heavily reference PR context.
3. **Build Insights API:** Add `@app.get("/insights/metrics")` and `@app.get("/insights/health")` in FastAPI.
4. **Tests:** Update missing Pytest coverage.

### Stream 2: Insights UI Dashboard (Frontend Phase)
1. **Install Recharts:** Guarantee `npm install recharts` is run.
2. **Page Structure:** Build the `/insights` page shell and tab architecture.
3. **Cards & Tooltips:** Map endpoint payload to Shadcn UI summary cards.
4. **Velocty Charts:** Map `/metrics` daily payload into Recharts components.
5. **Stats for Nerds:** Render the bottom collapsible table.
