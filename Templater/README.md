# Templater

Note templates for Obsidian Templater plugin.

## Available Templates

| Template | Purpose | Creates |
|----------|---------|---------|
| `Daily.md` | Daily note | `Operations/Periodic Notes/Daily/YYYY-MM-DD.md` |
| `Weekly.md` | Weekly review | `Operations/Periodic Notes/Weekly/YYYY-Www.md` |
| `Monthly.md` | Monthly review | `Operations/Periodic Notes/Monthly/YYYY-MM.md` |
| `Quarterly.md` | Quarterly review | `Operations/Periodic Notes/Quarterly/YYYY-Qq.md` |
| `Meeting.md` | Meeting notes | `Operations/Meetings/[Title].md` |
| `Project.md` | Project documentation | `Projects/[name]/README.md` |
| `Finances.md` | Monthly finances | `Personal/Finances/YYYY-MM.md` |
| `Event.md` | Personal event | `Personal/Events/[Title].md` |
| `Class.md` | Learning/course | `Personal/Classes/[Title].md` |

## Setup

1. Install the **Templater** plugin in Obsidian
2. Go to Settings → Templater
3. Set Template folder location to `Templater`
4. Enable "Trigger Templater on new file creation" (optional)

## Customizing Templates

Templates use Templater syntax:
- `<% tp.date.now("YYYY-MM-DD") %>` — Current date
- `<% tp.file.title %>` — File name
- `<% tp.date.now("YYYY-[W]WW") %>` — ISO week number

Customize templates to match your workflow!

## Linking Daily ↔ Weekly

Daily notes embed weekly priorities:
```markdown
## 🎯 Focus (from last weekly review)
![[YYYY-Www#Next]]
```

Weekly notes embed daily journals:
```markdown
## History
![[Monday#Dziennik]]
![[Tuesday#Dziennik]]
```

This keeps focus visible throughout the week.
