---
title: Product Requirements Document
description: gitpulse living PRD
status: Living Document
milestone: v1.3.0
---

# Product Requirements Document — gitpulse

## 1. Problem Statement & Vision

Developers often struggle to accurately recall exactly what they worked on during daily or weekly standup updates. Manually reading through git logs across multiple repositories is tedious and unformatted. `gitpulse` solves this by automating the retrieval of git commit histories and generating well-structured, professional, AI-powered standup summaries.

The vision is to maintain a multi-client tool that exposes this functionality anywhere: as a fast, offline-capable CLI tool reading local `.git` folders, and as an accessible Web UI analyzing public remote repositories dynamically via GitHub's API.

---

## 2. Goals

- Provide a fast, functional CLI tool to generate markdown standup summaries.
- Deliver an accessible web interface that generates these summaries without local CLI installation.
- Retrieve commit history seamlessly—either via local git iterations or remote GitHub public API integration.
- Leverage LLM text-generation capabilities via Groq API (`llama-3.3-70b-versatile`) to interpret structured commit history into human-readable narratives.
- Support multi-repo configurations easily via cross-platform methodologies (like `~/.gitpulse.toml`).
- Keep the CLI fully functional; the web interface acts as an additional client rather than a replacement.
- Host the backend and frontend sustainably on scalable free-tier infrastructure.
- Deliver a robust authenticated web experience utilizing user GitHub OAuth sessions for polished visual layouts.

---

## 3. Non-Goals / Out of Scope

- Private GitHub repository analysis (Targeted for later iterations, currently out of scope for early releases).
- Dedicated Mobile app / mobile optimization explicitly outside of responsive web standards.
- Real-time updates, webhooks, or bidirectional repository syncing.

---

## 4. Users / Personas

| Persona                    | Description                                                                              |
| -------------------------- | ---------------------------------------------------------------------------------------- |
| **Solo Developer**         | Primary user — Wants a quick standup summary synthesized from browser or local terminal. |
| **Team Lead / Manager**    | Secondary user — Wants concise readouts tracking what individual team members completed. |
| **Evaluator / Enthusiast** | Evaluating `gitpulse` via the web UI without performing a comprehensive local setup.     |

---

## 5. Releases

| Milestone | Description                                                                                         | Status         |
| --------- | --------------------------------------------------------------------------------------------------- | -------------- |
| **v0.1**  | Core CLI — Base Python application fetching local git logs and summarizing locally.               | ✅ Complete    |
| **v0.2**  | Web UI — Next.js frontend and FastAPI backend interacting via GitHub’s API.                   | ✅ Complete    |
| **v0.3**  | UI Polish — Styling overhauls, Markdown formats, layouts, NextAuth setups.                       | ✅ Complete    |
| **v0.4**  | Config & Scheduling — CLI configuration defaults, dry-run flags, and frontend improvements.       | ✅ Complete    |
| **v0.5**  | History & Analytics — PostgreSQL persistence, history page, analytics dashboard, UX improvements. | 🔄 In Progress |
| **v0.6**  | Integrations — Email, Slack, Gist delivery; private repo support; tone/language/mode selection.   | 📋 Planned     |
| **v0.7**  | Packaging & DX — PyPI distribution, `gitpulse init`, rich CLI help, shell completion.            | 📋 Planned     |
| **v0.8**  | Open Source Ready — README, MkDocs, in-app docs hub, changelog page.                            | 📋 Planned     |
| **v0.9**  | Depth & Intelligence — PR/issue activity, `/insights` dashboard, stats for nerds, GitHub Projects, repo metadata, retro generator. | 📋 Planned |
| **v1.0**  | Team & Reach — Team standup view, badge generator, presentation mode, smart notifications.       | 📋 Planned     |
| **v1.1**  | Pro Features — Private org repos, shareable summary links, comparison mode.                      | 📋 Planned     |
| **v1.2**  | AI & MCP — MCP server for Claude/Cursor/Windsurf, AI recommendations, prompt templates.          | 📋 Planned     |
| **v1.3**  | Delight — Year in review, gamification, streaks, VS Code extension.                              | 📋 Planned     |

---

## 6. Sprint Roadmap

| Sprint | Status | Milestone | Epic | Theme |
| ------ | ------ | --------- | ---- | ----- |
| Sprint 01 | ✅ Done | v0.1 | Epic #126 | Core CLI base application |
| Sprint 02 | ✅ Done | v0.2 | Epic #15, #16 | Codebase restructure + GitHub API adapter |
| Sprint 03 | ✅ Done | v0.2 | Epic #17, #18 | FastAPI backend + Next.js frontend |
| Sprint 04 | ✅ Done | v0.3 | Epic (Web Polish) | UI polish, GitHub OAuth, markdown rendering |
| Sprint 05 | ✅ Done | v0.4 | Epic #112 | CLI config defaults, `--dry-run`, error messages |
| Sprint 06 | ✅ Done | v0.4 | Epic #113 | Copy to clipboard, empty/error states, stats footer |
| Sprint 07 | ✅ Done | v0.5 | Epic #114 | DB persistence, `/history` page, `GET /history` |
| Sprint 08 | 📋 Planned | v0.6 | Epic #115 | Email + Slack + Gist delivery, private repos, tone/language |
| Sprint 09 | 📋 Planned | v0.7 | Epic #116 | PyPI packaging, `gitpulse init`, rich CLI help |
| Sprint 10 | ✅ Done | v0.5 | Epic #117 | Analytics dashboard (Recharts charts) |
| Sprint 11 | 📋 Planned | v0.8 | Epic #118 | README, MkDocs, in-app `/docs` hub |
| Sprint 12 | 📋 Planned | v0.5 | Epic #136 | UX fixes: error messages, repo dropdown, history filters, export, caching |
| Sprint 14 | 🆕 New | v0.9 | TBD | `/insights` dashboard, PR/issue enrichment, stats for nerds, GitHub Projects |
| Sprint 15 | 🆕 New | v1.0 | TBD | Team standup, badge generator, presentation mode, notifications |
| Sprint 16 | 🆕 New | v1.1 | TBD | Private org repos, shareable links, comparison mode |
| Sprint 17 | 🆕 New | v1.2 | TBD | MCP server (Claude/Cursor/Windsurf), AI recommendations |
| Sprint 18 | 🆕 New | v1.3 | TBD | Streaks, year in review, VS Code extension |

> Sprint 13 is a buffer/overflow slot between v0.6 and v0.9.

---

## 7. Epics & User Stories

### v0.1 — Core CLI (Milestone #11) ✅

**Epic: Core CLI Base Application (Epic #126) ✅**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Read repositories from `~/.gitpulse.toml` configuration. | S0.1 | #127 | Sprint 01 |
| Parse local git commits using GitPython libraries. | S0.2 | #128 | Sprint 01 |
| Map chronological commits to concise Groq AI logic prompts. | S0.3 | #129 | Sprint 01 |
| Expose CLI parameters (`--days`, `--repo`, `--debug`, `--output`). | S0.4 | #130 | Sprint 01 |
| Output to a cleanly formatted Markdown report file manually. | S0.5 | #131 | Sprint 01 |

### v0.2 — Web UI & API Additions (Milestone #1) ✅

**Epic: Codebase Restructure (Epic #15) ✅**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Move shared API parsing logic to `core/`. | S1.1 | #19 | Sprint 02 |
| Relocate CLI execution to `cli/`. | S1.2 | #20 | Sprint 02 |
| Remap imports and update dependent tests natively. | S1.3 | #21 | Sprint 02 |
| Direct CI to run checks across modular directories. | S1.4 | #22 | Sprint 02 |
| Formalize `AGENTS.md` system guidelines and repository skill files. | S1.5 | #23 | Sprint 02 |

**Epic: GitHub API Adapter (Epic #16) ✅**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Provision a specialized GitHub API adapter in `core/repo_reader.py`. | S2.1 | #24 | Sprint 02 |
| Introduce `source` parameter targeting either `local` or `github`. | S2.2 | #25 | Sprint 02 |
| Transmit GitHub username and multiple repository identifiers safely. | S2.3 | #26 | Sprint 02 |
| Institute tests evaluating API response parsing metrics. | S2.4 | #27 | Sprint 02 |
| Trap and degrade gracefully on external API threshold limitations. | S2.5 | #28 | Sprint 02 |

**Epic: FastAPI Backend (Epic #17) ✅**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Scaffold a lightweight FastAPI root container within `api/`. | S3.1 | #29 | Sprint 03 |
| Deploy specialized `POST /summarise` inference endpoint. | S3.2 | #30 | Sprint 03 |
| Inject `core/` functions directly into backend inference chains. | S3.3 | #31 | Sprint 03 |
| Allow domain-independent CORS connections prioritizing the Web UI. | S3.4 | #32 | Sprint 03 |
| Validate requests cleanly mapping Pydantic schemas. | S3.5 | #33 | Sprint 03 |
| Finalize API containerized test boundaries. | S3.6 | #34 | Sprint 03 |
| Orchestrate deployment structures pointing to Railway servers. | S3.7 | #35 | Sprint 03 |

**Epic: Next.js Frontend (Epic #18) ✅**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Scaffold Next.js 14 utilizing TypeScript and Tailwind CSS contexts. | S4.1 | #36 | Sprint 03 |
| Expose web form to input constraints (usernames, repositories, etc). | S4.2 | #37 | Sprint 03 |
| Consume backend summarization logic tracking REST responses. | S4.3 | #38 | Sprint 03 |
| Display parsed markdown structures effectively utilizing React. | S4.4 | #39 | Sprint 03 |
| Animate skeletons visualizing backend generation progress locally. | S4.5 | #40 | Sprint 03 |
| Surface readable constraints explicitly when an active request drops. | S4.6 | #41 | Sprint 03 |
| Direct deployments natively utilizing existing Vercel resources. | S4.7 | #42 | Sprint 03 |

### v0.3 — UI Polish (Milestone #5) ✅

**Epic: Web Component Polish & OAuth ✅**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| GitHub OAuth login with NextAuth.js. | SP4.1 | #65 | Sprint 04 |
| Apply permanent global generic structural components (Headers/Footers). | SP4.2 | #66 | Sprint 04 |
| Execute markdown typographical casting cleanly overriding standards. | SP4.3 | #67 | Sprint 04 |
| Refine form and results column layout responding to variable sizing. | SP4.4 | #68 | Sprint 04 |
| Fix layout transitions — form to drawer. | SP4.5 | #75 | Sprint 04 |
| Fix commit breakdown markdown rendering. | SP4.6 | #76 | Sprint 04 |
| Implement collapsible/expandable result sections. | SP4.7 | #77 | Sprint 04 |

### v0.4 — Config & Scheduling (Milestone #6) ✅

**Epic: CLI Configuration Defaults (Epic #112) ✅**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Add `--dry-run` flag to CLI to show commits without LLM calls. | S5.1 | #86 | Sprint 05 |
| Add `[defaults]` section to `~/.gitpulse.toml` configuration. | S5.2 | #87 | Sprint 05 |
| Improve CLI error messages for faster debugging. | S5.3 | #88 | Sprint 05 |
| Add automated tests for config defaults and dry-run flag. | S5.4 | #89 | Sprint 05 |

**Epic: Web UI States & Details (Epic #113) ✅**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Add copy to clipboard button to generated summaries. | S6.1 | #90 | Sprint 06 |
| Improve empty and error UI states for better user feedback. | S6.2 | #91 | Sprint 06 |
| Display word count and generation stats after completion. | S6.3 | #92 | Sprint 06 |

### v0.5 — History & Analytics (Milestone #7) 🔄

**Epic: Summary History Integration (Epic #114) ✅**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Set up Neon PostgreSQL schema for `summaries`. | S7.1 | #93 | Sprint 07 |
| Save summary payloads to DB asynchronously after generation. | S7.2 | #94 | Sprint 07 |
| Introduce `GET /history` API endpoint supporting robust filtering. | S7.3 | #95 | Sprint 07 |
| Build web UI `/history` page listing all past summaries. | S7.4 | #96 | Sprint 07 |
| Author tests evaluating database API endpoints properly. | S7.5 | #97 | Sprint 07 |

**Epic: Analytics Dashboard (Epic #117) ✅**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Implement commit frequency bar chart metrics via `recharts`. | S10.1 | #105 | Sprint 10 ✅ |
| Construct repo activity breakdown pie charts. | S10.2 | #106 | Sprint 10 ✅ |
| Calculate and display aggregate productivity insights. | S10.3 | #107 | Sprint 10 ✅ |

**Epic: Enhanced Input UX & Error Feedback (Epic #136) 📋**

| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Fix wrong repo name returning generic error — surface repo-specific 404 message. | S12.1 | #137 | Sprint 12 |
| Validate GitHub username live against GitHub API with visual feedback. | S12.2 | #138 | Sprint 12 |
| Show searchable repo multiselect dropdown fetched from GitHub API after username validates. | S12.3 | #139 | Sprint 12 |
| Add commit activity stats footer matching the summary stats panel. | S12.4 | #140 | Sprint 12 |
| Add search and date-range filter controls to the `/history` page. | S12.5 | #141 | Sprint 12 |
| Export standup summary as a downloadable `.md` file. | S12.6 | #142 | Sprint 12 |
| Fix days input field to accept direct keyboard entry without leading zero bug. | S12.7 | #208 | Sprint 12 |

**Epic: Performance & Caching (Epic TBD) 📋**

| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Cache repo list and commit data server-side (TTL: 5 min) to avoid repeated GitHub API calls. | S12.8 | #209 | Sprint 12 |
| Add a "🔄 Refresh" button on Dashboard and Summary Generator to force a fresh data pull. | S12.9 | #209 | Sprint 12 |
| Cache full analytics payload `(username, days)` server-side for sub-second dashboard reloads. | S12.10 | #211 | Sprint 12 |
| Show last-updated timestamp on Dashboard so users know data freshness. | S12.11 | #211 | Sprint 12 |
| Persist every generated summary to history; show non-blocking toast warning if DB save fails. | S12.12 | #210 | Sprint 12 |

### v0.6 — Integrations (Milestone #8) 📋

**Epic: Email Delivery Automation (Epic #115) 📋**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Set up Resend account integration locally and configure API keys. | S8.1 | #98 | Sprint 08 |
| Append optional email parameter to `POST /summarise`. | S8.2 | #99 | Sprint 08 |
| Implement email notification toggle directly within the web UI. | S8.3 | #100 | Sprint 08 |
| Configure GitHub Actions cron to distribute weekly summaries. | S8.4 | #101 | Sprint 08 |

### v0.7 — Packaging & DX (Milestone #9) 📋

**Epic: Standard PIP Distribution (Epic #116) 📋**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Refactor project structure enabling standard `pip install gitpulse`. | S9.1 | #102 | Sprint 09 |
| Orchestrate PyPI publishing triggered sequentially via CI. | S9.2 | #103 | Sprint 09 |
| Develop an interactive `gitpulse init` command standardizing onboarding. | S9.3 | #104 | Sprint 09 |

### v0.8 — Open Source Ready (Milestone #10) 📋

**Epic: OSS Documentation & Releases (Epic #118) 📋**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Rewrite `README.md` introducing demo GIFs, architectures, and badges. | S11.1 | #108 | Sprint 11 |
| Provide `CONTRIBUTING.md`, Code of Conduct, and PR templates. | S11.2 | #109 | Sprint 11 |
| Scaffold and deploy MkDocs static site linked to GitHub Pages. | S11.3 | #110 | Sprint 11 |
| Streamline semantic release workflow automating changelogs. | S11.4 | #111 | Sprint 11 |

---

### v0.9 — Depth & Intelligence (Milestone TBD) 🆕

**Epic: PR & Issue Activity Enrichment 🆕**

| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Include PR activity (opened/merged/reviewed) in standup summary. | S14.1 | TBD | Sprint 14 |
| Include issue activity (opened/closed) in standup summary. | S14.2 | TBD | Sprint 14 |
| Add GitHub Projects sprint card activity to summary. | S14.3 | TBD | Sprint 14 |
| Generate AI-powered sprint retrospective (2-week scope). | S14.4 | TBD | Sprint 14 |

**Epic: Developer Insights Dashboard (`/insights`) 🆕**

| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Build `/insights` page with metric cards (commits, PRs, issues, active repos). | S14.5 | TBD | Sprint 14 |
| Add commit frequency bar chart, PR velocity line chart, issue health area chart. | S14.6 | TBD | Sprint 14 |
| Add language breakdown donut chart and tech stack badge detection. | S14.7 | TBD | Sprint 14 |
| Add repo metadata panel (stars, forks, watchers, CI pass rate, traffic). | S14.8 | TBD | Sprint 14 |
| Add repo health score algorithm and display. | S14.9 | TBD | Sprint 14 |
| Add "Stats for Nerds" panel (avg PR cycle time, commit patterns, code churn). | S14.10 | TBD | Sprint 14 |
| Add date range and repo filters to `/insights`. | S14.11 | TBD | Sprint 14 |

---

### v1.0 — Team & Reach (Milestone TBD) 🆕

**Epic: Team Standup View 🆕**

| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Add multi-username input to generate aggregated team standup. | S15.1 | TBD | Sprint 15 |
| Build team roster management (save/load team member lists). | S15.2 | TBD | Sprint 15 |
| Add team delivery to Slack channel (vs personal DM). | S15.3 | TBD | Sprint 15 |

**Epic: Reach & Engagement 🆕**

| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Add README badge generator for commit streak, PR count, health score. | S15.4 | TBD | Sprint 15 |
| Add presentation mode (`/present`) for screen-share standups. | S15.5 | TBD | Sprint 15 |
| Add smart browser/email notifications for daily standup reminders. | S15.6 | TBD | Sprint 15 |

---

### v1.1 — Pro Features (Milestone TBD) 🆕

**Epic: Private & Org Access 🆕**

| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Support private org repos via expanded OAuth scope. | S16.1 | TBD | Sprint 16 |
| Add shareable public links for generated summaries (`/summary/:id`). | S16.2 | TBD | Sprint 16 |
| Add comparison mode — this period vs last period vs personal averages. | S16.3 | TBD | Sprint 16 |

---

### v1.2 — AI & MCP (Milestone TBD) 🆕

**Epic: MCP Server & IDE Integration 🆕**

| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Build `mcp/server.py` exposing gitpulse core as MCP Tools. | S17.1 | TBD | Sprint 17 |
| Expose `generate_standup`, `get_history`, `analyze_repo`, `get_insights` as MCP tools. | S17.2 | TBD | Sprint 17 |
| Publish MCP server alongside PyPI package. | S17.3 | TBD | Sprint 17 |
| Expose remote MCP server over HTTP/SSE from FastAPI backend. | S17.4 | TBD | Sprint 17 |
| Document MCP setup for Claude Code, Cursor, Windsurf in `/docs/mcp`. | S17.5 | TBD | Sprint 17 |

**Epic: AI Customization 🆕**

| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Add AI-powered proactive recommendations based on insights data. | S17.6 | TBD | Sprint 17 |
| Add saved prompt templates per project/team. | S17.7 | TBD | Sprint 17 |

---

### v1.3 — Delight (Milestone TBD) 🆕

**Epic: Gamification & Extensions 🆕**

| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Add commit streak tracking and personal best records. | S18.1 | TBD | Sprint 18 |
| Generate annual "Year in Review" summary from history data. | S18.2 | TBD | Sprint 18 |
| Build VS Code extension surfacing standup and insights in sidebar. | S18.3 | TBD | Sprint 18 |

---

## 8. Technical Decisions

| Decision            | Choice                                                 | Reason                                                                         |
| ------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------ |
| **Language Base**   | Python 3.12+ (Backend) & TypeScript (Frontend)         | Unifies scripting standards alongside modernized Web stability protocols.      |
| **Package Builder** | `uv`                                                   | Accelerates internal environment configurations implicitly lowering latencies. |
| **Git Adapters**    | `GitPython` & GitHub API                               | Separates localized executions from scalable lightweight remote endpoints.     |
| **Backend API**     | `FastAPI`                                              | Exposes asynchronous standard Python schemas minimizing deployment overhead.   |
| **Generative LLM**  | Groq (`llama-3.3-70b-versatile`)                       | Affords best-in-class reaction throughput paired with rigid contextual AI.     |
| **Frontend Node**   | Next.js App Router                                     | Extends React rendering boundaries securely integrating functional UIs.        |
| **Styling**         | Tailwind CSS + `shadcn/ui` + `@tailwindcss/typography` | Maximizes visual consistency effortlessly over rigid semantic CSS scopes.      |
| **Cloud Hosting**   | Vercel & Railway                                       | Free, responsive tiers orchestrating decoupled client-server structures.       |

---

## 9. Success Criteria

- Complete generation of multi-repository summary payloads reliably executing in under 30 seconds.
- Native capabilities exposed natively to terminal systems remaining largely uninterrupted.
- Successful authentication of Github-native clients yielding extended web bounds seamlessly via OAuth.
- Standardized markdown formats encompassing exactly four structural elements (`WHAT I DID`, `DETAILS`, `WHATS NEXT`, `BLOCKERS`) consistently.
- Fully operational CI/CD pipelines assuring passing tests continuously.
