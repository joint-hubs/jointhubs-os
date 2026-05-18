---
applyTo: "Second Brain/Operations/thoughtmap-out/**"
---

# ThoughtMap Output Instructions

> These instructions apply when working with ThoughtMap pipeline output in `Second Brain/Operations/thoughtmap-out/`.

## Purpose

ThoughtMap output is an auto-generated semantic map of the user's entire knowledge base — daily notes, project docs, voice transcripts, and reviews. Use it as a context index to understand topics, entities, and relationships before diving into source material.

Treat it as a **router**, not the final layer of understanding. Its job is to tell the agent where to look next at low cost.

## Core Rule

ThoughtMap output is a **derived index**, not the source of truth.

- Use it to discover what topics exist and how they relate
- Use it to choose the right next MCP query or source file, not to end the reasoning process on its own
- Use source files to confirm details before making claims or edits
- If output and source files disagree, trust the source files

For non-trivial strategic, relational, or status questions, do cheap routing here first and then hand off to ThoughtMap MCP for semantic grounding.

## Entry Points

Start navigation in this order depending on the task:

| Need | Start Here |
|------|------------|
| Broad overview | `REPORT.md` |
| Specific topic | `topics/{slug}.md` |
| Specific person, project, org | `entities/{type}/{slug}.md` |
| Machine-readable entity data | `entities.json` |
| Cluster relationships | `condensed.json` |
| Raw corpus search | `chunks.json` |

## File Reference

### REPORT.md — Executive Summary

The first file to read. Contains:
- **Summary**: chunk count, cluster count, unclustered count
- **Sources**: breakdown by source type (obsidian-daily, wispr-flow, second-brain, etc.)
- **Named Entities**: top entities per type with mention counts
- **God Nodes**: the 5 largest topic clusters with representative text samples
- **All Clusters**: full table of cluster ID, label, size
- **Bridge Thoughts**: chunks sitting between two clusters (cross-domain connections)

### topics/ — Topic Cluster Notes

One markdown note per cluster. Each contains:
- Frontmatter: `type: thoughtmap-topic`, `cluster_id`, `size`, `super_cluster`
- Summary: LLM-generated narrative of what the cluster is about
- Related Topics: ranked by cosine similarity (wikilinked)
- Representative Fragments: 3-5 example chunks from the cluster
- Mega-topic link: parent super-cluster grouping

**Navigation**: Use `[[wikilinks]]` between related topics to follow conceptual threads.

### entities/ — Named Entity Notes

Organized by type: `person/`, `organization/`, `project/`, `tool/`, `location/`.

Each entity note contains:
- Frontmatter: `type: entity`, `entity_type`, `name`, `aliases`, `clusters`, `mentions`, `first_seen`
- **Summary**: what this entity is and its role in the knowledge base
- **Topic Boundaries**: CENTER (core themes) and EDGES (peripheral connections)
- **Area Context**: embedding-space metrics — coverage %, focus (spread), distinctiveness, nearest/farthest clusters
- **Appearances by Cluster**: table showing which clusters mention this entity
- **Source Files**: list of original files where the entity appears

`_entity-index.md` links to all entity notes with mention counts and summaries.

### Data Files

| File | Format | Use |
|------|--------|-----|
| `chunks.json` | JSON array | Full corpus — each chunk has `id`, `text`, `timestamp`, `source_file`, `source`, `section` |
| `clusters.json` | JSON array | Cluster definitions with `cluster_id`, `label`, `size`, `centroid_2d`, `member_indices`, `representative_texts` |
| `condensed.json` | JSON | Cluster summaries + inter-cluster `related` list with similarity scores |
| `entities.json` | JSON array | Machine-readable entity data (name, type, aliases, mentions, clusters, summary, boundaries) |

### HTML Visualizations

- `thoughtmap.html` — full interactive 2D scatter plot of all chunks, colored by cluster
- `thoughtmap-condensed.html` — simplified cluster-level overview

Open in browser. Not for agent consumption — use the JSON/markdown files instead.

## How To Read Area Context

Entity Area Context describes where the entity sits in the embedding space:

- **Coverage**: fraction of total chunks — how much of the knowledge base this entity spans
- **Focus (cosine σ)**: how tightly clustered the entity's chunks are. Labels: `very tight` (<0.10), `tight` (<0.20), `moderate` (<0.35), `broad` (≥0.35)
- **Distinctiveness**: cosine distance from entity centroid to global centroid. Low = central/common topic, high = niche/specialized
- **Nearest/Farthest clusters**: which topic clusters this entity is semantically closest to and farthest from

## How To Navigate

### For broad questions ("what is the user working on?")
1. Read `REPORT.md` → God Nodes section
2. Check top entities by mention count
3. Scan topic notes for the largest clusters
4. If the question is about current direction, status, or priority, run a short MCP bundle before answering

### For entity questions ("who is X?" / "what is project Y?")
1. Open `entities/{type}/{slug}.md`
2. Read Summary and Topic Boundaries for quick context
3. Check Area Context for scope and positioning
4. Follow cluster links to topic notes for deeper context
5. Read source files listed at the bottom for ground truth
6. For active-work questions, run MCP queries such as `"<entity> current status"` or `"<entity> open questions"`

### For topic exploration ("what topics relate to X?")
1. Open the relevant `topics/{slug}.md`
2. Follow Related Topics links (sorted by similarity)
3. Check the mega-topic for the broader category
4. Cross-reference with entity notes for key people/projects in that topic
5. Use MCP relationally when needed: `get_cluster`, `cluster_distances`, and `text_distance` are the next step after static routing

## Hand-off Pattern

After using `thoughtmap-out` to find the right area, build a small semantic grounding bundle:

1. The user's exact phrasing
2. `"<anchor> current status"`
3. `"<anchor> open questions"` or `"<anchor> next step"`

Then keep the best hits, read the top 1-2 backing source files, and continue using a compact context pack instead of raw search results.

### For cross-domain discovery
1. Read Bridge Thoughts in `REPORT.md`
2. Check `condensed.json` for inter-cluster similarity scores
3. Look at entity Area Context — entities with high distinctiveness are niche; low distinctiveness = cross-cutting

## Conventions

- Filenames use kebab-case slugs derived from cluster labels or entity names
- All output is regenerated on each pipeline run — do not edit these files manually
- Wikilinks in topic notes use `[[slug|Display Name]]` format
- Cluster IDs are stable within a run but may change between runs
- `member_indices` reference positions in the `chunks.json` array

## Related

- `.github/instructions/thoughtmap.instructions.md` — ThoughtMap source code rules
- `.github/skills/thoughtmap/` — ThoughtMap pipeline, MCP tools, and output interpretation
- `Second Brain/Projects/thoughtmap/CONTEXT.md` — project architecture and decisions
