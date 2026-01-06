# Jointhubs Open Source Operating System

<p align="center">
  <img src="assets/jointhubs.png" alt="Jointhubs" width="600">
</p>

> Joining your knowledge hubs into one intelligent assistant

A multi-agent VS Code Copilot system that connects your **Obsidian vault**, **Google Calendar**, **Google Tasks**, **Gmail**, and **Discord** into a unified AI assistant that understands your context, sees patterns you miss, and helps you work smarter — especially on low-energy days.

## 🎯 Philosophy

**Jointhubs is meant to be forked and customized.** 

Everyone's brain works differently. Your vault structure, your projects, your workflow — they're unique to you. This repo is a starting point, not a finished product. Fork it, make it yours, and let your AI assistant truly understand *your* context.

The name says it all: **Joint** knowledge accross **hubs** — Obsidian, Calendar, Tasks, Email — into one assistant that thinks the way you think.

## ✨ Features

- **Planner Agent** — Daily/weekly planning, priority triage, schedule optimization
- **Journal Agent** — Pattern recognition, habit tracking, energy-aware reflection
- **Review Agent** — End-of-week synthesis and insight generation
- **Inbox Agent** — Email triage, meeting prep, task extraction
- **Deep Work Agent** — Focused coding sessions with minimal distractions
- **Discord Integration** — Send updates, share context, and receive notifications via Discord

### Focus-First Design

Built for how your brain actually works:
- Maximum 2-3 options when presenting choices
- Tasks broken into manageable steps
- Energy-level awareness
- Pattern detection to notice what you miss when overwhelmed

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        VS Code Copilot                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ Planner  │  │ Journal  │  │  Inbox   │  │  Weekly Review   │ │
│  │  Agent   │──│  Agent   │──│  Agent   │──│     Agent        │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘ │
│       │             │             │                  │          │
│       └─────────────┴─────────────┴──────────────────┘          │
│                              │                                   │
│  ┌───────────────────────────┴───────────────────────────────┐  │
│  │                      MCP Servers                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │  │
│  │  │Filesystem│ │  Google  │ │  Google  │ │   Discord    │  │  │
│  │  │ (Vault)  │ │Workspace │ │  Tasks   │ │              │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Obsidian Vault│    │Google Calendar│    │Discord Server │
│  (Local MD)   │    │  Gmail/Tasks  │    │               │
└───────────────┘    └───────────────┘    └───────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **[Obsidian](https://obsidian.md/)** — Free note-taking app (your knowledge base)
- **[VS Code](https://code.visualstudio.com/)** with [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) extension
- **[Node.js](https://nodejs.org/)** 18+ (for MCP servers)
- **[Python](https://www.python.org/)** 3.11+ with `uv` package manager
- **Google Cloud Project** with OAuth 2.0 credentials (for Calendar/Tasks/Gmail)

### Step 1: Install Required Tools

#### Windows

```powershell
# Install Obsidian
winget install Obsidian.Obsidian

# Install VS Code
winget install Microsoft.VisualStudioCode

# Install Node.js
winget install OpenJS.NodeJS.LTS

# Install Python
winget install Python.Python.3.12

# Install uv (Python package manager)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### macOS

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install everything
brew install --cask obsidian visual-studio-code
brew install node python@3.12

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Linux

```bash
# Install Obsidian (AppImage or Snap)
sudo snap install obsidian --classic

# Install VS Code
sudo snap install code --classic

# Install Node.js and Python
sudo apt install nodejs npm python3.12 python3.12-venv

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 2: Fork and Clone

**Fork this repo first** — you'll want your own copy to customize.

1. Click the **Fork** button at the top of this page
2. Clone your fork:

```bash
git clone https://github.com/YOUR-USERNAME/jointhubs.git
cd jointhubs
```

### Step 3: Set Up Obsidian

1. Open Obsidian
2. **Open this repo as your vault** — The entire jointhubs folder IS the Obsidian vault
3. Install recommended plugins:
   - **Templater** — For note templates
   - **Tasks** — For task management
   - **Dataview** — For queries (optional but recommended)

### Vault Structure

The repo is organized as an Obsidian vault:

```
jointhubs/                    # This IS your Obsidian vault
├── .github/                  # Copilot agents & skills (hidden in Obsidian)
├── .obsidian/                # Obsidian config (auto-generated)
├── Operations/               # Day-to-day operations
│   ├── Periodic Notes/       # Daily, Weekly, Monthly, Quarterly
│   │   ├── Daily/            # YYYY-MM-DD.md
│   │   └── Weekly/           # YYYY-Www.md
│   └── Meetings/             # Meeting notes
├── Personal/                 # Personal life tracking
│   ├── Health/               # Training, nutrition logs
│   ├── Finances/             # Financial tracking
│   ├── Events/               # Personal events
│   └── Classes/              # Learning & courses
├── Projects/                 # Professional projects
└── Templater/                # Note templates
```

### Step 4: Configure Google OAuth (Required for Calendar/Tasks/Gmail)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable these APIs:
   - Google Calendar API
   - Gmail API
   - Google Tasks API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download the `client.json` file to the project root

### Step 5: Configure MCP Servers

Create `.vscode/mcp.json` with your credentials:

```jsonc
{
  "servers": {
    "googleWorkspace": {
      "type": "stdio",
      "command": "uvx",
      "args": ["workspace-mcp", "--tool-tier", "core"],
      "env": {
        "GOOGLE_OAUTH_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_OAUTH_CLIENT_SECRET": "your-client-secret",
        "OAUTHLIB_INSECURE_TRANSPORT": "1"
      }
    },
    "discord": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "discord-mcp-mod"],
      "env": {
        "DISCORD_TOKEN": "your-discord-bot-token"
      }
    }
  }
}
```

> 💡 **Discord Setup**: See `.github/skills/discord-integration.md` for how to create a Discord bot and get your token.

### Step 6: First Run

1. Open the project in VS Code
2. Open Copilot Chat (Ctrl+Shift+I)
3. Select an agent from the dropdown (e.g., `@planner`)
4. Ask: "Plan my day"

The first time you use Google services, you'll be prompted to authenticate via browser.

## 🔧 Make It Yours

**This is the most important part.** Jointhubs only works well when it understands *your* context.

### What to Customize

| File | What to Change |
|------|----------------|
| `.github/instructions/assistant.instructions.md` | Your name, projects, hashtags |
| `.github/skills/obsidian-vault.md` | Your folder structure (if different) |
| `.github/agents/*.agent.md` | Agent personalities, handoffs |
| `Templater/` | Your note templates |

### Customization Tips

1. **Add your project tags** — Update `#fenix`, `#neurohubs` to your projects
2. **Personalize templates** — Edit `Templater/*.md` to match your workflow
3. **Tune agent voices** — Want more encouragement? More brevity? Edit the prompts
4. **Add custom skills** — Create new `.md` files in `.github/skills/` for domain knowledge

### Syncing with Upstream

To get updates from the main repo while keeping your customizations:

```bash
# Add the original repo as upstream (one time)
git remote add upstream https://github.com/ORIGINAL-OWNER/jointhubs.git

# Fetch and merge updates
git fetch upstream
git merge upstream/main

# Resolve any conflicts in your customized files
```

## 📁 Project Structure

```
jointhubs/                        # This IS your Obsidian vault
├── .github/                      # Copilot agents & config
│   ├── agents/                   # Agent definitions
│   │   ├── planner.agent.md
│   │   ├── journal.agent.md
│   │   ├── review.agent.md
│   │   ├── inbox.agent.md
│   │   └── deepwork.agent.md
│   ├── instructions/             # Global assistant instructions
│   │   └── assistant.instructions.md
│   └── skills/                   # Domain knowledge
│       ├── obsidian-vault.md
│       ├── focus-support.md
│       ├── weekly-review.md
│       ├── goal-tracking.md
│       └── discord-integration.md
├── .obsidian/                    # Obsidian config (auto-generated)
├── .vscode/
│   └── mcp.json                  # MCP server config (not committed)
├── Operations/                   # Day-to-day operations
│   ├── Periodic Notes/           # Daily, Weekly, Monthly reviews
│   └── Meetings/                 # Meeting notes
├── Personal/                     # Personal life tracking
│   ├── Health/                   # Training, nutrition
│   ├── Finances/                 # Financial tracking
│   ├── Events/                   # Personal events
│   └── Classes/                  # Learning & courses
├── Projects/                     # Professional projects
├── Templater/                    # Note templates
│   ├── Daily.md
│   ├── Weekly.md
│   ├── Monthly.md
│   ├── Quarterly.md
│   ├── Meeting.md
│   ├── Project.md
│   ├── Finances.md
│   ├── Event.md
│   └── Class.md
├── .gitignore
├── LICENSE
└── README.md
```

## 🤖 Agent Guide

### Planner Agent (`@planner`)

Daily and weekly planning assistant.

**Example prompts:**
- "Plan my day"
- "What's my schedule for tomorrow?"
- "Help me prioritize my tasks"
- "Schedule a focus block for deep work"

### Journal Agent (`@journal`)

Pattern recognition and reflection. The "think for me" agent for low-energy days.

**Example prompts:**
- "What patterns do you see in my week?"
- "I'm feeling overwhelmed, help me see what's happening"
- "How am I doing on my goals?"
- "Give me a reflection prompt"

### Review Agent (`@review`)

End-of-week synthesis and insights.

**Example prompts:**
- "Do my weekly review"
- "Summarize this week"
- "What did I accomplish vs plan?"
- "What should I focus on next week?"

### Inbox Agent (`@inbox`)

Email and communication management.

**Example prompts:**
- "Check my inbox for urgent items"
- "Prep me for my next meeting"
- "What emails need a response?"
- "Extract action items from recent emails"

### Deep Work Agent (`@deepwork`)

Focused work sessions with minimal distractions.

**Example prompts:**
- "Start a deep work session"
- "Focus mode for 90 minutes"
- "Help me stay on track with this task"

## 🔒 Security

**Never commit these files:**
- `client.json` — Google OAuth credentials
- `.vscode/mcp.json` — Contains secrets
- `credentials.json` / `token.json` — OAuth tokens

These are already in `.gitignore`.

## 🤔 Why Fork Instead of Clone?

Jointhubs isn't like a typical library you install and use. It's a **personal system** that needs to understand:

- Your folder structure
- Your projects and priorities
- Your energy patterns
- Your preferred communication style

By forking:
- ✅ You own your configuration
- ✅ You can customize freely without conflicts
- ✅ You can still pull updates from upstream
- ✅ Your personal notes stay in your repo (gitignored)
- ✅ You can contribute improvements back

Think of it like a dotfiles repo — everyone's is different, and that's the point.

## 📜 License

MIT License — See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with:
- [Obsidian](https://obsidian.md/) — The knowledge base
- [VS Code GitHub Copilot](https://github.com/features/copilot) — The AI backbone
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) — Tool integration
- [workspace-mcp](https://github.com/ergut/workspace-mcp) — Google Workspace integration
- [discord-mcp-mod](https://www.npmjs.com/package/discord-mcp-mod) — Discord integration

---

**Join your hubs. Think less. Do more.** 🧠
