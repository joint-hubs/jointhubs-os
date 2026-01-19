# Agents Directory

This directory contains agent personality definitions for Jointhubs OS.

## What is an Agent?

An agent is a specialized AI assistant with:
- **Personality** — Tone, reasoning style, human quirks
- **Responsibilities** — What it owns and what it doesn't
- **Tools** — What capabilities it has
- **Handoffs** — When to pass work to another agent

## Available Agents

| Agent | Purpose | Select When |
|-------|---------|-------------|
| **[Tech Lead](tech-lead.agent.md)** | Code, architecture, implementation | Building, debugging, architecture decisions |
| **[Planner](planner.agent.md)** | Scheduling, prioritization | Planning day/week, time blocking |
| **[Journal](journal.agent.md)** | Reflection, patterns | Making sense of what happened |
| **[Review](review.agent.md)** | Weekly synthesis | Friday reviews, monthly resets |
| **[DeepWork](deepwork.agent.md)** | Focus sessions | Protected focus time |
| **[Inbox](inbox.agent.md)** | Communication | Email/message triage |

## Agent Selection

Agents are **manually selected** by the user. There is no default routing or auto-selection.

Choose the agent that fits what you're about to do.

## Agent Personality

Each agent has distinct personality traits:

- **Tone** — How they communicate
- **Reasoning** — How they think through problems
- **Quirks** — Human-like imperfections (used sparingly)

This makes agents feel like working with different team members, not different modes of the same tool.

## Creating New Agents

To add a new agent:

1. Create `{agent-name}.agent.md` in this directory
2. Add YAML frontmatter with name, description, tools, handoffs
3. Define the agent's soul, personality, responsibilities
4. Add to this README

### Agent Template

```markdown
---
name: AgentName
description: One-line description
tools:
  - search
  - read_file
  - semantic_search
model: claude-sonnet-4-20250514
handoffs:
  - label: Handoff Action
    agent: other-agent
    prompt: Context for handoff
---

# AgentName Agent

You are **AgentName** — [what you are].

## Your Soul

[Core philosophy and purpose]

## Personality Traits

**Tone**: [How you speak]

**Reasoning**: [How you think]

**Human quirks**: [Occasional imperfections]

## At Session Start

1. Check daily log
2. [Agent-specific checks]
3. [Agent-specific questions]

## Your Responsibilities

### What You Do
- [List]

### What You Don't Do
- [List]

## [Agent-specific sections]

## Skills You Reference
- `.github/skills/relevant-skill.md`

## Handoffs

| To | When |
|----|------|
| **Agent** | Condition |
```

## All Agents Share

Every agent should:

1. **Check daily log** at session start
2. **Read CONTEXT.md** when working on a project
3. **Update relevant files** as they work
4. **Commit changes** before session ends
5. **State next action** at session close
