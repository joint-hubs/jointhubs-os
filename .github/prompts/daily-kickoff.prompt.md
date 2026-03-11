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

Propose a maximum of **3 priorities** for the day.

Ask: **"What's the ONE thing that, if done, makes today a win?"**

### 6. Output

Update today's log with:
- The 3 priorities
- The ONE thing highlighted
- Any relevant context

End with a clear first action: "Ready to start? Your first task is..."
