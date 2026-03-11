---
name: quick-capture
description: Quickly add an entry to today's daily log
agent: Planner
tools: ['read', 'edit']
argument-hint: What do you want to log?
---

# Quick Capture

Fast entry into today's log. No ceremony, just capture.

## Steps

### 1. Get Today's Log

Open: `Second Brain/Operations/Periodic Notes/Daily/{YYYY-MM-DD}.md`

If it doesn't exist, create it with minimal structure.

### 2. Add Timestamped Entry

Add to the log under the appropriate section:

```markdown
HH:MM — [Topic]
[User's input]
```

### 3. Categorize (if obvious)

If the entry clearly belongs to a category, place it there:
- Meeting notes → Meetings section
- Task completion → Done section  
- Blocker → Blockers section
- Random thought → Notes section

### 4. Confirm

Just confirm it's captured: "✓ Logged."

No extra commentary needed. This is a fast workflow.
