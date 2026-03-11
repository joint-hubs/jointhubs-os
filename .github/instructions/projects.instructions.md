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
└── {working files}   ← Notes, docs, research
```

## CONTEXT.md is Sacred

**Always read CONTEXT.md before making changes.**

If CONTEXT.md doesn't exist, ask the user if they want to create one.

After significant work, **update CONTEXT.md** to reflect the new state.

## The Three Sections

### Past (How We Got Here)
- Why does this project exist?
- What decisions have been made and why?
- What lessons have been learned?

### Current (Where We Are)
- What's the status right now?
- What tasks are active?
- What's blocking progress?

### Future (Where We're Going)
- What's the next milestone?
- What does "done" look like?
- What questions are unresolved?

## When to Update CONTEXT.md

- A task is completed or unblocked
- A new blocker is discovered
- An important decision is made (capture the why)
- Scope or direction changes
- A milestone is reached
- The session ends with significant progress

## Project Lifecycle

| Stage | Action |
|-------|--------|
| **Kickoff** | Create folder, README.md, CONTEXT.md |
| **Active** | Work, log progress, update CONTEXT.md regularly |
| **Paused** | Update CONTEXT.md with reason and resume conditions |
| **Done** | Final CONTEXT.md update with lessons, optionally move to `done/` |

## Knowledge Capture During Project Work

Work generates knowledge. Capture it:
- **Decisions** → Add to CONTEXT.md → Past → Key Decisions (with reasoning)
- **Patterns** → If reusable across projects, add to relevant skill
- **Blockers** → Note in CONTEXT.md → Current → Blockers (with workaround if found)
- **Insights** → If topic is growing, extract to a dedicated note in the project folder

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
- **Need to debug?** → Debug
