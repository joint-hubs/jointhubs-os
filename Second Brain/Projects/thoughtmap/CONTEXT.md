---
type: project
status: active
tags: [type/project, project/thoughtmap, project/jointhubs-os]
created: 2026-04-13
updated: 2026-04-29
---

# ThoughtMap Context

## Past

**Origin**: The idea emerged from the need to explore personal thinking patterns over time. Daily notes in Obsidian and voice dictation via Wispr Flow produce a continuous stream of raw thought — but it's trapped in linear files with no way to see topic density, recurring themes, or connections between days. Graphify showed the value of graph-based knowledge exploration; ThoughtMap applies a similar philosophy to the temporal, personal layer — not entities-and-edges, but vectors-and-proximity.

**Key Decisions**:
- 2026-04-13 — Project initiated after brainstorming session. Core insight: Wispr Flow's SQLite database (`flow.sqlite`) stores every dictation with full metadata (text, timestamp, app context, duration, language). This eliminates the need for any Wispr API integration — we read directly from the local DB.
- 2026-04-13 — Decided on `nomic-embed-text v1.5` via Ollama as the embedding model. Rationale: fully local (no API costs), multilingual (critical for mixed en/pl usage), 768 dimensions with Matryoshka support (truncate to 256 for visualization), 8192 token context window. Alternatives considered: OpenAI text-embedding-3-small (API-dependent), all-MiniLM-L6-v2 (no Polish), mxbai-embed-large (heavier at 1024 dims).
- 2026-04-13 — Chose ChromaDB as vector store. Already used in the office_ai project (Asystent Urzędnika), file-based persistent storage, no server process required in simple mode.
- 2026-04-13 — Wispr Flow transcripts that match text in the Obsidian daily `## Logs` section are tagged as `intent: note` (confirmed intentional notes). Unmatched transcripts are classified by app context into categories (coding, browsing, communication, etc.). This gives two layers: deliberate thought capture vs. operational voice commands.
- 2026-04-13 — Output location: `Second Brain/Operations/thoughtmap-out/` following the graphify-out convention. Runtime data (vector DB, cache) in `thoughtmap-data/` at repo root, gitignored.
- 2026-04-13 — Chunking strategy: ~200 tokens, sentence-boundary-aware, 2-sentence overlap, semantic merge when cosine similarity > 0.85. Text cleanup includes broken word rejoining, sentence boundary extension, and markdown artifact stripping.
- 2026-04-13 — Moved to fully Dockerized architecture. Replaced CLI-only design with an HTTP server (`server.py`) that shows a loading page while the pipeline runs, then auto-redirects to the interactive visualization. Ollama runs as a companion container; model pull is handled automatically by the ThoughtMap app on first start.
- 2026-04-13 — Project code relocated from `thoughtmap/` (repo root) to `Second Brain/Projects/thoughtmap/`. The project is a first-class Second Brain project, not a standalone tool.
- 2026-04-15 — Refactored the codebase into explicit packages: `core/` for ingestion/embedding/clustering, `analysis/` for condensation/indexing/NER/reporting, and `web/` for the server and visualization layer. Rationale: keep the root package small, make the pipeline easier to extend, and create a clean place for new analysis stages.
- 2026-04-15 — Added multilingual named entity extraction and contact discovery. Rationale: clusters show topical structure, but people, organizations, projects, and tools need their own layer for navigation and future agent memory. The implementation combines cache-backed regex matching, spaCy NER, project heuristics, fuzzy deduplication, and Ollama summaries.
- 2026-04-15 — Updated repo-level documentation and agent surfaces to make the privacy model explicit: ThoughtMap runs locally by default, while GitHub Copilot remains a cloud service. Added path-scoped ThoughtMap instructions and a shared `jointhubs-os` deep-work agent.
- 2026-04-16 — Added date-range filtering to the condensed visualization and hardened the runtime around optional local inputs. Rationale: the graph needs temporal slicing to make daily and weekly shifts visible, and transient Wispr/Ollama failures should degrade gracefully instead of aborting the entire pipeline.
- 2026-04-17 — Added **Echoes**: cross-corpus aggregation of near-duplicate thoughts via full cosine-similarity scan on normalized embeddings + union-find grouping. Rationale: clusters surface topics, but inside them the same idea often repeats verbatim across weeks. Echoes make recurrence legible so I can catalog groups as `observe`, `discard`, or `neutral`. Base threshold `0.95`, minimum group size `3` at pipeline time; UI default filter is `≥5`. Stable group IDs are `sha1(sorted(chunk_ids))[:16]` so catalog state survives reruns. State lives in `data/echo_catalog.json`, output in `thoughtmap-out/echoes.json`. Safety: pipeline step is wrapped in try/except and skips full matmul above 12 000 items.
- 2026-04-24 — Added Kanban intake post-processing after report/index generation. Rationale: daily execution should not have to rediscover the same urgent work from reviews and communication trackers each morning. ThoughtMap now emits `thoughtmap-out/kanban_tasks.json` plus `Operations/Kanban/ThoughtMap Intake.md`, using recent reviews, `communication-map.md`, `linkedin-tracker.md`, `thread-state.json`, and resolved entities. Tavily MCP is treated as optional enrichment for research cards via `tavily_query`, not as a core pipeline dependency.
- 2026-04-24 — Made `ThoughtMap Intake.md` a curation surface instead of a write-only artifact. Rationale: if the user deletes a generated card or corrects a person name directly in Obsidian, the next rerun should respect that decision. ThoughtMap now harvests suppressions and title/entity overrides into `thoughtmap-out/kanban_curation.json`, syncs them before NER, reapplies them during kanban regeneration, and promotes matching rename overrides into the generated entity notes/index.
- 2026-04-28 — Reframed the next ThoughtMap milestone as semantic processing v2. Rationale: the current sentence/token chunker is not enough for mixed daily logs and journals; ThoughtMap needs a ThoughtAtom layer, structured LLM preprocessing, entity registry, manual curation as source of truth, and hot/cold storage controls before further scaling the semantic map.
- 2026-04-28 — Added a junior developer implementation guide for ThoughtMap v2. Rationale: implementation should be easy to hand off without relying on verbal context; the guide explains product intent, code structure, module boundaries, coding standards, verification, phased rollout, and when the developer must ask the maintainer before making architectural or data decisions.
- 2026-04-28 — Clarified Phase 1 defaults for the junior developer: prototype `semantic` routing uses confidence `>= 0.80` only as a dry-run proposal, embedding cleanup must preserve meaning, durable manual entity registry should live in local `data/curation/entity_registry.json`, and the first atomization sample should focus on daily/review/Wispr sources before adding project notes as a comparison batch.
- 2026-04-28 — Added a local model-optimization direction for ThoughtMap v2. Rationale: the repeated tasks in ThoughtMap do not require one large general model; entity typing, atom routing, short summarization, and Vec2Text-style vector narration can be handled by smaller local fine-tuned models once curated training data exists.
- 2026-04-28 — Added an annotation/data-preparation framework before model training. Rationale: generated ThoughtMap output is a candidate/proposal layer, not automatic gold truth; user labels, durable registry decisions, and reviewed corrections must become the source of truth for fine-tuning datasets.
- 2026-04-29 — Reset production ChromaDB after an accidental full-corpus ThoughtAtom write. Rationale: Chroma is a derived store and can be rebuilt from source notes; the previous store had 117,134 embeddings, including 106,649 `atom:` records that entered production before curation quality was approved. The old store was moved to `data/chroma.backup-20260429-202827`, and the active store was recreated empty.
- 2026-04-29 — Gated the ThoughtAtom production pipeline behind `THOUGHTMAP_ENABLE_ATOM_PIPELINE=false` and returned default production runs to stable v1 chunking. Rationale: ThoughtAtom remains a prototype/curation layer until manual review proves quality.
- 2026-04-29 — Added Ollama rebuild tuning: `OLLAMA_NUM_PARALLEL=2`, `OLLAMA_MAX_LOADED_MODELS=1`, `OLLAMA_FLASH_ATTENTION=1`, `OLLAMA_KEEP_ALIVE=30m`, `THOUGHTMAP_OLLAMA_EMBED_BATCH_SIZE=16`, and `THOUGHTMAP_OLLAMA_EMBED_CONCURRENCY=2`. Ollama embeddings are truncated/renormalized to `EMBEDDING_DIMENSIONS=1024` before Chroma storage to avoid another 4096-dimension store.

**Lessons**:
- The raw input text is in two places that partially overlap: Wispr Flow captures everything spoken (including to VS Code), while Obsidian daily logs capture only what was intentionally dictated into notes. The matching mechanism is essential to distinguish deliberate thought from operational commands.
- Embeddings cannot be "decoded" back to text — the transform is lossy. Cluster labeling uses centroid → nearest chunks → keyword extraction instead.
- The Ollama Docker image does not include `curl` or `wget` — use `ollama list` for healthchecks instead.
- Port 11434 conflicts with locally-installed Ollama — the Docker Compose omits host port mapping for the Ollama container (containers communicate internally via Docker network).
- Optional local sources need defensive handling. The Wispr SQLite can be malformed or mid-write, and Ollama model probes can time out even when the model is usable.
- ChromaDB should be treated as rebuildable derived state, not manual truth. Before deleting it, move `data/chroma` to a timestamped backup; source notes, curation registries, and generated reports are the durable layers.
- Ollama parallelism only helps if both sides are configured: server env (`OLLAMA_NUM_PARALLEL`) and client-side concurrent embedding requests (`THOUGHTMAP_OLLAMA_EMBED_CONCURRENCY`). Keep concurrency conservative on 12 GB VRAM unless monitoring shows spare memory.

---

## Current

**Status**: Active — rebuilding the production ChromaDB from source notes with v1 chunking, 1024-dimensional Ollama embeddings, and ThoughtAtom production disabled by default

**Current Snapshot**:
- Full pipeline expanded and reorganized: extract → chunk → embed → cluster → condense → NER → report/index → viz
- Docker Compose orchestrates everything: `docker compose up --build` → opens at `http://localhost:8585`
- Code is now organized into `core/`, `analysis/`, and `web/` packages with root-level compatibility exports
- Named entity outputs now target `thoughtmap-out/entities/` plus `entities.json` and `_entity-index.md`
- Root and project READMEs now explain the local-first ThoughtMap runtime separately from Copilot's cloud execution
- Repo automation layer now includes `.github/instructions/thoughtmap.instructions.md` and `.github/agents/jointhubs-os.agent.md`
- Post-refactor import smoke test passed and the Docker stack rebuilt successfully
- The live Docker run now completes extraction, embedding, clustering, entity extraction, and report generation after fixing two `ner.py` syntax regressions discovered only at runtime
- Direct post-cluster validation inside the container now reproduces entity extraction and report generation deterministically from `chunks.json` + `clusters.json`
- NER output is now bounded and operationally safe: total retained entities capped at 250, Ollama summaries capped at 50, remaining entities receive fallback summaries
- Entity/contact-discovery outputs are generated successfully: `entities.json`, per-entity notes, `_entity-index.md`, and entity sections inside `REPORT.md`
- Report quality is materially improved versus the first runs: obvious false positives like task phrases and markdown-link tails were filtered out of the main report tables
- The pipeline now also emits Kanban-friendly derived artifacts: machine-readable `kanban_tasks.json` in `thoughtmap-out/` and a markdown-backed Obsidian intake board at `Operations/Kanban/ThoughtMap Intake.md`
- Manual edits in `Operations/Kanban/ThoughtMap Intake.md` now feed back into the pipeline: deleted cards suppress the same tracked thread on future reruns, while renamed cards persist as title overrides, seed entity alias corrections via the NER cache, and can change future generated entity notes / `_entity-index.md` naming
- Remaining quality issue is precision in the long tail of entity extraction, especially some organization/location noise and a few residual person false positives in `_entity-index.md`; this is a quality-tuning problem, not a pipeline blocker
- Kanban intake quality is good enough to act as a pre-processed candidate layer, but not yet good enough to replace final daily triage; duplicate action-item phrasing and contact normalization still need tuning
- Condensed HTML now exposes time filters for `All Time`, `Today`, `Yesterday`, `This Week`, `This Month`, `This Year`, `Last 2 Years`, plus a custom date range. Cluster and super-cluster metadata now include date ranges so filtering works client-side.
- Runtime hardening is in place for unstable local inputs: Wispr extraction now uses a copied SQLite snapshot and degrades cleanly on DB errors, while Ollama embedding sanitizes inputs, retries transient failures, and steps down to shorter fallbacks instead of failing the whole run on one bad chunk.
- First run processed **340 chunks** from 4 sources:
  - 186 from Obsidian daily notes (Logs, Dziennik, ideation)
  - 77 from Wispr Flow dictation
  - 66 from Obsidian root topic notes
  - 11 from jointhubs-os AI reviews
- 2 topic clusters detected: "Fenix / File / Created" (263 chunks) and "Priority / Google / Obsidian" (77 chunks)
- 16 Wispr entries matched as intentional notes (`intent: note`)
- All code lives in `Second Brain/Projects/thoughtmap/`
- Output lands in `Second Brain/Operations/thoughtmap-out/`
- Current product direction is captured in `PRD.md`: add semantic ThoughtAtoms before embedding, use structured LLM outputs for preprocessing, route atoms into separate semantic/entity/activity/communication/project/archive indexes, and make manual Obsidian curation the durable source of truth for entities and segment decisions.
- Model optimization direction is captured in `docs/model-optimization-finetuning-plan.md`: first build entity type-resolution training data and baselines, then consider LoRA/QLoRA fine-tunes for entity resolution, atom routing, summarization, and later Vec2Text/vector narration.
- Annotation direction is captured in `docs/annotation-data-preparation-framework.md`: ThoughtMap should generate annotation tasks from uncertain candidates, expose a simple web/Kanban review interface, store user labels in `data/annotations/`, and compile train/eval JSONL only from accepted annotations or durable registry decisions.
- Current rebuild target after Chroma reset: about 9,009 v1 semantic records, not the previous 106k+ accidental atom records.
- Ollama container sees the NVIDIA GPU during rebuild; first observed GPU utilization was ~93% with ~5.6 GB VRAM used under concurrency 2.

**Files**:

| File | Purpose |
|------|---------|
| `config.py` | Central configuration, env var overrides for Docker |
| `core/extract.py` | Reads all 4 data sources, fuzzy-matches Wispr ↔ Obsidian |
| `core/chunk.py` | Smart chunking with sentence boundaries, overlap, cleanup |
| `core/embed.py` | Ollama API wrapper + ChromaDB storage |
| `core/cluster.py` | UMAP reduction + HDBSCAN clustering + centroid labeling |
| `analysis/condense.py` | Generates condensed cluster narratives |
| `analysis/echoes.py` | Near-duplicate thought groups + catalog persistence |
| `analysis/kanban.py` | Generates `kanban_tasks.json` + `ThoughtMap Intake.md` from reviews and communication trackers |
| `analysis/ner.py` | Extracts people, orgs, projects, tools, and locations |
| `analysis/report.py` | Generates REPORT.md with summaries and entity overview |
| `web/viz.py` | Generates interactive HTML (D3.js scatter plot) |
| `web/server.py` | HTTP server with loading page + pipeline orchestration |
| `run.py` | CLI pipeline runner |
| `Dockerfile` | Python 3.11 image with all dependencies |
| `docker-compose.yml` | Ollama + ThoughtMap containers |
| `.env` / `.env.example` | Local data paths for Docker volume mounts |
| `docs/junior-developer-implementation-guide.md` | Self-contained handoff for implementing ThoughtMap v2 safely and maintainably |
| `docs/model-optimization-finetuning-plan.md` | Roadmap for local fine-tuning, entity resolver training data, summary models, and Vec2Text/vector narration |
| `docs/annotation-data-preparation-framework.md` | Annotation UI, task schemas, preannotation policy, data store, and dataset export framework for fine-tuning |

**Architecture**:

```
Data Sources                    Pipeline                      Output
─────────────                   ────────                      ──────

Obsidian Daily Notes ─┐
  (## Logs section)   │
                      ├→ extract.py ──→ chunk.py ──→ embed.py ──→ cluster.py ──→ report.py + viz.py
Obsidian Root Notes ──┤     │                                        │
                      │     │ fuzzy match                            │
jointhubs-os Reviews ─┤     ▼                                        ▼
                      │  Wispr entries                          thoughtmap-out/
Wispr Flow SQLite ────┘  matched? ─→ intent: note              ├── REPORT.md
                         not matched? ─→ classify by app       ├── thoughtmap.html
                                         (coding/browsing/     ├── chunks.json
                                          communication/other) └── clusters.json
```

**Wispr Flow Matching & Classification**:

| Match Status | Tag | Description |
|---|---|---|
| Matched in Obsidian `## Logs` | `intent: note` | Confirmed intentional thought capture. User chose to save this in their daily log. |
| Unmatched — app: Code/Terminal | `category: coding` | Commands, instructions, and thoughts spoken while programming. |
| Unmatched — app: Chrome/Edge/Firefox | `category: browsing` | Thoughts during web browsing, research, reading. |
| Unmatched — app: Obsidian (not in Logs) | `category: note-taking` | Dictation in Obsidian that didn't land in the Logs section (maybe in other files). |
| Unmatched — app: Discord/Slack/WhatsApp | `category: communication` | Messages composed via voice. |
| Unmatched — other/unknown app | `category: general` | Everything else. |

**Matching Algorithm**:
1. For each day, extract all text under `## Logs` from the Obsidian daily note
2. For each Wispr `History` entry on the same day where `app = 'Obsidian'`:
   - Compare `formattedText` against Logs content using substring matching (the Wispr text is literally pasted into Obsidian, so it should appear verbatim or near-verbatim)
   - Use normalized Levenshtein distance < 0.15 as the match threshold (accounting for minor formatting differences)
3. Matched entries: `intent: note`, unmatched: classify by `app` field

**Tasks**:

Phase 1 — Core pipeline: ✅
- [x] `extract.py` — read all four data sources, extract text segments with timestamps
- [x] `chunk.py` — smart chunking with sentence boundaries, overlap, semantic merge, cleanup
- [x] `embed.py` — Ollama wrapper for nomic-embed-text, ChromaDB storage
- [x] `cluster.py` — UMAP reduction + HDBSCAN clustering + centroid labeling
- [x] `report.py` — generate REPORT.md with cluster summary, god nodes, density metrics
- [x] `viz.py` — generate interactive HTML with semantic + timeline views
- [x] `config.py` — paths, thresholds, model config (with env var overrides)
- [x] `run.py` + `server.py` — CLI and web server entry points
- [x] `Dockerfile` + `docker-compose.yml` — fully containerized deployment
- [x] `.gitignore` updated for `thoughtmap-data/`

Phase 2 — Wispr integration: ✅
- [x] Wispr Flow SQLite reader in `extract.py`
- [x] Fuzzy matching between Wispr entries and Obsidian Logs
- [x] App-based classification for unmatched entries
- [x] `intent` and `category` metadata in chunk pipeline

Phase 3 — Structure, privacy, and discovery: ✅
- [x] Reorganize code into `core/`, `analysis/`, and `web/`
- [x] Add privacy/local-first documentation to root and project READMEs
- [x] Add multilingual NER with cache-backed discovery and entity note generation
- [x] Add repo-scoped ThoughtMap instructions
- [x] Add shared `jointhubs-os` agent
- [x] Validate Docker runtime end to end, including NER outputs and generated entity reports

Phase 4 — Polish:
- [ ] Incremental processing (file hash cache, skip already-embedded chunks)
- [ ] Windows Task Scheduler / cron for nightly runs
- [ ] Graphify integration (graph of ThoughtMap project itself)
- [ ] Improve cluster labeling (TF-IDF instead of simple frequency)
- [ ] Add search endpoint to web server

**Tech Stack**:
- Python 3.11+
- Ollama + `nomic-embed-text:v1.5`
- ChromaDB (persistent file-based)
- UMAP (`umap-learn`), HDBSCAN (`hdbscan`)
- D3.js (visualization)
- Docker Compose (Ollama provisioning)

---

## Future

**Next Milestone**: ThoughtAtom prototype + annotation-data MVP — generate `thought_atoms.json` and `routing_report.json` from 10-20 recent daily/review/Wispr segments without changing Chroma, then build the first entity type-resolution annotation queue/store before exporting JSONL.

**End Goal**: A tool that runs nightly, silently processes the day's thoughts, and produces an always-current interactive map of thinking patterns. Over time it becomes a personal cognitive observatory — showing not just what you thought, but how your thinking *moved* across topics, projects, and concerns.

**Open Questions**:
- Should old chunks (pre-2026) ever be backfilled, or is the system strictly forward-looking?
- When clusters change significantly between runs (topic drift), should the report highlight what shifted?
- Should the report be linked from the daily note template (e.g., embed `![[thoughtmap-out/REPORT.md]]`)?
- What minimum chunk count per cluster is meaningful? (2 chunks = noise? 5+ = real topic?)
- Should the vis include a search/query mode (type a question → highlight nearest chunks)?
- Should entity registry live in project runtime data (`data/curation/`) or in generated/operational output (`thoughtmap-out/curation/`)?
- Should communication atoms be embedded in a separate collection or kept as JSON-only tracking data?
- Should the first fine-tuned entity resolver be a decoder LoRA model or a cheaper encoder classifier?
- Which training sources are allowed for private local adapters, and should adapters remain uncommitted runtime artifacts?
- Which annotation task types should be available in the first UI beyond entity type resolution?
- Should Gemini/OpenAI preannotation be enabled only per-task, per-batch, or per-task-type?
