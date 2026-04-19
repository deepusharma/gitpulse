from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mcp", tags=["mcp"])

@router.get("/sse")
async def mcp_sse():
    """SSE endpoint advertising the available MCP tools."""
    tools_payload = [
        {
            "name": "generate_standup",
            "description": (
                "Fetch git activity for a GitHub user across one or more repositories "
                "and generate a professional standup summary using Groq LLaMA 3.3."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "GitHub username."},
                    "repos": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of repository names.",
                    },
                    "days": {"type": "integer", "default": 7},
                    "source": {
                        "type": "string",
                        "enum": ["github", "local"],
                        "default": "github",
                    },
                    "tone": {
                        "type": "string",
                        "enum": ["standup", "retro"],
                        "default": "standup",
                    },
                },
                "required": ["username", "repos"],
            },
        },
        {
            "name": "get_insights",
            "description": (
                "Return aggregated commit, PR, and issue counts for a GitHub user. "
                "Fast — no LLM call."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "repos": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "days": {"type": "integer", "default": 7},
                },
                "required": ["username", "repos"],
            },
        },
    ]

    async def event_stream():
        body = json.dumps(tools_payload)
        yield f"event: tools\ndata: {body}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/sse/call")
async def mcp_sse_call(body: dict):
    from gitpulse_mcp.server import handle_generate_standup, handle_get_insights

    tool_name = body.get("tool")
    params = body.get("params", {})

    if not tool_name:
        raise HTTPException(status_code=400, detail="'tool' is required")

    async def event_stream():
        try:
            if tool_name == "generate_standup":
                result = await handle_generate_standup(params)
            elif tool_name == "get_insights":
                result = await handle_get_insights(params)
            else:
                raise ValueError(f"Unknown tool: {tool_name!r}")

            if isinstance(result, dict):
                data = json.dumps(result)
            else:
                data = json.dumps({"text": result})
            yield f"event: result\ndata: {data}\n\n"
        except Exception as exc:
            logger.error("MCP SSE call failed: %s", exc, exc_info=True)
            yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
