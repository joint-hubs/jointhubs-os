---
name: weekly-review
description: |
  Weekly review process for reflection and planning.
  Use when: "weekly review", "week summary", "Friday review", "what happened this week", "plan week".
---

# Weekly Review

Structured reflection at the end of each week. The purpose is to find patterns, not just list events.

## When to Use

- Friday afternoon or Sunday evening
- Duration: 30-45 minutes
- Before Monday planning
- Agent: **Journal** (reflection) or **Planner** (forward planning)

## Location

```
Second Brain/Operations/Periodic Notes/Weekly/YYYY-Www.md
```

## Procedure

### 1. Gather (5 min)

Collect data from:
- Daily logs from the week (read all 5-7 entries)
- Completed tasks across projects
- CONTEXT.md files for active projects
- Any meeting notes from the week

### 2. Review (10 min)

Facts first:
- What got done? List concrete outputs.
- What didn't get done? Name the reason (blocked, skipped, deprioritized).
- What decisions were made? Were they documented?

### 3. Find Patterns (10 min)

This is the valuable part. Look for:
- **Energy patterns**: Which days were productive? What was different about them?
- **Recurring blockers**: Same blocker showing up across days?
- **Scope creep**: Did work expand beyond what was planned?
- **Knowledge gaps**: Did you have to look up the same thing twice?
- **Wins**: What went well that you should do more of?

Capture patterns as bullet points — these feed into future planning.

### 4. Plan Next Week (10 min)

Set up next week:
- **3-5 commitments** — not a wish list, actual commitments
- **One main focus** — what's the #1 thing to ship?
- **Moved items** — carry forward unfinished work explicitly (don't let it silently drop)
- **Protected time** — block focus sessions for deep work

### 5. Close (5 min)

- Update weekly note
- Update CONTEXT.md for any active projects whose state changed
- If a pattern keeps repeating, create a note about it or update a skill

## Weekly Note Structure

```markdown
---
type: weekly
tags: [type/weekly]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# YYYY-Www

## Next
- [ ] Commitment 1
- [ ] Commitment 2
- [ ] Commitment 3

## Wins
- What went well

## Patterns
- What you noticed

## Lessons
- What you'd do differently

## History
![[YYYY-MM-DD]]
![[YYYY-MM-DD]]
...
```

## What Goes Where

| Observation | Where It Goes |
|-------------|---------------|
| "I shipped feature X" | Weekly → Wins |
| "I keep getting stuck on Y" | Weekly → Patterns + project CONTEXT.md → Blockers |
| "I learned Z" | Weekly → Lessons + extract to project note if reusable |
| "I should change how I do W" | Update the relevant skill or instruction file |
| "Project A direction changed" | Project A CONTEXT.md → Past → Key Decisions |

## Template

See [template.md](template.md) for the full Obsidian Templater template.
