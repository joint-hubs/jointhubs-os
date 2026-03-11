---
applyTo: '.github/skills/**'
---

# Skills Directory Instructions

> Auto-loaded when working in `.github/skills/`

## What This Is

Skills are **domain knowledge** that agents load on-demand.

## Structure

```
.github/skills/
├── {skill-name}/
│   ├── SKILL.md       ← Main knowledge file
│   └── {extras}.md    ← Additional references
└── README.md
```

## SKILL.md Format

```markdown
# {Skill Name} Skill

> One-line description

## {Section 1}
{Content}

## {Section 2}
{Content}

## Related Skills
- [daily-log](../skills/daily-log/SKILL.md)
```

## Rules

1. **SKILL.md is the entry point** — agents load this file
2. **Be comprehensive but scannable** — tables, lists, headers
3. **Include examples** — show, don't just tell
4. **Link related skills** — build a knowledge graph
5. **Use `local/` for private skills** — keep personal or unstable workflows out of the shared root

## When to Create a Skill

- Domain knowledge needed by multiple agents
- Procedures that should be followed consistently
- Reference information agents need access to
