# Sprint 17 — AI & MCP

**Sprint goal:** Build MCP server to expose core functions to Claude/Cursor, and implement AI proactive recommendations.
**Milestone:** v1.2 — AI & MCP
**Duration:** Day 11 (~4 hours)
**Status:** Not Started

---

## Pre-Sprint Requirements
- Review Official Model Context Protocol (MCP) python SDK documentation online if necessary.

---

## AI Planning Prompt

### Planning Prompt (Gemini 3.1 Pro High — Planning Mode)
```text
Read these files before responding:
- AGENTS.md
- docs/sprint/sprint-17-brief.md
- docs/architecture/overview.md
- docs/decisions/feature-brainstorm-2026-04.md (specifically MCP section)

We are planning Sprint 17 — AI & MCP.

Before writing any code:
1. Review stories S17.1 through S17.7 mapped to this sprint.
2. Outline the Python MCP script structure wrapping the existing `core/` library functions.
3. Define the tool schemas for `generate_standup`, `analyze_repo`, and `get_insights`.
4. Devise the architecture for the `/mcp` SSE real-time remote endpoint on FastAPI.
5. Prepare prompts for the proactive "Nudges/Recommendations" feature.
6. Identify setup edge-cases for various IDEs.
7. Propose a step-by-step technical execution plan.
8. Save plan to `docs/sprint/sprint-17-plan.md`.

Do not write any code yet. Planning only.
```
