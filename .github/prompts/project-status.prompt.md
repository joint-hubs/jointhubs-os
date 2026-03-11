---
name: project-status
description: Get a bird's-eye view of all active projects
agent: Planner
tools: ['read', 'search']
argument-hint: Want a full overview or specific projects?
---

# Project Status Overview

See all projects at a glance. Useful for planning sessions.

## Steps

### 1. Scan All Projects

Read CONTEXT.md from each active project:
- Scan `Second Brain/Projects/*/CONTEXT.md` for all projects
- Skip any `done/` or archived directories

### 2. Build Status Matrix

Create a summary:

```markdown
## Project Status — {date}

| Project | Status | Next Milestone | Blockers |
|---------|--------|----------------|----------|
| {name} | 🟡 Active | {milestone} | {blocker} |
| {name} | 🟢 On track | {milestone} | None |
| {name} | 🔵 Paused | — | {reason} |
```

Status indicators:
- 🟢 On track, momentum
- 🟡 Active, needs attention
- 🔴 Blocked, urgent
- 🔵 Paused, intentionally waiting

### 3. Identify Priorities

Based on the matrix:
- What needs attention this week?
- What can wait?
- Any conflicts or dependencies?

### 4. Surface Patterns

Look for:
- Projects that haven't been touched in 2+ weeks
- Recurring blockers across projects
- Overcommitment signals

### 5. Recommendations

Suggest:
- "{Project} needs focus — it's been blocked for a week"
- "Consider pausing X to make progress on Y"
- "These two projects share a blocker — solve once"

### 6. Ask

"Which project do you want to focus on?"

Offer handoff to appropriate project lead agent.
