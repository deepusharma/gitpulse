# Sprint 18 Execution Plan — Delight (v1.3)

**Sprint Goal:** Gamify the user experience with commit streaks and personal bests, provide annual insights via "Year in Review," and establish a presence in the IDE with a VS Code extension sidebar.
**Milestone:** v1.3 — Delight
**Branch:** `feature/sprint-18-delight`
**Status:** Draft — Awaiting Approval

---

## 1. Technical Analysis & Design

### 1.1 Streak Calculation Logic (S18.1)

The streak calculation will be performed in the backend using the existing `summaries` table in PostgreSQL.

**Algorithm:**
1.  **Fetch Activity Days**: Query unique `generated_at::date` for a specific `username` from the `summaries` table.
2.  **Sort & Deduplicate**: Ensure dates are sorted descending.
3.  **Current Streak**:
    - Start from "today" (or the most recent activity if it was yesterday/today).
    - Iterate backwards.
    - If "Ignore Weekends" is enabled:
        - If current day is Monday and no activity on Sunday/Saturday, check Friday.
        - If Friday has activity, the streak continues.
    - Stop when a gap is found.
4.  **Longest Streak**:
    - Iterate through all activity days.
    - Maintain a counter for consecutive days (applying the same weekend logic).
    - Update `longest_streak` whenever the current sequence exceeds the previous maximum.

**API Endpoint:** `GET /badges/streak?username=X` (already exists but needs logic update) and a new internal helper in `api/routers/analytics.py`.

### 1.2 Year in Review Schema (S18.2)

A new endpoint `GET /analytics/year-in-review?username=X&year=2026` will return an aggregated object.

**Schema:**
```typescript
interface YearInReview {
  username: string;
  year: number;
  total_stats: {
    commits: number;
    prs: number;
    issues: number;
  };
  top_repos: { name: string; count: number }[]; // Top 5
  monthly_breakdown: {
    month: string; // "Jan", "Feb", ...
    commits: number;
  }[];
  busiest_day: {
    date: string;
    count: number;
  };
  ai_wrap_up: string; // AI generated summary of the year's achievements
}
```

**Implementation:**
- SQL aggregation over the `summaries` table for the given year.
- A single LLM call to Groq using a condensed version of the year's commit messages/repo list to generate the `ai_wrap_up`.

### 1.3 VS Code Extension Blueprint (S18.3)

**Structure:**
New top-level directory `vscode/` containing a standard VS Code extension project.

**Components:**
- **Sidebar Provider**: Implements `vscode.WebviewViewProvider`.
- **UI (Webview)**: A simplified version of the `gitpulse` web dashboard (Next.js-lite style) built using plain HTML/TS or a minimal React bundle.
- **API Integration**: Connects to the user's preferred GitPulse backend (defaults to `https://api.gitpulse.dev` or `http://localhost:8000`).

---

## 2. Step-by-Step Technical Plan

### S18.1 — Gamification (Streaks)

1.  **Backend (SQL)**: Write a robust SQL query (or Python post-processor) in `api/routers/analytics.py` to calculate streaks.
2.  **API Update**: Update `GET /badges/streak` in `api/routers/badges.py` to return the real streak instead of the placeholder.
3.  **Frontend**: Add a "Streak" counter and "Personal Best" badge to the `/insights` page.

### S18.2 — Year in Review

1.  **API Router**: Create `api/routers/yearly.py`.
2.  **Logic**: Implement the aggregation logic and the AI "Wrap-up" prompt.
3.  **Frontend**: Create `/year-in-review` page in Next.js.
4.  **UI**: Implement horizontal scrolling "Spotify Wrapped" style cards using Tailwind CSS and Framer Motion for animations.

### S18.3 — VS Code Extension

1.  **Scaffold**: Initialize `vscode/` using `yo code`.
2.  **Sidebar**: Implement the webview sidebar.
3.  **Auth**: Use VS Code's `SecretStorage` to store the GitPulse API key (if needed) or GitHub token.
4.  **Feature**: Allow users to trigger a standup summary for their current local workspace directly from the sidebar.

---

## 3. Order of Execution

1.  **S18.1**: Streak SQL & Badge logic (Backend)
2.  **S18.2**: Year in Review Aggregator & AI (Backend)
3.  **S18.1 + S18.2**: Dashboard & Year in Review UI (Frontend)
4.  **S18.3**: VS Code Extension (IDE)

---

## 4. Definition of Done

- [ ] `GET /badges/streak` returns accurate consecutive days (with weekend-ignore logic).
- [ ] `/year-in-review` page displays annual stats with a "Spotify Wrapped" aesthetic.
- [ ] AI "Wrap-up" generates meaningful annual achievements.
- [ ] VS Code Extension loads in the sidebar and fetches summaries.
- [ ] `uv run pytest -v` passes (all new API tests).
- [ ] `npm run lint` passes in `web/`.
- [ ] PR created and merged.
