# Jointhubs OS

<p align="center">
  <img src=".github/assets/jointhubs.png" alt="Jointhubs" width="450">
</p>

> **Your AI-powered Second Brain.** A multi-agent VS Code Copilot system built on Obsidian.

Fork it. Personalize it. Let AI agents that actually *know you* handle the grind: planning your week, reviewing your code, journaling your progress, managing your projects.

**Your brain works differently. Your AI assistant should too.**

---

## Why Jointhubs OS?

Most AI tools give you a blank chat window and wish you luck. Jointhubs OS gives you a **team of specialized agents** that read your notes, understand your projects, and remember what happened yesterday.

This is a **starter kit**, not a finished product. The agents, skills, prompts, and vault structure are all designed to be changed. Delete what you don't need, add what you do, reshape it around how *you* think and work.

- **7 agents**, each with a distinct personality and purpose
- **8 skills** with domain knowledge agents load when needed
- **13 prompts** for daily kickoff, commits, reviews, and more
- **Directory-scoped instructions** that apply automatically based on what you're working on
- **MCP integrations** to connect Google Workspace, web search, and other tools
- **100% yours**: fork, customize, extend. Your notes stay local, your AI stays personal

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                      VS Code Copilot                        │
│                                                             │
│  ┌──────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐        │
│  │Tech Lead │ │ Planner │ │ Journal │ │ Designer │  ...    │
│  └────┬─────┘ └────┬────┘ └────┬────┘ └────┬─────┘        │
│       └─────────────┴──────────┴────────────┘              │
│                         │                                   │
│            reads/writes │ your notes                        │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Second Brain/                       │  │
│  │    Operations/ ── Personal/ ── Projects/             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
          │
          │ MCP
          ▼
   ┌─────────────────────────────┐
   │   External Services (MCP)   │
   │   Google Workspace, etc.    │
   └─────────────────────────────┘
```

Agents maintain continuity through **daily logs**. They read yesterday's notes, pick up context, and keep working where you left off.

---

## Quick Start

```bash
# 1. Fork & clone
git clone https://github.com/YOUR_USERNAME/jointhubs-os.git
cd jointhubs-os

# 2. Open as an Obsidian vault (the repo IS your vault)

# 3. Configure MCP (optional)
cp .vscode/mcp.json.example .vscode/mcp.json
# Add your credentials to .vscode/mcp.json

# 4. Open in VS Code → Copilot Chat → Pick an agent → Go
```

> **Detailed setup:** [Repo Init Guide](Second%20Brain/Operations/Docs/repo-init/README.md) · [AI Development Guide](Second%20Brain/Operations/Docs/ai-development/README.md)

---

## Agents

Specialized personas you select in Copilot Chat. Each brings a different mindset to your work.

| Agent | Purpose |
|-------|---------|
| **Tech Lead** | Code, architecture, system design, debugging |
| **Planner** | Daily/weekly planning, prioritization, focus sessions |
| **Journal** | Reflection, pattern recognition, knowledge synthesis |
| **Designer** | UX review, accessibility, interface critique |
| **Debug** | Systematic bug investigation and resolution |
| **Investor** | Stock research, due diligence, scenario modeling |
| **Travel Planner** | Trip planning, accommodation research, itineraries |

Create your own: copy `_TEMPLATE.agent.md` → customize → done.

## Skills

Domain knowledge that agents load automatically when relevant.

| Skill | What It Teaches |
|-------|-----------------|
| **daily-log** | Daily note format, session continuity |
| **weekly-review** | Weekly reflection and planning process |
| **obsidian-vault** | Vault structure, naming, frontmatter, tags |
| **project-context** | Project lifecycle with `CONTEXT.md` pattern |
| **strategic-thinking** | Decision frameworks, trade-offs, scenarios |
| **design-review** | Design checklists, accessibility standards |
| **travel-research** | Accommodation, flights, travel deal strategies |
| **agentic-engineering** | Building agents, skills, and prompts |

## Prompts

One-command workflows. Type `/prompt-name` in Copilot Chat.

| Prompt | What It Does |
|--------|--------------|
| `/daily-kickoff` | Start your day with context and priorities |
| `/session-end` | Wrap up, log progress, set tomorrow's focus |
| `/weekly-review` | Weekly reflection and planning |
| `/commit` | Smart commit message generation |
| `/deep-work` | Set up a focused work session |
| `/design-review` | Run a UX/accessibility audit |
| `/project-status` | Get project status from `CONTEXT.md` |
| `/quick-capture` | Fast note capture |
| `/new-project` | Scaffold a new project |
| `/context-update` | Update project context |
| `/breakdown` | Break a task into steps |
| `/beast-mode` | Maximum intensity mode |
| `/new-scraper` | Generate a web scraper |

---

## Project Structure

```
jointhubs-os/
├── .github/
│   ├── agents/              ← Agent personalities (.agent.md)
│   ├── skills/              ← Domain knowledge (SKILL.md per folder)
│   ├── prompts/             ← One-command workflows (.prompt.md)
│   ├── instructions/        ← Directory-scoped rules
│   └── copilot-instructions.md
├── Second Brain/            ← YOUR NOTES (Obsidian vault)
│   ├── Operations/          ← Daily logs, meetings, docs
│   ├── Personal/            ← Health, finances, events
│   └── Projects/            ← Active work with CONTEXT.md
└── README.md
```

### What Goes Where

| Layer | Path | Purpose |
|-------|------|---------|
| **Agents** | `.github/agents/*.agent.md` | Who does the work: personalities and tool access |
| **Skills** | `.github/skills/*/SKILL.md` | What they know: domain knowledge loaded on demand |
| **Prompts** | `.github/prompts/*.prompt.md` | Repeatable workflows triggered with `/name` |
| **Instructions** | `.github/instructions/*.instructions.md` | Rules auto-applied by file path |
| **Notes** | `Second Brain/` | Your notes, read and written by agents for context |

---

## Customization

This is **your** system. Customize everything.

### The Agent Contract

When you change your notes, update the agents so they can still find things:

| You Changed | Update This |
|-------------|-------------|
| Folder paths | `.github/skills/obsidian-vault/SKILL.md` |
| Daily log format | `.github/skills/daily-log/SKILL.md` |
| Project structure | `.github/skills/project-context/SKILL.md` |
| New conventions | `.github/instructions/*.instructions.md` |

### Local / Private Configuration

Every customization layer has a `local/` subfolder for private files that won't be committed:

- `.github/agents/local/` - Private agents
- `.github/skills/local/` - Private skills
- `.github/prompts/local/` - Private prompts
- `.github/instructions/local/` - Private instructions
- `.vscode/mcp.json` - Your MCP credentials (gitignored)

---

## Documentation

| README | What's Inside |
|--------|---------------|
| [Second Brain](Second%20Brain/README.md) | Note structure, conventions, customization strategies |
| [Agents](.github/agents/README.md) | Agent catalog and how to create your own |
| [Skills](.github/skills/README.md) | Skill catalog and authoring guide |
| [Prompts](.github/prompts/README.md) | Available prompts and how to create them |
| [Instructions](.github/instructions/README.md) | Directory-scoped rules and patterns |
| [Operations Docs](Second%20Brain/Operations/Docs/README.md) | Setup guides and AI development reference |

---

## Contributing

Jointhubs OS is open source under the MIT license. We welcome new agents, skills, and prompts. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT. See [LICENSE](LICENSE)

---

**Your brain, your agents, your rules.** Fork it and make it yours. 🧠
