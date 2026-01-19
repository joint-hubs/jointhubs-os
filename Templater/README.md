# Templater

Core templates for Obsidian Templater plugin.

## Templates

| Template | Purpose | Creates |
|----------|---------|---------|
| `Daily.md` | Daily log (agent memory) | `Operations/Periodic Notes/Daily/YYYY-MM-DD.md` |
| `Weekly.md` | Weekly review | `Operations/Periodic Notes/Weekly/YYYY-Www.md` |
| `Context.md` | Project CONTEXT | `Projects/[name]/CONTEXT.md` |

## Setup

1. Install the **Templater** plugin in Obsidian
2. Go to Settings → Templater
3. Set Template folder location to `Templater`
4. Enable "Trigger Templater on new file creation" (optional)

## Session Rituals

Templates support structured planning and review sessions.

See `.github/skills/session-rituals.md` for:
- Planning sessions (Monday)
- Review sessions (Friday)
- Project kickoffs

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
