---
type: framework
status: active
project: thoughtmap
created: 2026-04-28
updated: 2026-04-28
tags: [type/framework, project/thoughtmap, topic/annotation, topic/fine-tuning, topic/data-preparation]
---

# ThoughtMap Annotation and Data Preparation Framework

## 1. Core Claim Boundary

This framework exists because ThoughtMap output is not automatically training truth.

Use this claim model everywhere:

| Layer | What it is | Can train from it? | Truth level |
|---|---|---|---|
| Raw source notes/transcripts | Evidence written or spoken by the user | Yes, as input/evidence | Ground evidence |
| Generated ThoughtMap output | Automatic interpretation of evidence | Yes, as candidate data only | Candidate/proposal |
| External LLM annotation | Gemini/OpenAI/local model suggestion | Yes, as weak label only | Preannotation |
| User annotation | Explicit user correction/accept/reject/retype/split decision | Yes, as gold label | Training truth |
| Dataset JSONL | Snapshot compiled from annotations and evidence | Yes, after validation | Derived training artifact |

The strongest rule:

> Generated ThoughtMap artifacts can propose annotation tasks, but only explicit user annotation or registry decisions become gold training labels.

This avoids overclaiming. ThoughtMap is a map of thoughts, but the map is generated. The user's annotations on top of that map are the durable source of truth for fine-tuning.

## 2. Product Goal

Build a simple annotation interface that turns ThoughtMap's uncertain or useful candidates into structured training examples.

The interface should let the user:

- review one candidate at a time,
- understand exactly what is being annotated,
- change only the fields relevant to that annotation type,
- accept, reject, retype, merge, split, or rewrite according to clear rules,
- optionally request Gemini/OpenAI/local LLM preannotation,
- export clean train/eval JSONL datasets for fine-tuning.

The UI should reduce cognitive load. It should not expose the full internal pipeline at once.

## 3. Recommended Surface

Use a two-layer annotation system.

### 3.1 Web Annotation Console

Extend the current ThoughtMap web UI with an `/annotate` route.

Purpose:

- fast review,
- side-by-side evidence and model proposal,
- constrained editing controls,
- immediate save into annotation store.

Suggested routes:

```text
/annotate
/annotate/entities
/annotate/atoms
/annotate/summaries
/annotate/relations
/annotate/vectors
```

Suggested API endpoints:

```text
GET  /api/annotations/tasks?type=entity_type_resolution&status=pending
POST /api/annotations/tasks/<task_id>
POST /api/annotations/preannotate/<task_id>
POST /api/annotations/export
GET  /api/annotations/stats
```

### 3.2 Obsidian Kanban Annotation Queue

Keep a generated Kanban-style queue for lightweight planning and review.

Suggested file:

```text
Second Brain/Operations/Kanban/ThoughtMap Annotation Queue.md
```

Columns:

```text
## Inbox
## Preannotated
## Needs Human Label
## Disputed
## Accepted
## Rejected
## Exported
```

The Kanban file is useful as an operational queue, but the canonical annotation records should live in a structured local store.

## 4. Annotation Store

Store durable annotation records under local runtime data, not generated output.

Suggested path:

```text
Second Brain/Projects/thoughtmap/data/annotations/annotations.jsonl
Second Brain/Projects/thoughtmap/data/annotations/tasks.jsonl
Second Brain/Projects/thoughtmap/data/annotations/datasets/
```

Reason:

- annotations may contain private source snippets,
- training examples may include sensitive personal notes,
- user labels should survive reruns,
- generated `thoughtmap-out/` should remain rebuildable.

## 5. Annotation Task Schema

Each annotation task should be a small, auditable object.

```json
{
  "task_id": "ann_20260428_ab12cd34",
  "task_type": "entity_type_resolution",
  "status": "pending",
  "priority": "high",
  "source": {
    "source_file": "Second Brain/Operations/Meetings/2026-04-22_fenix_konrad_bujak.md",
    "section": "Notes",
    "timestamp": "2026-04-22",
    "atom_id": "atom:...",
    "chunk_id": "atom:..."
  },
  "evidence": {
    "text": "Spotkanie z Konradem Bujakiem o Fenix i Roche.",
    "span": "Roche",
    "context_before": "",
    "context_after": ""
  },
  "proposal": {
    "model": "thoughtmap-ner-v1",
    "label": {"type": "location", "decision": "verify"},
    "confidence": 0.62,
    "reason": "spaCy classified candidate as GPE/LOC"
  },
  "preannotation": {
    "provider": null,
    "model": null,
    "label": null,
    "confidence": null,
    "reason": null
  },
  "user_label": null,
  "locked_fields": ["source", "evidence.text", "evidence.span"],
  "editable_fields": ["type", "decision", "canonical_name", "aliases", "reason"],
  "created_at": "2026-04-28T12:00:00",
  "updated_at": "2026-04-28T12:00:00"
}
```

## 6. Annotation Types

### 6.1 Entity Type Resolution

Purpose: fix incorrect entity type and false positives.

User sees:

- source text,
- highlighted candidate span,
- current ThoughtMap type,
- model confidence,
- existing registry matches.

User can change:

- `decision`: `verify | reject | retype | merge | alias | unsure`,
- `type`: `person | organization | project | tool | location | concept | other`,
- `canonical_name`,
- `aliases`,
- short reason.

User cannot change:

- source text,
- evidence span,
- source file metadata.

Export target:

```text
entity_type_resolver.train.jsonl
entity_type_resolver.eval.jsonl
```

### 6.2 Entity Canonicalization

Purpose: decide whether two names are the same entity.

User sees:

- candidate A,
- candidate B,
- mentions and source snippets for both,
- current registry entry if one exists.

User can change:

- `same_entity`: `true | false | unsure`,
- `canonical_name`,
- `aliases`,
- `target_entity_id`,
- reason.

Export target:

```text
entity_canonicalizer.train.jsonl
```

### 6.3 ThoughtAtom Split and Routing

Purpose: teach the system how to split mixed notes and route atoms.

User sees:

- original segment,
- proposed atoms,
- signal type and index targets for each atom.

User can change:

- split boundaries,
- atom title,
- `signal_type`,
- `domains`,
- `index_targets`,
- `quality`: `keep | low_value | duplicate | boilerplate | needs_review | discard`.

User cannot change:

- original segment text as evidence.

Export target:

```text
atom_router.train.jsonl
atom_router.eval.jsonl
```

### 6.4 Domain Assignment

Purpose: label which project/domain a thought belongs to.

User sees:

- atom text,
- proposed domains,
- nearest clusters/entities.

User can change:

- domain IDs,
- confidence category,
- whether the domain is central or peripheral,
- whether a new domain should be proposed.

Export target:

```text
domain_classifier.train.jsonl
```

### 6.5 Summary Faithfulness

Purpose: train/evaluate short summaries for clusters, entities, and topics.

User sees:

- representative atoms,
- generated summary,
- referenced entities,
- source links.

User can change:

- rating: `faithful | partly_faithful | misleading | too_broad | too_specific`,
- corrected summary,
- corrected label,
- reason.

Export target:

```text
summary_labeler.train.jsonl
summary_labeler.eval.jsonl
```

### 6.6 Relation Validation

Purpose: validate entity/project/person relations.

User sees:

- subject,
- predicate,
- object,
- evidence snippet,
- related source file.

User can change:

- `decision`: `verify | reject | change_predicate | unsure`,
- predicate,
- reason.

Export target:

```text
relation_validator.train.jsonl
```

### 6.7 Vector Narration / Vec2Text

Purpose: annotate what an embedding centroid, direction, or nearest-neighbor group means in human language.

User sees:

- anchor entity/topic,
- nearest examples,
- vector operation,
- proposed narration.

User can change:

- useful/not useful,
- corrected narration,
- whether the vector direction is interpretable,
- privacy risk flag.

Export target:

```text
vector_narrator.train.jsonl
vec2text_pairs.train.jsonl
```

## 7. UI Explanation Rules

Each task type must include an inline instruction panel. The panel should answer three questions:

1. What am I deciding?
2. Which fields can I change?
3. What makes a good label?

Example for Entity Type Resolution:

```text
Decide whether the highlighted span is a real entity and what type it is.
Do not correct the source text. Only correct the entity decision.
Reject generic phrases, task labels, markdown artifacts, and accidental spans.
Use organization for companies/institutions, location for places, project for named workstreams/products, tool for software/frameworks, person for people.
```

Example for Summary Faithfulness:

```text
Check whether the summary is faithful to the representative atoms.
Do not reward nice prose if it adds claims not supported by the evidence.
Prefer short, boring, accurate summaries over broad strategic interpretations.
```

## 8. Candidate Generation

Annotation tasks should be generated automatically from uncertainty, disagreement, and high-value training gaps.

Sources:

- low-confidence NER candidates,
- entity type conflicts between spaCy, heuristics, registry, and LLM validation,
- organization/location swaps,
- candidates manually renamed in Kanban,
- atoms routed to `needs_review`,
- large mixed segments split into multiple atoms,
- generated summaries for large/high-impact clusters,
- relation candidates above a minimum evidence threshold,
- vector directions with clear nearest-neighbor groups.

Do not generate annotation tasks for every record. Prefer high-information examples.

Priority rules:

1. Manual conflicts or repeated mistakes.
2. High-mention entities with low confidence.
3. Organization/location/person confusion.
4. Atoms that affect semantic Chroma routing.
5. Summaries shown prominently in UI/report.
6. Vector narration only after the core labels are improving.

## 9. Automatic Preannotation

Gemini/OpenAI can help label data, but their output is not gold truth.

Use them for:

- second-opinion labels,
- generating explanations for uncertain examples,
- proposing canonical names and aliases,
- suggesting corrected summaries,
- comparing multiple candidate labels.

Rules:

- cloud preannotation must be explicit and opt-in,
- store provider/model/prompt/hash with every preannotation,
- never treat external labels as user labels,
- preannotations can become silver data only after validation policy is defined,
- for private notes, default to local model preannotation unless the user explicitly chooses cloud.

Suggested preannotation record:

```json
{
  "provider": "openai",
  "model": "gpt-4.1-mini",
  "prompt_version": "entity_type_resolution_v1",
  "label": {"type": "organization", "decision": "verify"},
  "confidence": 0.88,
  "reason": "Roche is a company in the context of Fenix meeting notes.",
  "created_at": "2026-04-28T12:00:00"
}
```

## 10. Dataset Compilation

Datasets should be compiled from annotation records, not hand-written separately.

Compiler inputs:

- annotation records,
- source snippets,
- entity registry,
- task metadata,
- split policy.

Compiler outputs:

```text
data/training/entities/entity_type_resolver.train.jsonl
data/training/entities/entity_type_resolver.eval.jsonl
data/training/entities/entity_canonicalizer.train.jsonl
data/training/atoms/atom_router.train.jsonl
data/training/domains/domain_classifier.train.jsonl
data/training/summaries/summary_labeler.train.jsonl
data/training/relations/relation_validator.train.jsonl
data/training/vec2text/vector_narrator.train.jsonl
```

Split rules:

- split by source file or date, not random row when examples from the same source are similar,
- keep gold/user labels separate from silver/preannotated labels,
- keep hard negatives tagged,
- keep a frozen eval set for each task type,
- do not let the same entity/source snippet appear in both train and eval when measuring generalization.

## 11. Minimal Data Preparation Pipeline

First implementation target:

```text
candidate generation
  -> annotation tasks JSONL
  -> web/kanban annotation queue
  -> user labels
  -> validated annotation store
  -> dataset compiler
  -> train/eval JSONL
  -> baseline metrics
```

Suggested scripts/modules:

```text
annotation/tasks.py          # task dataclass/schema and validation
annotation/generate.py       # create tasks from ThoughtMap candidates
annotation/store.py          # append/load/update annotation records
annotation/export.py         # compile train/eval JSONL
annotation/preannotate.py    # optional Gemini/OpenAI/local preannotation
annotation/metrics.py        # coverage and confusion reports
web/annotation_api.py        # HTTP handlers or helpers for annotation endpoints
```

The first useful CLI can be:

```text
python -m thoughtmap.annotation.generate --task-type entity_type_resolution
python -m thoughtmap.annotation.export --task-type entity_type_resolution
```

## 12. Validation and Metrics

Track dataset quality before training.

Metrics:

- number of pending tasks by type,
- number of user-labeled examples by type,
- gold/silver ratio,
- hard negative count,
- organization/location/person confusion count,
- disagreement between ThoughtMap proposal and user label,
- disagreement between cloud preannotation and user label,
- eval set size and class balance,
- source leakage warnings.

Minimum viable dataset for the first Entity Type Resolver:

- 100-200 user-labeled examples,
- at least 30 hard negatives,
- at least 20 organization/location confusion examples if available,
- frozen eval set of at least 30 examples,
- class balance report before training.

## 13. UI MVP

First UI should be deliberately small.

Screen layout:

```text
left: task list / filters
center: evidence card with highlighted candidate
right: annotation form + instruction panel
bottom: source metadata and save actions
```

Filters:

- task type,
- status,
- priority,
- source,
- proposed type,
- disagreement only,
- hard negatives only.

Buttons:

- Accept proposal,
- Reject,
- Retype,
- Merge/Alias,
- Unsure,
- Ask local model,
- Ask Gemini/OpenAI,
- Save and next.

The MVP should start with `entity_type_resolution` only. Add atom routing and summaries after the annotation store and export path are proven.

## 14. Immediate Next Step

Build the annotation-data MVP in this order:

1. Add annotation schemas and local JSONL store.
2. Generate `entity_type_resolution` tasks from current entities and known conflicts.
3. Render `ThoughtMap Annotation Queue.md` as a Kanban queue.
4. Add `/annotate/entities` web screen for constrained labeling.
5. Export `entity_type_resolver.train.jsonl` and `entity_type_resolver.eval.jsonl`.
6. Print dataset metrics and confusion counts.
7. Only then train or fine-tune a model.

This makes annotation the foundation of the model layer instead of an afterthought.

## Related

- [[model-optimization-finetuning-plan|Model Optimization and Fine-Tuning Plan]]
- [[vec2text-training-guide|Vec2Text training guide]]
- [[../PRD|ThoughtMap v2 PRD]]