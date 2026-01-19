---
applyTo: "Second Brain/Operations/**"
---

# Operations Directory Instructions

> These instructions apply when working in the `Second Brain/Operations/` directory.

## Purpose

The Operations directory contains:
- **Periodic Notes** — Daily, weekly, monthly logs
- **Meetings** — Meeting notes and action items

This is the **operational memory** of your system.

## Directory Structure

```
Second Brain/Operations/
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
`Second Brain/Operations/Periodic Notes/Daily/YYYY-MM-DD.md`

### Template
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
- **Key**: [One main thing]
- **Blockers**: [What's in the way]

## Projects
- [ ] Project A: [Status]
- [ ] Project B: [Status]

## What Happened
<!-- Updated throughout the day -->

## End of Day
- **Done**: [What got done]
- **Carried**: [What didn't]
- **Tomorrow**: [One sentence]
```

### Rules
- Every session should check today's daily note
- Update it as work happens
- Commit changes to git

## Weekly Notes

### Location
`Second Brain/Operations/Periodic Notes/Weekly/YYYY-WNN.md`

### When
Created during Friday review (Review agent)

### Purpose
Synthesize the week's daily notes into insights

## Monthly Notes

### Location
`Second Brain/Operations/Periodic Notes/Monthly/YYYY-MM.md`

### When
Created first Monday of each month

### Purpose
Bigger picture review and goal adjustment

## Meeting Notes

### Location
`Second Brain/Operations/Meetings/YYYY-MM-DD-{topic}.md`

### Template
```markdown
---
type: meeting
status: done
tags: [type/meeting]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Meeting: {Topic}

**Date**: YYYY-MM-DD
**Attendees**: [Who was there]
**Duration**: [How long]

## Summary
[Key points]

## Decisions
- [Decision made]

## Action Items
- [ ] [Action] — Owner
- [ ] [Action] — Owner

## Links
- [[Daily log for this day]]
- [[Related project]]
```

## Git Conventions

```bash
# Daily log updates
git commit -m "log: daily update YYYY-MM-DD"

# Weekly reviews
git commit -m "review: weekly YYYY-WNN"

# Meeting notes
git commit -m "meeting: topic YYYY-MM-DD"
```
