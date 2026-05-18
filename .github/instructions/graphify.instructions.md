---
applyTo: "*/graphify-out/*"
---

# Graphify Instructions

> These instructions apply when a graphify graph exists in the repository.

## Purpose

Use the graph as the first-pass context map for large folders before reading source files one by one.

## Files To Check

When `graphify-out/` exists, treat these files as the graph entry points:

- `graphify-out/GRAPH_REPORT.md` — human summary of communities, bridges, risks, and suggested questions
- `graphify-out/graph.json` — machine-readable nodes, edges, communities, and metadata
- `graphify-out/graph.html` — visual inspection aid for humans

## Core Rule

The graph is an index, not the source of truth.

- Use the graph to find the relevant context quickly
- Use source files to confirm details before making claims, edits, or decisions
- If graph output and source files disagree, trust the source files and note the mismatch

## How To Read The Graph

1. Start with `graphify-out/GRAPH_REPORT.md`
2. Identify the relevant community or communities from the report labels
3. Check `God Nodes` for likely entry points if the user request is broad
4. Check `Surprising Connections` and bridge nodes when the request crosses domains
5. Use `graphify-out/graph.json` to inspect exact nodes, edges, confidence tags, and source files
6. Open only the source notes linked to the small subgraph you actually need

## Confidence Rules

Treat edge confidence levels as operating constraints:

- `EXTRACTED` — explicit in source, safe to rely on as a strong lead
- `INFERRED` — plausible but should usually be confirmed in source before asserting it as fact
- `AMBIGUOUS` — unresolved or weak; never present as settled fact

When answering questions or planning changes:

- Prefer `EXTRACTED` edges first
- Use `INFERRED` edges to guide exploration
- Call out `AMBIGUOUS` edges as open questions or possible gaps

## Recommended Agent Workflow

For any request about a large project, use this sequence:

1. Map the request to 1-3 candidate communities or god nodes
2. Expand to neighboring nodes only as needed
3. Read the linked source files for confirmation
4. Answer from the confirmed subgraph, not from the whole corpus

This is the default pattern for questions like:

- "what is this project really about"
- "where does this decision connect to the rest of the system"
- "what files should I read before changing X"
- "what changed in project direction"

## When To Rebuild The Graph

Ask for or recommend a graph refresh when:

- the relevant folder changed substantially
- the graph output is missing expected files or concepts
- many key nodes are isolated
- the task depends on new notes added after the last graph run

Use incremental rebuilds when possible.

## Output Expectations

When using graph context in an answer:

- name the community or bridge node that anchored the search
- distinguish between extracted facts and inferred links
- mention the source files used for confirmation
- say clearly when the graph does not contain enough information

## Graphify vs ThoughtMap

Both tools help agents understand context, but serve different purposes:

| Aspect | Graphify | ThoughtMap |
|--------|----------|------------|
| **Scope** | One project folder | All data sources (Second Brain, Obsidian, Wispr, reviews) |
| **Structure** | Entity-relationship graph (nodes, edges, communities) | Semantic clusters of text chunks |
| **Best for** | "How do parts of this project connect?" | "What does the user know/think about X?" |
| **Access** | Read `graphify-out/` files directly | MCP tools (`search_thoughts`, `list_clusters`, etc.) |
| **Granularity** | Entities and relationships | Raw text chunks with source metadata |

**Use graphify** when working within a specific project and needing structural context (dependencies, decisions, relationships between concepts).

**Use ThoughtMap MCP** when needing broad context across all the user's knowledge — especially for cross-project insights, historical decisions, or "what have I written about X?"

**Combine both** for the deepest context: graphify for project structure, ThoughtMap for semantic search across everything.