# PRD — gitpulse Web UI

**Version:** 0.1  
**Status:** Draft  
**Author:** Deepak Sharma  
**Date:** 2026-03-21  
**Milestone:** v0.2 — Web UI

---

## 1. Problem Statement

gitpulse CLI generates useful standup summaries but requires terminal access and manual execution. A web interface would make it accessible from any browser, remove the need for local setup, and enable sharing summaries with others.

---

## 2. Goals

- Provide a web interface to generate standup summaries without CLI access
- Read commit history from public GitHub repos via GitHub API
- Generate AI summaries using Groq API
- Deploy on free tier infrastructure (Vercel + Railway)
- Keep CLI fully functional — web is an additional client, not a replacement

---

## 3. Non-Goals (v0.2)

- Private GitHub repo support (v0.3+)
- Authentication / user accounts
- Saving or storing summaries
- Mobile app
- Real-time updates / webhooks

---

## 4. Users

| User                       | Description                                             |
| -------------------------- | ------------------------------------------------------- |
| Solo developer             | Primary user — wants quick standup summary from browser |
| Team lead                  | Secondary — wants to see what their team worked on      |
| Anyone evaluating gitpulse | Wants to try it without installing anything             |

---

## 5. User Stories

### Epic 1 — Codebase Restructure

> As a developer, I want the codebase organised into core/cli/api/web so each concern is separate and maintainable.

| ID   | Story                                 | Priority |
| ---- | ------------------------------------- | -------- |
| S1.1 | Move shared logic to `core/`          | High     |
| S1.2 | Move CLI code to `cli/`               | High     |
| S1.3 | Update imports and tests              | High     |
| S1.4 | Update CI to run tests from new paths | High     |
| S1.5 | Create AGENTS.md and skill files      | Medium   |

### Epic 2 — GitHub API Adapter

> As a user, I want gitpulse to read commits from public GitHub repos so I don't need local repo access.

| ID   | Story                                           | Priority |
| ---- | ----------------------------------------------- | -------- |
| S2.1 | Add GitHub API adapter to `core/repo_reader.py` | High     |
| S2.2 | Support `source` parameter: `local` or `github` | High     |
| S2.3 | Accept GitHub username and repo list as input   | High     |
| S2.4 | Write tests for GitHub API adapter              | High     |
| S2.5 | Handle rate limiting and API errors gracefully  | Medium   |

### Epic 3 — FastAPI Backend

> As a frontend, I want a REST API that accepts repo details and returns a standup summary.

| ID   | Story                                                      | Priority |
| ---- | ---------------------------------------------------------- | -------- |
| S3.1 | Create FastAPI app skeleton in `api/`                      | High     |
| S3.2 | Implement `POST /summarise` endpoint                       | High     |
| S3.3 | Wire `core/repo_reader` and `core/summarise` into endpoint | High     |
| S3.4 | Add CORS support for frontend                              | High     |
| S3.5 | Add request validation with Pydantic                       | High     |
| S3.6 | Write tests for API endpoints                              | High     |
| S3.7 | Deploy to Railway                                          | High     |

### Epic 4 — Next.js Frontend

> As a user, I want a simple web interface where I enter my GitHub username and repos and get a summary.

| ID   | Story                                                | Priority |
| ---- | ---------------------------------------------------- | -------- |
| S4.1 | Scaffold Next.js 14 app with TypeScript and Tailwind | High     |
| S4.2 | Build input form (username, repos, days)             | High     |
| S4.3 | Connect form to FastAPI backend                      | High     |
| S4.4 | Display commit breakdown and summary                 | High     |
| S4.5 | Add loading state while summary generates            | High     |
| S4.6 | Add error handling for failed requests               | High     |
| S4.7 | Deploy to Vercel                                     | High     |

---

## 6. API Contract

### `POST /summarise`

**Request:**

```json
{
  "username": "deepusharma",
  "repos": ["gitpulse", "dotfiles"],
  "days": 7
}
```

**Response:**

```json
{
  "display": "### gitpulse\n  - a1b2c3d ...",
  "summary": "# WHAT I DID\n* ...",
  "repos": ["gitpulse", "dotfiles"],
  "days": 7,
  "generated_at": "2026-03-21T10:00:00Z"
}
```

**Errors:**

```json
{
  "error": "GitHub API rate limit exceeded",
  "code": 429
}
```

---

## 7. Technical Decisions

| Decision         | Choice                                         | Reason                                      |
| ---------------- | ---------------------------------------------- | ------------------------------------------- |
| Repo source      | GitHub API                                     | No local access needed on server            |
| Backend          | FastAPI                                        | Existing Python stack, fast, easy to deploy |
| Frontend         | Next.js 14 + TypeScript + Tailwind + shadcn/ui | Modern stack, deploys on Vercel             |
| Backend hosting  | Railway                                        | Free tier, Python support, simple deploys   |
| Frontend hosting | Vercel                                         | First-party Next.js support, free tier      |
| Auth             | None (v0.2)                                    | Public repos only, no user data stored      |

---

## 8. Success Criteria

- [ ] User can enter GitHub username and repo names in web UI
- [ ] Summary generates in under 30 seconds
- [ ] CLI continues to work unchanged
- [ ] All existing tests pass after restructure
- [ ] New tests cover GitHub API adapter and FastAPI endpoints
- [ ] App is live on Vercel + Railway

---

## 9. Out of Scope

- Private repos (v0.4 target)
- Persisting summaries
- Mobile optimisation
- *(Note: User accounts and authentication are now in scope for v0.3)*
