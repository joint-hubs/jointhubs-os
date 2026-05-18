"""Clustering — UMAP dimensionality reduction + HDBSCAN topic detection."""

from __future__ import annotations

from dataclasses import dataclass

import hdbscan
import numpy as np
import umap

import thoughtmap.config as config


@dataclass
class ClusterInfo:
    """A topic cluster with label and member indices."""
    cluster_id: int
    label: str
    member_indices: list[int]
    centroid: list[float]       # 2D centroid
    centroid_hd: list[float]    # high-dimensional centroid
    size: int
    representative_texts: list[str]  # 3-5 nearest chunks to centroid


@dataclass
class ThoughtMapResult:
    """Full clustering result."""
    items: list[dict]                # chunk metadata + text
    embeddings_2d: list[list[float]] # UMAP 2D projections
    clusters: list[ClusterInfo]
    god_nodes: list[ClusterInfo]     # top clusters by size
    bridge_items: list[dict]         # items between clusters
    noise_count: int                 # unclustered items


def reduce_dimensions(embeddings: list[list[float]]) -> np.ndarray:
    """UMAP reduction to 2D for visualization."""
    if len(embeddings) < config.UMAP_N_NEIGHBORS:
        n_neighbors = max(2, len(embeddings) - 1)
    else:
        n_neighbors = config.UMAP_N_NEIGHBORS

    reducer = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=config.UMAP_MIN_DIST,
        n_components=config.UMAP_N_COMPONENTS,
        metric="cosine",
        random_state=42,
    )
    return reducer.fit_transform(np.array(embeddings))


def _reduce_for_clustering(embeddings: np.ndarray) -> np.ndarray:
    """UMAP reduction to intermediate dimensions for density-based clustering.

    High-dimensional embeddings (768-1024d) suffer from the curse of
    dimensionality — distances become uniform, making HDBSCAN ineffective.
    Reducing to ~15 dims preserves semantic structure while enabling
    meaningful density estimation.
    """
    n_components = min(config.UMAP_CLUSTER_COMPONENTS, len(embeddings) - 2)
    n_neighbors = min(config.UMAP_N_NEIGHBORS, len(embeddings) - 1)
    reducer = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=0.0,
        n_components=n_components,
        metric="cosine",
        random_state=42,
    )
    return reducer.fit_transform(embeddings)


def find_clusters(embeddings_hd: np.ndarray) -> np.ndarray:
    """HDBSCAN clustering on UMAP-reduced embeddings."""
    reduced = _reduce_for_clustering(embeddings_hd)

    min_cluster = min(config.HDBSCAN_MIN_CLUSTER_SIZE, max(2, len(embeddings_hd) // 15))
    min_samples = min(config.HDBSCAN_MIN_SAMPLES, min_cluster)

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster,
        min_samples=min_samples,
        metric="euclidean",
        cluster_selection_method="eom",
    )
    return clusterer.fit_predict(reduced)


def label_clusters(
    items: list[dict],
    embeddings_hd: np.ndarray,
    cluster_labels: np.ndarray,
) -> list[ClusterInfo]:
    """Label each cluster using the chunks nearest to its centroid (top words)."""
    unique_labels = set(cluster_labels)
    unique_labels.discard(-1)  # Remove noise label

    # First pass: gather representative texts per cluster
    cluster_rep_texts: dict[int, list[str]] = {}
    cluster_data: dict[int, tuple] = {}
    for cid in sorted(unique_labels):
        indices = [i for i, l in enumerate(cluster_labels) if l == cid]
        if not indices:
            continue
        member_embs = embeddings_hd[indices]
        centroid_hd = member_embs.mean(axis=0)
        dists = np.linalg.norm(member_embs - centroid_hd, axis=1)
        nearest_indices = np.argsort(dists)[:5]
        representative_texts = [items[indices[i]]["text"][:200] for i in nearest_indices]
        cluster_rep_texts[cid] = representative_texts
        cluster_data[cid] = (indices, centroid_hd, representative_texts)

    all_cluster_texts = list(cluster_rep_texts.values())

    # Second pass: create ClusterInfo with top-word labels
    clusters: list[ClusterInfo] = []
    for cid in sorted(cluster_data.keys()):
        indices, centroid_hd, representative_texts = cluster_data[cid]
        label = _extract_topic_label(representative_texts, all_cluster_texts=all_cluster_texts)
        clusters.append(ClusterInfo(
            cluster_id=int(cid),
            label=label,
            member_indices=indices,
            centroid=[0.0, 0.0],
            centroid_hd=centroid_hd.tolist(),
            size=len(indices),
            representative_texts=representative_texts,
        ))

    return clusters


def _extract_topic_label(texts: list[str], all_cluster_texts: list[list[str]] | None = None, max_words: int = 3) -> str:
    """Extract a topic label from most frequent words after stopword removal.

    The `all_cluster_texts` parameter is kept for backwards compatibility,
    but this strategy intentionally does not use cross-cluster TF-IDF.
    """
    from collections import Counter
    import re

    # Stopwords for en/pl — expanded set
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "must",
        "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
        "into", "that", "this", "it", "its", "not", "but", "and", "or", "if",
        "so", "no", "yes", "also", "just", "then", "than", "very", "too",
        "more", "most", "some", "any", "all", "each", "every", "both",
        "much", "many", "few", "other", "such", "only", "own", "same",
        "about", "up", "out", "over", "after", "before", "between",
        "through", "during", "without", "again", "there", "here", "when",
        "where", "why", "how", "what", "which", "who", "whom",
        "i", "you", "he", "she", "we", "they", "me", "him", "her", "us",
        "them", "my", "your", "his", "our", "their", "mine", "yours",
        "get", "got", "make", "made", "take", "took", "come", "came",
        "going", "went", "done", "doing", "want", "need", "think",
        "thought", "like", "know", "knew", "see", "saw", "new",
        "still", "well", "way", "use", "used", "work", "thing", "things",
        # Polish
        "w", "z", "na", "do", "od", "po", "za", "o", "i", "a", "ale",
        "że", "to", "się", "jest", "nie", "co", "jak", "ten", "ta", "te",
        "tym", "tego", "tej", "tych", "ile", "czy", "tak", "być", "był",
        "była", "było", "już", "jeszcze", "tylko", "może", "więc",
        "bardzo", "tutaj", "tam", "teraz", "wtedy", "kiedy", "gdzie",
        "który", "która", "które", "których", "którym",
        "ja", "ty", "on", "ona", "my", "wy", "oni", "mój", "twój",
    }

    def tokenize(text: str) -> list[str]:
        return [w for w in re.findall(r"\b[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]{3,}\b", text.lower())
                if w not in stopwords]

    # Term frequency in this cluster
    words = []
    for text in texts:
        words.extend(tokenize(text))

    if not words:
        return "Misc"

    tf = Counter(words)
    top = tf.most_common(max_words)

    result = [word.capitalize() for word, _ in top]
    return " / ".join(result) if result else "Misc"


def merge_similar_clusters(
    clusters: list[ClusterInfo],
    items: list[dict],
    threshold: float | None = None,
) -> list[ClusterInfo]:
    """Merge clusters whose high-dimensional centroids are very similar.

    Uses cosine similarity between centroid_hd vectors. When two clusters
    exceed the threshold, the smaller one is absorbed into the larger one
    and the merged cluster gets relabeled.
    """
    if threshold is None:
        threshold = config.CLUSTER_MERGE_THRESHOLD

    if len(clusters) < 2:
        return clusters

    # Build cosine similarity matrix between centroids
    centroids = np.array([c.centroid_hd for c in clusters])
    norms = np.linalg.norm(centroids, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1e-10, norms)
    normed = centroids / norms
    sim_matrix = normed @ normed.T

    # Union-Find for merging
    parent = list(range(len(clusters)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            # Larger cluster absorbs smaller
            if clusters[ra].size >= clusters[rb].size:
                parent[rb] = ra
            else:
                parent[ra] = rb

    # Find pairs to merge
    for i in range(len(clusters)):
        for j in range(i + 1, len(clusters)):
            if sim_matrix[i, j] >= threshold:
                union(i, j)

    # Group by root
    groups: dict[int, list[int]] = {}
    for i in range(len(clusters)):
        root = find(i)
        groups.setdefault(root, []).append(i)

    # Build merged clusters — collect all rep texts for TF-IDF relabeling
    group_data: list[tuple[list[int], list[str], np.ndarray]] = []
    all_rep_texts: list[list[str]] = []

    for root, member_idxs in groups.items():
        combined_indices: list[int] = []
        combined_rep: list[str] = []
        weighted_centroid = np.zeros_like(centroids[0])

        for m in member_idxs:
            combined_indices.extend(clusters[m].member_indices)
            combined_rep.extend(clusters[m].representative_texts)
            weighted_centroid += np.array(clusters[m].centroid_hd) * clusters[m].size

        weighted_centroid /= max(len(combined_indices), 1)
        combined_rep = combined_rep[:5]
        group_data.append((combined_indices, combined_rep, weighted_centroid))
        all_rep_texts.append(combined_rep)

    merged: list[ClusterInfo] = []
    for idx, (indices, rep_texts, centroid_hd) in enumerate(group_data):
        label = _extract_topic_label(rep_texts, all_cluster_texts=all_rep_texts)
        merged.append(ClusterInfo(
            cluster_id=idx,
            label=label,
            member_indices=indices,
            centroid=[0.0, 0.0],
            centroid_hd=centroid_hd.tolist(),
            size=len(indices),
            representative_texts=rep_texts,
        ))

    # Second pass: merge clusters that ended up with identical labels
    label_groups: dict[str, list[int]] = {}
    for i, c in enumerate(merged):
        label_groups.setdefault(c.label, []).append(i)

    final: list[ClusterInfo] = []
    used: set[int] = set()
    for label, idxs in label_groups.items():
        if idxs[0] in used:
            continue
        if len(idxs) == 1:
            final.append(merged[idxs[0]])
            used.add(idxs[0])
        else:
            # Merge all clusters with the same label
            combined_indices: list[int] = []
            combined_rep: list[str] = []
            weighted_centroid = np.zeros_like(centroids[0])
            for i in idxs:
                combined_indices.extend(merged[i].member_indices)
                combined_rep.extend(merged[i].representative_texts)
                weighted_centroid += np.array(merged[i].centroid_hd) * merged[i].size
                used.add(i)
            weighted_centroid /= max(len(combined_indices), 1)
            final.append(ClusterInfo(
                cluster_id=len(final),
                label=label,
                member_indices=combined_indices,
                centroid=[0.0, 0.0],
                centroid_hd=weighted_centroid.tolist(),
                size=len(combined_indices),
                representative_texts=combined_rep[:5],
            ))

    # Re-number cluster IDs
    for i, c in enumerate(final):
        c.cluster_id = i

    return final


def find_bridge_items(
    items: list[dict],
    cluster_labels: np.ndarray,
    embeddings_2d: np.ndarray,
    clusters: list[ClusterInfo],
) -> list[dict]:
    """Find items that sit between two clusters (potential bridges)."""
    if len(clusters) < 2:
        return []

    bridges = []
    noise_mask = cluster_labels == -1
    for i in range(len(items)):
        if not noise_mask[i]:
            continue
        # Find two nearest cluster centroids
        point = embeddings_2d[i]
        dists = []
        for c in clusters:
            centroid_2d = np.array(c.centroid)
            dists.append((np.linalg.norm(point - centroid_2d), c))
        dists.sort(key=lambda x: x[0])
        if len(dists) >= 2:
            d1, c1 = dists[0]
            d2, c2 = dists[1]
            # Bridge: close to two clusters, not just one
            if d2 < d1 * 2.0:
                bridges.append({
                    **items[i],
                    "bridge_between": [c1.label, c2.label],
                    "position_2d": point.tolist(),
                })

    return bridges[:20]  # Cap at 20 most interesting


def cluster_all(
    items: list[dict],
    embeddings: list[list[float]],
) -> ThoughtMapResult:
    """Full clustering pipeline."""
    embeddings_array = np.array(embeddings)

    # 1. UMAP reduction for visualization
    embeddings_2d = reduce_dimensions(embeddings)

    # 2. HDBSCAN clustering on high-dimensional embeddings (not 2D)
    cluster_labels = find_clusters(embeddings_array)

    # 3. Label clusters
    clusters = label_clusters(items, embeddings_array, cluster_labels)

    # 4. Merge clusters with very similar centroids
    pre_merge = len(clusters)
    clusters = merge_similar_clusters(clusters, items)

    # 5. Set 2D centroids
    for c in clusters:
        pts = embeddings_2d[c.member_indices]
        c.centroid = pts.mean(axis=0).tolist()

    # 6. Sort by size (god nodes = biggest)
    clusters.sort(key=lambda c: c.size, reverse=True)
    god_nodes = clusters[:5]

    # 7. Find bridges
    bridges = find_bridge_items(items, cluster_labels, embeddings_2d, clusters)

    # 8. Count noise
    noise_count = int((cluster_labels == -1).sum())

    return ThoughtMapResult(
        items=items,
        embeddings_2d=embeddings_2d.tolist(),
        clusters=clusters,
        god_nodes=god_nodes,
        bridge_items=bridges,
        noise_count=noise_count,
    )


def compute_sub_clusters(
    member_indices: list[int],
    all_embeddings_hd: list[list[float]],
    items: list[dict],
    min_total: int = 15,
    min_sub_size: int = 3,
) -> list[dict]:
    """Compute sub-clusters within a single cluster.

    Sub-clusters are computed once on ALL thoughts (no time-filtering) so
    the structure is stable. Time-filtering only affects the visible count.

    Returns:
        List of {sub_id, label, member_offsets, size, density} or []
        if the cluster is too small or produces no meaningful sub-structure.
        member_offsets = local positions (0-based) within member_indices list.
    """
    if len(member_indices) < min_total:
        return []

    embs = np.array([all_embeddings_hd[i] for i in member_indices])
    n = len(embs)

    # UMAP to intermediate dims
    n_components = min(10, n - 2)
    n_neighbors = min(10, n - 1)
    try:
        reducer = umap.UMAP(
            n_neighbors=n_neighbors,
            min_dist=0.0,
            n_components=n_components,
            metric="cosine",
            random_state=42,
        )
        reduced = reducer.fit_transform(embs)
    except Exception:
        return []

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_sub_size,
        min_samples=2,
        metric="euclidean",
        cluster_selection_method="eom",
    )
    labels = clusterer.fit_predict(reduced)

    unique_labels = set(labels)
    unique_labels.discard(-1)
    if len(unique_labels) < 2:
        return []  # No meaningful sub-structure

    # Gather texts per sub-cluster for top-word labeling
    sub_texts: dict[int, list[str]] = {}
    sub_data: dict[int, tuple] = {}

    for sid in sorted(unique_labels):
        local_idxs = [j for j, lv in enumerate(labels) if lv == sid]
        global_idxs = [member_indices[j] for j in local_idxs]
        sub_embs = embs[local_idxs]
        centroid = sub_embs.mean(axis=0)
        dists = np.linalg.norm(sub_embs - centroid, axis=1)
        nearest = np.argsort(dists)[:5]
        rep_texts = [items[global_idxs[j]].get("text", "")[:200] for j in nearest]
        sub_texts[sid] = rep_texts
        mean_dist = float(dists.mean())
        sub_data[sid] = (local_idxs, mean_dist, rep_texts)

    all_texts_list = list(sub_texts.values())
    result = []
    new_id = 0
    for sid in sorted(sub_data.keys()):
        local_idxs, mean_dist, rep_texts = sub_data[sid]
        label = _extract_topic_label(rep_texts, all_cluster_texts=all_texts_list, max_words=3)
        n_sub = len(local_idxs)
        density = round(n_sub / (1.0 + mean_dist), 2)
        result.append({
            "sub_id": new_id,
            "label": label,
            "member_offsets": local_idxs,
            "size": n_sub,
            "density": density,
        })
        new_id += 1

    return result
