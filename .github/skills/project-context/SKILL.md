---
name: project-context
description: |
  Project state management using CONTEXT.md files with Past/Current/Future sections.
  Use when: "project context", "CONTEXT.md", "project status", "where are we", "project state", "new project", "project lifecycle".
---

# Project Context

Every project has a `CONTEXT.md` that tracks its state across three time horizons. This is the project's memory — read it first, update it always.

## When to Use

- Starting a new project → Create CONTEXT.md
- Resuming work → Read CONTEXT.md to get current state
- After significant progress → Update Current section
- Making a decision → Add to Past → Key Decisions
- Planning next steps → Review and update Future section
- Pausing or completing a project → Update lifecycle stage

## Location

```
Second Brain/Projects/{project-name}/
├── README.md       ← What is this project? (stable overview)
├── CONTEXT.md      ← Past / Current / Future (living document)
└── {working files} ← Notes, docs, research
```

## CONTEXT.md Structure

### Past (How We Got Here)

This section grows over time. It's the project's history.

- **Origin**: Why this project exists. What problem triggered it.
- **Key Decisions**: Important choices and their reasoning (date + what + why)
- **Lessons**: What we learned that might be useful later

### Current (Where We Are)

This section changes frequently — it's the "state snapshot."

- **Status**: One-line summary (e.g., "Active — building MVP", "Paused — waiting on API access")
- **Tasks**: Active work items with status
- **Blockers**: What's preventing progress (with workarounds if known)

### Future (Where We're Going)

This section provides direction and surfaces uncertainty.

- **Next Milestone**: Concrete deliverable with rough timeline
- **End Goal**: What done looks like
- **Open Questions**: Unresolved decisions that affect direction

## Project Lifecycle

Projects move through stages. Track the stage in CONTEXT.md frontmatter (`status:` field) and update as transitions happen.

```
Idea → Active → [Paused] → Done → [Archived]
```

### Stage: Idea

A captured project that isn't actively being worked on.

```yaml
status: idea
```

**What to do**: Create minimal CONTEXT.md with Past (why) and Future (what done looks like). No Current section needed yet.

### Stage: Active

The project is being worked on. CONTEXT.md is updated regularly.

```yaml
status: active
```

**What to do**: Full CONTEXT.md with all three sections. Update after each session.

### Stage: Paused

Intentionally on hold. The key is documenting **why** and **when to resume**.

```yaml
status: paused
```

**What to do**: Update Current with:
- Why it's paused
- What state things are in (don't lose context)
- Conditions for resuming ("Resume when X happens")

### Stage: Done

Project goals are met.

```yaml
status: done
```

**What to do**: Final CONTEXT.md update:
- Move final status to Past
- Document final lessons learned
- Note what worked and what didn't

### Stage: Archived

No longer relevant. Move to `Second Brain/Projects/done/` if desired.

## When to Update CONTEXT.md

| Event | What to Update |
|-------|----------------|
| Task completed | Current → Tasks |
| New blocker found | Current → Blockers |
| Decision made | Past → Key Decisions (with date + reasoning) |
| Direction changed | Future → Next Milestone, and Past → Key Decisions |
| Milestone reached | Move to Past, set new Future milestone |
| Session ends with progress | Current → Status, Current → Tasks |
| Project paused | Status field, Current → explain why |

## Procedure

### At Session Start

1. Read the project's CONTEXT.md
2. Focus on Current section — what's the status, what's active, what's blocked?
3. Check if Future → Next Milestone is still accurate

### During Work

Update as state changes:
- Complete a task → mark it done in Current → Tasks
- Hit a blocker → add to Current → Blockers with what you tried
- Make a decision → add to Past → Key Decisions with reasoning

### At Session End

1. Update Current section to reflect session progress
2. Move completed milestones to Past if significant
3. Adjust Future if plans changed
4. Update `updated:` date in frontmatter

## Template

See [template.md](template.md) for the full Obsidian Templater template.
