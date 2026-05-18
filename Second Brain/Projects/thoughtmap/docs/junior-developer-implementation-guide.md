---
type: guide
status: active
project: thoughtmap
created: 2026-04-28
updated: 2026-04-28
tags: [type/guide, project/thoughtmap, audience/developer, level/junior]
---

# ThoughtMap v2 — Junior Developer Implementation Guide

## 1. Purpose

This file is the working guide for a junior developer implementing ThoughtMap v2. If you follow this document, you should be able to work in the repository without needing extra verbal instructions from the maintainer.

Your job is not to invent a new product direction. Your job is to implement the plan described in [ThoughtMap v2 PRD](../PRD.md) carefully, incrementally, and in a way that keeps the codebase easy to understand and maintain.

The most important idea:

> ThoughtMap must process thoughts, not just chunks of text.

The current system chunks text by sentence/token windows. The new system must first split mixed notes into semantic units called `ThoughtAtom`, then classify, route, curate, embed, and cluster those units.

## 2. Read This First

Before coding, read these files in this order:

1. `Second Brain/Projects/thoughtmap/CONTEXT.md` — project history and current milestone.
2. `Second Brain/Projects/thoughtmap/PRD.md` — product requirements for v2.
3. `Second Brain/Projects/thoughtmap/README.md` — how the current system runs.
4. `Second Brain/Projects/thoughtmap/docs/extraction-pipeline.md` — how clusters, topics, and entities currently work.
5. `.github/instructions/thoughtmap.instructions.md` — project coding rules.

Do not start by editing code. First understand the current pipeline.

## 3. Product Direction

ThoughtMap v2 should follow this rule:

```text
Raw text is evidence.
Structured output is interpretation.
Manual curation is truth.
Generated prose is presentation.
```

This means:

- Never replace source text with LLM prose as the primary record.
- Use LLMs mainly for structured JSON outputs: segmentation, classification, routing, entities, relations, and short titles.
- Manual curation must override automatic decisions.
- Generated summaries are useful for UI and reports, but should not become the main embedding corpus.

## 4. Current Architecture

Current high-level pipeline:

```text
extract_all
  -> chunk_all
  -> embed_batch
  -> merge_similar_chunks
  -> store_chunks
  -> load_all_embeddings
  -> cluster_all
  -> condense / entities / reports / UI / kanban
```

Current package layout:

```text
Second Brain/Projects/thoughtmap/
├── config.py
├── run.py
├── __main__.py
├── core/
│   ├── extract.py
│   ├── chunk.py
│   ├── embed.py
│   └── cluster.py
├── analysis/
│   ├── condense.py
│   ├── echoes.py
│   ├── index.py
│   ├── kanban.py
│   ├── ner.py
│   ├── report.py
│   └── semantic_layers.py
└── web/
    ├── server.py
    └── viz.py
```

Keep these top-level boundaries:

- `core/` — extraction, normalization, segmentation, chunking, embeddings, clustering.
- `analysis/` — classification, entities, curation, reports, semantic artifacts, routing, storage policies.
- `web/` — server and UI only.
- `run.py` — orchestration only. It should stay readable.
- `config.py` — configuration only. Do not hide business logic here.

## 5. Target Architecture

Target pipeline:

```text
source extraction
  -> TextSegment
  -> ThoughtAtom
  -> structured classification
  -> entity and relation candidates
  -> manual registry resolution
  -> routing
  -> embedding only for semantic atoms
  -> clustering and downstream outputs
```

Target module structure:

```text
Second Brain/Projects/thoughtmap/
├── config.py
├── run.py
├── __main__.py
├── core/
│   ├── models.py                 # dataclasses / typed models shared by the pipeline
│   ├── extract.py                # temporary compatibility wrapper, eventually thin
│   ├── chunk.py                  # embedding chunk creation, not semantic splitting
│   ├── embed.py
│   ├── cluster.py
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── obsidian_daily.py
│   │   ├── second_brain.py
│   │   ├── wispr.py
│   │   └── reviews.py
│   └── segment/
│       ├── __init__.py
│       ├── deterministic.py      # cheap splitters: headings, bullets, timestamps
│       ├── llm.py                # structured LLM thought atomizer
│       ├── prompts.py            # prompts/schemas for segmentation
│       └── validate.py           # schema validation and fallback handling
├── analysis/
│   ├── classify.py               # signal/domain/index classification
│   ├── routing.py                # index target decisions
│   ├── relations.py              # relation candidates
│   ├── storage_tiers.py          # hot/cold manifests and prune planning
│   ├── curation.py               # Obsidian curation board sync/generation
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── candidates.py         # candidate generation from atoms/spaCy/regex
│   │   ├── registry.py           # manual source-of-truth registry
│   │   ├── resolve.py            # verify/reject/merge/retype/alias logic
│   │   └── notes.py              # generated entity notes/index
│   └── reports/
│       ├── __init__.py
│       ├── routing_report.py
│       ├── curation_report.py
│       └── run_summary.py
├── web/
│   ├── server.py
│   └── viz.py
├── scripts/
│   ├── prototype_thought_atoms.py
│   ├── rebuild_semantic_store.py
│   └── inspect_routing_report.py
└── tests/
    ├── fixtures/
    ├── test_segment_deterministic.py
    ├── test_atom_schema.py
    ├── test_routing.py
    └── test_entity_registry.py
```

This is the preferred direction, not a command to perform one huge refactor. Move toward it gradually while preserving working behavior.

## 6. Refactoring Rule

Do not refactor the whole repository before the first feature works.

Use this order:

1. Add new code next to old code.
2. Create a read-only prototype output.
3. Validate the output on real data.
4. Add tests for the new behavior.
5. Only then connect the new module into the main pipeline.
6. Remove or simplify old code only after the replacement is proven.

Good first deliverable:

```text
scripts/prototype_thought_atoms.py
  -> reads 10-20 recent daily/review/Wispr TextSegments
  -> writes thought_atoms.json
  -> writes routing_report.json
  -> does not modify Chroma
```

## 7. Coding Standards

### 7.1 File Size

Keep Python files short enough to understand.

Guidelines:

- Aim for 150-300 lines per file.
- If a file grows beyond 400 lines, ask whether it should be split.
- A file should have one main responsibility.
- Avoid dumping unrelated helpers into the same module.

Examples:

- Good: `analysis/entities/registry.py` handles registry load/apply/write.
- Bad: `analysis/entities.py` handles spaCy, registry, notes, curation, reports, and prompts.

### 7.2 Function Size

Guidelines:

- Aim for functions under 50 lines.
- A function should do one thing and return a clear result.
- If a function needs many comments to explain the steps, split it into smaller functions.
- Keep orchestration functions readable as a sequence of named steps.

Good pattern:

```python
def atomize_segments(segments: list[TextSegment]) -> list[ThoughtAtom]:
    candidates = deterministic_split_segments(segments)
    mixed = select_segments_for_llm(candidates)
    llm_atoms = llm_atomize_segments(mixed)
    return merge_atomization_results(candidates, llm_atoms)
```

Bad pattern:

```python
def atomize_segments(segments):
    # 300 lines of parsing, prompts, validation, file writes, and routing
```

### 7.3 Naming

Use explicit names.

Good names:

- `ThoughtAtom`
- `EntityCandidate`
- `RoutingDecision`
- `load_entity_registry`
- `apply_manual_entity_decisions`
- `route_atom_to_indexes`

Avoid vague names:

- `data`
- `thing`
- `process`
- `handle`
- `magic`
- `obj`

Short names like `i`, `j`, `x`, `y` are okay only in tiny local loops or math.

### 7.4 Comments and Docstrings

Write comments that explain why something exists, not what every line does.

Good comment:

```python
# Fail closed: uncertain segmentation should go to review, not into Chroma.
```

Bad comment:

```python
# Set status to needs_review.
```

Use docstrings for public functions and important dataclasses:

```python
def route_atom_to_indexes(atom: ThoughtAtom) -> RoutingDecision:
    """Decide which indexes should receive a ThoughtAtom.

    This function must not write files or mutate Chroma. It returns a decision
    that later pipeline stages can apply or surface for manual review.
    """
```

Add comments for:

- non-obvious business rules,
- privacy boundaries,
- fail-closed behavior,
- compatibility bridges,
- manual curation precedence,
- assumptions that should be revisited.

Do not add comments that simply repeat the code.

### 7.5 Types and Data Models

Use dataclasses or Pydantic-style schemas for important records. Prefer typed models over loose dictionaries when data crosses module boundaries.

Required core models:

```python
@dataclass(frozen=True)
class TextSegment:
    segment_id: str
    source: str
    source_file: str
    section: str | None
    timestamp: str | None
    text: str


@dataclass(frozen=True)
class ThoughtAtom:
    atom_id: str
    parent_segment_id: str
    text: str
    title: str
    signal_type: str
    domains: list[DomainAssignment]
    index_targets: list[str]
    quality: str
    confidence: float
```

Do not pass raw dictionaries everywhere if the fields matter.

### 7.6 Side Effects

Separate pure logic from side effects.

Pure logic:

- parse text,
- split text,
- classify atom,
- resolve entity,
- decide route.

Side effects:

- read/write files,
- write Chroma,
- call Ollama,
- generate markdown boards,
- serve HTTP.

Rule:

> Most functions should return data. Only a small number of functions should write files or mutate external state.

### 7.7 Error Handling

ThoughtMap should degrade gracefully.

Rules:

- Bad LLM JSON must not crash the whole run.
- Bad LLM JSON must not be silently accepted.
- Invalid or uncertain records should be routed to `needs_review`.
- Optional local inputs, such as Wispr SQLite, must fail gracefully.
- Logs should explain what was skipped and why.

Fail-closed example:

```python
try:
    atoms = parse_llm_atoms(response)
except InvalidStructuredOutput as exc:
    return [make_review_atom(segment, reason=str(exc))]
```

## 8. Decision Boundaries

You may make small implementation decisions yourself. You must ask the maintainer before important product or data decisions.

### You Can Decide Yourself

- Function names and file names that follow this guide.
- Small helper extraction.
- Test fixture names.
- Internal variable names.
- Formatting changes inside files you are already editing.
- Small validation details that do not change behavior.
- Adding clear comments/docstrings.

### You Must Ask The Maintainer Before Deciding

Ask before making any decision that affects data, product behavior, or long-term architecture.

Examples:

- Deleting, pruning, or compacting existing Chroma data.
- Changing what sources are indexed by default.
- Changing which sections of daily notes are included or excluded.
- Sending any data to a cloud model or external API.
- Changing the entity registry format after it has data.
- Changing manual curation semantics.
- Reintroducing topology or ontology UI surfaces.
- Deciding that a class of user notes should be discarded permanently.
- Changing retention periods.
- Changing source-of-truth location for registry or curation files.
- Making breaking changes to generated output schemas.
- Removing old outputs before migration is validated.

When unsure, ask. A good question is better than an irreversible silent decision.

Use this format:

```markdown
## Decision Needed

**Context**: What I found.
**Options**: 2-3 reasonable options.
**Recommendation**: What I would do and why.
**Risk**: What could go wrong.
```

### 8.1 Phase 1 Defaults and Clarifications

These defaults answer the first implementation questions. Use them for Phase 1 unless the maintainer changes them explicitly.

#### Confidence threshold for `semantic`

Phase 1 is read-only, so it must not auto-write anything into Chroma.

For prototype reports, use this routing policy:

- `confidence >= 0.80` and `quality == "usable"` — propose `semantic` as an automatic target.
- `0.60 <= confidence < 0.80` — route to `needs_review`; include the likely target in the report as `suggested_target`.
- `confidence < 0.60` — route to `needs_review` or `discard_candidate`, depending on the reason.
- any atom that looks like boilerplate, generated output, duplicated operational noise, or malformed LLM output must not go directly to `semantic`, even if confidence is high.

Do not treat `0.80` as a permanent production threshold. It is the conservative prototype threshold. Production migration requires reviewing sample output first.

#### Minimal cleanup before embedding

Keep two text fields when practical:

- `raw_text` — exact evidence text from the source segment.
- `text` or `embed_text` — minimally cleaned text used for embedding.

Allowed cleanup before embedding:

- trim leading/trailing whitespace,
- collapse repeated blank lines and excessive internal whitespace,
- remove Obsidian task checkbox markers such as `- [ ]` or `- [x]` when they are not meaningful,
- remove hidden ThoughtMap card markers such as `%%tm:id=...%%`,
- strip markdown formatting markers when they do not change meaning, such as `**bold**`, backticks, or simple wikilink brackets,
- normalize obvious broken line wraps.

Not allowed before embedding:

- paraphrasing,
- summarizing,
- translating,
- removing dates, names, numbers, amounts, project names, or uncertainty markers,
- merging two unrelated thoughts because they are close in the same paragraph,
- deleting text because it seems unimportant without routing it to review.

If cleanup changes meaning, it is too much cleanup.

#### Durable registry location and shape

For Phase 3 and later, the durable manual registry should live locally in:

```text
Second Brain/Projects/thoughtmap/data/curation/entity_registry.json
```

This path is intentionally under `data/` because it may contain private names, aliases, suppressions, and decisions. It is local durable truth, not a generated public artifact.

Generated or human-facing curation surfaces may live in:

```text
Second Brain/Operations/Kanban/ThoughtMap Entity Curation.md
Second Brain/Operations/thoughtmap-out/curation_report.md
```

Expected registry shape:

```json
{
  "version": 1,
  "updated_at": "2026-04-28T00:00:00",
  "entities": {
    "entity_id": {
      "canonical_name": "Pietro Vinci",
      "type": "person",
      "aliases": ["Pietro", "P. Vinci"],
      "status": "verified",
      "source": "manual",
      "notes": "Optional short human note."
    }
  },
  "decisions": {
    "normalized candidate name": {
      "action": "reject | merge | retype | alias | verify",
      "target_entity_id": "entity_id-or-null",
      "reason": "Short reason from curation."
    }
  }
}
```

Do not change this schema after real curation data exists without asking the maintainer.

#### Phase 1 sampling scope

Start Phase 1 with only these sources:

- recent daily notes,
- recent daily/weekly reviews,
- recent Wispr-derived segments.

Do not include broad Second Brain project notes in the first prototype. Project notes are usually more structured and can hide whether the atomizer actually solves the hard problem: mixed daily logs and voice notes.

After the first sample review, add a second comparison batch from project notes:

- 5-10 recent or active project `CONTEXT.md` / project notes,
- reported separately as `project_note_sample`,
- no Chroma writes.

This lets the maintainer compare atom quality across messy journal material and cleaner project documentation before changing the main pipeline.

## 9. Implementation Phases

### Phase 1 — Read-Only ThoughtAtom Prototype

Goal: produce `thought_atoms.json` without changing Chroma or clustering.

Build:

- `core/models.py`
- `core/segment/deterministic.py`
- `core/segment/llm.py`
- `core/segment/validate.py`
- `scripts/prototype_thought_atoms.py`

Output:

```text
Second Brain/Operations/thoughtmap-out/prototypes/thought_atoms.json
Second Brain/Operations/thoughtmap-out/prototypes/routing_report.json
```

Acceptance criteria:

- 10-20 recent mixed segments produce plausible atoms.
- Atoms preserve source file, section, timestamp, and parent segment ID.
- Invalid LLM output becomes `needs_review`.
- No Chroma writes happen.
- Existing pipeline still runs as before.

### Phase 2 — Structured Routing Dry Run

Goal: classify atoms and decide targets without changing active store.

Build:

- `analysis/classify.py`
- `analysis/routing.py`
- `analysis/reports/routing_report.py`

Output:

```text
routing_report.json
```

Acceptance criteria:

- Counts by source, domain, signal type, quality, and target.
- Boilerplate/generated artifacts are identified.
- Communication and activity atoms do not automatically flood semantic clustering.
- Risky decisions are surfaced for review.

### Phase 3 — Entity Registry MVP

Goal: make manual entity decisions durable.

Build:

- `analysis/entities/registry.py`
- `analysis/entities/resolve.py`
- `analysis/curation.py`

Output:

```text
data/curation/entity_registry.json
Second Brain/Operations/Kanban/ThoughtMap Entity Curation.md
```

Acceptance criteria:

- Rejected entities do not reappear.
- Aliases and canonical names affect generated entity notes.
- Merge and retype decisions are respected.
- Existing `analysis/ner.py` can still run during migration.

### Phase 4 — Semantic Store Migration

Goal: embed ThoughtAtoms instead of raw mixed chunks.

Build:

- `analysis/storage_tiers.py`
- active manifest generation,
- dry-run Chroma prune plan,
- optional rebuild command.

Acceptance criteria:

- Chroma is not pruned without an explicit dry-run report first.
- Active manifest matches records intended for semantic clustering.
- Cold archive remains inspectable.
- Clusters are more coherent on mixed daily/review content.

### Phase 5 — Full Curation Loop

Goal: make Obsidian curation boards affect the next run.

Build:

- Entity curation board.
- Segment curation board.
- Domain curation board.
- Curation sync and report.

Acceptance criteria:

- Manual decisions are applied before generated outputs.
- Generated files do not overwrite manual truth.
- `curation_report.md` explains what was applied.

## 10. Output and Data Boundaries

Never manually edit generated ThoughtMap output files unless the task explicitly says to modify generation logic and rerun the pipeline.

Generated output location:

```text
Second Brain/Operations/thoughtmap-out/
```

Runtime data location:

```text
Second Brain/Projects/thoughtmap/data/
```

Suggested curation location:

```text
Second Brain/Projects/thoughtmap/data/curation/
```

Generated Obsidian boards:

```text
Second Brain/Operations/Kanban/
```

Important boundary:

- `thoughtmap-out/` is generated output.
- `data/curation/` is durable manual truth.
- Source notes are evidence.
- Chroma is a derived active store.

## 11. LLM Rules

Use local Ollama by default.

Allowed LLM uses:

- split mixed text into ThoughtAtoms,
- classify signal type,
- assign domains,
- propose index targets,
- extract entity candidates,
- extract relation candidates,
- generate short titles,
- generate short UI summaries.

Do not use LLMs to:

- rewrite source text as the embedded record,
- make permanent manual-truth decisions,
- discard data permanently,
- call cloud models unless the maintainer explicitly approves.

Structured output requirement:

- The LLM should return JSON or a schema-equivalent format.
- Validate every response.
- Log failures.
- Route uncertain output to review.

## 12. Testing Strategy

Every new module should have focused tests.

Minimum tests for Phase 1:

- deterministic splitter handles headings, bullets, timestamps, and blank lines,
- ThoughtAtom IDs are stable for unchanged input,
- invalid LLM output produces `needs_review`,
- mixed daily section fixture creates multiple atoms,
- atom JSON round-trips without losing required fields.

Minimum tests for routing:

- boilerplate is routed to `discard` or `archive`,
- communication goes to `communication`,
- project decisions go to `project` and `semantic`,
- tasks go to `activity`,
- low-confidence records go to `needs_review`.

Minimum tests for entity registry:

- rejected entity stays rejected,
- alias resolves to canonical name,
- retype changes entity type,
- merge collapses two entities,
- manual registry beats automatic NER.

Use small fixtures. Do not write tests that require the full vault unless the test is explicitly an integration test.

## 13. Verification Commands

Use the repository's Python environment. On Windows, the venv path is usually:

```powershell
.venv\Scripts\python.exe
```

Recommended checks after code changes:

```powershell
python -m py_compile "Second Brain/Projects/thoughtmap/run.py"
python -m py_compile "Second Brain/Projects/thoughtmap/core/segment/deterministic.py"
python -m py_compile "Second Brain/Projects/thoughtmap/analysis/routing.py"
```

When tests exist:

```powershell
pytest "Second Brain/Projects/thoughtmap/tests"
```

Import smoke test:

```powershell
python -c "from thoughtmap.core.extract import extract_all; from thoughtmap.core.chunk import chunk_all; from thoughtmap.core.cluster import cluster_all; print('OK')"
```

After major pipeline changes, also verify Docker still starts:

```powershell
docker compose up --build
```

Do not run expensive full rebuilds repeatedly while developing small modules. Prefer small fixtures and prototype scripts first.

## 14. Development Workflow

For every task:

1. Read relevant project docs.
2. Identify the smallest safe change.
3. Write or update focused tests/fixtures.
4. Implement the change.
5. Run targeted checks.
6. Inspect generated JSON or markdown output manually.
7. Update docs if behavior changed.
8. If a product decision appears, stop and ask the maintainer.

Recommended commit style, if asked to commit:

```text
thoughtmap: add thought atom prototype
thoughtmap: add entity registry resolver
thoughtmap: document semantic routing
```

Do not commit unless explicitly asked.

## 15. Definition of Done

A task is done only when all relevant items are true:

- Code is small and placed in the correct module.
- Public functions have clear types and docstrings.
- Non-obvious rules have comments explaining why.
- Tests or fixtures cover the important behavior.
- Failure modes are handled.
- No cloud dependency was added without approval.
- No destructive data operation was performed.
- Generated outputs are inspectable.
- Existing pipeline behavior is not broken.
- The change is reflected in docs or `CONTEXT.md` when it changes project direction.

## 16. What Not To Do

Do not:

- perform one giant refactor before proving the new pipeline,
- hide product logic inside `config.py`,
- let `run.py` become a large business-logic file,
- add cloud calls by default,
- embed LLM-generated summaries as source evidence,
- discard user notes permanently without approval,
- reintroduce topology or ontology UI tabs,
- silently change output schemas,
- manually edit `thoughtmap-out/` as if it were source truth,
- ignore manual curation when it conflicts with automatic extraction.

## 17. If You Discover Something Unexpected

If you find a problem that is not covered here, classify it:

### Small Implementation Issue

Examples:

- helper function should be split,
- test fixture needs another case,
- one module needs a better name,
- a parser should handle an obvious markdown variation.

You may fix it if the change is local and low-risk.

### Important Product or Data Issue

Examples:

- a source contains sensitive data not expected by the pipeline,
- a whole note category looks like noise,
- Chroma contains stale records that need deletion,
- entity registry schema needs a breaking change,
- manual curation conflicts with automatic output,
- a major domain is missing from routing,
- an LLM output cannot be trusted for a class of notes.

Stop and ask the maintainer using the `Decision Needed` format from section 8.

Do not guess silently.

## 18. First Recommended Task

Start with a read-only prototype:

```text
Goal: Generate ThoughtAtoms from recent mixed source segments.

Files to add:
- core/models.py
- core/segment/__init__.py
- core/segment/deterministic.py
- core/segment/validate.py
- scripts/prototype_thought_atoms.py
- tests/test_segment_deterministic.py
- tests/test_atom_schema.py

Files to avoid touching initially:
- core/embed.py
- core/cluster.py
- data/chroma/
- thoughtmap-out/ generated files except prototype output
```

Prototype output should be written to:

```text
Second Brain/Operations/thoughtmap-out/prototypes/
```

This gives the maintainer something concrete to review before the production pipeline changes.

## 19. Mental Model

Think of the system as four layers:

```text
Evidence Layer
  raw notes, Wispr transcripts, reviews, project docs

Interpretation Layer
  ThoughtAtoms, classifications, entity candidates, relation candidates

Truth Layer
  manual curation, entity registry, suppressions, aliases, route overrides

Presentation Layer
  reports, UI, topic notes, entity notes, kanban boards
```

Most bugs happen when these layers get mixed together.

If you keep the layers separate, the code will stay understandable.

## 20. Final Reminder

This project is personal knowledge infrastructure. Treat user notes, transcripts, and curation decisions as important data.

Be careful, incremental, and explicit. When in doubt, preserve evidence, route uncertainty to review, and ask before making irreversible decisions.
