# Periodic Notes

Regular planning and review notes.

## Folders

| Folder | Format | Purpose |
|--------|--------|---------|
| `Daily/` | `YYYY-MM-DD.md` | Daily notes with journal, logs, tasks |
| `Weekly/` | `YYYY-Www.md` | Weekly reviews and planning |
| `Monthly/` | `YYYY-MM.md` | Monthly reviews |
| `Quarterly/` | `YYYY-Qq.md` | Quarterly reviews |

## Templates

Use templates from `.github/skills/`:
- `daily-log/template.md` — Daily note with Tasks plugin integration
- `weekly-review/template.md` — Weekly review with embedded daily journals

For monthly/quarterly reviews, create your own templates and store them in `.github/skills/` or your template system.

## Daily ↔ Weekly Link

Daily notes embed weekly priorities:
```markdown
## 🎯 Focus (from last weekly review)
![[YYYY-Www#Next]]
```

This keeps you focused on what matters throughout the week.
