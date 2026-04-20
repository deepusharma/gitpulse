import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json
from api.api import app

client = TestClient(app)

def test_mcp_sse_advertises_tools():
    """Verify that the SSE endpoint advertises tools correctly."""
    with client.stream("GET", "/mcp/sse") as response:
        assert response.status_code == 200
        # Read the first event
        lines = []
        for line in response.iter_lines():
            if line:
                lines.append(line)
            if len(lines) >= 2:
                break
        
        assert "event: tools" in lines[0]
        assert "data: " in lines[1]
        data = json.loads(lines[1].replace("data: ", ""))
        assert any(tool["name"] == "generate_standup" for tool in data)
        assert any(tool["name"] == "get_insights" for tool in data)

@pytest.mark.anyio
async def test_mcp_sse_call_generate_standup():
    """Test calling the generate_standup tool via MCP SSE."""
    # We use a manual mock here because StreamingResponse is tricky with TestClient
    with patch("gitpulse_mcp.server.handle_generate_standup", new_callable=AsyncMock) as mock_handle:
        mock_handle.return_value = {"summary": "MCP Summary", "display": "MCP Display"}
        
        response = client.post("/mcp/sse/call", json={
            "tool": "generate_standup",
            "params": {"username": "dev", "repos": ["repo1"]}
        })
        
        assert response.status_code == 200
        # Check stream content
        content = response.text
        assert "event: result" in content
        assert "MCP Summary" in content

@pytest.mark.anyio
async def test_mcp_sse_call_invalid_tool():
    """Test calling an unknown tool via MCP SSE."""
    response = client.post("/mcp/sse/call", json={
        "tool": "unknown_tool",
        "params": {}
    })
    
    assert response.status_code == 200 # SSE returns 200 then error in stream
    assert "event: error" in response.text
    assert "Unknown tool" in response.text
