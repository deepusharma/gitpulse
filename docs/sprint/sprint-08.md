# Sprint 08 — Email & Scheduling

**Sprint goal:** Send summaries via email using Resend and automate weekly generation via GitHub Actions.
**Milestone:** v0.6 — Integrations
**Duration:** Day 4 (Weekday — ~1.5 hours)
**Status:** Not Started

---

## Pre-Sprint Manual Setup (Do before planning)

1. Sign up at resend.com (free tier — 3000 emails/month)
2. Add domain OR use resend.dev test subdomain
3. Get API key from Resend dashboard
4. Add to Railway environment variables: `RESEND_API_KEY=re_xxxxx`
5. Add to local `.env`: `RESEND_API_KEY=re_xxxxx`

---

## Antigravity Prompts

### Planning Prompt (Gemini 3.1 Pro High — Planning Mode)
```
Read these files before responding:
- AGENTS.md
- docs/sprint/sprint-08.md
- docs/architecture/overview.md
- docs/api/api-contract.md
- api/api.py
- web/components/SummaryForm.tsx

We are planning Sprint 08 — Email and Scheduling.

Before writing any code:
1. Review stories #98, #99, #100, #101
2. Confirm RESEND_API_KEY is available in environment
3. Review current POST /summarise request/response shape
4. Identify best approach for optional email parameter
5. Plan GitHub Actions cron workflow
6. Propose step-by-step execution plan
7. Save plan to docs/sprint/sprint-08-execution-plan.md

Do not write any code yet. Planning only.
Use @backend-dev skill for API work.
Use @frontend-dev skill for UI changes.
```

### Execution Prompt — Stream 1: Backend (Fast Mode)
```
Read these files before starting:
- AGENTS.md
- docs/sprint/sprint-08.md
- docs/sprint/sprint-08-execution-plan.md

Execute stories #98, #99 — Resend setup and API email delivery.
Branch: feature/sprint-08-email

Use @backend-dev skill.
Run pytest -v before committing.
Commit: "feat: add Resend email delivery to summarise endpoint (S#98-S#99)"
Push — do NOT create PR yet.
```

### Execution Prompt — Stream 2: Frontend + Actions (Fast Mode)
```
Stream 1 is complete. Execute stories #100, #101.
Still on branch: feature/sprint-08-email

Use @frontend-dev skill for #100.
For #101 — create .github/workflows/weekly-summary.yml

Run npm run build and pytest -v before committing.
Commit: "feat: email UI toggle and GitHub Actions cron (S#100-S#101)"
Push and create PR.
Closes #98
Closes #99
Closes #100
Closes #101
```

---

## Sprint Stories

| Issue | Story | Status | Priority |
|---|---|---|---|
| #98 | S8.1: set up Resend account and API integration | 🔵 This Sprint | High |
| #99 | S8.2: add email delivery to POST /summarise | 🔵 This Sprint | High |
| #100 | S8.3: add email input to web UI | 🔵 This Sprint | Medium |
| #101 | S8.4: add GitHub Actions cron for weekly summary | 🔵 This Sprint | High |

---

## Story Details

### #98 — Resend integration

**Implementation:**
- `pip install resend` — add to pyproject.toml
- Create `core/email.py` with `send_summary_email(to, summary, generated_at)`
- Use Resend Python SDK
- Test with Resend sandbox

**Done when:**
- [ ] Resend SDK installed
- [ ] core/email.py created
- [ ] Test email sends successfully
- [ ] RESEND_API_KEY in environment

---

### #99 — Email delivery in API

**Updated request body:**
```json
{
  "username": "deepusharma",
  "repos": ["gitpulse"],
  "days": 7,
  "email": "user@example.com"
}
```

**Implementation:**
- Add optional `email` field to `SummariseRequest`
- After generation — if email provided, call `send_summary_email()`
- Email failure must NOT break API response

**Done when:**
- [ ] Optional email field in request
- [ ] Email sent if provided
- [ ] Email failure logged but response still returned

---

### #100 — Email input in web UI

**Implementation:**
- Add email field to SummaryForm
- Pre-fill from GitHub OAuth session email
- Toggle to enable/disable
- Show confirmation after email sent

**Done when:**
- [ ] Email field visible in form
- [ ] Pre-filled from session
- [ ] Toggle works
- [ ] Confirmation shown

---

### #101 — GitHub Actions cron

**File:** `.github/workflows/weekly-summary.yml`

**Schedule:** Every Monday 3:30am UTC (9am IST)

```yaml
on:
  schedule:
    - cron: '30 3 * * 1'
  workflow_dispatch:  # manual trigger for testing
```

**Steps:**
1. Call POST /summarise with configured repos
2. Send email via Resend

**Secrets needed:**
- `RAILWAY_API_URL`
- `GITHUB_USERNAME`
- `SUMMARY_REPOS`
- `SUMMARY_EMAIL`
- `RESEND_API_KEY`

**Done when:**
- [ ] Workflow file created
- [ ] Manual trigger works
- [ ] Scheduled trigger works
- [ ] Email received on trigger

---

## Order of Work
```
#98 → #99 → #100 → #101
```

## Definition of Done
- [ ] Resend integrated and sending emails
- [ ] POST /summarise accepts optional email
- [ ] Web UI has email toggle
- [ ] GitHub Actions cron running weekly
- [ ] All tests pass
- [ ] PR merged
