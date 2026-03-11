---
applyTo: "Second Brain/Operations/**"
---

# Operations Directory Instructions

> These instructions apply when working in the `Second Brain/Operations/` directory.

## Purpose

The Operations directory is the **operational memory** of your system:
- **Periodic Notes** — Daily, weekly logs
- **Meetings** — Meeting notes and action items

## Directory Structure

```
Second Brain/Operations/
├── Periodic Notes/
│   ├── Daily/           ← Daily logs (most important)
│   │   ├── 2026-01-19.md
│   │   └── ...
│   └── Weekly/          ← Weekly reviews
│       ├── 2026-W03.md
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
[One main thing for today]

## Projects
- [ ] Project A: [Status]
- [ ] Project B: [Status]

## Logs
<!-- Timestamped entries throughout the day -->
HH:MM — [Topic]: [What happened]

## End of Day
- **Done**: [What got completed]
- **Carried**: [What moves to tomorrow]
- **Tomorrow**: [One sentence focus]
```

### Rules
- Every session starts by checking today's daily note
- Update it with timestamped entries as work happens
- End of Day section bridges to the next session
- Keep entries concise — details go in project files, linked with `[[wiki links]]`

## Weekly Notes

### Location
`Second Brain/Operations/Periodic Notes/Weekly/YYYY-Www.md`

### When
Created during Friday review

### Purpose
Synthesize the week's daily notes into patterns, lessons, and next-week priorities.

### Structure
```markdown
---
type: weekly
week: YYYY-Www
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

## Next
- [ ] Priority 1
- [ ] Priority 2
- [ ] Priority 3

## What Happened
[Summary per project, wins, misses]

## Patterns
[Themes, recurring blockers, energy observations]

## Lessons
[What to do differently next week]
```

## Meeting Notes

### Location
`Second Brain/Operations/Meetings/YYYY-MM-DD-{topic}.md`

### Template
```markdown
---
type: meeting
date: YYYY-MM-DD
attendees: [names]
tags: [type/meeting, project/name]
---

# Meeting: {topic}

## Agenda
- Item 1
- Item 2

## Notes
[Key points discussed]

## Decisions
[What was decided and why]

## Action Items
- [ ] [Who]: [What] 📅 [Due date]
```

## Knowledge Building Rules

- **Daily logs are operational** — Keep them lean, link to deeper notes
- **Extract recurring topics** — If something appears 3+ times, it deserves its own note
- **Link decisions to context** — Use `[[project/CONTEXT]]` when logging project decisions
- **Weekly reviews surface patterns** — This is where daily noise becomes signal
