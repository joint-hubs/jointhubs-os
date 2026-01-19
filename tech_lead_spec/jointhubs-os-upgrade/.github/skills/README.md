# Skills Directory

Skills are domain knowledge documents that agents reference for specialized guidance.

## What is a Skill?

A skill contains:
- **Domain knowledge** — How to do something
- **Templates** — Reusable patterns
- **Principles** — Guiding rules
- **Examples** — Concrete illustrations

Unlike agents (who have personality), skills are reference materials.

## Available Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| **[obsidian-vault.md](obsidian-vault.md)** | Frontmatter, tags, wiki links, file conventions | All agents |
| **[daily-log.md](daily-log.md)** | Daily logging conventions | All agents |
| **[project-lifecycle.md](project-lifecycle.md)** | How projects move from idea to done | Tech Lead, Planner |
| **[focus-support.md](focus-support.md)** | Focus strategies and flow states | DeepWork, Planner, Journal |
| **[weekly-review.md](weekly-review.md)** | Review process and templates | Review, Journal |
| **[goal-tracking.md](goal-tracking.md)** | Goal management patterns | Planner, Review |
| **[discord-integration.md](discord-integration.md)** | Discord MCP usage | Inbox, DeepWork |

## How Agents Use Skills

Agents reference skills when they need domain knowledge:

```markdown
## Skills You Reference
- `.github/skills/focus-support.md` — Focus patterns
- `.github/skills/weekly-review.md` — Review process
```

Skills are not personality — they're knowledge.

## Creating New Skills

1. Create `{skill-name}.md` in this directory
2. Structure with clear sections
3. Add to this README
4. Reference from relevant agents

### Skill Template

```markdown
# Skill Name

## Purpose

[What this skill is for]

## Key Concepts

[Core ideas]

## Templates

[Reusable patterns]

## Principles

[Guiding rules]

## Examples

[Concrete illustrations]

## Related

- [Other skills or resources]
```
