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
- web/src/app/api/auth/[...nextauth]/route.ts

We are planning Sprint 16 — Pro Features.

Before writing any code:
1. Review stories S16.1 through S16.3.
2. Detail how we map the expanded `repo` OAuth scope to the core library API client.
3. Design the database backend for `/summary/:id` public links.
4. Propose a step-by-step technical execution plan.
5. Save plan to `docs/sprint/sprint-16-plan.md`.

Do not write code yet. Planning only.
```

### Execution Prompt — Stream 1: Private Repos & OAuth
```text
Execute Stream 1 — OAuth scoped access.
Branch: feature/sprint-16-pro

Use @backend-dev and @frontend-dev.
- Update NextAuth to request `repo` scope when needed.
- Surface permission toggles to users before redirecting to GitHub.
- Ensure API passes token to fetch private org commits.

Commit and push.
```

### Execution Prompt — Stream 2: Shareable Links & Comparisons
```text
Execute Stream 2 — Public links.
Still on branch: feature/sprint-16-pro

- Implement DB flags for `is_public` on summaries.
- Build `/summary/:id` unauthenticated React page.
- Add historical comparison data overlays to `/insights`.

Commit, push, create PR.
```

---

## Sprint Stories

| Issue | Story | Status | Priority |
|---|---|---|---|
| TBD | S16.1: Support private org repos via expanded OAuth | 🔵 This Sprint | High |
| TBD | S16.2: Shareable public DB links (`/summary/:id`) | 🔵 This Sprint | High |
| TBD | S16.3: Comparison mode (this period vs last period) | 🔵 This Sprint | Medium |

---

## Story Details & Definition of Done

### Private Repos (S16.1)
**Done when:**
- [ ] Users can opt-in to private repo access.
- [ ] Application securely fetches commits from repos otherwise inaccessible to public APIs.

### Public Links & Comparisions (S16.2-S16.3)
**UI:**
- Share button automatically copies unique UUID permalink.
**Done when:**
- [ ] `/summary/:id` page resolves without Auth if marked public.
- [ ] Trends show red/green arrows based on previous periods.

---

## Order of Work
OAuth Scope Upgrade → Private API Verify → DB Public Flags → React Unauth Page → Trend Math
