# Sprint 15 — Team & Reach

**Sprint goal:** Enable multi-username team standups, Slack team delivery, README badge generation, and presentation mode.
**Milestone:** v1.0 — Team & Reach
**Duration:** Day 9 (~4 hours)
**Status:** Not Started

---

## Pre-Sprint Requirements
- Sprint 14 should be complete.
- Read up on the `shields.io` badge generation endpoint format if necessary.

---

## AI Planning Prompt

### Planning Prompt (Gemini 3.1 Pro High — Planning Mode)
```text
Read these files before responding:
- AGENTS.md
- docs/sprint/sprint-15-brief.md
- docs/architecture/overview.md
- docs/api/api-contract.md

We are planning Sprint 15 — Team & Reach.

Before writing any code:
1. Review stories S15.1 through S15.6 mapped to this sprint.
2. Define the schema and DB changes required to save and load "Team Rosters".
3. Formulate how to execute parallel GitHub calls for multiple users efficiently.
4. Detail the Next.js routing and UI styling plan for `/present` presentation mode.
5. Outline structure for badge-generation endpoints (`/api/badges/...`).
6. Identify any rate-limiting risks when querying data for whole teams.
7. Propose a step-by-step technical execution plan.
8. Save plan to `docs/sprint/sprint-15-plan.md`.

Do not write any code yet. Planning only.
```
