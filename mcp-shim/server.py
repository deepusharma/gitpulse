"""
Entry-point shim for ``mcp/server.py``.

This file exists so users can reference ``mcp/server.py`` directly in their
claude_desktop_config.json or IDE config.  The actual implementation lives in
the ``gitpulse_mcp`` Python package to avoid a naming conflict with the
``mcp`` SDK package.

Usage (uv):
    uv run python mcp/server.py

Or via the console script (after installation):
    gitpulse-mcp
"""

from gitpulse_mcp.server import main_sync

if __name__ == "__main__":
    main_sync()
