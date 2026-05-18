"""Standalone re-clustering script — loads embeddings from ChromaDB, re-clusters, writes output."""

import json
import time
import numpy as np

import thoughtmap.config as config
from thoughtmap.analysis.index import generate_cluster_indices
from thoughtmap.analysis.report import save_report
from thoughtmap.core.cluster import cluster_all
from thoughtmap.core.embed import load_all_embeddings
from thoughtmap.web.viz import generate_viz

print("=" * 60)
print("ThoughtMap — Re-clustering (no vectorization)")
print("=" * 60)

# Load existing embeddings
print("Loading embeddings from ChromaDB...")
items, all_embeddings = load_all_embeddings()
print(f"  Loaded {len(items)} chunks, embedding dim = {len(all_embeddings[0])}")

print(f"\nClustering params:")
print(f"  UMAP_N_NEIGHBORS = {config.UMAP_N_NEIGHBORS}")
print(f"  UMAP_CLUSTER_COMPONENTS = {config.UMAP_CLUSTER_COMPONENTS}")
print(f"  HDBSCAN_MIN_CLUSTER_SIZE = {config.HDBSCAN_MIN_CLUSTER_SIZE}")
print(f"  HDBSCAN_MIN_SAMPLES = {config.HDBSCAN_MIN_SAMPLES}")
print(f"  CLUSTER_MERGE_THRESHOLD = {config.CLUSTER_MERGE_THRESHOLD}")

# Cluster
print(f"\nClustering {len(items)} chunks (UMAP + HDBSCAN)...")
t0 = time.time()
result = cluster_all(items, all_embeddings)
elapsed = time.time() - t0
print(f"  Found {len(result.clusters)} clusters, {result.noise_count} unclustered ({elapsed:.1f}s)")

# God nodes
print("\n  God Nodes (dominant topics):")
for i, god in enumerate(result.god_nodes[:10], 1):
    print(f"    {i}. {god.label} ({god.size} chunks)")

# Save outputs
report_path = save_report(result)
print(f"\n  Report: {report_path}")

viz_path = generate_viz(result)
print(f"  Visualization: {viz_path}")

# Cluster index notes
index_dir = generate_cluster_indices(result, np.array(all_embeddings))
idx_count = len(list(index_dir.glob("*.md")))
print(f"  Cluster indices: {idx_count} files in {index_dir}")

# Save JSON artifacts
config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

chunks_json = list(result.items)
(config.OUTPUT_DIR / "chunks.json").write_text(
    json.dumps(chunks_json, indent=2, default=str), encoding="utf-8"
)

clusters_json = [
    {
        "cluster_id": c.cluster_id,
        "label": c.label,
        "size": c.size,
        "representative_texts": c.representative_texts,
    }
    for c in result.clusters
]
(config.OUTPUT_DIR / "clusters.json").write_text(
    json.dumps(clusters_json, indent=2, default=str), encoding="utf-8"
)

print(f"\n  Saved chunks.json ({len(chunks_json)} items)")
print(f"  Saved clusters.json ({len(clusters_json)} clusters)")
print("\nDone!")
