# Sprint 17 — AI & MCP

**Sprint goal:** Build MCP server exposing core functions to Claude/Cursor, and implement AI proactive recommendations.
**Milestone:** v1.2 — AI & MCP
**Duration:** Day 11 (~4 hours)
**Status:** Not Started

---

## Pre-Sprint Requirements
- Familiarity with the official Model Context Protocol (MCP) specifications.
- Environment with Claude Desktop or Cursor for local testing.

---

## AI Planning Prompt

### Planning Prompt (Gemini 3.1 Pro High — Planning Mode)
```text
Read these files before responding:
- AGENTS.md
- docs/sprint/sprint-17-brief.md
- docs/architecture/overview.md
- docs/decisions/feature-brainstorm-2026-04.md

We are planning Sprint 17 — AI & MCP.

Before writing any code:
1. Review stories S17.1 through S17.7.
2. Outline the Python MCP script structure wrapping the existing `core/` functions.
3. Define the tool JSON schemas.
4. Propose a step-by-step technical execution plan.
5. Save plan to `docs/sprint/sprint-17-plan.md`.

Do not write code yet. Planning only.
```

### Execution Prompt — Stream 1: MCP Server Core
```text
Execute Stream 1 — MCP Protocol Server.
Branch: feature/sprint-17-local-mcp

Use @backend-dev.
- Build `mcp/server.py` implementing stdio MCP wrappers around core library.
- Expose `generate_standup` and `get_insights` as precise tools.

Commit and push.
```

### Execution Prompt — Stream 2: Web Integration
```text
Execute Stream 2 — IDE Integrations & Proactive AI.
Still on branch: feature/sprint-17-local-mcp

- Map SSE real-time remote endpoint on FastAPI.
- Add AI proactive recommendations module generating dynamic insight prompts.
- Document `/docs/mcp` configuration blocks.

Commit, push, create PR.
```

---

## Sprint Stories

| Issue | Story | Status | Priority |
|---|---|---|---|
| TBD | S17.1: Build `mcp/server.py` wrapping core | 🔵 This Sprint | High |
| TBD | S17.2: Expose MCP JSON tool schemas | 🔵 This Sprint | High |
| TBD | S17.3: Publish MCP server to PyPI | 🔵 This Sprint | Medium |
| TBD | S17.4: FastAPI SSE MCP proxy | 🔵 This Sprint | Medium |
| TBD | S17.5: Document MCP IDE setup | 🔵 This Sprint | Low |
| TBD | S17.6: AI proactive recommendations | 🔵 This Sprint | Medium |
| TBD | S17.7: Saved prompt templates | 🔵 This Sprint | Low |

---

## Story Details & Definition of Done

### MCP Protocol Setup (S17.1-S17.5)
**Architecture:** Python `mcp` pip package using `stdio` transport.
**Done when:**
- [ ] Users can add `uv run mcp/server.py` to their `claude_desktop_config.json`.
- [ ] LLM inside IDE can request commit data and write standups automatically.

### AI Customization (S17.6-S17.7)
**UI:**
- Insights page displays a sidebar block with "AI Notice" suggestions based on anomalies.
**Done when:**
- [ ] LLM automatically identifies "unusually high PR cycle time".

---

## Order of Work
MCP Protocol → Server Functions → Testing via Claude Desktop → Proactive AI Gen → Documentation
