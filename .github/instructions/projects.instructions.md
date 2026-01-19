---
applyTo: "Second Brain/Projects/**"
---

# Project Directory Instructions

> These instructions apply when working in any `Second Brain/Projects/` subdirectory.

## At Session Start

1. **Read CONTEXT.md** — This is the project's memory
2. **Check daily log** — What's the broader context?
3. **Identify current task** — What are we working on?

## Required Files

Every project directory SHOULD have:

```
Second Brain/Projects/{project}/
├── README.md         ← What is this project?
├── CONTEXT.md        ← Past / Current / Future state
└── tasks/            ← Task breakdown (if needed)
```

## CONTEXT.md is Sacred

**Always read CONTEXT.md before making changes.**

If CONTEXT.md doesn't exist, ask the user if they want to create one.

After significant work, **update CONTEXT.md** to reflect the new state.

## The Three Sections

### Past (How We Got Here)
- Why does this project exist?
- What decisions have been made?
- What lessons have been learned?

### Current (Where We Are)
- What's the status right now?
- What tasks are active?
- What's blocking progress?

### Future (Where We're Going)
- What's the next milestone?
- What does "done" look like?
- What questions are unresolved?

## Task Files

For complex projects, break work into task files:

```
tasks/
├── 01-setup-infrastructure.md
├── 02-implement-core-feature.md
├── 03-add-tests.md
└── done/
    └── 00-initial-spike.md
```

Move completed tasks to `done/` subdirectory.

## Git Conventions

```bash
# Project work
git commit -m "{project-name}: description of change"

# Context updates
git commit -m "{project-name}: update CONTEXT with new direction"
```

## Handoffs

If the work requires a different agent:
- **Need to plan?** → Planner
- **Need to reflect?** → Journal
- **Need to focus?** → DeepWork

## Completion

When a project is complete:
1. Update CONTEXT.md with final state
2. Ensure all tasks are in `done/`
3. Consider archiving to `Second Brain/Projects/done/`
