# Sprint 17 Execution Plan — AI & MCP

**Sprint Goal:** Build an MCP (Model Context Protocol) server wrapping `gitpulse.core` so Claude Desktop / Cursor / Windsurf can generate standups and retrieve insights natively inside the IDE. Add proactive AI recommendations and saved prompt templates.
**Milestone:** v1.2 — AI & MCP
**Branch:** `feature/sprint-17-local-mcp`
**Status:** Approved — Ready to Execute

---

## Design Decisions (Pre-approved)

| Decision | Choice | Rationale |
|---|---|---|
| MCP transport | `stdio` (local) as primary; SSE endpoint on FastAPI as remote option | `stdio` is zero-infrastructure; Railway-hosted SSE unlocks Cloudflare/Vercel-hosted IDE integrations |
| MCP Python package | `mcp` pip package (official Anthropic SDK) | First-party, stable, aligns with Claude Desktop's expected protocol |
| Tool scope | `generate_standup` and `get_insights` (2 tools, high-value) | Keeps first iteration focused; more tools can be added in v1.3 |
| Proactive recommendations | New `gitpulse.core.recommendations.py` module; LLM call over aggregated DB metrics | Keeps recommendation logic in `core/` per project rules; FastAPI route just triggers it |
| Prompt templates | `prompt_templates` table in existing PostgreSQL DB; CRUD via API | Reuses existing DB infrastructure; no new data store needed |
| MCP server entry point | `mcp/server.py` at repo root; installable as `gitpulse-mcp` via `pyproject.toml` script | Keeps `gitpulse.core` package unchanged; MCP code lives in its own `mcp/` directory |
| PyPI publish | Separate `gitpulse-mcp` package (`mcp/pyproject.toml`) so users can `uvx gitpulse-mcp` | Clean separation; MCP users do not need the FastAPI stack |

---

## Architecture

### MCP Server (`mcp/server.py`)

```
Claude Desktop / Cursor
      │  stdio  (local install)
      ▼
mcp/server.py
  ├── tool: generate_standup   → gitpulse.core.repo_reader.get_activity()
  │                              → gitpulse.core.summarise.summarise()
  └── tool: get_insights       → gitpulse.core.repo_reader.get_activity()  [aggregate only]
```

The MCP server is a thin wrapper — no new business logic. It delegates entirely to `gitpulse.core`.

### SSE Remote MCP (FastAPI)

```
Claude (remote)  ←→  GET /mcp/sse  (FastAPI, Railway)  ←→  gitpulse.core
```

FastAPI's `StreamingResponse` will emit Server-Sent Events that proxy MCP tool calls. This is an **optional** route for users who prefer not to install anything locally.

### Proactive Recommendations

```
POST /insights/recommendations
  │
  ├── Query DB for last 30 days of summary + activity metrics for user
  ├── gitpulse.core.recommendations.build_recommendations_prompt(metrics)
  └── gitpulse.core.summarise.summarise(prompt) → Groq LLM → bulleted AI nudges
```

### Prompt Templates

```
POST   /prompt-templates           → create a saved template
GET    /prompt-templates           → list user's templates
DELETE /prompt-templates/{id}      → delete a template
```

Templates are stored in a new `prompt_templates` table and exposed as metadata options in the web UI.

---

## File Map

| File | Change | Stream |
|---|---|---|
| `mcp/__init__.py` | **NEW** — package marker | 1 |
| `mcp/server.py` | **NEW** — stdio MCP server with `generate_standup` + `get_insights` tools | 1 |
| `mcp/pyproject.toml` | **NEW** — standalone package for `uvx gitpulse-mcp` | 1 |
| `mcp/tests/test_mcp_server.py` | **NEW** — unit tests for tool handlers | 1 |
| `gitpulse/core/recommendations.py` | **NEW** — `build_recommendations_prompt` + `get_recommendations` | 1 |
| `gitpulse/core/tests/test_recommendations.py` | **NEW** — unit tests (mocked Groq) | 1 |
| `api/db.py` | Add `init_prompt_templates_table()` migration | 1 |
| `api/api.py` | Add `GET /mcp/sse`, `POST /insights/recommendations`, CRUD `/prompt-templates` | 1 |
| `api/tests/test_api.py` | New test cases for all new endpoints | 1 |
| `web/app/insights/page.tsx` | Add AI Recommendations sidebar panel | 2 |
| `web/app/templates/page.tsx` | **NEW** — saved prompt templates management UI | 2 |
| `web/components/RecommendationsPanel.tsx` | **NEW** — AI nudges rendered in the insights sidebar | 2 |
| `web/components/Header.tsx` | Add "Templates" nav link | 2 |
| `docs/mcp/README.md` | **NEW** — MCP setup guide for Claude Desktop, Cursor, Windsurf | 2 |

---

## Order of Execution

```
Stream 1 (Backend / MCP):
  1.1  mcp/ directory + mcp/server.py (stdio tools)
  1.2  mcp/pyproject.toml (standalone package)
  1.3  gitpulse/core/recommendations.py
  1.4  api/db.py — prompt_templates migration
  1.5  api/api.py — GET /mcp/sse (SSE proxy)
  1.6  api/api.py — POST /insights/recommendations
  1.7  api/api.py — CRUD /prompt-templates
  1.8  Tests for all new backend code

Stream 2 (Frontend / Docs):
  2.1  web/app/insights/page.tsx — AI Recommendations sidebar
  2.2  web/components/RecommendationsPanel.tsx
  2.3  web/app/templates/page.tsx — saved templates UI
  2.4  web/components/Header.tsx — Templates nav link
  2.5  docs/mcp/README.md — IDE setup guide
```

---

## Step-by-Step Technical Plan

### Stream 1 — Backend & MCP

#### Step 1.1: `mcp/server.py` — stdio MCP server

- Create `mcp/` directory with `__init__.py`.
- Install `mcp` as a dependency in `pyproject.toml` (optional group `mcp`).
- `mcp/server.py` uses the `mcp` SDK's `Server` class with `stdio_server` transport.
- **Tool 1: `generate_standup`**
  - Input schema: `{ "username": str, "repos": list[str], "days": int, "source": "github"|"local", "tone": str (optional) }`
  - Handler: calls `get_activity(source, username, repos, days)` → `format_activity()` → `build_prompt()` → `summarise()` → returns the summary string.
- **Tool 2: `get_insights`**
  - Input schema: `{ "username": str, "repos": list[str], "days": int }`
  - Handler: calls `get_activity(source="github", ...)` → aggregates commit/PR/issue counts → returns a structured dict summary (no LLM call, fast lookup).
- Both tools use `asyncio.run()` where needed since `gitpulse.core` functions are synchronous.
- Entry point: `if __name__ == "__main__": asyncio.run(main())`.

#### Step 1.2: `mcp/pyproject.toml` — standalone package

```toml
[project]
name = "gitpulse-mcp"
version = "1.2.0"
description = "MCP server for GitPulse — expose standup generation to Claude/Cursor"
dependencies = ["gitpulse>=1.2.0", "mcp>=1.0.0"]

[project.scripts]
gitpulse-mcp = "mcp.server:main_sync"
```

- `main_sync` is a thin wrapper that calls `asyncio.run(main())`.
- This allows `uvx gitpulse-mcp` to work without installing anything else.

#### Step 1.3: `gitpulse/core/recommendations.py` — proactive AI nudges

- **`build_recommendations_prompt(metrics: dict) -> str`**
  - `metrics` dict: `{ "commits": int, "prs": int, "issues": int, "avg_cycle_time_hrs": float, "stale_prs": int, "commit_streak_days": int, "prev_commits": int }`
  - Builds a system prompt that asks the LLM to identify worrying patterns and give 3–5 actionable suggestions.
- **`get_recommendations(metrics: dict) -> str`**
  - Calls `build_recommendations_prompt()` → `summarise(prompt)` → returns formatted nudge string.
- Google docstrings on all functions. No `print` statements.
- `gitpulse/core/tests/test_recommendations.py` — mock the Groq call, assert output is non-empty string.

#### Step 1.4: `api/db.py` — `prompt_templates` table migration

```sql
CREATE TABLE IF NOT EXISTS prompt_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username TEXT NOT NULL,
  name TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

- New `init_prompt_templates_table()` async function using `IF NOT EXISTS` (idempotent).
- Call from `init_db()` after existing migrations.

#### Step 1.5: `api/api.py` — `GET /mcp/sse`

- SSE proxy endpoint that wraps the MCP tool registry over HTTP.
- Uses FastAPI's `StreamingResponse` with `media_type="text/event-stream"`.
- On connection: sends an initial `event: tools` frame listing the two available tools with their JSON schemas.
- On `POST /mcp/sse/call` companion route: accepts `{ "tool": str, "params": dict }`, delegates to the same handler functions used in `mcp/server.py` (refactored into shared `mcp/handlers.py`), returns `event: result` SSE frame.
- Add to `analytics_cache` where appropriate (tool responses are cached for 1 minute).

#### Step 1.6: `api/api.py` — `POST /insights/recommendations`

```python
class RecommendationsRequest(BaseModel):
    username: str
    days: int = 30

class RecommendationsResponse(BaseModel):
    recommendations: str
    generated_at: str
```

- Fetches recent activity metrics from the DB (`SELECT COUNT(*) GROUP BY ...` over last N days).
- Constructs the `metrics` dict and calls `core.recommendations.get_recommendations(metrics)`.
- Caches result per `username+days` in `analytics_cache` with 10-minute TTL.
- Returns `RecommendationsResponse`.

#### Step 1.7: `api/api.py` — CRUD `/prompt-templates`

```python
POST   /prompt-templates          → insert row, return template with id
GET    /prompt-templates?username=X → list all templates for user (ordered by created_at DESC)
DELETE /prompt-templates/{id}     → delete, return 204
```

- Pydantic models: `PromptTemplateCreate`, `PromptTemplateResponse`.
- All routes return 503 if DB is disabled (same pattern as `/history`).

#### Step 1.8: Tests

- `api/tests/test_api.py`:
  - `test_get_mcp_sse_lists_tools` — verify SSE response contains the two tool schemas.
  - `test_recommendations_returns_string` — mock `get_recommendations`, verify 200 + `recommendations` key non-empty.
  - `test_create_prompt_template` — mock DB, verify insert returns `id`.
  - `test_list_prompt_templates` — mock DB, verify list returns array.
  - `test_delete_prompt_template` — verify 204 response.
- `mcp/tests/test_mcp_server.py`:
  - `test_generate_standup_tool` — mock `get_activity` + `summarise`, verify tool returns summary string.
  - `test_get_insights_tool` — mock `get_activity`, verify aggregated counts dict returned.

---

### Stream 2 — Frontend & Docs

#### Step 2.1: `web/app/insights/page.tsx` — AI Recommendations panel

- Add a new `<RecommendationsPanel username={username} days={days} />` component below the existing charts section.
- Fetches `POST {API_URL}/insights/recommendations` with `{ username, days }` on mount.
- Shows a loading skeleton (3 skeleton lines) while fetching.
- On success: renders the markdown-formatted nudge list inside a styled card with a "✨ AI Insights" heading.
- On error: renders a subtle "Recommendations unavailable" message (non-blocking).

#### Step 2.2: `web/components/RecommendationsPanel.tsx` — **NEW**

```tsx
interface RecommendationsPanelProps {
  username: string;
  days: number;
}
```

- Client component (`"use client"`).
- Fetches recommendations on mount and whenever `username` or `days` changes.
- Renders output as a markdown string using `<pre>` or the existing `@tailwindcss/typography` prose classes.
- Refresh button (icon: `RefreshCw` from lucide-react) to re-trigger the fetch and re-generate recommendations.
- Card styling: left accent border in the existing accent color, icon ✨, muted subtitle "Generated by Groq LLaMA 3.3".

#### Step 2.3: `web/app/templates/page.tsx` — **NEW** — saved templates

- Client page behind NextAuth session guard (same as `/insights`).
- Fetches `GET /prompt-templates?username=X` on mount.
- Renders a list of saved templates in cards: name, first 60 chars of content preview, delete button.
- "New Template" button at top → opens an inline form (textarea for content, text input for name) → submits `POST /prompt-templates`.
- On delete: optimistic UI removal + `DELETE /prompt-templates/{id}` call.
- Empty state: "No saved templates yet. Create one to reuse your custom instructions."

#### Step 2.4: `web/components/Header.tsx` — Templates link

- Add "Templates" nav link alongside existing links (History, Insights, Team).
- Only visible when session is active.

#### Step 2.5: `docs/mcp/README.md` — IDE setup guide

Must include:
1. **Prerequisites** — Python 3.12+, `uv`, `GROQ_API_KEY`, `GITHUB_TOKEN`.
2. **Claude Desktop setup** — exact JSON block to add to `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "gitpulse": {
         "command": "uvx",
         "args": ["gitpulse-mcp"],
         "env": {
           "GROQ_API_KEY": "your-key",
           "GITHUB_TOKEN": "your-token"
         }
       }
     }
   }
   ```
3. **Cursor setup** — equivalent `mcp.json` configuration block.
4. **Available tools** — table of `generate_standup` and `get_insights` with all params.
5. **Example prompts** — "Generate my standup for the last 7 days from my gitpulse repo."
6. **Troubleshooting** — common failure modes (missing env vars, wrong Python version).

---

## Definition of Done

- [ ] `mcp/server.py` connects via stdio and correctly executes both tools end-to-end
- [ ] `uvx gitpulse-mcp` installs and runs without errors on a clean machine
- [ ] `GET /mcp/sse` returns the tool list as an SSE frame
- [ ] `POST /insights/recommendations` returns a non-empty recommendations string
- [ ] `prompt_templates` table created idempotently on startup
- [ ] CRUD `/prompt-templates` endpoints all return correct status codes
- [ ] `web/app/templates/page.tsx` lists, creates, and deletes templates
- [ ] `RecommendationsPanel` renders on the Insights page without blocking existing charts
- [ ] `docs/mcp/README.md` tested against a fresh Claude Desktop install
- [ ] All new Python tests pass (`uv run pytest -v`)
- [ ] `npm run lint` passes in `web/`
- [ ] PR squash-merged to master

---

## Out of Scope (Deferred to v1.3)

- MCP tool: `list_history` (standup history search via IDE) — deferred, lower priority
- Prompt template sharing between users (team-scoped templates)
- Streaming SSE responses from Groq through the MCP tool (complex async plumbing)
- S18 gamification/streaks (next sprint)
