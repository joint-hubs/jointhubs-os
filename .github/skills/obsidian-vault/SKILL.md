---
name: obsidian-vault
description: |
  Vault structure, file naming, frontmatter, and linking conventions.
  Use when: "vault structure", "file naming", "frontmatter", "wiki links", "obsidian conventions".
---

# Obsidian Vault

Conventions for working with this Obsidian vault.

## When to Use

- Creating new notes
- Navigating vault structure
- Linking between notes
- Adding frontmatter

## Vault Structure

```
/
├── .github/              # Agent configuration
│   ├── agents/
│   ├── skills/
│   └── instructions/
└── Second Brain/          # Your notes
  ├── Operations/        # Day-to-day operations
  │   ├── Periodic Notes/# Daily, Weekly
  │   │   ├── Daily/     # YYYY-MM-DD.md
  │   │   └── Weekly/    # YYYY-Www.md
  │   └── Meetings/      # Meeting notes
  ├── Personal/          # Life tracking
  └── Projects/          # Active projects
    └── {project-name}/
      ├── README.md
      └── CONTEXT.md
```

## File Naming

| Type | Format | Example |
|------|--------|---------|
| Daily | `YYYY-MM-DD.md` | `2026-01-19.md` |
| Weekly | `YYYY-Www.md` | `2026-W03.md` |
| Project | Folder name | `my-project/` |

## Frontmatter

Every note needs frontmatter:

```yaml
---
type: daily | project | meeting
status: active | done | paused
tags: [type/daily, project/name]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

## Tags

Hierarchical tags:
- `#type/daily`, `#type/project`, `#type/meeting`
- `#status/active`, `#status/done`, `#status/paused`
- `#project/{name}`

## Linking

Wiki links: `[[Note Name]]` or `[[folder/Note|Display Text]]`

Common patterns:
- `[[2026-01-19]]` — Daily note
- `[[Second Brain/Projects/my-project/CONTEXT]]` — Project context
- `[[2026-W03#Next]]` — Section of weekly note
