# Agent System Maintenance Guide

> How to create, update, and maintain agents, skills, prompts, and instructions.

## Overview

The agent system has four components:

| Component | Purpose | Location | When Used |
|-----------|---------|----------|-----------|
| **Agents** | AI personas with personality | `.github/agents/` | Selected by user for a session |
| **Skills** | Domain knowledge | `.github/skills/` | Loaded on-demand when relevant |
| **Prompts** | Reusable workflows | `.github/prompts/` | Triggered with `/name` in chat |
| **Instructions** | Always-on rules | `.github/instructions/` | Auto-applied based on file patterns |

```
.github/
├── agents/           ← Personas (Tech Lead, Designer, etc.)
├── skills/           ← Knowledge packs (daily-log, project-context, obsidian-markdown, obsidian-bases, json-canvas)
├── prompts/          ← Workflows (/commit, /weekly-review)
├── instructions/     ← Rules (apply to Projects/**, etc.)
├── README_github.md  ← Folder overview
└── AGENT_MAINTENANCE.md  ← Maintenance guide
```

---

## Agents

### What is an Agent?

An agent is a specialized AI persona with:
- **Personality** — Tone, reasoning style, quirks
- **Tools** — What capabilities it has access to
- **Handoffs** — When to suggest switching to another agent

### File Format

```markdown
---
name: Agent Name
description: When to use this agent
tools: ['read', 'edit', 'search', 'web', 'todo']
argument-hint: Optional placeholder text for chat input
handoffs:
  - label: Button Text
    agent: other-agent
    prompt: What to say when switching
    send: false
---

# Agent Name

Personality and behavior instructions here...
```

### Creating a New Agent

1. Copy `_TEMPLATE.agent.md` to `{name}.agent.md`
2. Define the soul and personality first
3. List tools (only what's needed)
4. Add handoffs to related agents
5. Update `.github/agents/README.md`
6. Update any shared registry docs if you keep them

### Available Tools

| Tool | Purpose |
|------|---------|
| `read` | Read files |
| `edit` | Modify files |
| `search` | Search codebase |
| `web` | Browse web |
| `execute` | Run terminal commands |
| `todo` | Manage todo list |
| `agent` | Spawn subagents |
| `github/*` | GitHub operations |
| `mcp_*` | MCP server tools |

### Best Practices

- **Personality first**: Define *who* before *what*
- **Minimal tools**: Only grant tools the agent actually needs
- **Clear handoffs**: Make transitions to other agents smooth
- **Test the voice**: Run a few conversations, adjust tone

### When to Update

- Agent behavior feels wrong → adjust personality section
- Missing capability → add tool
- Awkward transitions → update handoffs
- New related agent created → add handoff

---

## Skills

### What is a Skill?

A skill is a folder of knowledge that agents load on-demand. Skills include:
- Instructions (SKILL.md)
- Templates
- Examples
- Scripts

### File Structure

```
.github/skills/{skill-name}/
├── SKILL.md          # Required: metadata + instructions
├── template.md       # Optional: template files
├── examples/         # Optional: example content
└── scripts/          # Optional: automation
```

### SKILL.md Format

```markdown
---
name: skill-name
description: |
  What this skill does.
  Use when: "trigger phrase 1", "trigger phrase 2".
---

# Skill Name

Instructions for how to use this skill...

## When to Use

List trigger scenarios...

## Procedure

Step-by-step instructions...
```

### Creating a New Skill

1. Create folder: `.github/skills/{skill-name}/`
2. Create `SKILL.md` with frontmatter and instructions
3. Add templates/resources as needed
4. Update `.github/skills/README.md`
5. Update any shared registry docs if you keep them

### Progressive Loading

Skills use three-level loading:

1. **Discovery** — Agent reads `name` and `description` only
2. **Loading** — When relevant, full SKILL.md loads
3. **Resources** — Templates/scripts load only when referenced

This means many skills with minimal context cost.

### Progressive Disclosure Patterns

The context window is a shared resource. Use these patterns to minimize bloat:

**Pattern 1: High-level guide with references**
```markdown
# PDF Processing

## Quick start
Basic example here...

## Advanced features
- **Forms**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md)
```

**Pattern 2: Domain-specific organization**
```
skill-name/
├── SKILL.md (overview + navigation)
└── references/
    ├── domain-a.md
    ├── domain-b.md
    └── domain-c.md
```

**Pattern 3: Conditional details**
Show basic content, link to advanced:
```markdown
## Basic Usage
Do the simple thing.

**For advanced use**: See [ADVANCED.md](ADVANCED.md)
```

**Guidelines:**
- Keep SKILL.md under 500 lines
- Avoid deeply nested references (max 1 level)
- Structure longer files with table of contents
- Split by domain when supporting multiple variants

### Best Practices

- **Clear triggers**: List when the skill should activate
- **Standalone**: Skills should work without other skills
- **Templates**: Include ready-to-use templates when relevant
- **Update live**: If you learn something, add it to the skill

### When to Update

- Missing knowledge → add to instructions
- Common question → add FAQ section
- Pattern discovered → document it
- Template outdated → update template

---

## Prompts

### What is a Prompt?

A prompt is a reusable workflow triggered by typing `/name` in chat. Unlike agents (personas) or skills (knowledge), prompts are **action-oriented**.

### File Format

```markdown
---
name: prompt-name
description: What this prompt does
agent: which-agent-to-use
tools: ['read', 'edit', 'search']
argument-hint: Placeholder text shown to user
handoffs:
  - label: Next Step
    agent: next-agent
    prompt: Continue with...
    send: false
---

# Prompt Title

Step-by-step instructions for the workflow...
```

### Creating a New Prompt

1. Create: `.github/prompts/{name}.prompt.md`
2. Add frontmatter (name, description, agent, tools)
3. Write step-by-step instructions
4. Add handoffs for follow-up actions
5. Update `.github/prompts/README.md`

### Best Practices

- **One purpose**: Each prompt does one thing well
- **Clear steps**: Numbered, actionable instructions
- **Agent alignment**: Use the right agent for the task
- **Minimal tools**: Only what the workflow needs
- **Handoffs**: Chain to next logical action

### Common Patterns

**Session bookends**: Start/end rituals
- `/daily-kickoff` → `/session-end`

**Planning flows**: Plan → execute → review
- `/plan-week` → work → `/weekly-review`

**Project lifecycle**: Create → update → status
- `/new-project` → `/context-update` → `/project-status`

### When to Update

- Workflow feels incomplete → add missing step
- Common follow-up action → add handoff
- Step is confusing → clarify instructions
- New tool available → incorporate if useful

---

## Instructions

### What are Instructions?

Instructions are rules that auto-apply based on file patterns. Unlike prompts (on-demand) or agents (session-wide), instructions apply **automatically** when editing matching files.

### File Format

```markdown
---
applyTo: "path/pattern/**"
---

# Instructions Title

Rules that apply when editing files matching the pattern...
```

### Creating New Instructions

1. Create: `.github/instructions/{name}.instructions.md`
2. Set `applyTo` glob pattern in frontmatter
3. Write rules and guidelines
4. Update `.github/instructions/README.md`

### applyTo Patterns

| Pattern | Matches |
|---------|---------|
| `**` | All files |
| `*.py` | Python files at root |
| `**/*.py` | All Python files |
| `src/**` | All files in src/ |
| `Second Brain/Projects/**` | All project files |

### Best Practices

- **Specific patterns**: Don't use `**` unless truly global
- **Short rules**: Keep instructions concise
- **No overlap**: Avoid conflicting instructions
- **Test patterns**: Verify the pattern matches correctly

### When to Update

- Rule doesn't apply when expected → fix pattern
- Missing guideline → add rule
- Rule causes issues → refine or remove

---

## Global Instructions

### Shared Registry Docs

This repo currently uses:
- `.github/README_github.md` for high-level orientation
- `.github/agents/README.md` for shared agent registry
- `.github/skills/README.md` for shared skill registry
- `.github/prompts/README.md` for shared prompt registry
- `.github/instructions/README.md` for shared instruction registry

### When to Update

- New shared agent added → update `.github/agents/README.md`
- New shared skill added → update `.github/skills/README.md`
- New shared prompt added → update `.github/prompts/README.md`
- New shared instruction added → update `.github/instructions/README.md`

---

## Maintenance Checklist

### Weekly (Friday review)

- [ ] Any agent personality adjustments needed?
- [ ] Any missing prompts for common workflows?
- [ ] Any skill knowledge gaps discovered?

### After Creating New Content

- [ ] Update relevant README.md files
- [ ] Update shared registry files if needed
- [ ] Test the new component in a conversation
- [ ] Commit with descriptive message

### Quarterly

- [ ] Review all agents for relevance
- [ ] Prune unused prompts
- [ ] Update skills with learned patterns
- [ ] Check for outdated references

---

## Troubleshooting

### Agent not behaving correctly

1. Check if tools list is correct
2. Review personality section — is it clear?
3. Test in isolation (new chat)
4. Check for conflicting instructions

### Skill not loading

1. Verify SKILL.md exists with correct frontmatter
2. Check description includes trigger phrases
3. Try explicit mention: "use the daily-log skill"
4. Check for syntax errors in frontmatter

### Prompt not appearing

1. Verify file is in `.github/prompts/`
2. Check file extension is `.prompt.md`
3. Verify frontmatter has `name` and `description`
4. Restart VS Code / reload window

### Instructions not applying

1. Check `applyTo` pattern matches the file path
2. Verify pattern uses forward slashes (even on Windows)
3. Check for syntax errors in frontmatter
4. Test with simpler pattern first

---

## File Naming Conventions

| Type | Format | Example |
|------|--------|---------|
| Agent | `{name}.agent.md` | `tech-lead.agent.md` |
| Skill folder | `{name}/` | `daily-log/` |
| Skill file | `SKILL.md` | `SKILL.md` |
| Prompt | `{name}.prompt.md` | `weekly-review.prompt.md` |
| Instructions | `{name}.instructions.md` | `projects.instructions.md` |

All names: lowercase, hyphenated, no spaces.

---

## Git Commit Conventions

```bash
# Agent changes
git commit -m "agents: add new designer agent"
git commit -m "agents: update planner handoffs"

# Skill changes
git commit -m "skills: add design-review templates"
git commit -m "skills: update daily-log procedure"

# Prompt changes
git commit -m "prompts: add weekly-review workflow"
git commit -m "prompts: fix commit message format"

# Instruction changes
git commit -m "instructions: add python-specific rules"
git commit -m "instructions: update project patterns"
```

---

## Related Resources

- [Agents README](.github/agents/README.md)
- [Skills README](.github/skills/README.md)
- [Prompts README](.github/prompts/README.md)
- [Instructions README](.github/instructions/README.md)
- [VS Code Agent Skills Docs](https://code.visualstudio.com/docs/copilot/copilot-customization)
- [Awesome Copilot Examples](https://github.com/github/awesome-copilot)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
