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
```text
Read these files before responding:
- AGENTS.md
- docs/sprint/sprint-12-brief.md
- docs/architecture/overview.md
- docs/api/api-contract.md
- web/src/app/page.tsx (or equivalent input form)

We are planning Sprint 12 — Enhanced Input UX & Error Feedback.

Before writing any code:
1. Review stories S12.1 through S12.6 mapped to this sprint.
2. Formulate approach for live GitHub username validation without exceeding rate limits.
3. Design the searchable repo multiselect dropdown behavior.
4. Plan the integration of date-range filters to the /history page.
5. Define the export-to-MD functionality from the frontend.
6. Identify risks — particularly UX latency and external API limits.
7. Propose step-by-step technical execution plan.
8. Save plan to `docs/sprint/sprint-12-plan.md`.

Do not write any code yet. Planning only.
```
