---
name: new-project
description: Scaffold a new project with proper structure and CONTEXT.md
agent: Planner
tools: ['read', 'edit', 'search']
argument-hint: What's the project name and what problem does it solve?
---

# New Project Setup

Create a new project with proper structure from the start.

## Steps

### 1. Gather Project Info

Ask:
- "What's the project name?" (lowercase, hyphenated)
- "What problem does it solve?"
- "Who is it for?"
- "What does success look like?"

### 2. Create Directory Structure

Create: `Second Brain/Projects/{project-name}/`

With files:
```
{project-name}/
├── README.md
└── CONTEXT.md
```

### 3. Generate README.md

```markdown
# {Project Name}

> One-line description of what this is.

## Problem

What problem does this solve? Who has this problem?

## Solution

How does this project solve it?

## Status

🟡 Active Development

## Quick Links

- CONTEXT.md — Project state
- tasks/ — Active work
```

### 4. Generate CONTEXT.md

```markdown
---
type: project-context
project: {project-name}
status: active
created: {date}
updated: {date}
---

# {Project Name} — Context

## Past

### Origin
Why does this project exist? What triggered it?

### Key Decisions
None yet.

### Lessons Learned
None yet.

---

## Current

### Status
🟡 Just started — setting up structure.

### Active Tasks
- [ ] Define MVP scope
- [ ] Set first milestone

### Blockers
None yet.

---

## Future

### Next Milestone
{First milestone description}

### End Goal
{What does "done" look like?}

### Open Questions
- What's the MVP?
- Who are the first users?
```

### 5. Log the Creation

Add to today's log:
```markdown
HH:MM — New Project Created
Project: {project-name}
Purpose: {one-liner}
```

### 6. Next Steps

Ask: "What's the first thing to work on for this project?"

Offer handoff to appropriate agent (Tech Lead for building, Designer for design, etc.)
