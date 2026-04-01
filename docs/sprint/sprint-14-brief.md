# Sprint 14 — Depth & Intelligence

**Sprint goal:** Add PR and Issue activity tracking to summaries, and build the rich `/insights` dashboard with Recharts.
**Milestone:** v0.9 — Depth & Intelligence
**Duration:** Day 8 (~4-5 hours)
**Status:** Not Started

---

## Pre-Sprint Requirements
- All prior Sprints (S12) must be complete.
- Ensure `recharts` is installed.
- Review `docs/decisions/feature-brainstorm-2026-04.md` for context on the required metrics.

---

## AI Planning Prompt

### Planning Prompt (Gemini 3.1 Pro High — Planning Mode)
```
Read these files before responding:
- AGENTS.md
- docs/sprint/sprint-14-brief.md
- docs/architecture/overview.md
- docs/api/api-contract.md
- docs/decisions/feature-brainstorm-2026-04.md

We are planning Sprint 14 — Depth & Intelligence.

Before writing any code:
1. Review stories S14.1 through S14.11 mapped to this sprint.
2. Outline how you will fetch and aggregate PR and Issue data alongside Commits.
3. Plan the endpoints required for the `/insights` page metric cards and charts.
4. Propose step-by-step technical execution plan.
5. Save plan to `docs/sprint/sprint-14-plan.md`.

Do not write any code yet. Planning only.
```

### Execution Prompt — Stream 1: PR/Issue Enrichment
```
Execute Stream 1 — PR/Issue enrichment in core summarization.
Branch: feature/sprint-14-depth

Use @backend-dev.
- Update GitHub API calls to fetch PRs (opened/merged/reviewed) and Issues (opened/closed).
- Update the core Markdown generator to include these new sections.
- Create 2-week Sprint Retrospective prompt mode.

Commit and push.
```

### Execution Prompt — Stream 2: Insights UI Dashboard
```
Execute Stream 2 — /insights dashboard.
Still on branch: feature/sprint-14-depth

Use @frontend-dev.
- Build /insights page with metric cards utilizing recharts (bar charts, line charts).
- Include hover popovers for drill-down tooltips.
- Add "Stats for Nerds" panel.

Commit, push, create PR.
```

---

## Sprint Stories

| Issue | Story | Status | Priority |
|---|---|---|---|
| TBD | S14.1: PR activity in standup summary | 🔵 This Sprint | High |
| TBD | S14.2: Issue activity in standup summary | 🔵 This Sprint | High |
| TBD | S14.3: GitHub Projects sprint card activity | 🔵 This Sprint | Medium |
| TBD | S14.4: AI-powered sprint retrospective | 🔵 This Sprint | High |
| TBD | S14.5: Metric cards for /insights | 🔵 This Sprint | High |
| TBD | S14.6: Advanced Recharts (Velocity/Health area charts) | 🔵 This Sprint | Medium |
| TBD | S14.7: Language breakdown donut chart & badges | 🔵 This Sprint | Low |
| TBD | S14.8: Repo metadata panel (stars, forks, CI) | 🔵 This Sprint | Medium |
| TBD | S14.9: Repo health score algorithm | 🔵 This Sprint | Low |
| TBD | S14.10: Stats for Nerds panel | 🔵 This Sprint | Low |
| TBD | S14.11: Date range and repo filters on /insights | 🔵 This Sprint | Medium |

---

## Story Details

### PR & Issue Parsing (S14.1-S14.3)

**Data source:** GitHub GraphQL or REST (Pulls & Issues).

**UI:**
- Included natively in Markdown outputs.

**Done when:**
- [ ] Summaries include properly formatted lists of reviewed PRs.
- [ ] Closed issues are linked with # references.

---

### Insights Dashboard (S14.5-S14.11)

**Data source:** `GET /insights/...` aggregation endpoints.
**Library:** recharts

**UI:**
- Modern dashboard with grid layout.
- Hover popovers explicitly capped at 8 items.

**Done when:**
- [ ] /insights renders correctly without hydration errors.
- [ ] Charts populate via backend endpoints.

---

## New API Endpoints Needed

```python
GET /insights/metrics?username=X
# Returns aggregated PR and commit velocity
GET /insights/health?username=X
# Returns computed health score
```

---

## Order of Work
```text
Core Python Fetchers → Markdown Updater → Insights API → React Dashboard
```

---

## Definition of Done
- [ ] Core fetcher supports PRs and Issues
- [ ] Generated Markdown includes activity sections
- [ ] Insights API endpoints return correct datasets
- [ ] /insights components render recharts appropriately
- [ ] All tests pass
- [ ] PR merged
