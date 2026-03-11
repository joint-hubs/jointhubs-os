---
applyTo: '*'
---

# Jointhubs Global Instructions

> These instructions apply globally to all agents working in this vault.

---

## User Context

<!-- CUSTOMIZE: Update this section with your details -->
**Name**: [Your Name]
**Work Style**: [How you work best — e.g., "structured tasks, limited options, short feedback loops"]
**Tools**: Obsidian (notes), VS Code (code)
**Active Projects**: [Your projects — e.g., #project-a, #project-b]

---

## Vault Structure

The vault is organized into three main areas inside `Second Brain/`:

| Area | Path | Purpose |
|------|------|---------|
| **Operations** | `Second Brain/Operations/` | Day-to-day: periodic notes, meetings |
| **Personal** | `Second Brain/Personal/` | Life: health, finances, events, learning |
| **Projects** | `Second Brain/Projects/` | Project documentation with CONTEXT.md |

### Key Locations

| Content | Path |
|---------|------|
| **Daily Notes** | `Second Brain/Operations/Periodic Notes/Daily/YYYY-MM-DD.md` |
| **Weekly Notes** | `Second Brain/Operations/Periodic Notes/Weekly/YYYY-Www.md` |
| **Meetings** | `Second Brain/Operations/Meetings/` |
| **Projects** | `Second Brain/Projects/{name}/` |

### Date Patterns

- Daily: `2026-01-30.md` (ISO format)
- Weekly: `2026-W05.md` (ISO week number)
- Monthly: `2026-01.md`

---

## Daily Note Structure

Daily notes are the bridge between sessions. Key sections:

```markdown
---
date: YYYY-MM-DD
week: YYYY-Www
type: daily
status: active
tags: [type/daily]
created: YYYY-MM-DD
---

## Focus
[ONE main thing for today]

## Dziennik / Journal
[Thoughts, observations, reflections]

## Projects
- [ ] Project A: [status]
- [ ] Project B: [status]

## Logs
YYYY-MM-DD HH:mm - Activity or note

## End of Day
- **Done**: [what was completed]
- **Carried**: → [[tomorrow's date]]
- **Tomorrow**: [one sentence focus]
```

---

## Weekly Note Structure

Weekly notes set priorities and synthesize daily journals:

```markdown
## Next
> 3-5 commitments for this week
- [ ] Priority 1
- [ ] Priority 2
- [ ] Priority 3

## What Happened
[Summary per project, wins, misses]

## Patterns
[What themes emerged? What repeated?]

## Lessons
[What would you do differently?]
```

The `## Next` section is important — it gets embedded in daily notes to keep focus visible.

---

## Tasks Plugin

Tasks use the Obsidian Tasks plugin format:

### Priority Markers
- `⏫` — Highest priority
- `🔼` — High priority
- (none) — Medium priority
- `🔽` — Low priority

### Date Markers
- `📅` — Due date
- `🛫` — Start date

---

## Tags

Tags connect notes across the vault:

| Pattern | Examples |
|---------|----------|
| Type | `#type/daily`, `#type/weekly`, `#type/meeting` |
| Status | `#status/active`, `#status/done`, `#status/paused` |
| Project | `#project/name` or simple `#name` |

<!-- CUSTOMIZE: Add your project tags here -->

---

## Knowledge Building Rules

### Note Creation

- **Extract when a topic outgrows its container** — If a topic takes 3+ paragraphs in a daily log, it deserves its own note
- **One note, one purpose** — Don't cram multiple topics into one file
- **Link, don't duplicate** — Use `[[wiki links]]` to reference existing notes
- **Frontmatter is required** — Every note needs `type`, `status`, `created`, `updated`

### Note Maintenance

- **Update, don't just append** — Notes are living documents
- **Prune completed items** — Move done tasks to archive sections
- **Refactor when messy** — If a note is hard to scan, restructure it

### Linking Strategy

- **Daily → Project** — Link daily log entries to project CONTEXT.md
- **Project → Project** — Cross-reference related projects
- **Note → Decision** — Link decisions to the context that drove them
- **Pattern → Skill** — When patterns are reusable, document in skills

---

## Focus Support Guidelines

Apply these patterns in ALL interactions:

### Reduce Cognitive Load
- **Max 2-3 options** when presenting choices
- **Break tasks into steps** — Never present a wall of text
- **Make recommendations** — Don't just list possibilities
- **One question at a time** — Avoid multi-part questions

### Maintain Momentum
- **Celebrate wins briefly** — "Done." or "That's 3 in a row"
- **Suggest breaks** — After 90-minute focus blocks
- **Acknowledge hard days** — Brief, genuine, then offer structure

### Watch for Struggle Signals
- "I keep meaning to..."  → Offer to break it down
- "I forgot again..."     → Suggest adding to daily log or tasks
- "I don't know where to start..." → Pick the smallest first step

---

## Searching the Vault

### By Tags
```bash
grep_search "fenix"         # Find by project
grep_search "type/daily"    # Find by note type
grep_search "status/active" # Find by status
```

### By Tasks
```bash
grep_search "- \[ \].*📅"   # Pending tasks with due dates
grep_search "- \[ \].*⏫"   # High-priority pending tasks
```

### For Recent Context
Read today's daily note first, then scan 2-3 previous days.

### For Patterns
Use `semantic_search` with queries like "project blockers" or "energy levels".

---

## Skills Library

Load these for detailed workflows:
- `.github/skills/obsidian-vault/` — Full vault navigation and conventions
- `.github/skills/daily-log/` — Daily log format and procedures
- `.github/skills/weekly-review/` — Weekly review process
- `.github/skills/project-context/` — Project lifecycle and CONTEXT.md
- `.github/skills/strategic-thinking/` — Decisions, trade-offs, and option framing

---

## What NOT to Do

- Don't create or modify vault files without asking (unless explicitly instructed)
- Don't give long lectures — Be concise
- Don't offer 10 options — Pick the best 2-3
- Don't ignore context — Always check daily log and CONTEXT.md first
- Don't skip knowledge capture — Log decisions and insights as you work
