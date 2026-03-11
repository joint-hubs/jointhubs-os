# Agents Directory

This directory contains agent personality definitions for Jointhubs OS.

## Shared vs Local

- Shared agents that are safe to commit live directly in `.github/agents/`
- Private or experimental agents should live in `.github/agents/local/`
- `.github/agents/local/` is ignored by git, so you can keep personal voice, sensitive workflows, and unstable experiments there

## What is an Agent?

An agent is a specialized AI assistant with:
- **Personality** — Tone, reasoning style, human quirks
- **Responsibilities** — What it owns and what it doesn't
- **Tools** — What capabilities it has
- **Handoffs** — When to pass work to another agent

## Available Agents

### Core Agents

| Agent | Purpose | Select When |
|-------|---------|-------------|
| **[Tech Lead](tech-lead.agent.md)** | Code, architecture, implementation | Building, debugging, architecture decisions |
| **[Planner](planner.agent.md)** | Planning, prioritization, focus sessions | Planning day/week, time blocking, focus time |
| **[Journal](journal.agent.md)** | Reflection, patterns, weekly synthesis | Making sense of what happened, weekly reviews |
| **[Debug](debug.agent.md)** | Systematic debugging | Hunting bugs, root cause analysis |
| **[Designer](designer.agent.md)** | UX, visual design, user empathy | Interface review, design decisions |

### Specialized Agents

Create your own agents for specific domains. Examples:

| Agent | Purpose | Select When |
|-------|---------|-------------|
| Scraper | Web scraping, data extraction | Building scrapers |
| Business Lead | Strategic decisions, market analysis | Business planning |
| Project Lead | Product decisions for a specific project | Deep project work |

See **[_TEMPLATE.agent.md](_TEMPLATE.agent.md)** to create your own.

### Shared Domain Agents In This Repo

These are the currently shared, domain-specific agents that remain in the repo:

| Agent | Purpose |
|-------|---------|
| [Travel Planner](travel.agent.md) | Travel research and trip planning |
| [Investor](investor.agent.md) | Stock and investment research |

## Local-Only Agents

Use `.github/agents/local/` when an agent is:

- Personal to your workflow or voice
- Tied to sensitive clients, notes, or internal context
- Still experimental and not ready to share

If an agent becomes stable and generally useful, move it from `local/` into `.github/agents/` and add it to this README.

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

1. Decide whether the agent is `shared` or `local`
2. Copy `_TEMPLATE.agent.md` to `{your-agent}.agent.md` for shared agents, or to `local/{your-agent}.agent.md` for private agents
3. Fill in the sections (soul and personality first)
4. Define tools and handoffs
5. Add shared agents to this README
6. Update any shared registry docs only for shared agents

### Project-Specific Agents

You can create agents scoped to specific projects:

```
Second Brain/Projects/{project-name}/.github/agents/
└── {project-agent}.agent.md
```

These inherit global context but have project-specific knowledge.

For private project agents that should not be committed, prefer `.github/agents/local/` or a project-local path that is ignored by git.

---

*See `_TEMPLATE.agent.md` for the full template with documentation.*

## All Agents Share

Every agent should:

1. **Check daily log** at session start
2. **Read CONTEXT.md** when working on a project
3. **Update relevant files** as they work
