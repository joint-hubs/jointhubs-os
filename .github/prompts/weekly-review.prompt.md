---
name: weekly-review
description: Friday synthesis — review the week, extract patterns, plan next week
agent: Journal
tools: ['read', 'edit', 'search']
argument-hint: Ready for your weekly review?
---

# Weekly Review

Friday ritual. Step back, see patterns, prepare for next week.

After the review, switch to Planner if you want to turn the output into a concrete weekly plan.

## Steps

### 1. Gather the Week

Read daily logs from the past 7 days:
`Second Brain/Operations/Periodic Notes/Daily/{date}.md`

Create a mental picture of what happened.

### 2. Create Weekly Note

Create: `Second Brain/Operations/Periodic Notes/Weekly/{YYYY}-W{WW}.md`

Use this structure:

```markdown
---
type: weekly
week: {YYYY}-W{WW}
created: {date}
---

# Week {WW} Review

## What Happened

### Projects
<!-- List active projects and their progress -->
- **Project A**: [summary]
- **Project B**: [summary]

### Wins
- Win 1
- Win 2

### Challenges
- Challenge 1
- Challenge 2

## Patterns

What kept coming up? Any recurring blockers? Energy patterns?

## Lessons

What did you learn this week?

## Next Week

### Focus Areas
1. Primary focus
2. Secondary focus

### Key Deliverables
- [ ] Deliverable 1
- [ ] Deliverable 2
```

### 3. Prompt Reflection

Ask these questions:
- "What went well that you want to continue?"
- "What drained energy that you want to change?"
- "What's the one thing you're most proud of?"

### 4. Update Project Contexts

For any project with significant movement:
- Update CONTEXT.md to reflect new state
- Move completed items to "Past"
- Update "Current" and "Future" sections

### 5. Close the Week

End with encouragement and a preview of next week's focus.
