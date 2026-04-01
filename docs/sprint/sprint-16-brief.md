# Sprint 16 — Pro Features

**Sprint goal:** Add support for private org repos via expanded OAuth scope, public shareable summary links, and comparison modes.
**Milestone:** v1.1 — Pro Features
**Duration:** Day 10 (~3-4 hours)
**Status:** Not Started

---

## Pre-Sprint Requirements
- Ensure NextAuth.js setup is accessible for scope modification.

---

## AI Planning Prompt

### Planning Prompt (Gemini 3.1 Pro High — Planning Mode)
```text
Read these files before responding:
- AGENTS.md
- docs/sprint/sprint-16-brief.md
- docs/architecture/overview.md
- web/src/app/api/auth/[...nextauth]/route.ts (or equivalent OAuth Config)

We are planning Sprint 16 — Pro Features.

Before writing any code:
1. Review stories S16.1 through S16.3 mapped to this sprint.
2. Detail exactly how we map the expanded `repo` OAuth scope to the core library API client.
3. Design the database migration and API routing for `/summary/:id` public links.
4. Formulate the approach for fetching and comparing historical date-ranges in `/insights`.
5. Identify security/permissions risks with sharing and private scopes.
6. Propose a step-by-step technical execution plan.
7. Save plan to `docs/sprint/sprint-16-plan.md`.

Do not write any code yet. Planning only.
```
