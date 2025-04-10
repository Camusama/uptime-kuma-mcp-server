# Uptime Kuma MCP Server

A server for managing Uptime Kuma monitors via MCP protocol.

## Installation

```bash
uvx uptime-kuma-mcp-server
```

```bash
"mcpServers": {
  "uptime-kuma-mcp-server": {
    "command": "uvx",
    "args": ["uptime-kuma-mcp-server"]
  }
}
```

## .env

```bash
KUMA_URL=https://kuma.yourdomain.com
KUMA_USERNAME=marquezyang
KUMA_PASSWORD=yourpassowrd
```
