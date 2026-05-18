# Instructions Directory

> ← [Back to Jointhubs OS](../../README.md)

This directory contains context-specific instructions that apply to particular directories or situations.

## What are Instructions?

Instructions are rules that apply based on context:
- **Directory-scoped** — Apply only in specific folders
- **Situation-scoped** — Apply in specific scenarios

Unlike agents (personality) and skills (knowledge), instructions are **rules**.

## Shared vs Local

- Shared instructions that define repo behavior live directly in `.github/instructions/`
- Private or machine-specific instructions should live in `.github/instructions/local/`
- `.github/instructions/local/` is ignored by git, so you can keep personal constraints and experiments there

## Available Instructions

| Instruction | Scope | Purpose |
|-------------|-------|---------|
| **[assistant](assistant.instructions.md)** | Global | Base Jointhubs instructions, vault structure |
| **[graphify](graphify.instructions.md)** | Global when `graphify-out/` exists | Use graph outputs as a fast context map before deep reading |
| **[jointhubs](jointhubs.instructions.md)** | `Second Brain/Projects/jointhubs/**` | Prefer strategic vs implementation graphs appropriately inside Jointhubs |
| **[projects](projects.instructions.md)** | `Second Brain/Projects/**` | Working in project directories |
| **[operations](operations.instructions.md)** | `Second Brain/Operations/**` | Operational tasks, daily notes |
| **[health](health.instructions.md)** | `Second Brain/Personal/Health/**` | Health tracking |
| **[agents](agents.instructions.md)** | `.github/agents/**` | Agent definitions |
| **[skills](skills.instructions.md)** | `.github/skills/**` | Skill knowledge files |

Project-specific or private instructions that should not be shared upstream belong in `local/`.

## Instruction Layers

| Layer | Purpose |
|-------|---------|
| Global | Shared rules for the whole vault and repo |
| Directory-scoped | Shared rules for folders like Operations or Projects |
| Project-specific | Rules for a single project such as Fenix or Neurohubs |
| Local | Private rules for your workflow, machine, or experimental setup |

## How Instructions Work

Instructions use the `applyTo` frontmatter to specify when they apply:

```yaml
---
applyTo: "Second Brain/Projects/**"
---
```

When the user is working in a matching directory, these instructions are active.

## Creating New Instructions

1. Decide whether the instruction is `shared` or `local`
2. Create `{scope}.instructions.md` in this directory for shared rules, or in `local/` for private rules
3. Add `applyTo` frontmatter with glob pattern
4. Write the instruction rules
5. Add to this README only for shared instructions

## When To Keep Instructions Local

- The rule encodes personal preferences you do not want upstream
- The rule is tied to local secrets, tools, or machine setup
- The rule is experimental and still being tested

### Instruction Template

```markdown
---
applyTo: "Path/Pattern/**"
---

# [Scope] Directory Instructions

> These instructions apply when [context].

## Purpose

[What this instruction set covers]

## Rules

[The actual instructions]

## Templates

[Any templates relevant to this context]

## Git Conventions

[How to commit changes in this context]
```

---

## Navigation

| Where | What |
|-------|------|
| ← [Jointhubs OS](../../README.md) | System overview |
| → [Agents](../agents/README.md) | Agent personalities |
| → [Skills](../skills/README.md) | Knowledge vs rules |
| → [Prompts](../prompts/README.md) | One-command workflows |
