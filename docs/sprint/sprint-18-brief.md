# Sprint 18 — Delight

**Sprint goal:** Gamify with commit streaks, generate annual Year in Review summaries, and build a VS Code extension.
**Milestone:** v1.3 — Delight
**Duration:** Day 12 (~5 hours)
**Status:** Not Started

---

## Pre-Sprint Requirements
- Sprint 17 must be complete.
- Verify node/npm tooling for VS Code extension building.

---

## AI Planning Prompt

### Planning Prompt (Gemini 3.1 Pro High — Planning Mode)
```
Read these files before responding:
- AGENTS.md
- docs/sprint/sprint-18-brief.md
- docs/architecture/overview.md

We are planning Sprint 18 — Delight.

Before writing any code:
1. Review stories S18.1 through S18.3.
2. Outline the logic for accurately calculating commit streak days.
3. Design the schema for the "Year in Review" aggregator endpoint.
4. Establish the blueprint for integrating the VS Code extension sidebar.
5. Propose a step-by-step technical execution plan.
6. Save plan to `docs/sprint/sprint-18-plan.md`.

Do not write code yet. Planning only.
```

### Execution Prompt — Stream 1: Gamification & Year-in-Review
```
Execute Stream 1 — Core data delights.
Branch: feature/sprint-18-delight

Use @backend-dev.
- Build SQL optimized streak calculators.
- Create `/api/year-in-review` endpoint.
- Render special Year in Review celebration UI in Next.js.

Commit and push.
```

### Execution Prompt — Stream 2: VS Code Extension
```
Execute Stream 2 — IDE extension sidebar.
Still on branch: feature/sprint-18-delight

Use @frontend-dev.
- Scaffold VS Code webview extension.
- Integrate fetching from local or remote GitPulse API.

Commit, push, create PR.
```

---

## Sprint Stories

| Issue | Story | Status | Priority |
|---|---|---|---|
| TBD | S18.1: Commit streak tracking & personal bests | 🔵 This Sprint | High |
| TBD | S18.2: Generate annual Year in Review | 🔵 This Sprint | High |
| TBD | S18.3: VS Code extension sidebar | 🔵 This Sprint | Medium |

---

## Story Details

### Gamification (S18.1-S18.2)

**Data source:** SQL query counting localized consecutive days with `commit_count > 0`.

**UI:**
- Interactive Year in Review horizontal block scrolling.

**Done when:**
- [ ] Streak badges correctly ignore weekends (optional setting).
- [ ] Year in Review groups data by month and generates "Spotify Wrapped" style UI.

---

### VS Code Extension (S18.3)

**Architecture:** Typescript `vscode-extension` boilerplate utilizing React webview.

**UI:**
- Config panel for entering standard GitPulse backend endpoint.

**Done when:**
- [ ] Plugin runs cleanly in local VS Code.
- [ ] Displays summarized standup view directly in sidebar without leaving editor.

---

## New API Endpoints Needed

```python
GET /gamification/streak?username=X
# Returns current and best unbroken streak
GET /yearly-review?year=2026&username=X
# Returns grouped analytical review chunks
```

---

## Order of Work
```text
Streak SQL → Year-in-Review Endpoint → Celebration UI → VS Code Scaffold
```

---

## Definition of Done
- [ ] Gamification logic parses commit timelines precisely
- [ ] Annual review endpoint fetches within latency budgets
- [ ] UI visualizes annual data without crashes
- [ ] Extension works locally inside VS Code runtime
- [ ] All tests pass
- [ ] PR merged
