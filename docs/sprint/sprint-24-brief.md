# Sprint 24 Brief: v1.6 — Observability & Growth

## 1. Goal

Launch **v1.6** with a focus on three themes: making gitpulse more **self-aware** (usage metrics, error visibility), more **discoverable** (public profile pages, social sharing), and more **robust for daily use** (scheduled digests, smarter caching, CLI improvements).

---

## 2. Context

gitpulse v1.5 is a clean, well-tested, production-ready codebase. The core feature surface is mature. The next step is making it stickier for existing users and more visible to new ones. The biggest gaps right now are:

1. **No scheduled/automated delivery** — users must manually trigger summaries. A cron-based or webhook-based daily digest would drive daily active use.
2. **No public-facing presence** — there is no way for a user to share a live "profile" of their activity (beyond one-off shareable links). A public `/u/:username` page would make gitpulse a social layer on top of GitHub.
3. **No observability** — the API has no request logging, error tracking, or usage analytics. We don't know which endpoints fail, how often, or for whom.
4. **CLI is underutilized** — the CLI is functional but has no shell completion, no `--watch` mode, and no way to pipe output to other tools cleanly.

---

## 3. Scope & Requirements

### Epic A: Scheduled Digests
- **Daily/Weekly Cron**: Add a `POST /schedule` endpoint that saves a user's preferred delivery schedule (daily/weekly, time, channel: email or Slack).
- **Worker**: A lightweight async worker (or GitHub Actions cron) that reads the schedule table and triggers summaries + delivery automatically.
- **Web UI**: A "Schedule" settings panel in the web UI where users configure their digest preferences.

### Epic B: Public Profile Pages
- **`/u/:username` route**: A public, no-auth page showing a user's recent activity summary, current streak, top repos, and health score — shareable as a live link.
- **OG meta tags**: Generate dynamic Open Graph metadata so the link unfurls nicely in Slack/Discord/Twitter.
- **"Share my profile" button**: One-click copy of the public profile URL from the web UI.

### Epic C: API Observability
- **Structured request logging**: Add a FastAPI middleware that logs every request (path, status, latency, username) using `structlog` or a compatible structured logger.
- **Error tracking**: Integrate Sentry (free tier) for automatic exception capture across the API.
- **`GET /admin/stats`**: Internal endpoint (auth-gated) returning aggregate usage counts: total summaries generated, unique users, top repos, error rate.

### Epic D: CLI Polish
- **Shell completion**: Register `gitpulse` with `typer`'s built-in shell completion for bash/zsh/fish.
- **`--format` flag**: Add `--format json` output mode so `gitpulse generate` can be piped into other tools (e.g., `jq`, Slack bots).
- **`gitpulse status`**: New command that shows the current config, API connectivity, and key health — a quick sanity check for new users.

---

## 4. Acceptance Criteria

- [ ] A user can configure a daily email digest from the web UI settings page.
- [ ] `/u/deepusharma` loads a public profile without requiring a login.
- [ ] The profile page link unfurls correctly in Slack (OG tags present).
- [ ] Every API request is logged with path, latency, and status code.
- [ ] `gitpulse --install-completion` sets up shell completion.
- [ ] `gitpulse generate --format json` outputs valid JSON.
- [ ] `gitpulse status` prints config summary and API health.

---

## 5. Constraints

- No breaking changes to existing API endpoints.
- Sentry DSN must be an optional environment variable (Sentry disabled if unset).
- Scheduled digest worker must degrade gracefully if `RESEND_API_KEY` or `GITHUB_TOKEN` is not set.
- Public profile page must not leak private repo names.
- All new endpoints must have tests before merge.

---

## 6. Milestone

**v1.6.0** — Observability & Growth

---

## 7. AI Planning Prompt

```text
@antigravity Read docs/sprint/sprint-24-brief.md. Review the current state of
api/routers/, web/app/, and gitpulse/cli/cli.py. Then create docs/sprint/sprint-24-plan.md
with a detailed, phased technical execution plan. Include file-level changes,
new endpoints, schema additions, and frontend component breakdown. Wait for
approval before executing.
```
