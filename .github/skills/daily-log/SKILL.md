---
name: daily-log
description: |
  Daily log conventions for agent memory between sessions.
  Use when: "daily log", "today's note", "what happened today", "session start", "check context".
---

# Daily Log

The daily log is **agent memory** between sessions. Every conversation starts by checking it.

## When to Use

- Session start → check if today's log exists
- After completing work → update log
- When blocked → note blocker
- End of session → summarize

## Location

```
Second Brain/Operations/Periodic Notes/Daily/YYYY-MM-DD.md
```

## Procedure

### At Session Start

1. Get today's date (YYYY-MM-DD)
2. Check if `Second Brain/Operations/Periodic Notes/Daily/{date}.md` exists
3. If exists: read it for context
4. If missing: ask user if they want to create one

### During Work

Add timestamped entries:
```
HH:MM — [Topic]
[What happened / learned / blocked]
```

### At Session End

Update the End of Day section:
- **Done**: what was completed
- **Carried**: what moves to tomorrow
- **Tomorrow**: one sentence focus

## Key Sections

| Section | Purpose |
|---------|---------|
| Focus | ONE thing for today |
| Projects | Active project status |
| What Happened | Timestamped log entries |
| End of Day | Summary for next session |

## Template

See [template.md](template.md) for the full template.
