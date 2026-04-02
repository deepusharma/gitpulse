# Sprint 12 Execution Plan — Enhanced Input UX & Performance Caching

**Goal:** Improve form validation, repository selection, and history filtering while optimizing performance through server-side caching.
**Milestone:** v0.5 — History & Analytics

---

## 1. Analysis & Pre-Work Responses

1.  **Review UX Stories (S12.1–S12.7)**:
    - **S12.1 (404 reporting)**: Current `repo_reader.py` logs 404s but doesn't surface them to the API response. We'll change this to return a list of failed repos.
    - **S12.2/S12.3 (Validation & Multiselect)**: Requires new API endpoints to poll GitHub. Debouncing is critical to avoid rate limiting.
    - **S12.5 (History Filters)**: `GET /history` needs to support `search` and `date-range` query params.
    - **S12.6 (Export)**: Client-side file generation for `.md` summaries.

2.  **Review Performance Stories (S12.8–S12.12)**:
    - **S12.8/S12.10 (Caching)**: In-memory dictionary with TTL. Keys will include parameters (username, repos, days).
    - **S12.9 (Refresh)**: Add `refresh=true` to force cache bypass and re-save to DB.

3.  **Plan API wrapper for live GitHub validation**:
    - `GET /github/validate?username=X` -> Returns profile data (avatar) if user exists.
    - `GET /github/repos?username=X` -> Returns searchable list of public repos.
    - Use the existing `GITHUB_TOKEN` to ensure high rate limits.

4.  **Plan React component for searchable multiselect**:
    - Will combine `shadcn`'s `Command` (search), `Popover` (floating list), and `Badge` (selected items display).
    - Fetches data dynamically when the username is valid.

5.  **Plan Caching Strategy**:
    - **Cache implementation**: `InMemoryCache` in `api/cache.py`.
    - **TTL**: 5 minutes (300s) for commits and analytics.
    - **Refresh**: Allow a query param `refresh=true` to force a new pull from GitHub.

---

## 2. Step-by-Step Execution Plan

### Step 1: Initialize Workspace
- Checkout new branch: `feature/sprint-12-input-ux-cache`
- Verify database connectivity and current test suite status.

### Step 2: Backend — Performance Caching (S12.8, S12.10)
- **Create `api/cache.py`**:
    - Implement `InMemoryCache` with `get`, `set`, and `delete`.
- **Modify `api/api.py`**:
    - Integrate `InMemoryCache` into `/summarise` and `/analytics/all`.
    - Implement `refresh=true` logic.
    - Export `last_updated` timestamp in responses.

### Step 3: Backend — Validation & Repo Endpoints (S12.1, S12.2, S12.3)
- **Modify `core/repo_reader.py`**:
    - Update `_get_github_commits` to return a `(commits, errors)` tuple, where `errors` lists failed/private repos.
- **Modify `api/api.py`**:
    - Add `GET /github/validate?username=X`.
    - Add `GET /github/repos?username=X`.
    - Update `/summarise` error handling to report specific repo-level 404s (S12.1).

### Step 4: Frontend — Multi-select & Validation (S12.2, S12.3)
- **Create `web/components/ui/multi-select.tsx`**:
    - Build searchable multiselect using `Command` and `Popover`.
- **Modify `web/components/SummaryForm.tsx`**:
    - Implement debounced username check using `validateUser` API.
    - Swap static repository text input for the new `MultiSelect` component.
    - Add "Force Refresh" toggle/button.

### Step 5: Frontend — History Filters & Export (S12.5, S12.6, S12.7)
- **Modify `web/app/history/page.tsx`**:
    - Add `Search` input.
    - Add `DateRangePicker` (simple inputs or `shadcn` Calendar).
    - Update `fetchHistory` to pass filter parameters to the backend.
- **Modify `web/components/Results.tsx`**:
    - Add "Export as Markdown" button.
    - Implement activity stats footer (commits per repo/day).
- **Fix `web/components/SummaryForm.tsx`**:
    - Ensure `days` field avoids leading zero bugs.

### Step 6: Backend — History Search (S12.5)
- **Modify `api/api.py`**:
    - Update `/history` to support filtering by `search` (repos/summary content) and `date-range`.

### Step 7: Push & PR
- Run `pytest api/tests` and verify manual frontend flows.
- Commit all changes: `feat: implement enhanced UX and performance caching (S12.1-S12.12)`
- Open PR for review.

---

## 3. Post-Sprint Verification
- Verify sub-second dashboard reloads after the first generation.
- Confirm "Refresh" button successfully clears cache and pulls fresh data.
- Ensure history filters accurately narrow down previous summaries.
