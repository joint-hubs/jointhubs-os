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
| **ThoughtMap Output** | `Second Brain/Operations/thoughtmap-out/` |

### Communication Notes Workflow

For outgoing messages drafted by the assistant (email, message, administrative reply), create a communication note before sending.

- Base location: `Second Brain/Operations/Communication/`
- Use domain subfolders as needed (for example: `joint hubs/administracja/`)
- File naming: `YYYYMMDD_semantic-name.md` (date without hyphens, then a clear semantic slug)
- Keep the note copy-paste ready for email clients (plain text, no markdown formatting inside the message body)
- Include frontmatter with at least: `date`, `type`, `status`, `tags`, `created`, `updated`

### ThoughtMap Output — your map of the knowledge base

Auto-generated semantic map of the entire vault + Wispr transcripts. Treat it as **Copilot's primary navigation index** — before running expensive searches or semantic queries, check whether the answer is already pre-computed here.

**Location:** `Second Brain/Operations/thoughtmap-out/`

**Read-first strategy (cheap → expensive):**
1. `REPORT.md` — snapshot: god nodes, top entities, bridge thoughts, source counts, build date
2. `entities/_entity-index.md` — quick lookup for any person / org / project / tool / location name mentioned by the user
3. `entities/{type}/<slug>.md` — full entity note: summary, topic boundaries (CENTER/EDGES), area context (coverage, focus, distinctiveness), source files, cluster memberships
4. `topics/<slug>.md` — cluster note: summary, related topics (wikilinked, similarity-ranked), representative fragments
5. `clusters.json` / `condensed.json` / `entities.json` — machine-readable; grep/filter, never dump whole file
6. Source files listed in entity notes — ground truth when the index disagrees
7. ChromaDB semantic query (via `thoughtmap` MCP or local PersistentClient) — semantic grounding after cheap routing, and mandatory for non-trivial strategic or relational tasks

**When Copilot should consult ThoughtMap-out first:**
- User mentions a name → `entities/_entity-index.md` → specific entity note
- User asks "what am I working on?" / "what have I been thinking about?" → REPORT.md god nodes + top entities
- User mentions a topic → `topics/<slug>.md` + its related topics
- Before creating a new note → check if an entity or topic note already covers it (avoid duplication)
- Cross-domain question ("how does X relate to Y?") → `condensed.json` inter-cluster similarity + Bridge Thoughts in REPORT.md
- Staleness rule: if REPORT.md is >7 days old, treat entity/cluster data as advisory and prefer fresh ChromaDB query

**Routing + Grounding Rule:**
- Treat `thoughtmap-out` as the cheap routing layer, not the final understanding layer.
- For non-trivial questions about strategy, project status, relations between topics, "what do we already know", or "how does this connect", do a short ThoughtMap retrieval pack after reading the cheapest relevant static context.
- Retrieval pack minimum:
	1. the user's exact phrasing
	2. `"<anchor> current status"`
	3. `"<anchor> open questions"` or `"<anchor> next step"`
- Keep only strong results when possible (for example distance < 0.40), read the top 1-2 source files behind the best hits, then continue using a compact context pack:
	- Prior decisions
	- Open threads
	- Reusable assets
	- Freshest relevant source
	- Gaps / conflicts

**Rules:**
- ThoughtMap-out is a **derived index, not source of truth**. Always verify before making claims or edits.
- Never edit files in `thoughtmap-out/` manually — they regenerate on each pipeline run.
- Entity/cluster IDs are stable within a run but may shift between rebuilds.
- Wikilinks inside topic/entity notes use `[[slug|Display Name]]` format.

See `.github/instructions/thoughtmap-out.instructions.md` for the full navigation guide and `.github/skills/thoughtmap/SKILL.md` for MCP query patterns.

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

### For Deep Context (MCP Knowledge Tools)
Use ThoughtMap MCP tools for semantic search across all knowledge sources:
- `search_thoughts("query")` — find relevant notes, transcripts, project docs by meaning
- `list_clusters()` — see all topic groups the user thinks about
- `get_cluster(id)` — drill into a specific topic cluster
- `cluster_distances(id)` — find related or distant topics
- `text_distance(a, b)` — measure semantic similarity between two texts

ThoughtMap may index three local source families depending on configuration:
- repo-local `Second Brain/` markdown
- an external Obsidian Vault path (optional)
- Wispr Flow local SQLite history (optional)

Treat the external vault and Wispr Flow as optional local integrations: present in some setups, absent in others.

Use graphify output for project-specific structural context:
- Read `graphify-out/GRAPH_REPORT.md` for entity-relationship maps within a project
- See `.github/instructions/graphify.instructions.md` for full workflow

**When to use which:**
- **ThoughtMap MCP** → broad, cross-project, meaning-based ("what do I know about X?")
- **Graphify** → structural, within one project ("how do parts of this project relate?")
- **grep_search** → exact text, tags, task markers
- **file_search** → known file names or patterns

---

## Skills Library

Load these for detailed workflows:
- `.github/skills/thoughtmap/` — ThoughtMap pipeline, output interpretation, and MCP vector search tools
- `.github/skills/obsidian-vault/` — Full vault navigation and conventions
- `.github/skills/obsidian-markdown/` — Wikilinks, embeds, callouts, and Obsidian Markdown features
- `.github/skills/obsidian-bases/` — `.base` files with views, filters, and formulas
- `.github/skills/json-canvas/` — `.canvas` files with nodes, groups, and edges
- `.github/skills/obsidian-cli/` — Obsidian CLI commands and plugin/theme development workflows
- `.github/skills/firecrawl/` — If the user gives a concrete URL, prefer Firecrawl. Use `map` for links and `crawl`/`extract` for content.
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
