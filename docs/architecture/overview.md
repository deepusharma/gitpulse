# Architecture Overview — gitpulse

**Version:** 0.2  
**Status:** Draft  
**Author:** Deepak Sharma  
**Date:** 2026-03-22  
**Milestone:** v0.3 — UI Polisȟ

---

## 1. System Overview

gitpulse is a multi-client tool that reads git commit history and generates AI-powered standup summaries. It has two clients — a CLI for local use and a web interface for browser access — both sharing a common Python core library.

```
┌─────────────────────────────────────────────────────┐
│                    Clients                          │
│                                                     │
│   ┌─────────────┐          ┌─────────────────────┐  │
│   │   CLI       │          │   Web (Next.js)     │  │
│   │   cli.py    │          │   Vercel            │  │
│   └──────┬──────┘          └──────────┬──────────┘  │
│          │                            │             │
│          │                   ┌────────▼──────────┐  │
│          │                   │   API (FastAPI)   │  │
│          │                   │   Railway         │  │
│          │                   └────────┬──────────┘  │
│          │                            │             │
└──────────┼────────────────────────────┼─────────────┘
           │                            │
           ▼                            ▼
┌──────────────────────────────────────────────────────┐
│                  core/                               │
│                                                      │
│   repo_reader.py    summarise.py    utils.py         │
│                                                      │
└──────────────┬───────────────────┬───────────────────┘
               │                   │
               ▼                   ▼
      ┌─────────────────┐   ┌─────────────┐
      │   Data Sources  │   │  External   │
      │                 │   │  APIs       │
      │  Local Git      │   │             │
      │  GitHub API     │   │  Groq API   │
      └─────────────────┘   └─────────────┘
```

---

## 2. Component Breakdown

### `core/` — Shared Python Library

The heart of gitpulse. Contains all business logic. Imported by both CLI and API.

| Module           | Responsibility                             |
| ---------------- | ------------------------------------------ |
| `repo_reader.py` | Reads commits — local git or GitHub API    |
| `summarise.py`   | Formats commits, builds prompt, calls Groq |
| `utils.py`       | Loads .env, validates required keys        |

### `cli/` — Command Line Client

Thin wrapper around `core/`. Handles argument parsing and output formatting.

| File     | Responsibility                                 |
| -------- | ---------------------------------------------- |
| `cli.py` | Parses --days, --debug, --output, --repo flags |

### `api/` — FastAPI Backend

REST API that exposes `core/` functionality over HTTP. Deployed on Railway.

| File     | Responsibility                       |
| -------- | ------------------------------------ |
| `api.py` | FastAPI app, routes, Pydantic models |

### `web/` — Next.js Frontend

Browser interface. Calls the FastAPI backend. Deployed on Vercel.

| File               | Responsibility                           |
| ------------------ | ---------------------------------------- |
| `src/app/page.tsx` | Main UI — input form and results display |

---

## 3. Data Flow

### CLI Flow

```
User runs cli.py
       ↓
parse args (--days, --repo, --output)
       ↓
core/repo_reader.get_commits(source="local", days=N)
       ↓
core/summarise.format_commits(commits)
       ↓
core/summarise.to_prompt_str(formatted)
core/summarise.to_display_str(formatted)
       ↓
core/summarise.build_prompt(prompt_str)
       ↓
core/summarise.summarise(prompt) → Groq API
       ↓
print to terminal + write to output/summary.md
```

### Web Flow

```
User fills form (username, repos, days)
       ↓
Next.js POST /summarise → FastAPI (Railway)
       ↓
core/repo_reader.get_commits(source="github", username=X, repos=Y, days=N)
       ↓ GitHub API
core/summarise.format_commits(commits)
       ↓
core/summarise.build_prompt(to_prompt_str(formatted))
       ↓
core/summarise.summarise(prompt) → Groq API
       ↓
return {display, summary} → Next.js → render
```

---

## 4. repo_reader.py — Adapter Pattern

`repo_reader.py` supports two sources via a `source` parameter:

```python
# Local git (CLI)
get_commits(source="local", days=7)

# GitHub API (Web)
get_commits(source="github", username="deepusharma", repos=["gitpulse"], days=7)
```

Internally:

```python
def get_commits(source="local", **kwargs) -> list:
    if source == "local":
        return _get_local_commits(**kwargs)
    elif source == "github":
        return _get_github_commits(**kwargs)
    else:
        raise ValueError(f"Unknown source: {source}")
```

Both return the same flat list of commit dicts — same shape, same keys. Everything downstream is unchanged.

---

## 5. API Contract

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

**Error Response:**

```json
{
  "error": "GitHub API rate limit exceeded",
  "code": 429
}
```

### `GET /health`

```json
{
  "status": "ok",
  "version": "0.2.0"
}
```

---

## 6. Folder Structure

```
gitpulse/
├── core/
│   ├── __init__.py
│   ├── repo_reader.py
│   ├── summarise.py
│   ├── utils.py
│   ├── tests/
│   │   ├── test_repo_reader.py
│   │   ├── test_summarise.py
│   │   └── test_utils.py
│   └── docs/
│       └── core-guide.md
├── cli/
│   ├── __init__.py
│   ├── cli.py
│   ├── tests/
│   │   └── test_cli.py
│   └── docs/
│       └── cli-guide.md
├── api/
│   ├── __init__.py
│   ├── api.py
│   ├── tests/
│   │   └── test_api.py
│   └── docs/
│       └── api-guide.md
├── web/
│   ├── src/
│   │   └── app/
│   │       └── page.tsx
│   ├── tests/
│   └── docs/
│       └── web-guide.md
├── docs/
│   ├── prd/
│   │   └── prd-web.md
│   ├── architecture/
│   │   └── overview.md
│   ├── decisions/
│   └── sphinx/
├── AGENTS.md
├── .antigravity/
│   ├── rules/
│   │   └── project-rules.md
│   └── skills/
│       ├── backend-dev/SKILL.md
│       ├── frontend-dev/SKILL.md
│       ├── reviewer/SKILL.md
│       ├── tester-backend/SKILL.md
│       └── tester-frontend/SKILL.md
├── pyproject.toml
└── package.json
```

---

## 7. Technology Decisions

| Decision            | Choice                         | Reason                                    |
| ------------------- | ------------------------------ | ----------------------------------------- |
| Shared library      | `core/` Python package         | Single source of truth for business logic |
| Repo source — local | GitPython                      | Already working, no changes               |
| Repo source — web   | GitHub REST API via `httpx`    | No local access needed on server          |
| Backend framework   | FastAPI                        | Python, async, auto docs, easy deploy     |
| Frontend framework  | Next.js 14 App Router          | React, TypeScript, Vercel-native          |
| Styling             | Tailwind + shadcn/ui           | Fast, consistent, professional            |
| Backend hosting     | Railway                        | Free tier, Python, simple deploys         |
| Frontend hosting    | Vercel                         | First-party Next.js, free tier            |
| LLM                 | Groq — llama-3.3-70b-versatile | Fast, free tier, already integrated       |

---

## 8. Environment Variables

### CLI + API (Python)

```
GROQ_API_KEY=          # Required — Groq API key
GITHUB_TOKEN=          # Optional — increases GitHub API rate limit
```

### Web (Next.js)

```
NEXT_PUBLIC_API_URL=   # FastAPI backend URL
```

---

## 9. Deployment

```
GitHub push
    ↓
GitHub Actions CI (pytest)
    ↓
    ├── api/ → Railway (auto-deploy from master)
    └── web/ → Vercel (auto-deploy from master)
```

---

## 10. Authentication (v0.3)

For v0.3, gitpulse introduces authentication using **NextAuth.js** with the **GitHub OAuth** provider.
- This allows the Next.js frontend to securely authenticate users.
- In the future, this will unlock access to private repositories and user-specific rate limits.
- The FastAPI backend remains stateless, but the frontend will manage the GitHub OAuth session.

---

## 11. Out of Scope (v0.3)

- Private GitHub repos
- Persisting summaries
- Rate limit caching
- Streaming responses
