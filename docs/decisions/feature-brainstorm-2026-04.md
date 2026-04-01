# GitPulse — Final Feature Brainstorm v4 (Complete Vision)

> Full product vision. Priority-ranked. Includes hover tooltip design, CLI help UX, and platform decisions.

---

## Part 1: Answers to Open Questions (Confirmed)

| Question | Decision |
|---|---|
| Private repos vs team first? | **Private repos first** — v0.6 |
| Slack in Sprint 08? | **Yes, bundle with email** |
| PR/Issue data — inline or dashboard? | **Both** — prose in summary + visual in `/insights` |
| GitLab timing? | **v1.1** — after GitHub depth is complete |
| Tone/language — preference or form? | **Form first, saved defaults in Phase 2** |

---

## Part 2: In-App Documentation Hub (`/docs`)

> FastAPI already auto-generates OpenAPI. Surface it beautifully with user-facing docs on the same domain.

### Pages

| Page | Content | Value |
|---|---|---|
| `/docs` | User guide — getting started, form walkthrough, history, insights | New user onboarding |
| `/docs/api` | Interactive API reference (OpenAPI/Swagger UI, styled to match app) | Developer integration |
| `/docs/cli` | CLI reference — all flags, examples, config file format | Power users |
| `/docs/changelog` | Version history, what changed in each release | Transparency |
| `/docs/roadmap` | Public roadmap (derived from PRD) — planned features, voting | Community engagement |
| `/docs/mcp` | MCP server setup guide for Claude Code, Cursor, Windsurf | Plugin audience |

### API Documentation Specifics
- FastAPI already generates `/openapi.json` — wrap it with a polished Swagger/Redoc UI
- Add example request/response for every endpoint
- Include rate limit info, auth requirements, error codes
- Add a "Try it" live playground against the production API

### Onboarding Flow
- First-visit tour (Shepherd.js or custom) — highlight the form, explain what it does
- Empty state on `/history` that guides you to generate your first summary
- `gitpulse init` wizard (CLI equivalent, Sprint 09) — mirrors the web experience

**Priority: Medium — should ship with v0.8 (Open Source Ready)**

---

## Part 3: GitHub Projects Integration

> GitHub Projects (v2) uses GraphQL. This is the most underserved data source in developer tools.

| Feature | What It Shows | Data Source |
|---|---|---|
| **Active project boards** | List of open Projects for a user/org | GraphQL `projectsV2` |
| **Sprint progress** | Items % complete in current sprint iteration | GraphQL `ProjectV2Item` |
| **Overdue items** | Cards past their target date | Derived |
| **Blocked items** | Cards with "blocked" status | Status field |
| **Velocity tracking** | Items completed per sprint over time | Historical iterations |
| **Standup enrichment** | "I moved 3 cards to Done in Sprint 14" added to summary | GraphQL |

### What This Enables
The standup summary becomes: *"I merged PR #45, closed 3 issues, and completed 4 sprint cards in the Security Improvements project."* — That's a complete picture of a developer's day, not just commits.

**Priority: Medium — v0.9/Sprint 14**

---

## Part 4: Repo Intelligence & Metadata Insights

> You asked specifically about private/public, CI, forks, stars, visitors. Here's the full map:

### Repo Metadata Cards (in `/insights` dashboard)

| Metric | API Source | Value |
|---|---|---|
| **Stars** | `GET /repos/:owner/:repo` | Popularity indicator |
| **Forks** | Same | Adoption indicator |
| **Watchers** | Same | Interest indicator |
| **Open issues count** | Same | Backlog health |
| **Open PRs count** | `GET /repos/:owner/:repo/pulls` | WIP indicator |
| **Default branch** | Same | Convention check |
| **License type** | Same | OSS compliance |
| **Visibility (public/private)** | Same | Portfolio context |
| **Topics/Tags** | `GET /repos/:owner/:repo/topics` | Tech stack |
| **Last pushed** | `GET /repos/:owner/:repo` | Freshness indicator |

### Traffic Insights (owner's own repos only)
> GitHub Traffic API requires push access — works for your own repos.

| Metric | API Source |
|---|---|
| **Page views (14d)** | `GET /repos/:owner/:repo/traffic/views` |
| **Unique visitors (14d)** | Same |
| **Clone count (14d)** | `GET /repos/:owner/:repo/traffic/clones` |
| **Top referrers** | `GET /repos/:owner/:repo/traffic/popular/referrers` |
| **Top content paths** | `GET /repos/:owner/:repo/traffic/popular/paths` |

### CI/CD Insights
| Metric | API Source |
|---|---|
| **Latest workflow runs** | `GET /repos/:owner/:repo/actions/runs` |
| **Pass/fail rate (30d)** | Derived from runs |
| **Average CI duration** | Derived from run timing |
| **Most failing workflows** | Ranked by failure count |
| **Dependabot alerts** | `GET /repos/:owner/:repo/vulnerability-alerts` |

### Repo Health Score (refined algorithm)
```
Score = 
  commit_frequency_score (0-20)     # commits per week in last month
  + issue_close_rate (0-20)         # closed/opened ratio
  + pr_merge_rate (0-15)            # merged/opened ratio  
  + ci_pass_rate (0-15)             # GitHub Actions green rate
  + staleness_penalty (-0 to -20)   # days since last commit
  + has_readme (0-10)               # README.md present
  + has_tests (0-10)                # test files detected
  + has_license (0-5)               # LICENSE file present
  + has_ci (0-5)                    # .github/workflows present
```

**Priority: High for stars/forks/issues (Low complexity). Medium for traffic (needs owner scope). Sprint 14.**

---

## Part 5: Stats for Nerds 🤓

> Time-based analytics that no other standup tool exposes. This is a genuine differentiator.

### Timing Metrics

| Metric | How Calculated | Why It Matters |
|---|---|---|
| **Avg PR cycle time** | Time from PR opened → merged, averaged over period | Engineering velocity indicator |
| **Avg first review time** | Time from PR opened → first review comment | Review responsiveness |
| **Avg commit-to-merge time** | First commit in branch → PR merged | Development loop speed |
| **Time between commits** | Stddev of commit timestamps | Consistency vs burst pattern |
| **PR size distribution** | Lines changed per PR, bucketed (S/M/L/XL) | Healthy PR sizing habits |
| **Bug fix ratio** | Commits with "fix/bug/patch" keywords vs new features | Code quality proxy |
| **Avg commits per PR** | Total commits / total PRs in period | PR granularity |
| **Reopened PR rate** | PRs that were closed and reopened | Rework indicator |
| **Review round trips** | Avg number of review cycles before merge | Process health |
| **Issue response time** | Time from issue opened → first comment | Community responsiveness |
| **Issue resolution time** | Time from issue opened → closed | Bug lifecycle efficiency |
| **Commit by hour/day** | Heatmap of when you commit | Work pattern visibility |
| **Commit message length** | Avg chars in commit message | Message quality proxy |
| **Code churn** | Lines added vs deleted ratio | Rework detection |

### "Stats for Nerds" UI Panel
A collapsible panel at the bottom of `/insights` styled like Spotify's or YouTube's stats section:
```
┌─ Stats for Nerds ──────────────────────────────────────────────────────┐
│ Avg PR cycle time: 14.2 hrs   │ Avg first review: 3.1 hrs              │
│ PR size: S:45% M:38% L:12% XL:5% │ Bug fix ratio: 23%                 │
│ Peak commit hours: 10am-12pm (UTC) │ Commit streak: 12 days 🔥         │
│ Code churn: +1,847 / -622 lines   │ Reviews given: 8 PRs this month    │
└────────────────────────────────────────────────────────────────────────┘
```

**Priority: Medium — exciting differentiator. Sprint 14 alongside `/insights`.**

---

## Part 6: Rich CLI Help & UX

> `rich` is already a dependency. Use it fully.

### `gitpulse --help` (current vs proposed)

**Current:** Basic Typer auto-generated help.

**Proposed:** Full Rich-formatted help panel:
```
╭─ gitpulse v0.7.0 ────────────────────────────────────────────────────────╮
│  Your weekly standup, done.                                               │
│  Generate AI-powered standup summaries from your git commit history.      │
╰───────────────────────────────────────────────────────────────────────────╯

 Usage: gitpulse [OPTIONS] COMMAND [ARGS]...

╭─ Commands ────────────────────────────────────────────────────────────────╮
│  run        Generate a standup summary (default)                          │
│  insights   Show developer analytics dashboard in terminal                │
│  history    List past summaries stored in history                         │
│  init       Interactive setup wizard                                      │
│  config     Show or edit ~/.gitpulse.toml                                 │
╰───────────────────────────────────────────────────────────────────────────╯

╭─ Options (run) ───────────────────────────────────────────────────────────╮
│  --days    INTEGER   Lookback period in days [default: 7]                 │
│  --repo    TEXT      Repo name(s), comma-separated [default: from config] │
│  --tone    TEXT      Summary tone: technical|casual|executive             │
│  --lang    TEXT      Output language: english|spanish|french|...          │
│  --length  TEXT      Summary length: brief|standard|detailed              │
│  --mode    TEXT      Standup mode: daily|weekly                           │
│  --team    TEXT      Comma-separated GitHub usernames (team standup)      │
│  --include-prs       Include PR activity in summary                       │
│  --include-issues    Include issue activity in summary                    │
│  --dry-run           Show commits without LLM call                        │
│  --deliver TEXT      Delivery: clipboard|slack|gist|email                 │
│  --output  PATH      Save output to file                                  │
│  --debug             Enable verbose logging                               │
╰───────────────────────────────────────────────────────────────────────────╯

╭─ Examples ──────────────────────────────────────────────────────────────╮
│  gitpulse run                          # use config defaults             │
│  gitpulse run --days 14 --tone casual  # 2-week casual summary           │
│  gitpulse run --team alice,bob,carol   # team standup                    │
│  gitpulse run --language spanish       # Spanish output                  │
│  gitpulse run --deliver slack          # post to Slack                   │
│  gitpulse insights --days 30           # terminal analytics              │
╰─────────────────────────────────────────────────────────────────────────╯
```

### Additional CLI improvements
- **Colour-coded output:** Green for commits, blue for PRs, yellow for issues
- **Progress bar** during LLM generation: `Generating summary ████████░░ 80%`
- **Interactive mode:** `gitpulse --interactive` → guided prompts via `rich.prompt`
- **`gitpulse config`** subcommand to view/edit `~/.gitpulse.toml` without opening a text editor
- **Shell completion:** `gitpulse --install-completion zsh` (Typer supports this natively)

**Priority: Medium — ship with Sprint 09 (Packaging & DX)**

---

## Part 7: Other Missing Features (Bonus Round)

### 🏆 Gamification & Streaks
- **Commit streak counter** (like GitHub's contribution graph streak)
- **Weekly badges:** "🚀 Shipping Machine (10+ commits)", "🐛 Bug Squasher (5+ fixes)"
- **Personal bests:** "Your fastest PR merge ever: 47 minutes"
- **Year in review:** Annual wrap-up (Spotify Wrapped for your code)
- *Priority: Low — fun engagement feature. v1.3*

### 📛 Badge Generator
- Auto-generate README badges from your stats:
  ```
  ![Commit Streak](https://gitpulse.io/badge/streak/deepusharma)
  ![PRs This Month](https://gitpulse.io/badge/prs/deepusharma)
  ![Health Score](https://gitpulse.io/badge/health/deepusharma/gitpulse)
  ```
- Shield.io-compatible format, embeddable anywhere
- *Priority: Medium — viral distribution through README badges. v1.0*

### 🎙 Sprint Retrospective Generator
- Broader than standup — covers a full 2-week sprint
- Sections: What went well / What didn't / What to improve / Action items
- Pull from 14 days of commits + PRs + issues + sprint board
- *Priority: High — distinct from daily standup, new use case. v0.9*

### 🖥 Presentation Mode
- `/present` route — full-screen standup card optimized for screen sharing
- Large fonts, dark background, no UI chrome
- Keyboard shortcuts: next section, copy, share
- *Priority: Low — nice polish. v1.0*

### 🔔 Smart Notifications
- Daily 9am browser notification (if enabled): "Your standup is ready — 7 commits since yesterday"
- Weekly email digest with insights summary (Sunday evening)
- PR staleness alert: "You have 3 PRs untouched for 5+ days"
- *Priority: Medium — drives daily habit formation. v1.0*

### 🔗 Shareable Links
- `/summary/:id` — public shareable link for a specific generated summary
- Optional password protection
- Read-only view with Open Graph preview for Slack/Twitter unfurls
- *Priority: Low — useful for sharing standups with manager. v1.1*

### 🤖 AI Recommendations
- "You haven't pushed to `main` in 8 days — are you blocked?"
- "Your PR review time is 3x slower than your personal average this week"
- "You've squashed 60% more bugs than features this sprint — is this a hotfix week?"
- Uses the history + insights data to generate proactive nudges
- *Priority: Medium — differentiating AI layer. v1.2*

### 📊 Comparison Mode
- Compare your stats this period vs last period (% change)
- Compare against your personal historical averages
- (Optional, with consent) Anonymous aggregate benchmarks: "You commit 2x more than the median solo dev"
- *Priority: Medium — powerful for self-improvement. v1.1*

---

## Part 8: Complete Priority Matrix

| Feature | User Value | Complexity | Target |
|---|---|---|---|
| **Private repo OAuth** | 🔴 Critical | Low–Med | v0.6 / Sprint 08 |
| **Slack delivery** | 🔴 Critical | Low | v0.6 / Sprint 08 |
| **PR + Issue in summary** | 🔴 Critical | Medium | v0.9 / Sprint 14 |
| **`/insights` dashboard** | 🔴 Critical | Medium | v0.9 / Sprint 14 |
| **Team standup view** | 🔴 Critical | Medium | v1.0 / Sprint 15 |
| **Rich CLI help** | 🟠 High | Low | v0.7 / Sprint 09 |
| **Tone/language/length** | 🟠 High | Low | v0.6 / Sprint 08 |
| **GitHub Projects integration** | 🟠 High | Medium | v0.9 / Sprint 14 |
| **Stats for nerds** | 🟠 High | Medium | v0.9 / Sprint 14 |
| **Sprint retrospective generator** | 🟠 High | Medium | v0.9 / Sprint 14 |
| **Repo metadata (stars/forks/CI)** | 🟠 High | Low | v0.9 / Sprint 14 |
| **Traffic insights** | 🟠 High | Low | v0.9 / Sprint 14 |
| **MCP server** | 🟠 High | Medium | v1.2 / Sprint 17 |
| **In-app docs hub** | 🟡 Medium | Low–Med | v0.8 / Sprint 11 |
| **Badge generator** | 🟡 Medium | Low | v1.0 / Sprint 15 |
| **GitHub Gist delivery** | 🟡 Medium | Low | v0.6 / Sprint 08 |
| **Smart notifications** | 🟡 Medium | Medium | v1.0 |
| **AI recommendations** | 🟡 Medium | Medium | v1.2 |
| **Comparison mode** | 🟡 Medium | Medium | v1.1 |
| **Shareable links** | 🟡 Medium | Low | v1.1 |
| **Presentation mode** | 🟢 Low–Med | Low | v1.0 |
| **Gamification/streaks** | 🟢 Low | Low | v1.3 |
| **GitLab adapter** | ❌ Drop | Disproportionate complexity vs user value. CLI already works with local GitLab repos via GitPython. Web UI stays GitHub-only. |
| **Bitbucket** | ❌ Never | Declining market share, not worth the maintenance cost |
| **Azure DevOps** | ❌ Never | Completely different paradigm, enterprise-only |
| **VS Code extension** | 🟡 Medium | High | v1.3 |

---

## Part 9: Final Revised Milestone Plan

| Milestone | Theme | Key Additions |
|---|---|---|
| **v0.5** 🔄 | History & Analytics | DB, history, analytics dashboard, UX fixes |
| **v0.6** 📋 | Integrations + Private | Email, Slack, Gist, private repos, tone/language/mode |
| **v0.7** 📋 | Packaging & DX | PyPI, `gitpulse init`, rich CLI help, shell completion |
| **v0.8** 📋 | Open Source Ready | README, MkDocs, in-app `/docs` hub, changelog |
| **v0.9** 🆕 | Depth & Intelligence | PR/issue in summary, `/insights` dashboard, stats for nerds, GitHub Projects, repo metadata, retro generator, traffic insights |
| **v1.0** 🆕 | Team & Reach | Team standup, Slack channels, badge generator, presentation mode, smart notifications |
| **v1.1** 🆕 | Platform Expansion | Private orgs, shareable links, comparison mode |
| **v1.2** 🆕 | AI & MCP | MCP server (Claude/Cursor/Windsurf), AI recommendations, prompt templates |
| **v1.3** 🆕 | Delight | Year in review, gamification, streaks, VS Code extension |

---

## Part 10: UX Refinements (Latest Additions)

### 10a: Hover Tooltips on Metric Cards

When the `/insights` dashboard shows a metric card with a count (e.g. "12 PRs Merged"), hovering
should reveal the actual items — not just a number.

**Design rules:**
- **PRs Merged card** → popover list of PR titles, each a clickable GitHub link, with merge date and target branch
- **Issues Closed card** → popover list of issue titles, label badge (bug/feature/chore), close date, and link
- **Commits card** → too many to list individually; hover shows a **breakdown by repo** instead
  (e.g. `gitpulse: 23  dotfiles: 8  blog: 4`) — clicking a repo drills into its commit list
- **Active Repos card** → hover shows the repo names as a quick list

**Popover cap:** Show max 8 items, then a `+3 more →` link to the full GitHub list. Keeps the popover
clean without hiding data.

**Data implication:** The `/insights` API must return the PR/issue *list* (not just counts) so the
frontend can populate the popover without a second API call. This is a schema consideration for
Sprint 14 API design.

**Tooltip UX pattern:**
```
┌─ PRs Merged — 12 ───────────────────────────────┐
│ ✅ feat: add /history page          #132  Mar 31 │
│ ✅ fix: asyncpg missing in Railway  #134  Apr 01 │
│ ✅ docs: sprint 07 complete         #133  Apr 01 │
│ ✅ chore: PRD formatting            #144  Apr 01 │
│ ✅ docs: extend PRD v0.9–v1.3       #145  Apr 01 │
│                              +7 more on GitHub → │
└──────────────────────────────────────────────────┘
```

**Priority: Medium — high UX impact, data design decision needed early. Sprint 14.**

---

### 10b: CLI Help — Clarified Design

The goal: when a user types `gitpulse --help` (or just `gitpulse` with no arguments), they
immediately see what commands exist and how to use them — without reading docs.

**Two levels of help:**

**Level 1 — `gitpulse` (no args) or `gitpulse --help`:**
Shows a brief, scannable overview. Commands first, options second, examples third.
```
 gitpulse — Your weekly standup, done.

 Usage:  gitpulse <command> [options]

 Commands:
   run       Generate a standup summary (default)
   insights  Developer analytics in terminal
   history   List your past summaries
   init      Interactive setup wizard
   config    View / edit ~/.gitpulse.toml

 Quick start:
   gitpulse run                        # defaults from config
   gitpulse run --days 14              # last 2 weeks
   gitpulse run --tone casual          # casual tone
   gitpulse insights --days 30         # analytics view

 Run 'gitpulse <command> --help' for more options.
 Docs: https://gitpulse.io/docs/cli
```

**Level 2 — `gitpulse run --help`:**
Shows the full options list for that specific subcommand only, keeping each help page focused.

**Key UX decisions:**
- `gitpulse` with no args → show Level 1 help (friendlier for new users than silently running with defaults)
- `gitpulse run` with no args → run with defaults (power user shortcut)
- Keep Level 1 short enough to fit in one terminal screen without scrolling
- `rich` adds colour (green for commands, dimmed for defaults) but the *structure* is the real value
- Typer natively supports custom help groups and rich formatting — minimal implementation effort

**Additional related CLI improvements:**
- Progress indicator during generation: `Generating summary... ████████░░ 80%`
- Colour-coded output: green for new commits, blue for PRs, yellow for issues
- Shell completion: `gitpulse --install-completion zsh` (Typer built-in, one line to enable)

**Priority: High within v0.7 — polish that makes first impressions count.**

---

> **Status: Brainstorm complete — ready for PRD update and GitHub issue creation on your go-ahead.**
> No changes have been made to the PRD or any code files.
