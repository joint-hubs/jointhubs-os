---
applyTo: "Operations/**"
---

# Operations Directory Instructions

> These instructions apply when working in the `Operations/` directory.

## Purpose

The Operations directory contains:
- **Periodic Notes** — Daily, weekly, monthly logs
- **Meetings** — Meeting notes and action items

This is the **operational memory** of your system.

## Directory Structure

```
Operations/
├── Periodic Notes/
│   ├── Daily/           ← Daily logs (most important)
│   │   ├── 2026-01-19.md
│   │   └── ...
│   ├── Weekly/          ← Weekly reviews
│   │   ├── 2026-W03.md
│   │   └── ...
│   └── Monthly/         ← Monthly resets
│       ├── 2026-01.md
│       └── ...
└── Meetings/
    ├── 2026-01-19-standup.md
    └── ...
```

## Daily Notes

### Location
`Operations/Periodic Notes/Daily/YYYY-MM-DD.md`

### Template
```markdown
# Daily Log: YYYY-MM-DD

## Morning Context
- **Key focus**: [One main thing]
- **Blockers**: [What's in the way]

## Projects in Flight
- [ ] Project A: [Status]
- [ ] Project B: [Status]

## What Happened
<!-- Updated throughout the day -->

## End of Day
- **Completed**: [What got done]
- **Carried over**: [What didn't]
- **Tomorrow**: [One sentence]
```

### Rules
- Every session should check today's daily note
- Update it as work happens
- Commit changes to git

## Weekly Notes

### Location
`Operations/Periodic Notes/Weekly/YYYY-WNN.md`

### When
Created during Friday review (Review agent)

### Purpose
Synthesize the week's daily notes into insights

## Monthly Notes

### Location
`Operations/Periodic Notes/Monthly/YYYY-MM.md`

### When
Created first Monday of each month

### Purpose
Bigger picture review and goal adjustment

## Meeting Notes

### Location
`Operations/Meetings/YYYY-MM-DD-{topic}.md`

### Template
```markdown
# Meeting: {Topic}

**Date**: YYYY-MM-DD
**Attendees**: [Who was there]
**Duration**: [How long]

## Agenda
1. [Topic 1]
2. [Topic 2]

## Notes
[What was discussed]

## Decisions
- [Decision made]

## Action Items
- [ ] @person: [Action] by [date]
```

## Git Conventions

```bash
# Daily logs
git commit -m "log: daily update 2026-01-19"

# Weekly reviews
git commit -m "review: weekly 2026-W03"

# Meeting notes
git commit -m "meeting: standup 2026-01-19"
```

## What NOT to Put Here

- Project-specific work → `Projects/`
- Personal notes → `Personal/`
- Reference material → Appropriate knowledge base
