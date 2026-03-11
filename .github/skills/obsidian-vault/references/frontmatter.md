# Frontmatter Reference

YAML frontmatter standards for Obsidian notes.

## Required Fields

Every note should have frontmatter:

```yaml
---
type: daily | project | meeting | analysis | note
status: active | done | paused | archived
tags: [type/daily, project/my-app]
created: 2026-01-20
updated: 2026-01-20
---
```

## Field Definitions

| Field | Required | Values | Purpose |
|-------|----------|--------|---------|
| `type` | Yes | daily, project, meeting, analysis, note | Categorizes the note |
| `status` | Yes | active, done, paused, archived | Current state |
| `tags` | Yes | Array of strings | Hierarchical categorization |
| `created` | Yes | YYYY-MM-DD | When note was created |
| `updated` | Yes | YYYY-MM-DD | Last modification |

## Optional Fields

```yaml
---
# ... required fields ...
aliases: [alternative name, shorthand]
project: my-app
week: 2026-W03
date: 2026-01-20
---
```

## Type-Specific Templates

### Daily Note

```yaml
---
type: daily
status: active
tags: [type/daily]
date: 2026-01-20
week: 2026-W03
created: 2026-01-20
updated: 2026-01-20
---
```

### Project CONTEXT.md

```yaml
---
type: project
status: active
tags: [type/project, project/my-app]
created: 2026-01-01
updated: 2026-01-20
---
```

### Meeting Note

```yaml
---
type: meeting
status: done
tags: [type/meeting, project/my-app]
date: 2026-01-20
attendees: [person1, person2]
created: 2026-01-20
updated: 2026-01-20
---
```

### Analysis Document

```yaml
---
type: analysis
status: active
tags: [type/analysis, project/my-app, analysis/deep]
created: 2026-01-20
updated: 2026-01-20
---
```
