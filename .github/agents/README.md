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
| **[Designer](designer.agent.md)** | UX, visual design, user empathy | Interface review, design decisions |
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

Use **[_TEMPLATE.agent.md](_TEMPLATE.agent.md)** to create your own agents.

### Steps

1. Copy `_TEMPLATE.agent.md` to `{your-agent}.agent.md`
2. Fill in the sections (soul and personality first)
3. Define tools and handoffs
4. Add to this README
5. Update `copilot-instructions.md` agent table

### Project-Specific Agents

You can create agents scoped to specific projects:

```
Projects/{project-name}/.github/agents/
└── {project-agent}.agent.md
```

These inherit global context but have project-specific knowledge.

---

*See `_TEMPLATE.agent.md` for the full template with documentation.*

## All Agents Share

Every agent should:

1. **Check daily log** at session start
2. **Read CONTEXT.md** when working on a project
3. **Update relevant files** as they work
