# Uptime Kuma MCP Server

A server for managing Uptime Kuma monitors via MCP protocol.

## Installation

```bash
uvx uptime-kuma-mcp-server
```

```json
"mcpServers": {
  "uptime-kuma-mcp-server": {
    "command": "uvx",
    "args": ["uptime-kuma-mcp-server"],
    "env": {
      "KUMA_URL": "https://yourdomain.xyz",
      "KUMA_USERNAME": "username",
      "KUMA_PASSWORD": "passwd"
    }
  },
}
```

## Available Tools

- `add_monitors` - Batch add multiple monitors to Uptime Kuma, returns Uptime Kuma page URLs after completion
  - `urls` (list[str], required): List of monitor URLs (must be deduplicated and include full protocol, e.g. https://bing.com)
- `get_monitors` - Get all monitors list, returns trimmed fields to prevent context overflow
- `delete_monitors` - Batch delete multiple monitors
  - `ids` (list[int], required): List of monitor IDs to delete

## Run SSE

```python
# run_sse.py

from uptime_kuma_mcp_server import run_sse

run_sse()

#  Uvicorn running on http://0.0.0.0:8000
```
