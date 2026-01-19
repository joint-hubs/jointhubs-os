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
│   ├── tech-lead.agent.md       ← Code, architecture, building
│   ├── planner.agent.md         ← Scheduling, prioritization
│   ├── journal.agent.md         ← Reflection, patterns
│   ├── review.agent.md          ← Weekly synthesis
│   ├── deepwork.agent.md        ← Focus sessions
│   └── inbox.agent.md           ← Communication triage
├── instructions/
│   ├── README.md                ← Instructions overview
│   ├── projects.instructions.md ← Rules for Projects/ directory
│   └── operations.instructions.md ← Rules for Operations/ directory
└── skills/
    ├── README.md                ← Skills overview
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
