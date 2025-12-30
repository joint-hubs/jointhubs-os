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

Use templates from `Templater/`:
- `Daily.md` — Creates daily note with Tasks plugin integration
- `Weekly.md` — Creates weekly review with embedded daily journals
- `Monthly.md` — Monthly review with goal tracking
- `Quarterly.md` — Quarterly review with habit assessment

## Daily ↔ Weekly Link

Daily notes embed weekly priorities:
```markdown
## 🎯 Focus (from last weekly review)
![[YYYY-Www#Next]]
```

This keeps you focused on what matters throughout the week.
