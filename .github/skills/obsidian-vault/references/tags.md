# Tags Reference

Tagging system for organizing and searching notes.

## Tag Patterns

Tags can be **hierarchical** (`project/my-app`) or **simple** (`#my-app`). Both are valid.

### Hierarchical Tags (Preferred)

| Prefix | Purpose | Examples |
|--------|---------|----------|
| `type/` | Note type | `type/daily`, `type/project`, `type/meeting`, `type/analysis` |
| `status/` | Current state | `status/active`, `status/done`, `status/paused` |
| `project/` | Project association | `project/my-app`, `project/research`, `project/side-project` |
| `area/` | Life area | `area/health`, `area/finances`, `area/career` |

### Simple Tags (Also Common)

<!-- CUSTOMIZE: Add your own project tags -->
Many notes use simple project tags:
- `#my-app` — Main project
- `#research` — Research project
- `#side-project` — Side project

## Common Tags

### Type Tags
- `type/daily` — Daily notes
- `type/project` — Project documentation
- `type/meeting` — Meeting notes
- `type/analysis` — Deep analysis documents
- `type/note` — General notes

### Status Tags
- `status/active` — Currently working on
- `status/done` — Completed
- `status/paused` — On hold
- `status/archived` — No longer relevant

### Project Tags
<!-- CUSTOMIZE: Replace with your project tags -->
- `project/my-app` — Main application
- `project/research` — Research project
- `project/side-project` — Side project

### Area Tags
- `area/health` — Health & fitness
- `area/finances` — Financial tracking
- `area/career` — Career development

## Searching by Tags

### Using grep_search

```bash
# Find project-related notes (catches both #my-app and project/my-app)
grep_search "my-app"

# Find all active projects
grep_search "status/active"

# Find all meeting notes
grep_search "type/meeting"

# More specific: only hierarchical project tag
grep_search "project/my-app"
```

### Using the Tag Scanner

```bash
# Run from repository root
python .github/skills/obsidian-vault/scripts/scan_tags.py

# Options
--by-file    # Show tags per file
--json       # JSON output
--path PATH  # Custom vault path
```

## Best Practices

1. **Always use hierarchical tags** — `project/my-app` not just `my-app`
2. **Put tags in frontmatter** — More reliable than inline
3. **Use consistent prefixes** — Stick to type/, status/, project/, area/
4. **Limit inline tags** — Reserve for quick categorization in text
