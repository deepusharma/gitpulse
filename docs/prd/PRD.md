# Product Requirements Document — gitpulse

**Status:** Living Document  
**Milestone:** v0.8.0

---

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
- Persisting summaries to a structured database natively (Targeted for later versions/milestones).
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
| **v0.3** | UI Polish — Styling overhauls, Markdown format rendering, NextAuth setups. | ✅ Complete |
| **v0.4** | Config & Scheduling — CLI configuration defaults and frontend scheduled deliveries. | ✅ Complete |
| **v0.5** | History & Analytics — PostgreSQL Database persistence and dashboard aggregations. | 📋 Planned |
| **v0.6** | Integrations — Resend email delivery notifications and repository webhooks. | 📋 Planned |
| **v0.7** | Packaging & DX — Executable distribution on PyPI and improved Developer workflows. | 📋 Planned |
| **v0.8** | Open Source Ready — Comprehensive README structures, doc sites, and releases. | 📋 Planned |

---

## 6. Epics & User Stories

### v0.1 — Core CLI
| ID   | Story                                                               |
| ---- | ------------------------------------------------------------------- |
| S0.1 | Read repositories from `~/.gitpulse.toml` configuration.           |
| S0.2 | Parse local git commits using GitPython libraries.                  |
| S0.3 | Map chronological commits to concise Groq AI logic prompts.         |
| S0.4 | Expose CLI parameters (`--days`, `--repo`, `--debug`, `--output`). |
| S0.5 | Output to a cleanly formatted Markdown report file manually.        |

### v0.2 — Web UI & API Additions
**Epic 1 — Codebase Restructure**
| ID   | Story                                                               |
| ---- | ------------------------------------------------------------------- |
| S1.1 | Move shared API parsing logic to `core/`                            |
| S1.2 | Relocate CLI execution to `cli/`                                    |
| S1.3 | Remap imports and update dependent tests natively.                  |
| S1.4 | Direct CI to run checks across modular directories.                 |
| S1.5 | Formalize `AGENTS.md` system guidelines and repository skill files. |

**Epic 2 — GitHub API Adapter**
| ID   | Story                                                               |
| ---- | ------------------------------------------------------------------- |
| S2.1 | Provision a specialized GitHub API adapter in `core/repo_reader.py` |
| S2.2 | Introduce `source` parameter targeting either `local` or `github`.  |
| S2.3 | Transmit GitHub username and multiple repository identifiers safely.|
| S2.4 | Institute tests evaluating API response parsing metrics.            |
| S2.5 | Trap and degrade gracefully on external API threshold limitations.  |

**Epic 3 — FastAPI Backend**
| ID   | Story                                                               |
| ---- | ------------------------------------------------------------------- |
| S3.1 | Scaffold a lightweight FastAPI root container within `api/`.        |
| S3.2 | Deploy specialized `POST /summarise` inference endpoint.            |
| S3.3 | Inject `core/` functions directly into backend inference chains.    |
| S3.4 | Allow domain-independent CORS connections prioritizing the Web UI.  |
| S3.5 | Validate requests cleanly mapping Pydantic schemas.                 |
| S3.6 | Finalize API containerized test boundaries.                         |
| S3.7 | Orchestrate deployment structures pointing to Railway servers.      |

**Epic 4 — Next.js Frontend**
| ID   | Story                                                               |
| ---- | ------------------------------------------------------------------- |
| S4.1 | Scaffold Next.js 14 utilizing TypeScript and Tailwind CSS contexts. |
| S4.2 | Expose web form to input constraints (usernames, repositories, etc).|
| S4.3 | Consume backend summarization logic tracking REST responses.        |
| S4.4 | Display parsed markdown structures effectively utilizing React.     |
| S4.5 | Animate skeletons visualizing backend generation progress locally.   |
| S4.6 | Surface readable constraints explicitly when an active request drops |
| S4.7 | Direct deployments natively utilizing existing Vercel resources.    |

### v0.3 — UI Polish
| ID   | Story                                                               |
| ---- | ------------------------------------------------------------------- |
| #65  | Integrate robust user-level GitHub OAuth utilizing NextAuth.js.     |
| #66  | Apply permanent global generic structural components (Headers).     |
| #67  | Execute markdown typographical casting cleanly overriding standards.|
| #68  | Refine Results components responding explicitly to variable sizing. |

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
