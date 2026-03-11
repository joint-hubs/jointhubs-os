# Obsidian Tasks Reference

Using the Obsidian Tasks plugin syntax for task management.

## Task Format

```markdown
- [ ] Task description 📅 2026-01-20 🛫 2026-01-15 🔺 ➕ 2026-01-10
```

## Emoji Markers

| Emoji | Meaning | Example |
|-------|---------|---------|
| `📅` | Due date | `📅 2026-01-20` |
| `🛫` | Start date | `🛫 2026-01-15` |
| `⏳` | Scheduled date | `⏳ 2026-01-18` |
| `➕` | Created date | `➕ 2026-01-10` |
| `✅` | Done date | `✅ 2026-01-19` |

## Priority Markers

| Emoji | Priority |
|-------|----------|
| `🔺` | Highest |
| `⏫` | High |
| `🔼` | Medium |
| `🔽` | Low |

## Examples

### Basic task with due date
```markdown
- [ ] Review PR 📅 2026-01-20
```

### High-priority task with dates
```markdown
- [ ] Ship MVP 📅 2026-01-25 🛫 2026-01-20 ⏫ ➕ 2026-01-15
```

### Completed task
```markdown
- [x] Write documentation 📅 2026-01-18 ✅ 2026-01-18
```

## Tasks Query Block

In daily notes, use a tasks query to show pending work:

````markdown
## ToDo

```tasks
not done
due after 2024-01-01
sort by priority
group by priority
group by function task.start.format("YYYY-MM-DD dddd")
```
````

## Searching for Tasks

### Using grep_search

```bash
# Find pending tasks with due dates
grep_search "- \[ \].*📅"

# Find high-priority pending tasks
grep_search "- \[ \].*🔺"

# Find tasks in a specific project
grep_search "- \[ \].*my-app"
```

### Using the Task Scanner

```bash
# Run from repository root
python .github/skills/obsidian-vault/scripts/scan_tasks.py

# Options
--pending    # Only pending (not done) tasks
--overdue    # Only overdue tasks
--json       # JSON output
--path PATH  # Custom vault path
```

## Best Practices

1. **Always add due dates** for actionable tasks
2. **Use priority markers** to sort what matters
3. **Add start dates** for tasks that shouldn't appear until later
4. **Mark done with ✅ date** for tracking completion
