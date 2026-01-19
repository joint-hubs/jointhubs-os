# Project Lifecycle Skill

## Purpose

Projects are the unit of progress. This skill defines how projects move from idea to done.

## Project Location

```
Projects/
├── {project-name}/
│   ├── README.md         ← Project overview
│   ├── CONTEXT.md        ← Past/Current/Future state
│   └── tasks/            ← Task files
│       ├── 01-first-task.md
│       ├── 02-second-task.md
│       └── done/
│           └── 00-spike.md
```

## Project States

| State | Meaning | Location |
|-------|---------|----------|
| **Idea** | Not started, just captured | Notes or backlog |
| **Active** | Currently being worked on | `Projects/{name}/` |
| **Paused** | Intentionally on hold | `Projects/{name}/` with note |
| **Complete** | Done, shipped | Archive or `Projects/done/` |

## CONTEXT.md Template

Every active project MUST have a CONTEXT.md file:

```markdown
---
type: project
status: active
tags: [type/project, project/project-name]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# {Project Name} Context

## Past (How We Got Here)

### Origin
[Why this project exists]

### Key Decisions
- [Decision 1]: [Reasoning]
- [Decision 2]: [Reasoning]

### Lessons Learned
- [What we know now that we didn't before]

---

## Current (Where We Are)

### Status
[One sentence: what's the current state?]

### Active Tasks
- [ ] Task 1: [Status]
- [ ] Task 2: [Status]

### Blockers
- [What's in the way, if anything]

### Dependencies
- [What this project is waiting on]

---

## Future (Where We're Going)

### Next Milestone
[What's the next concrete deliverable?]

### End Goal
[What does "done" look like?]

### Open Questions
- [Unresolved decisions]
- [Things we need to figure out]

---

## Links
- [Related docs, repos, tools]
```

## Task Files

For complex work, create task files in `{project}/tasks/`:

```markdown
# Task: {Title}

## Context
[Why this exists]

## Acceptance Criteria
- [ ] Outcome 1
- [ ] Outcome 2

## Notes
[Learnings]
```

Move completed to `tasks/done/`.

## Workflow

1. **Start** — Create `{project}/README.md` + `CONTEXT.md`
2. **Work** — Read CONTEXT first, pick/create task, update CONTEXT
3. **Complete task** — Verify criteria, move to `done/`
4. **Complete project** — Final CONTEXT update, archive

## Git

Commit format: `{project}: {description}`

## Principles

- One CONTEXT.md per project (single source of truth)
- Tasks optional for small projects
- Update as you go

## Related

- `.github/skills/daily-log.md` — Daily progress tracking
- `.github/skills/weekly-review.md` — Weekly project review
