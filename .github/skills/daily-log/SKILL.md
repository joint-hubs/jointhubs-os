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
- After completing work → update log with what happened
- When blocked → note blocker and what you tried
- Making a decision → log the decision and why
- End of session → summarize, note what carries forward

## Location

```
Second Brain/Operations/Periodic Notes/Daily/YYYY-MM-DD.md
```

## Procedure

### At Session Start

1. Get today's date (YYYY-MM-DD)
2. Check if `Second Brain/Operations/Periodic Notes/Daily/{date}.md` exists
3. If exists: read it for context — what's in progress, what's blocked, what's the focus?
4. If missing: ask user if they want to create one using the template

### During Work

Add timestamped entries as things happen:
```markdown
HH:MM — [Topic]
[What happened / decided / learned / blocked]
```

**What to log:**

| Event | Format |
|-------|--------|
| Starting work on something | `HH:MM — Starting [task] on [project]` |
| Completing a task | `HH:MM — Done: [task]. [Brief result]` |
| Making a decision | `HH:MM — Decision: [what] because [why]` |
| Hitting a blocker | `HH:MM — Blocked: [what's stuck]. Tried [what]` |
| Learning something | `HH:MM — TIL: [insight]` |
| Switching context | `HH:MM — Switching to [new topic]. [Why]` |

**What NOT to log:**
- Every tiny action (keep it meaningful, not noisy)
- Information that belongs in project files (link instead: `see [[project/CONTEXT]]`)
- Long paragraphs (if it's more than 3 lines, extract to its own note)

### At Session End

Update the End of Day section:
```markdown
## End of Day
- **Done**: [What was completed — be specific]
- **Carried**: → [[YYYY-MM-DD]] [What moves to next session]
- **Tomorrow**: [One sentence: what's the first thing to do?]
```

This section is critical — it's the bridge to the next session. Be specific enough that future-you (or the agent) can pick up without asking "where were we?"

## Key Sections

| Section | Purpose |
|---------|---------|
| Focus | ONE thing for today (set at session start) |
| Projects | Brief status of active projects |
| Logs | Timestamped entries during work |
| End of Day | Summary for next session |

## Tips

- **Link, don't dump** — If a topic grows beyond 3 lines, create a note and link to it
- **Be specific in "Done"** — "Finished hero section" beats "worked on Fenix"
- **Name blockers clearly** — "Waiting on API docs from team" not "stuck"
- **The Carried section is accountability** — If something appears there 3+ days in a row, it needs attention or needs to be dropped

## Template

See [template.md](template.md) for the full Obsidian Templater template.
