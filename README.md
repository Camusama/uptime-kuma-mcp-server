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

## .env

```bash
KUMA_URL=https://kuma.yourdomain.com
KUMA_USERNAME=marquezyang
KUMA_PASSWORD=yourpassowrd
```
