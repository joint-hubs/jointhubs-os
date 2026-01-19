# Jointhubs OS Agent Framework Upgrade

> Applying Fenix patterns to jointhubs-os for project progression

## Overview

This folder contains a complete upgrade to the jointhubs-os `.github/` agent framework. It introduces:

1. **Daily log as memory** — Every conversation starts by checking the daily log
2. **Project-focused** — All work is about moving projects forward
3. **CONTEXT.md pattern** — Each project has past/current/future state
4. **Human-like agents** — Personalities with tone, reasoning style, and quirks
5. **Directory-scoped instructions** — Rules that apply in specific folders

## Structure

```
.github/
├── copilot-instructions.md      ← Global rules (daily log check, etc.)
├── agents/
│   ├── README.md                ← Agent overview
│   ├── _TEMPLATE.agent.md       ← Template for custom agents
│   ├── tech-lead.agent.md       ← Code, architecture, building
│   ├── designer.agent.md        ← UX, visual design, user empathy
│   ├── planner.agent.md         ← Scheduling, prioritization
│   ├── journal.agent.md         ← Reflection, patterns
│   ├── review.agent.md          ← Weekly synthesis
│   ├── deepwork.agent.md        ← Focus sessions
│   └── inbox.agent.md           ← Communication triage
├── instructions/
│   ├── README.md                ← Instructions overview
│   ├── _TEMPLATE.instructions.md ← Template for custom instructions
│   ├── projects.instructions.md ← Rules for Projects/ directory
│   └── operations.instructions.md ← Rules for Operations/ directory
└── skills/
    ├── README.md                ← Skills overview
    ├── _TEMPLATE.skill.md       ← Template for custom skills
    ├── daily-log.md             ← Daily logging conventions
    └── project-lifecycle.md     ← How projects move from idea to done
```

## Key Changes from Current jointhubs-os

| Current | Upgraded |
|---------|----------|
| Agents have function descriptions | Agents have personality ("soul") |
| No session start protocol | Always check daily log first |
| Personal productivity focus | Project progression focus |
| Flat skills | Skills + directory instructions |
| No project state tracking | CONTEXT.md pattern |

## How to Apply

### Option A: Replace .github/ entirely

1. Back up existing `.github/`
2. Copy this `.github/` folder to jointhubs-os
3. Merge in existing skills (obsidian-vault.md, etc.)
4. Test with each agent

### Option B: Incremental upgrade

1. Add `copilot-instructions.md` (update existing)
2. Update each agent with personality sections
3. Add new skills (daily-log.md, project-lifecycle.md)
4. Add instructions files

## Files to Keep from Current jointhubs-os

These existing files should be preserved/merged:

- `.github/skills/obsidian-vault.md` — Vault navigation
- `.github/skills/focus-support.md` — Focus strategies
- `.github/skills/weekly-review.md` — Review process
- `.github/skills/goal-tracking.md` — Goal management
- `.github/skills/discord-integration.md` — Discord MCP

## Sample Daily Log Location

Create this folder structure:

```
Operations/Periodic Notes/
├── Daily/
│   └── 2026-01-19.md
├── Weekly/
│   └── 2026-W03.md
└── Monthly/
    └── 2026-01.md
```

## Sample Project Structure

```
Projects/
└── my-project/
    ├── README.md
    ├── CONTEXT.md          ← The key addition
    └── tasks/
        ├── 01-first-task.md
        └── done/
```

## Testing

After applying:

1. Start a conversation with Tech Lead
2. Verify it asks about daily log
3. Navigate to a project
4. Verify it reads CONTEXT.md
5. Test handoffs between agents

---

## Extensibility

### Adding Custom Agents

Use the template to create project-specific or personal agents:

```bash
# Copy template
cp .github/agents/_TEMPLATE.agent.md .github/agents/my-agent.agent.md

# Or create project-specific agent
mkdir -p Projects/my-project/.github/agents
cp .github/agents/_TEMPLATE.agent.md Projects/my-project/.github/agents/specialist.agent.md
```

### Adding Custom Skills

Domain knowledge for specific projects or topics:

```bash
cp .github/skills/_TEMPLATE.skill.md .github/skills/my-domain.md
```

### Adding Directory Instructions

Rules that apply to specific folders:

```bash
cp .github/instructions/_TEMPLATE.instructions.md .github/instructions/my-context.instructions.md
```

Set the `applyTo` pattern to match your directory.

---

## Templates

| Template | Purpose |
|----------|---------|
| `_TEMPLATE.agent.md` | Create new agents |
| `_TEMPLATE.skill.md` | Create new skills |
| `_TEMPLATE.instructions.md` | Create directory instructions |
| `templates/DAILY_LOG.md` | Daily log structure |
| `templates/PROJECT_CONTEXT.md` | Project CONTEXT.md |
| `templates/PROJECT_README.md` | Project README |
