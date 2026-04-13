"""
GitPulse MCP server.

Exposes two tools to any MCP-compatible client (Claude Desktop, Cursor, Windsurf):

  * generate_standup — fetches git activity and produces an AI standup summary.
  * get_insights     — returns aggregated commit/PR/issue counts (no LLM call).

Transport: stdio  (add to claude_desktop_config.json or mcp.json).
Entry point: ``python -m gitpulse_mcp.server`` or the ``gitpulse-mcp`` script
defined in mcp/pyproject.toml.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

import mcp as _mcp_sdk  # noqa: F401 — ensures SDK is resolved ahead of local mcp/ dir
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from gitpulse.core.repo_reader import get_activity
from gitpulse.core.summarise import (
    format_activity,
    to_prompt_str,
    build_prompt,
    summarise,
)

# ---------------------------------------------------------------------------
# Tool schemas
# ---------------------------------------------------------------------------

TOOLS: list[types.Tool] = [
    types.Tool(
        name="generate_standup",
        description=(
            "Fetch git activity for a GitHub user across one or more repositories "
            "and generate a professional standup summary using Groq LLaMA 3.3."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "GitHub username whose activity to summarise.",
                },
                "repos": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of repository names (without the username prefix).",
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days of history to include (default 7).",
                    "default": 7,
                },
                "source": {
                    "type": "string",
                    "enum": ["github", "local"],
                    "description": "Activity source: 'github' (default) or 'local' (.git via ~/.gitpulse.toml).",
                    "default": "github",
                },
                "tone": {
                    "type": "string",
                    "enum": ["standup", "retro"],
                    "description": "Summary tone: 'standup' (default) or 'retro' for sprint retrospectives.",
                    "default": "standup",
                },
            },
            "required": ["username", "repos"],
        },
    ),
    types.Tool(
        name="get_insights",
        description=(
            "Return aggregated commit, PR, and issue counts for a GitHub user across "
            "one or more repositories. Fast — no LLM call."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "GitHub username.",
                },
                "repos": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of repository names.",
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days of history to analyse (default 7).",
                    "default": 7,
                },
            },
            "required": ["username", "repos"],
        },
    ),
]

# ---------------------------------------------------------------------------
# Handler helpers
# ---------------------------------------------------------------------------


async def handle_generate_standup(arguments: dict) -> str:
    """Handle the generate_standup tool call.

    Args:
        arguments: Decoded tool input dict validated against the JSON schema.

    Returns:
        The AI-generated standup summary as a plain string.

    Raises:
        ValueError: If required arguments are missing.
        EnvironmentError: If GROQ_API_KEY is not set.
    """
    username: str = arguments.get("username", "")
    repos: list[str] = arguments.get("repos", [])
    days: int = int(arguments.get("days", 7))
    source: str = arguments.get("source", "github")
    tone: str = arguments.get("tone", "standup")

    if not username:
        raise ValueError("'username' is required for generate_standup")
    if not repos:
        raise ValueError("'repos' must be a non-empty list for generate_standup")

    logger.info(
        "generate_standup: user=%s repos=%s days=%d source=%s tone=%s",
        username,
        repos,
        days,
        source,
        tone,
    )

    activity, errors = await get_activity(
        source=source,
        username=username,
        repos=repos,
        days=days,
    )

    if errors:
        logger.warning("get_activity returned errors: %s", errors)

    commits = activity.get("commits", [])
    prs = activity.get("prs", [])
    issues = activity.get("issues", [])

    if not commits and not prs and not issues:
        return f"No activity found for {username} across {repos} in the last {days} days."

    formatted = format_activity(activity)
    prompt_str = to_prompt_str(formatted)
    prompt = build_prompt(prompt_str, mode=tone)
    summary = await summarise(prompt)

    return summary


async def handle_get_insights(arguments: dict) -> dict:
    """Handle the get_insights tool call.

    Returns aggregated activity counts without calling the LLM.

    Args:
        arguments: Decoded tool input dict validated against the JSON schema.

    Returns:
        A dict with keys ``commits``, ``prs``, ``issues``, ``repos``,
        ``username``, ``days``, and ``generated_at``.

    Raises:
        ValueError: If required arguments are missing.
    """
    username: str = arguments.get("username", "")
    repos: list[str] = arguments.get("repos", [])
    days: int = int(arguments.get("days", 7))

    if not username:
        raise ValueError("'username' is required for get_insights")
    if not repos:
        raise ValueError("'repos' must be a non-empty list for get_insights")

    logger.info(
        "get_insights: user=%s repos=%s days=%d",
        username,
        repos,
        days,
    )

    activity, errors = await get_activity(
        source="github",
        username=username,
        repos=repos,
        days=days,
    )

    if errors:
        logger.warning("get_activity returned errors: %s", errors)

    commits = activity.get("commits", [])
    prs = activity.get("prs", [])
    issues = activity.get("issues", [])

    # Aggregate per-repo commit counts
    repo_commit_counts: dict[str, int] = {}
    for commit in commits:
        repo = commit["repo"]
        repo_commit_counts[repo] = repo_commit_counts.get(repo, 0) + 1

    insights = {
        "username": username,
        "repos": repos,
        "days": days,
        "total_commits": len(commits),
        "total_prs_merged": len(prs),
        "total_issues_closed": len(issues),
        "commits_per_repo": repo_commit_counts,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    return insights


# ---------------------------------------------------------------------------
# MCP server wiring
# ---------------------------------------------------------------------------


async def main() -> None:
    """Run the GitPulse MCP stdio server.

    Registers the two tool handlers and starts the stdio transport loop.
    """
    server = Server("gitpulse-mcp")

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        """Return the list of available tools."""
        return TOOLS

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Dispatch an MCP tool call to the appropriate handler.

        Args:
            name: Tool name as registered in TOOLS.
            arguments: Tool input as a dict.

        Returns:
            A list containing a single TextContent item with the result.

        Raises:
            ValueError: If the tool name is not recognised.
        """
        logger.info("call_tool: name=%s", name)

        if name == "generate_standup":
            result = await handle_generate_standup(arguments)
            return [types.TextContent(type="text", text=result)]

        if name == "get_insights":
            result = await handle_get_insights(arguments)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        raise ValueError(f"Unknown tool: {name!r}")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main_sync() -> None:
    """Synchronous entry point for the ``gitpulse-mcp`` console script."""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
