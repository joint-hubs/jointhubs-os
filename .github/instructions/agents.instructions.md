---
applyTo: '.github/agents/**'
---

# Agents Directory Instructions

> Auto-loaded when working in `.github/agents/`

## What This Is

Agent definitions — the personalities, tools, and behaviors of each AI agent.

## File Format

```markdown
---
name: Agent Name
description: One-line description
tools: ['tool1', 'tool2']
handoffs:
  - label: Handoff Label
    agent: target-agent
    prompt: Context to pass
---

# Agent Name Agent

{Personality and behavior definition}
```

## Rules

1. **Keep agents lean** — personality + core behavior only
2. **Put knowledge in skills** — link to `.github/skills/`
3. **Define clear boundaries** — what this agent does/doesn't do
4. **Personality should feel human** — quirks, voice, tone
5. **Use `local/` for private agents** — keep personal or experimental agents out of the shared root

## Template

Copy `_TEMPLATE.agent.md` to create new agents.

## Related

- [agentic-engineering skill](../skills/agentic-engineering/SKILL.md)
