# GitPulse MCP — IDE Setup Guide

Use GitPulse as an MCP (Model Context Protocol) server so Claude Desktop, Cursor, or Windsurf
can generate standups and retrieve repo insights natively inside your IDE — no copy-pasting needed.

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.12+ | Check with `python --version` |
| `uv` | latest | Install: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `GROQ_API_KEY` | — | Get one free at [console.groq.com](https://console.groq.com) |
| `GITHUB_TOKEN` | optional | Raises the GitHub API rate limit from 60 → 5000 req/hr |

---

## Option A — Claude Desktop (local stdio)

### 1. Locate your config file

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

### 2. Add the `gitpulse` MCP server block

Open the file (create it if it does not exist) and add:

```json
{
  "mcpServers": {
    "gitpulse": {
      "command": "uvx",
      "args": ["gitpulse-mcp"],
      "env": {
        "GROQ_API_KEY": "your-groq-api-key",
        "GITHUB_TOKEN": "your-github-token"
      }
    }
  }
}
```

> **Note:** If you already have other MCP servers, merge the `"gitpulse"` key into the existing
> `"mcpServers"` object — do not create a second `"mcpServers"` key.

### 3. Restart Claude Desktop

Fully quit and reopen Claude Desktop. The `gitpulse` server appears under **Settings → MCP** with
a green status dot when it connects successfully.

---

## Option B — Cursor

### 1. Create (or edit) `.cursor/mcp.json` in your home directory

```json
{
  "mcpServers": {
    "gitpulse": {
      "command": "uvx",
      "args": ["gitpulse-mcp"],
      "env": {
        "GROQ_API_KEY": "your-groq-api-key",
        "GITHUB_TOKEN": "your-github-token"
      }
    }
  }
}
```

The global path is `~/.cursor/mcp.json` (applies to all projects).  
For a project-scoped config use `.cursor/mcp.json` inside the repo root.

### 2. Enable MCP in Cursor settings

Go to **Cursor Settings → Features → MCP** and toggle it **on**. Restart if prompted.

---

## Option C — Remote SSE (no local install)

If you prefer not to install anything locally, the deployed GitPulse API exposes an SSE endpoint:

```
GET https://<your-railway-url>/mcp/sse
```

Some IDEs (e.g. Windsurf) support remote MCP servers via SSE. Configure the endpoint URL in your
IDE's MCP settings panel. No `GROQ_API_KEY` env var is needed on the client side — the server uses
its own key.

---

## Available Tools

| Tool | Description | Parameters |
|---|---|---|
| `generate_standup` | Generates an AI standup summary for one or more GitHub repos | `username` (str), `repos` (list[str]), `days` (int, default 7), `source` (`"github"` \| `"local"`), `tone` (str, optional) |
| `get_insights` | Returns aggregated commit/PR/issue counts — no LLM call, fast | `username` (str), `repos` (list[str]), `days` (int, default 30) |

---

## Example Prompts

Once the server is connected, try these prompts directly in Claude or Cursor chat:

```
Generate my standup for the last 7 days from my gitpulse repo.
```

```
What are my GitHub metrics for the last 30 days across all my repos?
```

```
Write a formal standup for @alice covering repos ["api", "web"] over the past 14 days.
```

```
Get insights for user deepusharma for the last 30 days.
```

---

## Running Locally (Without uvx)

If you want to run from source without publishing to PyPI:

```bash
# Clone the repo
git clone https://github.com/deepusharma/gitpulse.git
cd gitpulse

# Install deps
uv sync

# Test the server directly
GROQ_API_KEY=your-key uv run python mcp/server.py
```

Then update your Claude Desktop config to point at the local script:

```json
{
  "mcpServers": {
    "gitpulse": {
      "command": "uv",
      "args": ["run", "python", "/absolute/path/to/gitpulse/mcp/server.py"],
      "env": {
        "GROQ_API_KEY": "your-groq-api-key",
        "GITHUB_TOKEN": "your-github-token"
      }
    }
  }
}
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Server shows red dot in Claude Desktop | `uvx` not found in PATH | Run `which uvx`; if empty, reinstall `uv` and ensure `~/.cargo/bin` is in `$PATH` |
| `GROQ_API_KEY not set` error | Env var missing from config | Add `GROQ_API_KEY` to the `"env"` block in your config file |
| `Python 3.12+ required` error | System Python is older | Use `uv python install 3.12` and re-run `uvx gitpulse-mcp` |
| Empty standup returned | No commits found in window | Increase `days` parameter or verify the `repos` list spelling |
| GitHub rate limit errors | No token set | Add `GITHUB_TOKEN` to the `"env"` block |
| Changes not picked up | Claude Desktop cached old config | Fully quit (`Cmd+Q`) and reopen — do not just close the window |
| `Connection refused` (SSE mode) | API server not running | Ensure your Railway deployment is live and the URL is correct |

---

## Architecture Reference

```
Claude Desktop / Cursor / Windsurf
        │
        │  stdio transport (local)          SSE transport (remote)
        ▼                                   ▼
mcp/server.py  ──────────────────  GET /mcp/sse  (FastAPI, Railway)
        │                                   │
        └──── gitpulse.core ────────────────┘
                ├── repo_reader.get_activity()
                ├── summarise.summarise()
                └── recommendations.get_recommendations()
```

---

## See Also

- [GitPulse Web UI](https://gitpulse.vercel.app) — browser-based standup dashboard
- [API Contract](../api/api-contract.md) — full endpoint reference
- [Model Context Protocol Specification](https://modelcontextprotocol.io/docs)
