---
title: Product Requirements Document
description: gitpulse living PRD
status: Living Document
milestone: v0.8.0
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

| Milestone | Description | Status |
| --------- | ----------- | ------ |
| **v0.1** | Core CLI — Base Python application fetching local git logs and summarizing locally. | ✅ Complete |
| **v0.2** | Web UI — Next.js frontend and FastAPI backend interacting via GitHub's API. | ✅ Complete |
| **v0.3** | UI Polish — Styling overhauls, Markdown formats, layouts, NexthAuth setups. | ✅ Complete |
| **v0.4** | Config & Scheduling — CLI configuration defaults, dry-run flags, and frontend improvements. | ✅ Complete |
| **v0.5** | History & Analytics — PostgreSQL Database persistence and dashboard aggregations. | 🔄 In Progress |
| **v0.6** | Integrations — Resend email delivery notifications and repository webhooks. | 📋 Planned |
| **v0.7** | Packaging & DX — Executable distribution on PyPI and interactive CLI onboarding. | 📋 Planned |
| **v0.8** | Open Source Ready — Comprehensive README structures, doc sites, and automated releases. | 📋 Planned |

---

## 6. Epics & User Stories

### v0.1 — Core CLI (Milestone #11)

**Epic: Core CLI Base Application (Epic #126)**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Read repositories from `~/.gitpulse.toml` configuration. | S0.1 | #127 | Sprint 01 |
| Parse local git commits using GitPython libraries. | S0.2 | #128 | Sprint 01 |
| Map chronological commits to concise Groq AI logic prompts. | S0.3 | #129 | Sprint 01 |
| Expose CLI parameters (`--days`, `--repo`, `--debug`, `--output`). | S0.4 | #130 | Sprint 01 |
| Output to a cleanly formatted Markdown report file manually. | S0.5 | #131 | Sprint 01 |

### v0.2 — Web UI & API Additions (Milestone #1)

**Epic: Codebase Restructure (Epic #15)**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Move shared API parsing logic to `core/`. | S1.1 | #19 | Sprint 02 |
| Relocate CLI execution to `cli/`. | S1.2 | #20 | Sprint 02 |
| Remap imports and update dependent tests natively. | S1.3 | #21 | Sprint 02 |
| Direct CI to run checks across modular directories. | S1.4 | #22 | Sprint 02 |
| Formalize `AGENTS.md` system guidelines and repository skill files. | S1.5 | #23 | Sprint 02 |

**Epic: GitHub API Adapter (Epic #16)**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Provision a specialized GitHub API adapter in `core/repo_reader.py`. | S2.1 | #24 | Sprint 02 |
| Introduce `source` parameter targeting either `local` or `github`. | S2.2 | #25 | Sprint 02 |
| Transmit GitHub username and multiple repository identifiers safely. | S2.3 | #26 | Sprint 02 |
| Institute tests evaluating API response parsing metrics. | S2.4 | #27 | Sprint 02 |
| Trap and degrade gracefully on external API threshold limitations. | S2.5 | #28 | Sprint 02 |

**Epic: FastAPI Backend (Epic #17)**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Scaffold a lightweight FastAPI root container within `api/`. | S3.1 | #29 | Sprint 03 |
| Deploy specialized `POST /summarise` inference endpoint. | S3.2 | #30 | Sprint 03 |
| Inject `core/` functions directly into backend inference chains. | S3.3 | #31 | Sprint 03 |
| Allow domain-independent CORS connections prioritizing the Web UI. | S3.4 | #32 | Sprint 03 |
| Validate requests cleanly mapping Pydantic schemas. | S3.5 | #33 | Sprint 03 |
| Finalize API containerized test boundaries. | S3.6 | #34 | Sprint 03 |
| Orchestrate deployment structures pointing to Railway servers. | S3.7 | #35 | Sprint 03 |

**Epic: Next.js Frontend (Epic #18)**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Scaffold Next.js 14 utilizing TypeScript and Tailwind CSS contexts. | S4.1 | #36 | Sprint 03 |
| Expose web form to input constraints (usernames, repositories, etc). | S4.2 | #37 | Sprint 03 |
| Consume backend summarization logic tracking REST responses. | S4.3 | #38 | Sprint 03 |
| Display parsed markdown structures effectively utilizing React. | S4.4 | #39 | Sprint 03 |
| Animate skeletons visualizing backend generation progress locally. | S4.5 | #40 | Sprint 03 |
| Surface readable constraints explicitly when an active request drops. | S4.6 | #41 | Sprint 03 |
| Direct deployments natively utilizing existing Vercel resources. | S4.7 | #42 | Sprint 03 |

### v0.3 — UI Polish (Milestone #5)

**Epic: Web Component Polish & OAuth**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| GitHub OAuth login with NextAuth.js. | SP4.1 | #65 | Sprint 04 |
| Apply permanent global generic structural components (Headers/Footers). | SP4.2 | #66 | Sprint 04 |
| Execute markdown typographical casting cleanly overriding standards. | SP4.3 | #67 | Sprint 04 |
| Refine form and results column layout responding to variable sizing. | SP4.4 | #68 | Sprint 04 |
| Fix layout transitions — form to drawer. | SP4.5 | #75 | Sprint 04 |
| Fix commit breakdown markdown rendering. | SP4.6 | #76 | Sprint 04 |
| Implement collapsible/expandable result sections. | SP4.7 | #77 | Sprint 04 |

### v0.4 — Config & Scheduling (Milestone #6)

**Epic: CLI Configuration Defaults (Epic #112)**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Add `--dry-run` flag to CLI to show commits without LLM calls. | S5.1 | #86 | Sprint 05 |
| Add `[defaults]` section to `~/.gitpulse.toml` configuration. | S5.2 | #87 | Sprint 05 |
| Improve CLI error messages for faster debugging. | S5.3 | #88 | Sprint 05 |
| Add automated tests for config defaults and dry-run flag. | S5.4 | #89 | Sprint 05 |

**Epic: Web UI States & Details (Epic #113)**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Add copy to clipboard button to generated summaries. | S6.1 | #90 | Sprint 06 |
| Improve empty and error UI states for better user feedback. | S6.2 | #91 | Sprint 06 |
| Display word count and generation stats after completion. | S6.3 | #92 | Sprint 06 |

### v0.5 — History & Analytics (Milestone #7)

**Epic: Summary History Integration (Epic #114)**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Set up Neon PostgreSQL schema for `summaries`. | S7.1 | #93 | Sprint 07 |
| Save summary payloads to DB asynchronously after generation. | S7.2 | #94 | Sprint 07 |
| Introduce `GET /history` API endpoint supporting robust filtering. | S7.3 | #95 | Sprint 07 |
| Build web UI `/history` page listing all past summaries. | S7.4 | #96 | Sprint 07 |
| Author tests evaluating database API endpoints properly. | S7.5 | #97 | Sprint 07 |

**Epic: Analytics Dashboard (Epic #117)**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Implement commit frequency bar chart metrics via `recharts`. | S10.1 | #105 | Sprint 10 |
| Construct repo activity breakdown pie charts. | S10.2 | #106 | Sprint 10 |
| Calculate and display aggregate productivity insights. | S10.3 | #107 | Sprint 10 |

### v0.6 — Integrations (Milestone #8)

**Epic: Email Delivery Automation (Epic #115)**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Set up Resend account integration locally and configure API keys. | S8.1 | #98 | Sprint 08 |
| Append optional email parameter to `POST /summarise`. | S8.2 | #99 | Sprint 08 |
| Implement email notification toggle directly within the web UI. | S8.3 | #100 | Sprint 08 |
| Configure GitHub Actions cron to distribute weekly summaries. | S8.4 | #101 | Sprint 08 |

### v0.7 — Packaging & DX (Milestone #9)

**Epic: Standard PIP Distribution (Epic #116)**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Refactor project structure enabling standard `pip install gitpulse`. | S9.1 | #102 | Sprint 09 |
| Orchestrate PyPI publishing triggered sequentially via CI. | S9.2 | #103 | Sprint 09 |
| Develop an interactive `gitpulse init` command standardizing onboarding. | S9.3 | #104 | Sprint 09 |

### v0.8 — Open Source Ready (Milestone #10)

**Epic: OSS Documentation & Releases (Epic #118)**
| Story | Internal ID | GitHub Issue | Implemented In |
| ----- | ----------- | ------------ | -------------- |
| Rewrite `README.md` introducing demo GIFs, architectures, and badges. | S11.1 | #108 | Sprint 11 |
| Provide `CONTRIBUTING.md`, Code of Conduct, and PR templates. | S11.2 | #109 | Sprint 11 |
| Scaffold and deploy MkDocs static site linked to GitHub Pages. | S11.3 | #110 | Sprint 11 |
| Streamline semantic release workflow automating changelogs. | S11.4 | #111 | Sprint 11 |

---

## 7. Technical Decisions

| Decision            | Choice                                              | Reason                                                                       |
| ------------------- | --------------------------------------------------- | ---------------------------------------------------------------------------- |
| **Language Base**   | Python 3.12+ (Backend) & TypeScript (Frontend)      | Unifies scripting standards alongside modernized Web stability protocols.    |
| **Package Builder** | `uv`                                                | Accelerates internal environment configurations implicitly lowering latencies. |
| **Git Adapters**    | `GitPython` & GitHub API                            | Separates localized executions from scalable lightweight remote endpoints.   |
| **Backend API**     | `FastAPI`                                           | Exposes asynchronous standard Python schemas minimizing deployment overhead. |
| **Generative LLM**  | Groq (`llama-3.3-70b-versatile`)                    | Affords best-in-class reaction throughput paired with rigid contextual AI.   |
| **Frontend Node**   | Next.js App Router                                  | Extends React rendering boundaries securely integrating functional UIs.      |
| **Styling**         | Tailwind CSS + `shadcn/ui` + `@tailwindcss/typography` | Maximizes visual consistency effortlessly over rigid semantic CSS scopes.    |
| **Cloud Hosting**   | Vercel & Railway                                    | Free, responsive tiers orchestrating decoupled client-server structures.     |

---

## 8. Success Criteria

- Complete generation of multi-repository summary payloads reliably executing in under 30 seconds.
- Native capabilities exposed natively to terminal systems remaining largely uninterrupted.
- Successful authentication of Github-native clients yielding extended web bounds seamlessly via OAuth.
- Standardized markdown formats encompassing exactly four structural elements (`WHAT I DID`, `DETAILS`, `WHATS NEXT`, `BLOCKERS`) consistently.
- Fully operational CI/CD pipelines assuring passing tests continuously.
