# Sprint 10 — Analytics Dashboard

**Sprint goal:** Add commit frequency charts, repo activity breakdown, and productivity insights.
**Milestone:** v0.5 — History & Analytics
**Duration:** Day 6 (Weekend — ~3-4 hours)
**Status:** Not Started

---

## Pre-Sprint Requirements
- Sprint 07 must be complete (history/DB must exist)
- Neon DB must have some summaries stored

---

## Antigravity Prompts

### Planning Prompt (Gemini 3.1 Pro High — Planning Mode)
```
Read these files before responding:
- AGENTS.md
- docs/sprint/sprint-10.md
- docs/architecture/overview.md
- docs/api/api-contract.md
- api/api.py
- web/app/history/page.tsx (if exists)

We are planning Sprint 10 — Analytics Dashboard.

Before writing any code:
1. Review stories #105, #106, #107
2. Review what history data is available in DB
3. Confirm recharts is available or needs installing
4. Plan new API endpoints needed for analytics data
5. Plan analytics page layout and component structure
6. Identify risks — performance with large datasets
7. Propose step-by-step execution plan
8. Save plan to docs/sprint/sprint-10-execution-plan.md

Do not write any code yet. Planning only.
Use @backend-dev for API work.
Use @frontend-dev for charts and UI.
```

### Execution Prompt — Stream 1: Analytics API (Fast Mode)
```
Read these files before starting:
- AGENTS.md
- docs/sprint/sprint-10.md
- docs/sprint/sprint-10-execution-plan.md

Execute Stream 1 — analytics API endpoints.
Branch: feature/sprint-10-analytics

Add these endpoints to api/api.py:
- GET /analytics/commits-per-day?username=X&days=30
- GET /analytics/repos-breakdown?username=X
- GET /analytics/insights?username=X

Use @backend-dev skill.
Run pytest -v before committing.
Commit: "feat: add analytics API endpoints (S#105-S#107 stream 1)"
Push — do NOT create PR yet.
```

### Execution Prompt — Stream 2: Charts UI (Fast Mode)
```
Stream 1 is complete. Execute Stream 2 — analytics charts and UI.
Still on branch: feature/sprint-10-analytics

Use @frontend-dev skill.
Install recharts if not already installed.

Build:
- /analytics page in Next.js
- CommitFrequencyChart component (bar chart)
- RepoActivityChart component (pie/bar chart)
- InsightsPanel component

Run npm run build before committing.
Commit: "feat: add analytics dashboard with charts (S#105-S#107 stream 2)"
Push and create PR.
Closes #105
Closes #106
Closes #107
```

---

## Sprint Stories

| Issue | Story | Status | Priority |
|---|---|---|---|
| #105 | S10.1: add commit frequency chart | 🔵 This Sprint | Medium |
| #106 | S10.2: add repo activity breakdown chart | 🔵 This Sprint | Medium |
| #107 | S10.3: add productivity insights | 🔵 This Sprint | Low |

---

## Story Details

### #105 — Commit frequency chart

**Chart type:** Bar chart — commits per day
**Data source:** GET /analytics/commits-per-day
**Library:** recharts

**UI:**
- Bar chart showing commits per day
- Last 30 days default
- Filterable by repo
- Hover tooltip with date and count

**Done when:**
- [ ] Chart renders on /analytics page
- [ ] Data from API
- [ ] Date filter works
- [ ] Mobile responsive

---

### #106 — Repo activity breakdown

**Chart type:** Pie chart or horizontal bar
**Data source:** GET /analytics/repos-breakdown

**UI:**
- Shows % of commits per repo
- Based on all history for logged-in user
- Interactive tooltips
- Legend showing repo names

**Done when:**
- [ ] Chart renders correctly
- [ ] Accurate percentages
- [ ] Interactive tooltips

---

### #107 — Productivity insights

**Data source:** GET /analytics/insights

**Insights to show:**
- Most active day of week
- Current commit streak (days)
- Most worked on repo
- Average commits per day
- Total summaries generated

**UI:**
- Card grid showing each insight
- Icons for each metric
- Trend indicator (up/down vs last period)

**Done when:**
- [ ] Insights panel shows on /analytics
- [ ] Accurate calculations
- [ ] Clean card layout

---

## New API Endpoints Needed

```python
GET /analytics/commits-per-day?username=X&days=30
# Returns: [{"date": "2026-03-28", "count": 5}, ...]

GET /analytics/repos-breakdown?username=X
# Returns: [{"repo": "gitpulse", "count": 45, "percentage": 78.5}, ...]

GET /analytics/insights?username=X
# Returns: {"most_active_day": "Monday", "streak": 5, "top_repo": "gitpulse", ...}
```

---

## Order of Work
```
API endpoints → #105 → #106 → #107
```

## Definition of Done
- [ ] Analytics API endpoints working
- [ ] Commit frequency chart renders
- [ ] Repo activity breakdown renders
- [ ] Productivity insights panel shows
- [ ] /analytics page accessible from nav
- [ ] All tests pass
- [ ] PR merged
