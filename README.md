# Jointhubs open source operating system

<p align="center">
  <img src=".github/assets/jointhubs.png" alt="Jointhubs" width="450">
</p>

> Multi-agent VS Code Copilot system for Obsidian + Google + Discord

**Fork this repo and make it yours.** Your brain works differently — so should your AI assistant.

## What It Does

| Agent | Purpose |
|-------|---------|
| **Tech Lead** | Code, architecture, debugging |
| **Designer** | UX review, interface critique |
| **Planner** | Daily/weekly planning, scheduling |
| **Journal** | Reflection, pattern recognition |
| **Review** | Weekly synthesis, retrospectives |
| **DeepWork** | Focus sessions |
| **Inbox** | Email/message triage |

All agents share context through **daily logs** — your memory between sessions.

## Quick Start

### Prerequisites

- [Obsidian](https://obsidian.md/) 
- [VS Code](https://code.visualstudio.com/) + [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)
- [Node.js](https://nodejs.org/) 18+
- [Python](https://www.python.org/) 3.11+ with [uv](https://docs.astral.sh/uv/)

### Setup

1. **Fork & clone** this repo
2. **Open in Obsidian** — This repo IS your vault
3. **Configure MCP** — Create `.vscode/mcp.json`:

```jsonc
{
  "servers": {
    "googleWorkspace": {
      "type": "stdio",
      "command": "uvx",
      "args": ["workspace-mcp", "--tool-tier", "core"],
      "env": {
        "GOOGLE_OAUTH_CLIENT_ID": "your-client-id",
        "GOOGLE_OAUTH_CLIENT_SECRET": "your-secret"
      }
    },
    "discord": {
      "type": "stdio", 
      "command": "npx",
      "args": ["-y", "discord-mcp-mod"],
      "env": { "DISCORD_TOKEN": "your-token" }
    }
  }
}
```

4. **Open VS Code** → Copilot Chat → Select agent → Start working

## Structure

```
jointhubs-os/
├── .github/
│   ├── agents/           ← Agent personalities
│   ├── skills/           ← Domain knowledge  
│   └── instructions/     ← Directory-scoped rules
├── Operations/
│   └── Periodic Notes/   ← Daily/Weekly logs
├── Projects/             ← Your work
└── Personal/             ← Life tracking
```

## Customize

| What | Where |
|------|-------|
| Agent personalities | `.github/agents/*.agent.md` |
| Domain knowledge | `.github/skills/*/SKILL.md` |
| Global rules | `.github/copilot-instructions.md` |

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT — See [LICENSE](LICENSE)

---

**Join your hubs. Ship your work.** 🧠
