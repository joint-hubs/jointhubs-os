---
name: project-context
description: |
  Project state management using CONTEXT.md files with Past/Current/Future sections.
  Use when: "project context", "CONTEXT.md", "project status", "where are we", "project state".
---

# Project Context

Every project has a `CONTEXT.md` that tracks its state across three time horizons.

## When to Use

- Starting a new project
- Resuming work on a project
- Updating project status
- Planning next steps

## Location

```
Second Brain/Projects/{project-name}/CONTEXT.md
```

## Structure

### Past (How We Got Here)

- **Origin**: Why this project exists
- **Key Decisions**: What was decided and why
- **Lessons**: What we learned

### Current (Where We Are)

- **Status**: One sentence state
- **Tasks**: Active work items
- **Blockers**: What's in the way

### Future (Where We're Going)

- **Next Milestone**: Concrete deliverable
- **End Goal**: What done looks like
- **Open Questions**: Unresolved decisions

## Procedure

### At Session Start

1. Read the project's CONTEXT.md
2. Focus on Current section
3. Note any blockers

### During Work

Update as state changes:
- Complete a task → update Tasks
- Hit a blocker → add to Blockers
- Make a decision → add to Key Decisions

### At Session End

1. Update Current section
2. Move completed work to Past if significant
3. Adjust Future if plans changed

## Template

See [template.md](template.md) for the full template.
