---
name: session-rituals
description: |
  Structured planning and review sessions for projects.
  Use when: "planning session", "review session", "project kickoff", "weekly planning".
metadata:
  author: jointhubs
  version: "1.0"
---

# Session Rituals

## Purpose

Projects need rhythm. This skill defines structured sessions that agents facilitate to keep projects moving forward.

## Session Types

### 1. Planning Session

**When**: Start of week, start of sprint, or when stuck

**Agent**: Planner (primary) or project-specific agent

**Duration**: 15-30 min

**Flow**:

```
1. Review CONTEXT.md
   - What's the current state?
   - What blockers exist?

2. Define this period's focus
   - What's the ONE thing?
   - What would make this week/sprint successful?

3. Break down into tasks
   - [ ] Task with owner and date
   - [ ] Task with owner and date

4. Block time
   - When will deep work happen?
   - What meetings need to move?

5. Update CONTEXT.md
   - Current section reflects new plan
```

**Output**: Updated CONTEXT.md + calendar blocks

---

### 2. Review Session

**When**: End of week, end of sprint, before planning

**Agent**: Review (primary) or Journal

**Duration**: 15-20 min

**Flow**:

```
1. What happened?
   - Done: [list]
   - Not done: [list]
   - Surprises: [list]

2. What did we learn?
   - What worked?
   - What didn't?
   - What would we do differently?

3. Update CONTEXT.md
   - Move completed to Past (if significant)
   - Update Current status
   - Adjust Future if needed

4. Prepare for next planning
   - What's top priority next?
   - Any blockers to address first?
```

**Output**: Updated CONTEXT.md + notes for next planning

---

### 3. Project Kickoff

**When**: Starting a new project

**Agent**: Tech Lead or Planner

**Duration**: 30 min

**Flow**:

```
1. Define the project
   - Why does this exist?
   - What does done look like?
   - Who is this for?

2. Create structure
   Projects/{name}/
   ├── README.md
   └── CONTEXT.md

3. Initial CONTEXT.md
   - Past: Origin story
   - Current: First tasks
   - Future: End goal + milestones

4. First planning session
   - What's the first deliverable?
   - When will we review?
```

**Output**: Project folder + CONTEXT.md + first tasks

---

## Scheduling Rituals

### Weekly Rhythm

| Day | Session | Agent |
|-----|---------|-------|
| Monday AM | Planning | Planner |
| Friday PM | Review | Review |

### Per-Project

For active projects, schedule:
- **Planning**: Every Monday or sprint start
- **Review**: Every Friday or sprint end

Use calendar blocks: `🔄 {Project} Planning` or `🔄 {Project} Review`

---

## Agent Handoffs

| From | To | When |
|------|-----|------|
| Planner | Tech Lead | Plan is set, time to build |
| Review | Planner | Review done, need next plan |
| Any | DeepWork | Starting a focus block |

---

## Templates

### Planning Session Note

```markdown
# Planning: {Project} — YYYY-MM-DD

## Review of Current State
[from CONTEXT.md]

## This Period's Focus
**ONE thing**: 

## Tasks
- [ ] 
- [ ] 

## Time Blocks
- 

## Updated CONTEXT.md
[yes/no]
```

### Review Session Note

```markdown
# Review: {Project} — YYYY-MM-DD

## Done
- 

## Not Done
- 

## Learned
- 

## Next Priority
- 

## Updated CONTEXT.md
[yes/no]
```

## Related

- `.github/skills/project-lifecycle.md`
- `.github/skills/weekly-review.md`
- `.github/agents/planner.agent.md`
- `.github/agents/review.agent.md`
