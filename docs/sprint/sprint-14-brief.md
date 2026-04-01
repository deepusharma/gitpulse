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
```text
Read these files before responding:
- AGENTS.md
- docs/sprint/sprint-14-brief.md
- docs/architecture/overview.md
- docs/api/api-contract.md
- docs/decisions/feature-brainstorm-2026-04.md

We are planning Sprint 14 — Depth & Intelligence.

Before writing any code:
1. Review stories S14.1 through S14.12 mapped to this sprint.
2. Outline how you will fetch and aggregate PR and Issue data alongside Commits.
3. Plan the endpoints required for the `/insights` page metric cards and charts.
4. Detail the React component structure for hover popup tooltips on metric cards.
5. Detail the plan for generating the 2-week Sprint Retrospective.
6. Identify risks — especially regarding complex API aggregations.
7. Propose step-by-step technical execution plan.
8. Save plan to `docs/sprint/sprint-14-plan.md`.

Do not write any code yet. Planning only.
```
