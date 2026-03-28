# Sprint 06 — Web UI Polish

**Sprint goal:** Copy to clipboard, better empty/error states, summary stats.
**Milestone:** v0.4 — Config & Scheduling
**Duration:** Day 2 (Weekday — ~1 hour)
**Status:** Not Started

---

## Antigravity Prompts

### Planning Prompt (Gemini 3.1 Pro High — Planning Mode)
```
Read these files before responding:
- AGENTS.md
- docs/sprint/sprint-06.md
- docs/architecture/overview.md
- web/app/page.tsx
- web/components/Results.tsx
- web/components/SummaryForm.tsx

We are planning Sprint 06 — Web UI Polish.

Before writing any code:
1. Review stories #90, #91, #92
2. Review current web component structure
3. Identify best approach for clipboard API
4. Propose step-by-step execution plan
5. Save plan to docs/sprint/sprint-06-execution-plan.md

Do not write any code yet. Planning only.
Use @frontend-dev skill.
```

### Execution Prompt (Fast Mode)
```
Read these files before starting:
- AGENTS.md
- docs/sprint/sprint-06.md
- docs/sprint/sprint-06-execution-plan.md

Execute stories #91, #90, #92 in that order.
Branch: feature/sprint-06-ui-polish

Use @frontend-dev skill.
Run npm run build before committing — no TypeScript errors.
Commit: "feat: copy button, empty states, summary stats (S#90-S#92)"
Push and create PR.
Closes #90
Closes #91
Closes #92
```

---

## Sprint Stories

| Issue | Story | Status | Priority |
|---|---|---|---|
| #90 | S6.1: add copy to clipboard button | 🔵 This Sprint | Medium |
| #91 | S6.2: improve empty and error states | 🔵 This Sprint | Medium |
| #92 | S6.3: add word count and stats | 🔵 This Sprint | Low |

---

## Story Details

### #90 — Copy to clipboard

**Goal:** One-click copy of generated summary.

**Implementation:**
- Add Copy button to Results component
- Use `navigator.clipboard.writeText()`
- Show "Copied" confirmation for 2 seconds
- Use shadcn/ui Button component

**Done when:**
- [ ] Copy button visible on summary
- [ ] Copies markdown to clipboard
- [ ] Confirmation shown after click

---

### #91 — Empty and error states

**Goal:** Better UX when no commits or errors occur.

**States to handle:**
- No commits found → friendly message + suggestion
- API error → specific error message per status code
- Loading → smooth skeleton

**Done when:**
- [ ] Empty state shown when no commits found
- [ ] Error messages are human readable
- [ ] Loading state is smooth

---

### #92 — Summary stats

**Goal:** Show metadata after generation.

**Stats to show:**
- Word count
- Generation time
- Commits processed
- Repos included

**Done when:**
- [ ] Stats displayed below summary
- [ ] Accurate counts shown

---

## Order of Work
```
#91 → #90 → #92
```

## Definition of Done
- [ ] Copy button works
- [ ] Empty states handled gracefully
- [ ] Stats shown after generation
- [ ] npm run build passes
- [ ] PR merged
