# ThoughtMap Extraction Pipeline: Clusters, Entities, and Topics

> Detailed walkthrough of how ThoughtMap transforms raw chunks into structured clusters, enriched topics, and named entities through a multi-stage processing pipeline.

## Overview

The entire pipeline is orchestrated by [run.py](../run.py) in **9 sequential steps**. Steps 6–8 produce the three main output layers: **clusters** (base groupings), **topics** (enriched clusters with LLM summaries and hierarchy), and **entities** (named entities with summaries and areas of focus).

All three layers start from a shared foundation: `items` (chunk metadata + text) and `all_embeddings` (768-dimensional vectors) loaded from ChromaDB after deduplication.

```
Raw Chunks (ChromaDB)
        ↓
   [Step 6] Cluster
        ↓
   Basic Clusters (HDBSCAN + UMAP)
     ↙        ↓         ↘
 Clusters  Topics     Entities
 (.json)   (LLM)      (NER)
```

---

## Step 6: Clustering — UMAP + HDBSCAN

**File**: [core/cluster.py](../core/cluster.py)  
**Function**: `cluster_all(items, embeddings) → ThoughtMapResult`

### Why Two UMAP Reductions?

HDBSCAN fails in high dimensions (768d) because distances become uniform — this is the *curse of dimensionality*. Plus, you need a 2D projection for visualization. So ThoughtMap runs two separate UMAP passes:

1. **Intermediate (15d) for HDBSCAN** — `_reduce_for_clustering()`
   - Reduces 768d → ~15 dimensions
   - Metric: cosine
   - Preserves semantic structure for density estimation
   - Fed to HDBSCAN (`min_cluster_size ≈ N/15`, `min_samples` tuned from it)

2. **2D for Visualization** — `reduce_dimensions()`
   - Reduces 768d → 2D independently
   - Metric: cosine
   - Produces the scatter plot you see in the UI
   - Each point is plotted at the 2D centroid of its cluster

### Clustering Algorithm

```python
# 1. Reduce to intermediate dims (cosine metric)
embeddings_15d = _reduce_for_clustering(embeddings_768d)

# 2. HDBSCAN on the 15d space (euclidean after cosine-UMAP is meaningful)
clusterer = HDBSCAN(
    min_cluster_size = min(N/15, config.HDBSCAN_MIN_CLUSTER_SIZE),
    min_samples = min_cluster_size,
    metric="euclidean",
    cluster_selection_method="eom"
)
labels = clusterer.fit_predict(embeddings_15d)
# Returns: 0, 1, 2, ... or -1 (noise)

# 3. Compute centroids + representative texts per cluster
for cluster_id in unique(labels):
    indices = [i for i, l in enumerate(labels) if l == cluster_id]
    centroid_hd = mean(embeddings_768d[indices])
    # Find 5 nearest chunks to centroid
    nearest = argsort(distance(embeddings_768d[indices], centroid_hd))[:5]
    representative_texts = [items[i]["text"][:200] for i in nearest]
```

### Labeling Strategy

`_extract_topic_label(representative_texts)` generates labels without cross-cluster TF-IDF (that strategy was tested and intentionally rejected):

1. Tokenize representative texts (regex `[a-zA-Z...]{3,}` for 3+ char words)
2. Remove en/pl stopwords (expanded set: "the", "is", "w", "z", "na", "który", etc.)
3. Count term frequency
4. Take top 3 words
5. Capitalize and join: `"Fenix / File / Created"`

### Merging Small Clusters

`merge_similar_clusters()` uses union-find to consolidate clusters whose high-dimensional centroids are very close:

```python
# Cosine similarity on normalized centroid_hd vectors
sim_matrix = normalize(centroids) @ normalize(centroids).T

# Union-find: merge if sim >= CLUSTER_MERGE_THRESHOLD (default ~0.75)
for i < j:
    if sim_matrix[i,j] >= threshold:
        merge(i, j)
        relabel merged cluster
```

### Output

[thoughtmap-out/clusters.json](../../Operations/thoughtmap-out/clusters.json):
```json
[
  {
    "cluster_id": 0,
    "label": "Fenix / File / Created",
    "size": 263,
    "centroid_2d": [0.5, 0.3],
    "representative_texts": ["text1...", "text2...", ...],
    "member_indices": [0, 5, 12, 23, ...]
  },
  ...
]
```

---

## Step 7: Condensation — Topics + Super-Clusters + Edges

**File**: [analysis/condense.py](../analysis/condense.py)  
**Functions**: `condense(result) → condensed_dict`

This step enriches raw clusters with LLM summaries, builds a hierarchy (super-clusters), computes inter-cluster edges, and generates Obsidian topic notes.

### 7a. LLM Labeling per Cluster

`_summarize_cluster(cluster)` queries Ollama with a structured prompt:

```
You are analyzing a topic cluster from a personal knowledge base.
Below are representative text fragments.

Provide TWO things:
1. A SHORT topic label (2-5 words): "Travel Planning & Bookings", "AI Product Strategy"
2. A concise 2-3 sentence summary.

Format EXACTLY as:
LABEL: <your short label>
SUMMARY: <your summary>

Size: 263 thought fragments
Representative fragments:
<sample texts>
```

Ollama responds, and `_parse_label_summary()` extracts the label and summary. This replaces the generic word-frequency labels with human-readable ones like *"Travel Planning & Bookings"* instead of *"Travel / Planning / Booking"*.

### 7b. Inter-Cluster Edges

`_compute_cluster_edges(clusters)` finds which clusters are conceptually close:

```python
# Normalize cluster centroids_hd
normed_centroids = normalize(centroids)
sim_matrix = normed_centroids @ normed_centroids.T

# Keep edges where cosine sim >= CONDENSE_EDGE_THRESHOLD (~0.65)
edges = []
for i < j:
    if sim_matrix[i,j] >= threshold:
        edges.append({
            "from": cluster_i.id,
            "to": cluster_j.id,
            "similarity": sim_matrix[i,j]
        })
```

These edges are visualized as lines connecting nodes in the condensed visualization.

### 7c. Super-Clustering (Mega-Topics)

`_super_cluster(clusters)` groups clusters into ~10–15 mega-topics using greedy complete-linkage:

```python
# Threshold is edge_threshold + 0.12 (e.g., 0.77 if edges at 0.65)
super_threshold = min(CONDENSE_EDGE_THRESHOLD + 0.12, 0.88)

# For each unassigned cluster i:
#   Start group [i]
#   Add all unassigned j where min_similarity(j, all in group) >= super_threshold
#   (complete linkage: every pair must be similar)

# Merge tiny groups (size < MIN_SIZE) into nearest large neighbor
```

Each super-cluster gets a TP-IDF label from its member clusters' representative texts.

### 7d. Sub-Clusters (Levels 2 & 3)

For clusters with >50 members, `compute_sub_clusters()` applies UMAP + HDBSCAN *within* each cluster to find finer structure. This creates a hierarchy visible in the UI (`drillIntoCluster()` in condense.py).

### 7e. Topic Notes for Obsidian

For each cluster, generates `thoughtmap-out/topics/<slug>.md`:

```markdown
# Topic: AI Product Strategy

> Cluster #5 · 47 thought fragments

## Summary
LLM-generated summary paragraph.

## Related Topics
- [[TravelPlanning&Bookings]] (similarity: 0.82)
- [[HealthNutrition]] (similarity: 0.71)
```

Cross-cluster wikilinks are sorted by cosine similarity.

### 7f. Domain Indices

[analysis/index.py](../analysis/index.py) groups clusters by project/domain:

```python
DOMAIN_RULES = [
    ("Projects/fenix", "fenix", "Fenix"),
    ("Projects/neurohubs", "neurohubs", "Neurohubs"),
    ("Personal/Health", "health", "Health"),
    # etc.
]

# For each cluster, check if source_file matches any domain
# Group and generate thoughtmap-out/clusters/<domain>.md
```

Result: one rich `.md` per domain (e.g., `clusters/fenix.md`) that serves as a project-level thought map.

### Output

- [thoughtmap-out/condensed.json](../../Operations/thoughtmap-out/condensed.json) — topics + super-clusters + edges
- [thoughtmap-out/topics/](../../Operations/thoughtmap-out/topics) — per-topic `.md` notes
- [thoughtmap-out/clusters/](../../Operations/thoughtmap-out/clusters) — per-domain `.md` indices
- [thoughtmap-out/thoughtmap-condensed.html](../../Operations/thoughtmap-out/thoughtmap-condensed.html) — interactive drill-down visualization

---

## Step 8: Named Entity Extraction (NER)

**File**: [analysis/ner.py](../analysis/ner.py)  
**Function**: `extract_entities(result, items, embeddings) → list[Entity]`

Populates `thoughtmap-out/entities/` with people, organizations, projects, tools, and locations from the corpus, with summaries and area-of-focus scoring.

### Entity Discovery Pipeline

#### Phase 1: Regex Cache Lookup (Fast)

[data/entity_cache.json](../data/entity_cache.json) persists previously seen entities:

```json
{
  "marcin_lewandowski": {
    "name": "Marcin Lewandowski",
    "type": "person",
    "aliases": ["Marcin", "ML", "Lewandowski"],
    "first_seen": "2026-03-15"
  },
  ...
}
```

`build_regex_patterns(cache)` builds case-insensitive patterns and scans all chunks. Already-matched chunks are marked to skip NLP.

#### Phase 2: spaCy NER (New Candidates)

`spacy_extract(items, matched_indices)` runs `xx_ent_wiki_sm` (multilingual) on unmatched chunks:

```python
nlp = spacy.load("xx_ent_wiki_sm")
for doc in nlp.pipe(texts):
    for ent in doc.ents:
        yield Entity(name=ent.text, type=spacy_to_thoughtmap(ent.label_))
        # PERSON → "person", ORG → "organization", GPE/LOC → "location"
```

#### Phase 3: Heuristic Projects

`_extract_project_entities()` pulls project names from:
- Source file paths: `Projects/fenix` → "Fenix"
- Hashtags and markdown links
- Manual project directory names

#### Phase 4: Sanitization & Filtering

Several layers remove noise:

1. **Stopwords** (`_STOP_WORDS`): "api", "app", "github", "day", "note", "jointhubs", "thoughtmap", etc.
2. **Noisy tokens** (`_NOISY_ENTITY_TOKENS`): "action", "decision", "data", "file", "framework", etc.
3. **Person shape validation**: `_is_person_name_shape()` checks capitalization (reject all-lowercase unless known)
4. **Type-specific bans**: `_is_type_banned_phrase()` rejects false positives per type

```python
if entity_type == "person" and name.lower() == name:
    # All lowercase: likely "copyright holder", "author", not a person
    skip()
```

#### Phase 5: Deduplication

`deduplicate(candidates)` merges variants using Levenshtein distance on normalized names:

```python
# Normalize: lowercase, strip accents, remove extra whitespace
# If Levenshtein(norm_a, norm_b) < threshold:
#   Merge into one Entity with aliases
```

So `"Marcin"`, `"Marcinek"`, `"M. Lewandowski"` → single entity "Marcin Lewandowski" + aliases list.

#### Phase 6: Enrichment

`_enrich_entities(entities, result, items)` adds:

```python
entity.cluster_ids = [clusters where entity appears]
entity.source_files = [sources where entity appears]
entity.mention_count = total chunks containing entity
entity.first_seen = earliest date in those chunks
```

#### Phase 7: Filtering by Mention Count

```python
NER_MIN_MENTIONS = 3  # configurable
entities = [e for e in entities if e.mention_count >= NER_MIN_MENTIONS]
entities.sort(key=lambda e: (-e.mention_count, e.name.lower()))
if NER_MAX_ENTITIES > 0:
    entities = entities[:250]  # Default cap
```

#### Phase 8: LLM Validation

`_llm_validate_entities()` sends batches to Ollama:

```
Entity: "John Smith", Type: "person"
Contexts where it appears:
- "John Smith is a software engineer at X"
- "I met John Smith at the conference"

Question: Is this definitely a real person (not a product, code name, or false positive)?
Answer: Yes / No
```

Entities marked "No" are discarded. This catches odd ones like company names mistaken for people.

#### Phase 9: Summarization

- **First 50 entities** (via `NER_MAX_OLLAMA_SUMMARIES`): get real LLM summaries

```python
summary, boundaries = summarize_entity(entity, items)
```

Ollama generates a paragraph and identifies *area*: CENTER (core focus), EDGES (mentioned peripherally), or ISOLATED.

- **Remaining entities**: `_fallback_summary()` uses templates

```
"{name} is a {type} mentioned {mention_count} times across {cluster_count} topics. 
Sources: {source_files[:3]}."
```

#### Phase 10: Embedding-Space Area Context

Each entity's cluster membership and embedding distance to each cluster's centroid determine coverage and distinctiveness:

```python
entity_embedding = mean(embeddings[chunks_containing_entity])
for cluster_centroid:
    distance_to_centroid = cosine_distance(entity_embedding, centroid)
    if distance < 0.2:  # Very close
        entity.coverage += 1  # Entity is tightly focused here
    if distance < 0.5:
        entity.mention_count += 1  # Entity relevant here
```

### Output

- [thoughtmap-out/entities.json](../../Operations/thoughtmap-out/entities.json)

```json
{
  "Marcin Lewandowski": {
    "type": "person",
    "aliases": ["Marcin", "ML"],
    "summary": "Software engineer focused on backend architecture...",
    "mention_count": 47,
    "cluster_ids": [3, 7, 12],
    "source_files": ["daily/2026-04-10.md", "Projects/fenix/notes.md"],
    "first_seen": "2026-03-15",
    "area": "CENTER"
  },
  ...
}
```

- [thoughtmap-out/entities/_entity-index.md](../../Operations/thoughtmap-out/entities/_entity-index.md) — summary table sorted by mention count

- [thoughtmap-out/entities/{type}/<slug>.md](../../Operations/thoughtmap-out/entities) — detailed per-entity note with related clusters and topics

- `thoughtmap-out/entities/entity_cache.json` — updated with newly discovered entities for next run

---

## Shared Foundations

All three layers (clusters, topics, entities) rely on:

1. **ChromaDB vector store** ([core/embed.py](../core/embed.py))
   - Persistent storage of embeddings
   - Deduplication at load time (exact-match text)
   - Batched updates

2. **Configuration** ([config.py](../config.py))
   - Thresholds: `CLUSTER_MERGE_THRESHOLD`, `CONDENSE_EDGE_THRESHOLD`, `SUPER_CLUSTER_MIN_SIZE`, `NER_MIN_MENTIONS`, `NER_MAX_ENTITIES`
   - Model settings: `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `CONDENSE_MODEL`, `NER_SPACY_MODEL`
   - IO paths: `OUTPUT_DIR`, `DATA_DIR`

3. **Determinism**
   - UMAP: `random_state=42`
   - HDBSCAN: deterministic output for same input
   - Non-deterministic: Ollama (LLM summaries vary slightly)

---

## Data Persistence

### Run Artifacts (Gitignored)

- `thoughtmap-data/` — ChromaDB vector store, embeddings cache
- `data/entity_cache.json` — persisted entity names + aliases for next run
- `data/echo_catalog.json` — user-cataloged near-duplicate groups (observe/discard/neutral status)

### Output (Checked In)

- `Second Brain/Operations/thoughtmap-out/` — all generated reports, notes, visualizations (can be committed to repo)

---

## Performance Notes

- **Full run**: ~5–10 minutes on first start (includes Ollama model download ~500MB)
- **Subsequent runs**: ~2–3 minutes (embedding cache, entity cache, model in memory)
- **Scaling**: Safe up to ~50,000 chunks. Beyond that, full similarity matrix for Echoes (step 6.5) becomes OOM-risky — guarded at 12,000 items.

---

## References

- **UMAP**: LeCun et al., "Uniform Manifold Approximation and Projection"
- **HDBSCAN**: McInnes et al., "Density-based clustering based on hierarchical density estimates"
- **Spacy NER**: `xx_ent_wiki_sm` model from [spacy.io](https://spacy.io)
- **Ollama**: Local LLM inference framework
