---
name: daily-kickoff
description: Start your day with context check, priority setting, and planning
agent: Planner
tools: ['read', 'edit', 'search', 'todo']
argument-hint: Any specific focus for today?
---

# Daily Kickoff

Start the day with context and focus. This is the morning ritual.

## Steps

### 1. Check Today's Log

Look for: `Second Brain/Operations/Periodic Notes/Daily/{YYYY-MM-DD}.md`

- If exists: Read it, summarize any carried items or notes
- If missing: Offer to create it using the daily-log skill template

### 2. Quick Context Scan

Check the last 2-3 daily logs to understand momentum:
- What was done recently?
- Any patterns or blockers?
- Anything that keeps getting pushed?

### 3. Review Active Projects

Scan `Second Brain/Projects/*/CONTEXT.md` files for:
- What's marked as "Current" status
- Any urgent blockers
- Deadlines approaching

### 4. Calendar Awareness

Ask: "Any meetings or hard commitments today?"

Factor these into the plan — they fragment focus time.

### 5. Set Today's Priorities

**If today is Monday:** First check for maintenance window tasks — small operational items (<15 min each) that have been accumulating. List them as a batch for 08:00–09:00. These are separate from the day's focus and don't count toward the priorities below.

Propose a maximum of **3 priorities** for the day — framed as outcomes, not tasks.

Ask: **"What's the ONE thing that, if done, makes today a win?"**

If a task has been on the list for 3+ weeks and is clearly <15 minutes, move it to the maintenance window instead of treating it as a priority.

### 6. Output

Update today's log with:
- **Maintenance window** (Monday only): list of operational tasks for 08:00–09:00 batch
- The ONE thing (outcome framing: "X will be true by end of day")
- Max 2 additional focus areas
- Any relevant context

End with a clear first action: "Ready to start? Your first task is..."
