# Sprint 12 — Enhanced Input UX & Error Feedback

**Sprint goal:** Improve form validation (live username checks), searchable repo multiselect, date-range filtering, and export to MD.
**Milestone:** v0.5 — History & Analytics
**Duration:** Day 7 (~3-4 hours)
**Status:** Not Started

---

## Pre-Sprint Requirements
- Sprint 10 (Analytics) must be complete to ensure UI and charts are in place.
- Ensure valid GitHub tokens are accessible for the live repo lookups.

---

## AI Planning Prompt

### Planning Prompt (Gemini 3.1 Pro High — Planning Mode)
```
Read these files before responding:
- AGENTS.md
- docs/sprint/sprint-12-brief.md
- docs/architecture/overview.md
- docs/api/api-contract.md

We are planning Sprint 12 — Enhanced Input UX & Error Feedback.

Before writing any code:
1. Review stories S12.1–S12.6
2. Plan API wrapper for live GitHub username/repo validation
3. Plan React component for searchable multiselect
4. Propose step-by-step execution plan
5. Save plan to docs/sprint/sprint-12-plan.md

Do not write code yet. Planning only.
```

### Execution Prompt — Stream 1: GitHub API Validation & UI
```
Execute Stream 1 — live validation and multiselect.
Branch: feature/sprint-12-input-ux

Use @frontend-dev and @backend-dev.
- Build /api/github/validate-user endpoints
- Build searchable repo multiselect component in Next.js
- Handle repo-specific 404 messages.

Commit and push.
```

### Execution Prompt — Stream 2: History Filters & Export
```
Execute Stream 2 — filters and export.
Still on branch: feature/sprint-12-input-ux

Use @frontend-dev.
- Add search and date-range controls to /history
- Build Markdown export function returning downloadable .md
- Add commit activity stats footer matching summary.

Commit, push, create PR.
```

---

## Sprint Stories

| Issue | Story | Status | Priority |
|---|---|---|---|
| #137 | S12.1: Surface repo-specific 404 message | 🔵 This Sprint | High |
| #138 | S12.2: Validate GitHub username live | 🔵 This Sprint | High |
| #139 | S12.3: Searchable repo multiselect dropdown | 🔵 This Sprint | High |
| #140 | S12.4: Commit activity stats footer | 🔵 This Sprint | Medium |
| #141 | S12.5: Search and date-range filters | 🔵 This Sprint | Medium |
| #142 | S12.6: Export standup as .md file | 🔵 This Sprint | Low |

---

## Story Details

### #137, #138, #139 — Form Validation & Multiselect

**Data source:** GitHub REST API.

**UI:**
- Live typing debounce for username check.
- Shows green checkmark if valid.
- Searchable dropdown fetches user repos.

**Done when:**
- [ ] Username validates instantly via `/github/validate`.
- [ ] Repo multiselect accurately searches GitHub API.
- [ ] Specific 404 errors are bubbled up gracefully.

---

### #140, #141, #142 — History Filters & Export

**Data source:** Local PostgreSQL summaries.

**UI:**
- Date picker and search bar on `/history`.
- Export button on specific summary views.

**Done when:**
- [ ] Filter updates list in real-time.
- [ ] Export generates valid `.md` file download.

---

## New API Endpoints Needed

```python
GET /github/validate?username=X
# Returns {"valid": true, "avatar_url": "..."}

GET /github/repos?username=X&search=Y
# Returns [{"name": "repo1"}, ...]
```

---

## Order of Work
```text
Validation API → Multiselect UI → Filter UI → Export Button
```

---

## Definition of Done
- [ ] Validation API endpoints working
- [ ] Frontend multiselect component renders and interacts
- [ ] History search and filters work
- [ ] Standup export functions properly
- [ ] All tests pass
- [ ] PR merged
