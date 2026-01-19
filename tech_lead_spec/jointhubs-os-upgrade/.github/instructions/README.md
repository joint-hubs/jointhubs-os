# Instructions Directory

This directory contains context-specific instructions that apply to particular directories or situations.

## What are Instructions?

Instructions are rules that apply based on context:
- **Directory-scoped** — Apply only in specific folders
- **Situation-scoped** — Apply in specific scenarios

Unlike agents (personality) and skills (knowledge), instructions are **rules**.

## Available Instructions

| Instruction | Scope | Purpose |
|-------------|-------|---------|
| **[projects.instructions.md](projects.instructions.md)** | `Projects/**` | How to work in project directories |
| **[operations.instructions.md](operations.instructions.md)** | `Operations/**` | How to handle operational tasks |

## How Instructions Work

Instructions use the `applyTo` frontmatter to specify when they apply:

```yaml
---
applyTo: "Projects/**"
---
```

When the user is working in a matching directory, these instructions are active.

## Creating New Instructions

1. Create `{scope}.instructions.md` in this directory
2. Add `applyTo` frontmatter with glob pattern
3. Write the instruction rules
4. Add to this README
