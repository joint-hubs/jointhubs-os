---
name: context-update
description: Update a project's CONTEXT.md after significant progress
agent: Planner
tools: ['read', 'edit', 'search']
argument-hint: Which project? (or I'll detect from recent work)
---

# Context Update

Keep project memory current. Run after significant progress.

## Steps

### 1. Identify the Project

Either:
- User specifies: "Update {project} context"
- Infer from recent work: Check git changes or conversation history

### 2. Read Current Context

Open: `Second Brain/Projects/{project}/CONTEXT.md`

Understand the current state.

### 3. Gather Updates

Ask:
- "What changed since last update?"
- "Any decisions made?"
- "Any new blockers?"
- "Did the next milestone shift?"

Or infer from:
- Recent daily logs mentioning this project
- Git history for project files
- Conversation context

### 4. Update Each Section

#### Past Section
Add to "Key Decisions" if any decisions were made:
```markdown
- **{date}**: {Decision and reasoning}
```

Add to "Lessons Learned" if any insights emerged.

#### Current Section
- Update status indicator (🟢 🟡 🔴)
- Refresh "Active Tasks" list
- Update "Blockers" (add new, remove resolved)

#### Future Section
- Adjust "Next Milestone" if it changed
- Update "Open Questions" (add new, mark resolved)

### 5. Update Timestamp

Change frontmatter:
```yaml
updated: {today's date}
```

### 6. Confirm

Summarize what was updated:
"Updated {project} CONTEXT.md:
- Added decision about X
- Moved Y to completed
- New blocker: Z"

### 7. Commit

Suggest: `git commit -m "{project}: update context"`
