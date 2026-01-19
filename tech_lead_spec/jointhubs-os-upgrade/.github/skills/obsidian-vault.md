# Obsidian Vault Conventions

## Purpose

This skill defines how to use Obsidian features consistently across the vault: frontmatter, tags, wiki links, and file organization.

---

## Frontmatter (YAML)

Every note SHOULD have YAML frontmatter at the top:

```yaml
---
type: daily | weekly | monthly | project | task | meeting
status: active | paused | blocked | complete | archived
tags:
  - type/daily
  - project/project-name
created: 2026-01-19
updated: 2026-01-19
---
```

### Required Properties

| Property | Values | Purpose |
|----------|--------|---------|
| `type` | daily, weekly, monthly, project, task, meeting | Enables filtering by note type |
| `status` | active, paused, blocked, complete, archived | Track lifecycle |
| `created` | YYYY-MM-DD | When created |
| `updated` | YYYY-MM-DD | Last modified |

### Optional Properties

| Property | Example | Purpose |
|----------|---------|---------|
| `tags` | `[type/daily, project/x]` | Additional categorization |
| `project` | `project-name` | Link to project |
| `due` | YYYY-MM-DD | For tasks |

---

## Tags

Tags provide flexible categorization. Use hierarchical tags with `/` separator.

### Core Tag Hierarchy

```
#type/
  #type/daily
  #type/weekly
  #type/monthly
  #type/project
  #type/task
  #type/meeting

#status/
  #status/active
  #status/blocked
  #status/done
  #status/paused
  #status/archived

#project/
  #project/project-name
  #project/another-project

#priority/
  #priority/high
  #priority/medium
  #priority/low
```

### Tag Usage

| Context | Tags to Add |
|---------|-------------|
| Daily log | `#type/daily` |
| Project note | `#type/project`, `#status/active` |
| Completed item | `#status/done` |
| Blocked item | `#status/blocked` |
| Meeting note | `#type/meeting`, `#project/related-project` |

### Inline Tags

Use inline tags to mark specific items:

```markdown
- [x] Finished the API endpoint #status/done
- [ ] Waiting on design review #status/blocked
- [ ] High priority task #priority/high
```

---

## Wiki Links

Use `[[double brackets]]` to create links between notes.

### Basic Linking

```markdown
[[Note Name]]           → Links to Note Name.md
[[Folder/Note Name]]    → Links to note in folder
[[Note Name|Display]]   → Links with custom display text
[[Note Name#Heading]]   → Links to specific heading
```

### Common Link Patterns

| Link To | Format | Example |
|---------|--------|---------|
| Daily log | `[[YYYY-MM-DD]]` | `[[2026-01-19]]` |
| Yesterday | `[[YYYY-MM-DD]]` | See `[[2026-01-18]]` |
| Weekly review | `[[YYYY-WNN]]` | `[[2026-W03]]` |
| Project context | `[[Project Name/CONTEXT]]` | `[[My App/CONTEXT]]` |
| Project (display) | `[[Project/CONTEXT\|Project]]` | `[[My App/CONTEXT\|My App]]` |
| Meeting | `[[YYYY-MM-DD-topic]]` | `[[2026-01-19-standup]]` |
| Task | `[[Project/tasks/01-task]]` | `[[My App/tasks/01-setup]]` |

### Creating Link Trails

Good notes link forward and backward:

```markdown
## Links

- Previous: [[2026-01-18]]
- Next: [[2026-01-20]]
- Week: [[2026-W03]]
- Related: [[Some Other Note]]
```

### Backlink Awareness

When creating a note, think: "What notes should link TO this?"

- Daily logs → link to projects worked on
- Projects → link to relevant meetings
- Weekly reviews → link to all daily logs that week
- Tasks → link to parent project

---

## File Naming

### Conventions

| Type | Format | Example |
|------|--------|---------|
| Daily log | `YYYY-MM-DD.md` | `2026-01-19.md` |
| Weekly review | `YYYY-WNN.md` | `2026-W03.md` |
| Monthly review | `YYYY-MM.md` | `2026-01.md` |
| Meeting | `YYYY-MM-DD-topic.md` | `2026-01-19-standup.md` |
| Task | `NN-task-name.md` | `01-setup-database.md` |

### Why This Matters

- ISO dates sort chronologically
- Predictable names enable easy linking
- Numbered tasks show order

---

## Folder Structure

```
/
├── Projects/
│   └── {project-name}/
│       ├── README.md
│       ├── CONTEXT.md
│       └── tasks/
│           ├── 01-first-task.md
│           └── done/
├── Operations/
│   ├── Periodic Notes/
│   │   ├── Daily/
│   │   │   └── YYYY-MM-DD.md
│   │   ├── Weekly/
│   │   │   └── YYYY-WNN.md
│   │   └── Monthly/
│   │       └── YYYY-MM.md
│   └── Meetings/
│       └── YYYY-MM-DD-topic.md
└── Personal/
    └── ...
```

---

## Agent Behavior

When creating/updating notes: add frontmatter, use wiki links, update `updated` field.

---

## Related

- `.github/skills/daily-log.md`
- `.github/skills/project-lifecycle.md`
- `.github/skills/weekly-review.md`
