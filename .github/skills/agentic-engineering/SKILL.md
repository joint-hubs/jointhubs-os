# Agentic Engineering Skill

> Domain knowledge for building and maintaining the Jointhubs agentic AI system.

## System Architecture

The Jointhubs ecosystem is built from composable components:

| Component | Location | Purpose |
|-----------|----------|---------|
| **Agents** | `.github/agents/*.agent.md` | Define personalities, tools, handoffs |
| **Skills** | `.github/skills/*/SKILL.md` | Domain knowledge loaded on-demand |
| **MCP Servers** | `.vscode/mcp.json` | External integrations (googleWorkspace, etc.) |
| **Instructions** | `.github/instructions/*.md` | Global and directory specific assistant behavior rules |

## Key Distinction

| Other Agents | Tech Lead |
|--------------|-----------|
| Help user via chat conversation | Build and improve the system itself |
| Use repo contents as context | Write and modify repo contents |
| Think: "What answer helps?" | Think: "What code/tool/agent solves this?" |
| Consume MCP tools and skills | Create and maintain MCP tools and skills |

## When To Create Components

### Create a new **Agent** when:
- User needs a distinct persona for a specific domain
- Different tool access is required
- Handoffs between contexts make sense

### Create a new **MCP Server** when:
- External data source needs agent access
- Complex logic needs to run server-side
- API integration is required

### Create a new **Skill** when:
- Domain knowledge should be shared across agents
- Procedures need documentation for agents to follow
- System context needs to be captured

## Technical Stack

| Layer | Technologies |
|-------|-------------|
| Backend | Python, FastAPI, Firebase |
| Frontend | TypeScript, React, Next.js |
| Data | PostgreSQL, ChromaDB, Firestore |
| AI/ML | LLMs, embeddings, RAG patterns |
| Infra | Docker, GCP, Vercel |

## Environment Standards

```bash
# Python projects
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# TypeScript projects
npm install  # uses node_modules/

# MCP Servers (Python)
uv venv
uv pip install -r requirements.txt
```

## Development Process

### Task Management

For complex work, create task files:

```
Second Brain/Projects/{project}/tasks/
├── feature-x.md          ← In progress
├── bug-fix-y.md          ← In progress
└── done/
    └── completed-task.md ← Finished
```

### Task File Template

```markdown
# Task: {Title}

## Date
YYYY-MM-DD

## Context
Why this task exists, what problem it solves.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Hints
Implementation guidance, gotchas.

## Notes
Learnings during implementation.
```

## Philosophy

> "Everything should be made as simple as possible, but not simpler." — Einstein

- Start with the simplest solution that could work
- Add complexity only when data proves it's needed
- Question assumptions constantly
- Measure everything that matters

## Tools Reference

| Tool | Purpose |
|------|---------|
| `github/*` | Read/write code, issues, PRs |
| `vscode` | Execute code, terminals |
| `playwright/*` | Test web applications |
| `agent` | Spawn sub-agents for research |
| `todo` | Track session tasks |

## Related Skills

- [project-context](../project-context/SKILL.md) — Project state management
- [daily-log](../daily-log/SKILL.md) — Session logging
- [obsidian-vault](../obsidian-vault/SKILL.md) — Vault conventions

## External References

- [VS Code: Custom agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
- [VS Code: Prompt files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)
- [VS Code: Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- [VS Code: Custom instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
- [VS Code: MCP servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
- [Anthropic: Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Agent Skills standard](https://agentskills.io/)
