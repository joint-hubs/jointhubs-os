---
name: session-end
description: Wrap up current work session, log progress, set up tomorrow
agent: Planner
tools: ['read', 'edit', 'search']
argument-hint: What did you work on?
---

# Session End

Close out a work session cleanly. Capture progress, set up the next session.

## Steps

### 1. Gather What Happened

Ask: "What did you work on this session?"

Or infer from:
- Recent file changes (git status)
- Today's log entries
- Conversation context

### 2. Update Daily Log

Add to today's log (`Second Brain/Operations/Periodic Notes/Daily/{YYYY-MM-DD}.md`):

```markdown
## End of Day

**Done:**
- [ ] Task 1 completed
- [ ] Task 2 completed

**Carried:**
- [ ] Task that moves to tomorrow

**Tomorrow:**
One sentence: what's the first thing to do?
```

### 3. Update Project Context (if needed)

If significant progress was made on a project:
- Update the project's CONTEXT.md "Current" section
- Note any decisions made
- Flag any new blockers

### 4. Git Commit

If there are uncommitted changes, suggest a commit:
- `log: daily update {date}` for log updates
- `{project}: {description}` for project work

### 5. Clear Close

End with:
- Summary of what was accomplished
- What's queued for next session
- "Good session. Rest well." or similar human close
