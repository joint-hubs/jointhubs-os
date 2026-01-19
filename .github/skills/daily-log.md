# Daily Log Skill

## Purpose

The daily log is the **memory** between AI sessions. It's the one place you update every day, so any agent can pick up context.

## Location

```
Operations/Periodic Notes/Daily/
├── 2026-01-19.md    ← Today
├── 2026-01-18.md    ← Yesterday
├── 2026-01-17.md    ← ...
└── ...
```

## Why

Daily logs are **memory between sessions**. Agents don't remember — logs do.

## Template

```markdown
---
type: daily
status: active
tags: [type/daily]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Daily Log: YYYY-MM-DD

## Focus
- **Key**: [ONE thing for today]
- **Blockers**: [What's in the way]

## Projects
- [ ] [[Project A/CONTEXT|A]]: [status]
- [ ] [[Project B/CONTEXT|B]]: [status]

## What Happened

### HH:MM — [Topic]
[What you did / learned / blocked]

## End of Day
- **Done**: [list] #status/done
- **Carried**: [list] → [[YYYY-MM-DD+1]]
- **Tomorrow**: [one sentence]

## Links
Prev: [[YYYY-MM-DD-1]] | Next: [[YYYY-MM-DD+1]] | Week: [[YYYY-WNN]]
```

## When to Update

- Session start (check exists)
- After completing something
- When stuck
- End of day (summary)

## What to Include

**DO include:**
- What you actually worked on
- Key decisions made
- Blockers encountered
- Notable wins or struggles

**DON'T include:**
- Every minor task
- Detailed meeting notes (link to them instead)
- Long reflections (that's weekly review territory)

## Agent Behavior

Every session: check for log → read it → update as work happens.
If no log exists, ask if user wants to create one.

## Git

Commit: `log: daily update YYYY-MM-DD`

## Weekly Integration

Review agent reads Mon-Fri logs → creates `Operations/Periodic Notes/Weekly/YYYY-WNN.md`

## Related

- `.github/skills/weekly-review.md` — How reviews use daily logs
- `Operations/Periodic Notes/` — Where logs live

---

## Obsidian Conventions

### Required Frontmatter

```yaml
---
type: daily
status: active
tags:
  - type/daily
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

### Tags to Use

| Tag | When |
|-----|------|
| `#status/done` | Mark completed items |
| `#status/blocked` | Mark stuck items |
| `#project/name` | Reference specific project |

### Wiki Links

Daily logs should link to:

```markdown
- Projects worked on: [[Project Name/CONTEXT]]
- Yesterday: [[2026-01-18]]
- Tomorrow: [[2026-01-20]]
- This week's review: [[2026-W03]]
- Related meetings: [[2026-01-19-standup]]
```

### Naming Convention

Daily logs use ISO date format: `YYYY-MM-DD.md`

```
Operations/Periodic Notes/Daily/
├── 2026-01-19.md
├── 2026-01-18.md
└── ...
```

This enables natural linking with `[[2026-01-19]]`.
