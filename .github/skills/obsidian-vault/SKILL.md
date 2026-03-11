---
name: obsidian-vault
description: |
  Vault structure, file naming, frontmatter, tags, tasks, and linking conventions.
  Use when: "vault structure", "file naming", "frontmatter", "wiki links", "obsidian", "tags", "tasks", "create note", "organize notes".
---

# Obsidian Vault Skill

Conventions for working with this Obsidian vault. Every note should be findable, linkable, and useful months later.

## Quick Reference

| Topic | File | Use When |
|-------|------|----------|
| Vault structure | [references/vault-structure.md](references/vault-structure.md) | Navigating directories, creating notes |
| Frontmatter | [references/frontmatter.md](references/frontmatter.md) | Adding metadata to notes |
| Tags | [references/tags.md](references/tags.md) | Organizing, searching by tag |
| Tasks | [references/tasks.md](references/tasks.md) | Obsidian Tasks plugin syntax |
| Wiki links | [references/wiki-links.md](references/wiki-links.md) | Linking between notes |

## Scripts

Utility scripts for vault analysis:

| Script | Purpose | Example |
|--------|---------|---------|
| [scripts/scan_tags.py](scripts/scan_tags.py) | Find all tags | `python .github/skills/obsidian-vault/scripts/scan_tags.py` |
| [scripts/scan_tasks.py](scripts/scan_tasks.py) | Find all tasks | `python .github/skills/obsidian-vault/scripts/scan_tasks.py --pending` |

## Essential Patterns

### File Naming
- Daily: `YYYY-MM-DD.md` → `2026-01-20.md`
- Weekly: `YYYY-Www.md` → `2026-W03.md`
- Meeting: `YYYYMMDD meeting-topic.md`
- Event/Trip: `YYYYMMDD_event_name_YYYYMMDD.md` (start_end dates)

### Required Frontmatter
```yaml
---
type: daily | project | meeting | note
status: active | done | paused | idea
tags: [type/daily, project/name]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

### Tags
Tags can be hierarchical (`project/myproject`) or simple (`#myproject`).

Common prefixes: `type/`, `status/`, `project/`, `area/`

<!-- CUSTOMIZE: Add your project tags here -->
<!-- Simple tags: `#project-a`, `#project-b` -->

### Searching
```bash
# By project tag
grep_search "project-name"

# Pending tasks with due dates
grep_search "- \[ \].*📅"

# Find all notes of a type
grep_search "type: meeting"
```

### Task Emoji
| `📅` Due | `🛫` Start | `🔺` Highest | `⏫` High | `🔼` Medium | `🔽` Low |

## Knowledge Building Patterns

The vault is a knowledge base, not a filing cabinet. Every note should connect to something.

### When to Create a New Note

| Signal | Action |
|--------|--------|
| A topic grows beyond 2-3 paragraphs in a daily log | Extract to its own note |
| A recurring pattern emerges across sessions | Document it in the relevant project or skill |
| A decision has lasting impact | Record it in CONTEXT.md or a dedicated decision note |
| Research spans multiple sources | Create a synthesis note |
| You explain the same thing twice | Write it once, link to it |

### When to Update an Existing Note

- Facts change → Update the source note
- Context grows → Add to the relevant section
- Something is resolved → Mark it done, note the outcome
- You learn something new about an existing topic → Enrich the note

### Linking Strategy

**Link, don't duplicate.** If information exists elsewhere, use a `[[wiki link]]` to it.

- Daily logs link to project notes: `Worked on [[Project/CONTEXT]]`
- Project notes link to decisions: `See [[2026-01-20]] for discussion`
- Meeting notes link to action items: `Task assigned, tracked in [[Project/CONTEXT]]`

**One note, one purpose.** If a note covers two distinct topics, split it.

**Notes are living documents.** When a note gets messy or outdated, refactor it. Don't just keep appending.

---

*Load reference files for detailed documentation on any specific topic.*
