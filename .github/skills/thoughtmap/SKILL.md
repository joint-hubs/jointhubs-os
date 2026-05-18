---
name: thoughtmap
description: |
  ThoughtMap pipeline, output interpretation, and MCP vector search tools.
  Use when: "thoughtmap", "thought clusters", "search thoughts", "what am I thinking about",
  "semantic search notes", "knowledge base", "vector search", "find context in notes",
  "cluster distances", "topic map", "thinking patterns".
---

# ThoughtMap

ThoughtMap is a personal knowledge pipeline that extracts, embeds, clusters, and visualizes all of the user's thoughts from multiple sources. It produces a semantic map of topics and exposes vector search via MCP tools.

## When to Use

- **Finding context for non-trivial work** → route cheaply through `thoughtmap-out`, then use MCP for semantic grounding
- **Understanding what topics exist** → Use `list_clusters` to see the landscape
- **Exploring a specific topic** → Use `get_cluster` to see representative texts
- **Measuring topic relationships** → Use `cluster_distances` or `text_distance`
- **Interpreting pipeline output** → Read this skill for file format reference

## Routing Model

ThoughtMap has two complementary layers:

- **`thoughtmap-out`** is the cheap router. Use it to identify the right project, entity, topic, or cluster quickly.
- **ThoughtMap MCP** is the grounding layer. Use it to determine what is currently most relevant, what remains open, and which source files deserve closer reading.

Do not treat MCP as a fallback only when static notes fail. For strategic, relational, or status-oriented tasks, use MCP after cheap routing even when static notes exist.

## Data Sources

ThoughtMap ingests from these sources (tagged in `source` metadata):

| Source | Tag | What It Contains |
|--------|-----|-----------------|
| Second Brain markdown | `second-brain` | Project docs, notes, reviews, decisions |
| Obsidian Daily Notes | `obsidian-daily` | Daily journal entries from the Obsidian vault |
| Obsidian Root Notes | `obsidian-root` | Non-daily Obsidian notes (project files, references) |
| Wispr Flow | `wispr-flow` | Voice transcriptions (dictated thoughts, notes) |
| Jointhubs Reviews | `jointhubs-review` | Daily review summaries |

## MCP Tools Reference

Five tools are available via the `thoughtmap` MCP server:

### `search_thoughts(query, n_results=10)`

Semantic search over all chunks. Returns the closest matches by cosine distance.

**When to use**: Finding relevant context about any topic. This is often faster and more complete than `grep_search` because it matches by meaning, not exact words.

**Returns** per result:
- `text` — the chunk content
- `source_file` — original file path
- `source` — source tag (see table above)
- `timestamp` — when the content was created
- `distance` — cosine distance (lower = more relevant, typically 0.2–0.5 for good matches)
- `section`, `project_tag`, `category` — optional metadata

**Interpreting distances**:
- `< 0.25` — very strong match
- `0.25–0.40` — good match, likely relevant
- `0.40–0.55` — moderate match, may be tangential
- `> 0.55` — weak match, probably noise

### `list_clusters(domain=None)`

List all topic clusters discovered by the pipeline, sorted by size.

**When to use**: Getting an overview of what the user thinks about. Use `domain` filter to narrow (e.g., `domain="fenix"` for Fenix-related clusters).

**Returns**: `cluster_id`, `label` (TF-IDF generated 3-word label), `size` (chunk count).

### `get_cluster(cluster_id)`

Get details of a specific cluster including representative text samples.

**When to use**: After `list_clusters` identifies an interesting topic. The representative texts show the most central content of that cluster.

### `cluster_distances(cluster_id, top_n=10)`

Compute cosine distances from one cluster's centroid to all others. Returns the nearest and farthest clusters.

**When to use**: Understanding how topics relate to each other. "What's close to this topic?" or "What's completely different?"

**Note**: First call computes centroids by embedding representative texts (~30s). Subsequent calls are cached in memory.

### `text_distance(text_a, text_b)`

Compute semantic distance between two arbitrary texts.

**When to use**: Comparing concepts, checking if two ideas are related, or validating whether a piece of content belongs to a certain topic.

**Returns**: `distance` (0 = identical, ~1 = unrelated), `similarity` (1 - distance).

## Output Files

The pipeline writes to `Second Brain/Operations/thoughtmap-out/`:

| File | Purpose | When to Read |
|------|---------|-------------|
| `REPORT.md` | Summary: chunk count, clusters, god nodes, sources | Quick overview of the knowledge base state |
| `clusters.json` | Machine-readable cluster definitions | Programmatic access to all cluster data |
| `clusters/_index.md` | Domain-grouped cluster index with trends | Understanding which domains are growing/shrinking |
| `clusters/{domain}.md` | Per-domain cluster details | Deep dive into a specific domain's topics |
| `thoughtmap.html` | Interactive 2D visualization | Visual exploration (browser only, not for agents) |
| `chunks.json` | All processed chunks with metadata | Raw data inspection |

### Reading `REPORT.md`

The report starts with a summary line: `N chunks · M topic clusters · K unclustered`.

Key sections:
- **Sources** — where chunks come from and distribution
- **God Nodes** — largest clusters (dominant topics)
- **Complete Cluster List** — all clusters with sizes and representative samples

### Reading `clusters/_index.md`

Shows clusters grouped into domains with trend arrows:
- `↗` — growing (more recent activity)
- `↘` — declining (less recent activity)

This helps the agent understand what the user is currently focused on vs. historical topics.

### Reading `clusters/{domain}.md`

Each domain file lists clusters belonging to that domain with:
- Cluster label, size, time span
- Representative text samples
- Source file links

## Agent Workflow

### When gathering context for a task:

1. **Extract anchors**: people, projects, topics, decisions from the user's request
2. **Route cheaply first**: read `REPORT.md`, the relevant entity note, topic note, or project `CONTEXT.md`
3. **Run a short MCP bundle**:
  - the user's exact phrasing
  - `"<anchor> current status"`
  - `"<anchor> open questions"` or `"<anchor> next step"`
4. **Keep strong hits**: prefer results with distance < 0.40 when possible
5. **Read source files**: follow the top 1-2 `source_file` paths behind the best hits
6. **Build a compact context pack**:
  - Prior decisions
  - Open threads
  - Reusable assets
  - Freshest relevant source
  - Gaps / conflicts
7. **Continue the task from the context pack**, not from raw search output

### When analyzing thinking patterns:

1. `list_clusters()` — see all topic groups
2. `cluster_distances(id)` — find related and unrelated topics
3. Read `clusters/_index.md` — check domain trends (what's growing?)

### Prefer MCP over manual search when:

- The query is conceptual (meaning-based, not exact text)
- You need to search across all data sources at once
- You want to understand topic relationships
- The user asks "what do I know about X" or "what have I been thinking about"
- The task is strategic, relational, or status-oriented and static notes alone are not enough

### Prefer grep_search / file_search when:

- Looking for an exact string, tag, or file name
- The target is a specific file you already know about
- Searching for task markers (`- [ ]`, `📅`, `⏫`)
