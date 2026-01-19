# Second Brain

Your personal knowledge base — notes, projects, and life tracking.

## Structure

```
Second Brain/
├── Operations/       ← Day-to-day ops, meetings, periodic notes
├── Personal/         ← Health, finances, events, learning
└── Projects/         ← Active work with CONTEXT.md pattern
```

## Your Strategy, Your Rules

**There is no "right" way to organize notes.** What works for one person fails for another.

Some approaches:
- **PARA** — Projects, Areas, Resources, Archive
- **Zettelkasten** — Atomic notes with heavy linking
- **Folders** — Simple hierarchy by topic
- **Tags-first** — Flat files, rich tagging
- **Hybrid** — Mix of above

**Pick what fits your brain.** The structure here is a starting point — adapt it.

## The Agent Contract

When you change your note structure, **update the agents**:

| Changed | Update |
|---------|--------|
| Folder paths | `.github/skills/obsidian-vault/SKILL.md` |
| Daily log format | `.github/skills/daily-log/SKILL.md` |
| Project structure | `.github/skills/project-context/SKILL.md` |
| New templates | `.github/skills/*/template.md` |
| Directory rules | `.github/instructions/*.instructions.md` |

Agents only know what you teach them. If they can't find your notes, you haven't told them where to look.

## Key Conventions

### Daily Logs

Location: `Second Brain/Operations/Periodic Notes/Daily/YYYY-MM-DD.md`

These are **agent memory** — the bridge between sessions. Check them first, update them always.

### Project Context

Every project has a `CONTEXT.md`:
- **Past** — How we got here
- **Current** — Where we are  
- **Future** — Where we're going

### Wiki Links

Use `[[double brackets]]` for connections:
- `[[2026-01-19]]` — Link to daily log
- `[[Second Brain/Projects/Project Name/CONTEXT]]` — Link to project

## Related

- [Agents README](../.github/agents/README.md) — Agent personalities
- [Skills README](../.github/skills/README.md) — Domain knowledge
- [Root README](../README.md) — System overview
