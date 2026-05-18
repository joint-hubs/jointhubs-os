---
type: plan
status: active
project: thoughtmap
created: 2026-04-28
updated: 2026-04-28
tags: [type/plan, project/thoughtmap, topic/fine-tuning, topic/entities, topic/vec2text]
---

# ThoughtMap Model Optimization and Fine-Tuning Plan

## 1. Thesis

ThoughtMap does not need one large general-purpose language model for every stage. The project does a small number of repeated, structured tasks:

- split mixed notes into ThoughtAtoms,
- classify atoms into signal types, domains, and index targets,
- extract and type entities,
- resolve entity aliases and false positives,
- generate short cluster/entity summaries,
- describe embedding centroids and vector directions.

These are good candidates for small specialized models trained on ThoughtMap's own data and curation history.

The target is not to replace the whole pipeline with a model. The target is to replace fragile generic prompts with smaller, testable, local models whose outputs are schema-bound and measurable.

Important boundary: generated ThoughtMap output is not automatically gold training truth. It can create candidates and annotation tasks. Gold labels come from explicit user annotation, durable registry decisions, or reviewed corrections. See [[annotation-data-preparation-framework|Annotation and Data Preparation Framework]].

## 2. Recommended Model Stack

Use several narrow models rather than one universal model.

| Model | Primary job | Output | Why it matters |
|---|---|---|---|
| Atomizer / Router | split and classify source segments | `ThoughtAtom` JSON + routing decision | improves cluster purity and reduces Chroma noise |
| Entity Type Resolver | fix person/org/location/tool/project confusion | typed entity candidates + confidence | directly attacks the current NER quality problem |
| Entity Canonicalizer | aliases, merges, rejects, retypes | registry decisions | converts manual curation into repeatable behavior |
| Summary / Labeler | short cluster/entity/topic summaries | 1-3 sentence summaries + labels | improves report/UI quality without large runtime models |
| Vec2Text / Vector Narrator | describe embeddings, centroids, and directions | text hypothesis or direction description | makes vector-space meaning inspectable |

Priority order:

1. Entity Type Resolver.
2. Atomizer / Router.
3. Summary / Labeler.
4. Vec2Text / Vector Narrator.
5. Entity Canonicalizer once enough manual registry data exists.

This order gives the fastest quality gain because the current visible weakness is entity precision: organizations as locations, locations as organizations, and generic phrases treated as entities.

## 3. Training Data Strategy

### 3.1 Gold Data

Gold data comes from human-curated truth.

Sources:

- `data/curation/entity_registry.json`
- `Second Brain/Operations/Kanban/ThoughtMap Entity Curation.md`
- `Second Brain/Operations/Kanban/ThoughtMap Segment Curation.md`
- `Second Brain/Operations/Kanban/ThoughtMap Domain Curation.md`
- corrected entity note names and aliases
- manually accepted/rejected Kanban cards in `ThoughtMap Intake.md`

Gold examples should be small but trusted. They become the test set and high-weight training set.

Gold examples should be created through an annotation workflow, not inferred silently from generated output. The annotation workflow should preserve the original source text, the automatic proposal, optional preannotation, and the user's final decision.

### 3.2 Silver Data

Silver data comes from high-confidence automatic outputs.

Sources:

- existing `thought_atoms.json` and `routing_report.json`
- current NER candidates after registry filtering
- high-confidence entity matches from source paths, project folders, and known peer notes
- cluster summaries generated from representative atoms and then accepted by the user

Silver examples are useful for scale, but they must be separated from gold examples in evaluation.

External Gemini/OpenAI labels belong here by default. They can preannotate, explain, or suggest corrections, but they are not gold labels until the user accepts or edits them.

### 3.4 Annotation UI and Queue

Before training, build a small annotation interface over the current ThoughtMap UI.

The first version should focus on `entity_type_resolution` because it is the most visible quality issue and easiest to evaluate.

Required pieces:

- `/annotate/entities` route in the current web UI,
- generated `ThoughtMap Annotation Queue.md` Kanban board,
- local annotation store under `data/annotations/`,
- explicit task types with instructions and editable fields,
- optional local/Gemini/OpenAI preannotation,
- JSONL dataset export from accepted user labels.

The full plan is in [[annotation-data-preparation-framework|Annotation and Data Preparation Framework]].

### 3.3 Hard Negatives

Hard negatives are the most valuable data for entity quality.

Collect examples like:

- company classified as `location`,
- location classified as `organization`,
- project classified as generic `organization`,
- tool names classified as people,
- common phrases such as `acceptance criteria` treated as entities,
- Polish inflected names that should resolve to one canonical entity.

The Entity Type Resolver should be trained heavily on these mistakes.

## 4. Dataset Formats

### 4.1 Entity Type Resolver JSONL

Each example should include context, candidate span, source metadata, and the desired decision.

```json
{
  "task": "entity_type_resolution",
  "text": "Spotkanie z Konradem Bujakiem o Fenix i Roche.",
  "candidate": "Roche",
  "source_file": "Second Brain/Operations/Meetings/2026-04-22_fenix_konrad_bujak.md",
  "expected": {
    "type": "organization",
    "canonical_name": "Roche",
    "decision": "verify",
    "confidence": 0.95
  }
}
```

For a false positive:

```json
{
  "task": "entity_type_resolution",
  "text": "Acceptance criteria: pipeline should finish without errors.",
  "candidate": "Acceptance Criteria",
  "expected": {
    "type": "concept",
    "decision": "reject",
    "reason": "generic phrase, not a named entity"
  }
}
```

### 4.2 Atomizer / Router JSONL

```json
{
  "task": "thought_atom_routing",
  "segment": {
    "source": "jointhubs-review",
    "section": "Action Items",
    "text": "Pietro Vinci needs a reply. Also check AWS password reset and KSeF annex."
  },
  "expected": {
    "atoms": [
      {
        "text": "Pietro Vinci needs a reply.",
        "signal_type": "communication",
        "index_targets": ["communication", "activity", "entity"],
        "entities": [{"name": "Pietro Vinci", "type": "person"}]
      },
      {
        "text": "Check AWS password reset.",
        "signal_type": "task",
        "index_targets": ["activity"]
      },
      {
        "text": "Check KSeF annex.",
        "signal_type": "task",
        "index_targets": ["activity", "project"]
      }
    ]
  }
}
```

### 4.3 Summary / Labeler JSONL

```json
{
  "task": "cluster_summary",
  "cluster_label": "Fenix Context Engine",
  "representative_atoms": [
    "Fenix needs a context engine that preserves domain decisions.",
    "Konrad feedback suggests onboarding should expose assumptions and next actions."
  ],
  "expected": {
    "label": "Fenix Context Engine",
    "summary": "This cluster centers on improving Fenix through a context engine that captures assumptions, decisions, and onboarding feedback. The strongest signals come from Konrad's review and recurring implementation notes."
  }
}
```

### 4.4 Vec2Text JSONL

Vec2Text examples are model-specific and should only use embeddings generated by the exact production embedding model.

```json
{
  "embedding_model": "qwen3-embedding:8b",
  "embedding_dim": 4096,
  "embedding": [0.0123, -0.0456],
  "text": "Fenix needs a context engine that preserves domain decisions."
}
```

For centroid/direction narration, store both the vector operation and a target human description:

```json
{
  "task": "vector_direction_narration",
  "embedding_model": "qwen3-embedding:8b",
  "operation": "entity_centroid - global_centroid",
  "anchor": "Pietro Vinci",
  "nearest_examples": ["Pietro Vinci demo email", "Agent Marketingowy thread"],
  "expected_description": "This direction points toward business-development communication around Pietro Vinci, agent demos, and follow-up obligations."
}
```

## 5. Fine-Tuning Framework

Recommended initial stack:

| Layer | Choice | Why |
|---|---|---|
| SFT framework | `trl` or `Axolotl` | common, inspectable, works with LoRA/QLoRA |
| Fast local experiments | `Unsloth` | good for consumer GPUs and LoRA speed |
| Model family | small Qwen / Phi / Gemma instruct models | strong structured output at 1.5B-4B scale |
| Entity classifier baseline | encoder classifier, e.g. XLM-R / ModernBERT style | cheaper than decoder for type classification |
| Artifact tracking | local JSONL + metrics files | local-first, easy to diff |

Do not start with full fine-tuning of a large model. Start with LoRA or QLoRA adapters.

Candidate first models:

- `Qwen2.5-1.5B-Instruct` or similar for structured JSON tasks.
- `Qwen2.5-3B-Instruct` if 1.5B underfits.
- encoder classifier for entity type resolution if we want maximum speed.
- T5-small/base for Vec2Text experiments if using the architecture in [[vec2text-training-guide|Vec2Text training guide]].

## 6. Evaluation

### 6.1 Entity Metrics

Track entity quality by type and decision.

| Metric | Definition | Target for MVP |
|---|---|---|
| Type accuracy | correct `person/org/project/tool/location/concept` | >90% on curated eval |
| Reject precision | false positives correctly rejected | >90% |
| Alias resolution accuracy | inflected/variant names resolve correctly | >85% |
| Organization/location confusion | rate of org-location swaps | <5% |

### 6.2 Atom/Routing Metrics

| Metric | Definition | Target for MVP |
|---|---|---|
| Atom purity | one thought per atom | >85% manual score |
| Routing accuracy | correct index targets | >85% |
| Boilerplate exclusion | generated/low-value text excluded | >95% |
| Needs-review recall | uncertain cases routed to review | high recall over precision |

### 6.3 Summary Metrics

Use lightweight human scoring first.

Score 1-5 for:

- faithfulness to representative atoms,
- compactness,
- entity/type correctness,
- usefulness for navigation.

Avoid BLEU/ROUGE as primary metrics for summaries; they reward wording overlap more than usefulness.

### 6.4 Vec2Text Metrics

For reconstruction:

- embedding cosine similarity between original and reconstructed text,
- token F1,
- exact match only for very short snippets,
- privacy leakage risk score.

For vector narration:

- human usefulness score,
- agreement with nearest-neighbor evidence,
- stability across reruns.

## 7. Implementation Phases

### Phase A — Dataset Builder

Add the annotation/data-preparation foundation before creating training/eval datasets.

First deliverables:

- annotation task schema,
- `entity_type_resolution` task generator,
- `ThoughtMap Annotation Queue.md`,
- local annotation JSONL store,
- `/annotate/entities` MVP or equivalent simple review UI.

Then add scripts that create local training/eval datasets without training anything.

Suggested outputs:

```text
Second Brain/Projects/thoughtmap/data/training/entities/entity_type_resolver.train.jsonl
Second Brain/Projects/thoughtmap/data/training/entities/entity_type_resolver.eval.jsonl
Second Brain/Projects/thoughtmap/data/training/atoms/atom_router.train.jsonl
Second Brain/Projects/thoughtmap/data/training/summaries/cluster_summary.train.jsonl
Second Brain/Projects/thoughtmap/data/training/vec2text/qwen3_embedding_pairs.train.jsonl
```

Acceptance:

- no cloud calls by default; Gemini/OpenAI preannotation must be explicit opt-in and stored separately from user labels,
- deterministic splits by source/date,
- no generated ThoughtMap output used as gold truth,
- hard negatives explicitly tagged.
- gold labels trace back to explicit user annotation or durable registry decisions.

### Phase B — Baselines Before Training

Before fine-tuning, build baselines:

- rule + registry entity resolver,
- generic local LLM prompt for entity type resolution,
- nearest-neighbor + LLM vector narration,
- current summary generation.

This tells us whether fine-tuning is actually improving the system.

### Phase C — Entity Type Resolver MVP

Train the first small model on entity typing and rejection.

Why first:

- current failure is visible and concrete,
- data can be created from existing mistakes,
- evaluation is straightforward,
- runtime payoff is immediate.

Acceptance:

- beats generic prompt baseline on curated eval,
- reduces organization/location swaps,
- produces confidence and decision reason,
- never overrides manual registry decisions.

### Phase D — Atomizer / Router Fine-Tune

Train a structured-output model for ThoughtAtom splitting and routing.

Acceptance:

- outputs schema-valid JSON,
- preserves original text spans,
- improves manual atom purity score,
- reduces low-value records entering semantic Chroma.

### Phase E — Summary / Labeler Fine-Tune

Train or distill a short-output summarizer for clusters and entities.

Acceptance:

- summaries are shorter and more faithful than current generic model output,
- entity summaries preserve type and role,
- cluster labels become more navigable.

### Phase F — Vec2Text / Vector Narrator

Start with nearest-neighbor + LLM baseline, then train Vec2Text only if the baseline is not enough.

Acceptance:

- describes centroids and vector directions in useful language,
- does not get used as source truth,
- documents privacy implications clearly,
- works only against the exact active embedding model.

## 8. Runtime Integration

All fine-tuned models must remain optional.

Suggested config:

```env
THOUGHTMAP_MODEL_LAYER_ENABLED=false
THOUGHTMAP_ENTITY_RESOLVER_MODEL=local/entity-type-resolver-lora
THOUGHTMAP_ATOM_ROUTER_MODEL=local/atom-router-lora
THOUGHTMAP_SUMMARY_MODEL=local/cluster-summary-lora
THOUGHTMAP_VEC2TEXT_MODEL=local/qwen3-embedding-vec2text
```

Runtime rule:

1. Apply manual registry first.
2. Apply deterministic rules second.
3. Use fine-tuned model only for unresolved or uncertain cases.
4. If the model fails schema validation, route to curation instead of accepting output.

## 9. Privacy and Safety

Fine-tuning on a personal knowledge base creates a new private artifact: the model weights or LoRA adapter may memorize sensitive source text.

Rules:

- keep training data and adapters local by default,
- do not upload raw notes or adapters to public model hubs,
- store training outputs under `data/training/` or another gitignored runtime path,
- document which data sources were used in each model card,
- treat Vec2Text as a privacy-risk diagnostic as well as a useful interpretability tool.

## 10. Decision Points

Before training production models, decide:

1. Which embedding model is canonical for the next 3-6 months?
2. Should entity type resolution be a decoder fine-tune or an encoder classifier?
3. How much manually curated gold data is enough for the first evaluation set?
4. Which sources are allowed in training data?
5. Are LoRA adapters private runtime artifacts or commit-worthy project assets? Recommendation: private runtime artifacts.

## 11. Immediate Next Step

Build an annotation-data MVP for entity type resolution before training any model.

Minimum deliverable:

```text
annotation/generate.py
  -> reads entities.json, entity_registry.json, entity curation board, source snippets
  -> creates entity_type_resolution annotation tasks
  -> writes local annotation task JSONL
  -> renders ThoughtMap Annotation Queue.md

annotation/export.py
  -> reads accepted user annotations
  -> writes train/eval JSONL
  -> tags hard negatives
  -> prints baseline confusion counts by entity type
```

This directly targets the current quality issue and creates the first reusable training/evaluation foundation.

## Related

- [[../PRD|ThoughtMap v2 PRD]]
- [[annotation-data-preparation-framework|Annotation and Data Preparation Framework]]
- [[vec2text-training-guide|Vec2Text training guide]]
- [[junior-developer-implementation-guide|ThoughtMap v2 junior developer guide]]