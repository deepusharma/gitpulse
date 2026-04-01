# Sprint 15 — Team & Reach

**Sprint goal:** Enable multi-username team standups, Slack team delivery, README badge generation, and presentation mode.
**Milestone:** v1.0 — Team & Reach
**Duration:** Day 9 (~4 hours)
**Status:** Not Started

---

## Pre-Sprint Requirements
- Sprint 14 should be complete.
- Slack Webhook URL required for end-to-end testing.

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
1. Review stories S15.1 through S15.6.
2. Define the schema to save/load "Team Rosters".
3. Plan Next.js `/present` presentation mode.
4. Outline structure for badge-generation endpoints (`/badges/*`).
5. Propose a step-by-step technical execution plan.
6. Save plan to `docs/sprint/sprint-15-plan.md`.

Do not write code yet. Planning only.
```

### Execution Prompt — Stream 1: Team Rosters & Summary
```text
Execute Stream 1 — Team logic.
Branch: feature/sprint-15-team

Use @backend-dev.
- Update the API to accept multiple usernames.
- Build Team Roster CRUD endpoints.
- Map generated aggregations for Slack webhook delivery.

Commit and push.
```

### Execution Prompt — Stream 2: Presentation & Badges
```text
Execute Stream 2 — Reach and UI.
Still on branch: feature/sprint-15-team

Use @frontend-dev.
- Add /present view for screen-share standups (large typography, carousel).
- Build the `/badges/` endpoint returning SVG or redirecting to shields.io.

Commit, push, create PR.
```

---

## Sprint Stories

| Issue | Story | Status | Priority |
|---|---|---|---|
| TBD | S15.1: Multi-username team standup | 🔵 This Sprint | High |
| TBD | S15.2: Team roster management (save/load) | 🔵 This Sprint | Medium |
| TBD | S15.3: Slack channel team delivery | 🔵 This Sprint | High |
| TBD | S15.4: README badge generator | 🔵 This Sprint | Low |
| TBD | S15.5: Presentation mode (`/present`) | 🔵 This Sprint | Medium |
| TBD | S15.6: Smart reminders for standups | 🔵 This Sprint | Low |

---

## Story Details & Definition of Done

### Team Standups & Slack (S15.1-S15.3)
**Data source:** existing core aggregator, mapped over list of users.
**Done when:**
- [ ] Users can enter multiple commas separated usernames or save them as a roster.
- [ ] API can post the aggregated standup blocks to a configurable Slack channel.

### Present & Badges (S15.4-S15.5)
**UI:**
- Present mode strips out sidebars and uses pure markdown typography scaled up 150%.
**Done when:**
- [ ] Present mode scales with viewport.
- [ ] Badges successfully render streak counts via simple HTTP GET.

---

## Order of Work
Roster CRUD → Core Multi-User Aggregator → Slack Integration → Present UI → Badges API
