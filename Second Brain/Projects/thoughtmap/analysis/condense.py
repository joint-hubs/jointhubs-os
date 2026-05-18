"""Condense ThoughtMap clusters → LLM summaries, super-clusters, Obsidian topic notes, condensed viz.

Pipeline step added after clustering:
  1. Summarize each cluster with Ollama (gemma4:e2b)
  2. Compute inter-cluster edges (cosine similarity on HD centroids)
  3. Super-cluster: HDBSCAN on cluster centroids → ~10-15 mega-topics
  4. Generate Obsidian topic notes with wikilinks
  5. Generate condensed HTML visualization (cluster-level nodes)
"""

from __future__ import annotations

import json
import re
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Callable

import numpy as np
import requests

import thoughtmap.config as config
from thoughtmap.core.cluster import ClusterInfo, ThoughtMapResult, compute_sub_clusters


# ─── LLM summarization ───

def _parse_label_summary(text: str, fallback_label: str) -> tuple[str, str]:
    """Parse LLM response containing LABEL: and SUMMARY: into (label, summary)."""
    label = fallback_label
    summary = text

    if "LABEL:" in text and "SUMMARY:" in text:
        try:
            label_part, summary_part = text.split("SUMMARY:", 1)
            label = label_part.split("LABEL:", 1)[1].strip().rstrip(".")
            summary = summary_part.strip()
            # Clean up label: remove quotes, limit length
            label = label.strip('"\'')
            if len(label) > 60:
                label = label[:60].rsplit(" ", 1)[0]
            if not label:
                label = fallback_label
        except (IndexError, ValueError):
            pass

    return label, summary


def _summarize_cluster(cluster: ClusterInfo, items: list[dict]) -> tuple[str, str]:
    """Generate a label and summary for a cluster using Ollama.

    Returns (label, summary) tuple.
    """
    # Gather representative content: centroid-nearest texts + source diversity
    sample_texts = []
    for text in cluster.representative_texts[:5]:
        sample_texts.append(text[:300])

    # Add a few more diverse samples if cluster is large
    if cluster.size > 50:
        step = max(1, len(cluster.member_indices) // 5)
        for idx in cluster.member_indices[::step][:3]:
            txt = items[idx].get("text", "")[:200]
            if txt and txt not in sample_texts:
                sample_texts.append(txt)

    content_block = "\n---\n".join(sample_texts)

    prompt = (
        "You are analyzing a topic cluster from a personal knowledge base.\n"
        "Below are representative text fragments from this cluster.\n\n"
        "Provide TWO things:\n"
        "1. A SHORT topic label (2-5 words) — a descriptive title, like a book chapter name.\n"
        "   Good examples: 'Travel Planning & Bookings', 'Health & Nutrition', 'AI Product Strategy'\n"
        "   Bad examples: 'Sri & Lanka', 'Pln & Kurs', 'Copyright & Event'\n"
        "2. A concise 2-3 sentence summary.\n\n"
        "Format your response EXACTLY as:\n"
        "LABEL: <your short label>\n"
        "SUMMARY: <your summary>\n\n"
        "Write in the same language as the majority of fragments.\n"
        "Do NOT start the summary with 'This cluster...' — just state the theme directly.\n\n"
        f"Size: {cluster.size} thought fragments\n\n"
        f"Representative fragments:\n{content_block}"
    )

    try:
        resp = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": config.CONDENSE_MODEL,
                "prompt": prompt,
                "stream": False,
                "think": False,
                "options": {"temperature": 0.3, "num_predict": 250},
            },
            timeout=120,
        )
        resp.raise_for_status()
        text = resp.json().get("response", "").strip()
        return _parse_label_summary(text, cluster.label)
    except Exception as e:
        return cluster.label, f"(Summary generation failed: {e})"


def _summarize_super_cluster(
    super_label: str,
    member_clusters: list[ClusterInfo],
    summaries: dict[int, str],
) -> tuple[str, str]:
    """Generate a label and summary for a super-cluster.

    Returns (label, summary) tuple.
    """
    parts = []
    for c in member_clusters[:6]:
        parts.append(f"- {c.label} ({c.size} thoughts): {summaries.get(c.cluster_id, '')[:150]}")
    cluster_list = "\n".join(parts)

    prompt = (
        "You are analyzing a mega-topic that groups several related topic clusters "
        "from a personal knowledge base.\n"
        "Below are the sub-topics with their summaries.\n\n"
        "Provide TWO things:\n"
        "1. A SHORT mega-topic label (2-5 words) — a broad, descriptive title.\n"
        "   Good examples: 'Personal Finance & Investments', 'Software Architecture', 'Travel & Experiences'\n"
        "   Bad examples: 'Konrad & Bujak', 'Copyright & Event', 'Ideas & Today'\n"
        "2. A concise 2-3 sentence overview.\n\n"
        "Format your response EXACTLY as:\n"
        "LABEL: <your short label>\n"
        "SUMMARY: <your summary>\n\n"
        "Write in the same language as the content.\n\n"
        f"Sub-topics:\n{cluster_list}"
    )

    try:
        resp = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": config.CONDENSE_MODEL,
                "prompt": prompt,
                "stream": False,
                "think": False,
                "options": {"temperature": 0.3, "num_predict": 250},
            },
            timeout=120,
        )
        resp.raise_for_status()
        text = resp.json().get("response", "").strip()
        return _parse_label_summary(text, super_label)
    except Exception as e:
        return super_label, f"(Summary generation failed: {e})"


# ─── Inter-cluster edges ───

def _compute_cluster_edges(
    clusters: list[ClusterInfo],
    threshold: float | None = None,
) -> list[dict]:
    """Compute edges between clusters based on centroid cosine similarity."""
    if threshold is None:
        threshold = config.CONDENSE_EDGE_THRESHOLD

    if len(clusters) < 2:
        return []

    centroids = np.array([c.centroid_hd for c in clusters])
    norms = np.linalg.norm(centroids, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1e-10, norms)
    normed = centroids / norms
    sim_matrix = normed @ normed.T

    edges = []
    for i in range(len(clusters)):
        for j in range(i + 1, len(clusters)):
            sim = float(sim_matrix[i, j])
            if sim >= threshold:
                edges.append({
                    "from": clusters[i].cluster_id,
                    "to": clusters[j].cluster_id,
                    "similarity": round(sim, 4),
                })

    return edges


# ─── Super-clustering ───

def _super_cluster(
    clusters: list[ClusterInfo],
) -> list[dict]:
    """Group clusters into super-clusters using hierarchical cosine similarity.

    Returns list of super-cluster dicts with label, member cluster IDs, and centroid.
    """
    if len(clusters) < config.SUPER_CLUSTER_MIN_SIZE * 2:
        # Not enough clusters to form meaningful super-groups
        return [{
            "super_id": 0,
            "label": "All Topics",
            "member_ids": [c.cluster_id for c in clusters],
            "centroid_hd": np.mean([c.centroid_hd for c in clusters], axis=0).tolist(),
        }]

    centroids = np.array([c.centroid_hd for c in clusters])

    # Use agglomerative-style grouping: cosine similarity matrix → threshold cut
    norms = np.linalg.norm(centroids, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1e-10, norms)
    normed = centroids / norms
    sim_matrix = normed @ normed.T

    # Use a higher threshold than edge threshold to form tighter groups
    super_threshold = min(config.CONDENSE_EDGE_THRESHOLD + 0.12, 0.88)

    # Simple greedy clustering: assign each cluster to its most similar unassigned group
    assigned = [-1] * len(clusters)
    super_id = 0

    for i in range(len(clusters)):
        if assigned[i] >= 0:
            continue
        # Start new super-cluster with this cluster
        group = [i]
        assigned[i] = super_id
        # Pull in all unassigned clusters above threshold
        for j in range(i + 1, len(clusters)):
            if assigned[j] >= 0:
                continue
            # Check similarity to ALL current group members (complete linkage)
            min_sim = min(sim_matrix[j, g] for g in group)
            if min_sim >= super_threshold:
                group.append(j)
                assigned[j] = super_id
        super_id += 1

    # Build super-cluster objects
    groups: dict[int, list[int]] = defaultdict(list)
    for i, sid in enumerate(assigned):
        groups[sid].append(i)

    # Merge tiny super-clusters (size < min_size) into nearest neighbor
    super_centroids: dict[int, np.ndarray] = {}
    for sid, members in groups.items():
        member_centroids = centroids[members]
        weights = np.array([clusters[m].size for m in members], dtype=float)
        super_centroids[sid] = np.average(member_centroids, axis=0, weights=weights)

    final_groups: dict[int, list[int]] = {}
    for sid, members in groups.items():
        if len(members) >= config.SUPER_CLUSTER_MIN_SIZE:
            final_groups[sid] = members
        else:
            # Find nearest large super-cluster
            best_sid = None
            best_sim = -1
            sc = super_centroids[sid]
            sc_norm = sc / max(np.linalg.norm(sc), 1e-10)
            for other_sid, other_members in groups.items():
                if other_sid == sid or len(other_members) < config.SUPER_CLUSTER_MIN_SIZE:
                    continue
                oc = super_centroids[other_sid]
                oc_norm = oc / max(np.linalg.norm(oc), 1e-10)
                sim = float(sc_norm @ oc_norm)
                if sim > best_sim:
                    best_sim = sim
                    best_sid = other_sid
            if best_sid is not None:
                final_groups.setdefault(best_sid, list(groups[best_sid]))
                final_groups[best_sid].extend(members)
            else:
                final_groups[sid] = members

    # Build result with TF-IDF labels for super-clusters
    result = []
    all_super_texts: list[list[str]] = []
    super_data: list[tuple] = []

    for sid, member_indices in final_groups.items():
        rep_texts = []
        for mi in member_indices:
            rep_texts.extend(clusters[mi].representative_texts[:2])
        all_super_texts.append(rep_texts[:8])
        weighted_centroid = np.zeros_like(centroids[0])
        total_size = 0
        for mi in member_indices:
            weighted_centroid += np.array(clusters[mi].centroid_hd) * clusters[mi].size
            total_size += clusters[mi].size
        weighted_centroid /= max(total_size, 1)
        super_data.append((sid, member_indices, rep_texts[:8], weighted_centroid, total_size))

    for idx, (sid, member_indices, rep_texts, centroid, total_size) in enumerate(super_data):
        label = _super_cluster_label(rep_texts, all_super_texts)
        result.append({
            "super_id": idx,
            "label": label,
            "member_ids": [clusters[mi].cluster_id for mi in member_indices],
            "centroid_hd": centroid.tolist(),
            "total_size": total_size,
        })

    return result


def _super_cluster_label(
    texts: list[str],
    all_texts: list[list[str]] | None = None,
) -> str:
    """TF-IDF label for a super-cluster (broader scope → 2 words)."""
    from collections import Counter

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

    words = []
    for text in texts:
        words.extend(tokenize(text))
    if not words:
        return "Misc"

    tf = Counter(words)

    if all_texts and len(all_texts) > 1:
        n_docs = len(all_texts)
        doc_freq: Counter = Counter()
        for doc_texts in all_texts:
            doc_words = set()
            for t in doc_texts:
                doc_words.update(tokenize(t))
            for w in doc_words:
                doc_freq[w] += 1

        scored = {}
        for word, count in tf.items():
            idf = math.log(n_docs / max(doc_freq.get(word, 1), 1))
            scored[word] = count * (1 + idf)
        top = sorted(scored.items(), key=lambda x: x[1], reverse=True)
    else:
        top = tf.most_common(4)

    result = [word.capitalize() for word, _ in top[:2]]
    return " & ".join(result) if result else "Misc"


# ─── Obsidian topic notes ───

def _slugify(label: str) -> str:
    """Convert a cluster label to a filename-safe slug."""
    slug = label.lower()
    slug = re.sub(r"[/&]", "-", slug)
    slug = re.sub(r"[^a-z0-9ąćęłńóśźż\-]", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:60]


def _generate_topic_note(
    cluster: ClusterInfo,
    summary: str,
    related: list[tuple[ClusterInfo, float]],
    super_cluster: dict | None,
    items: list[dict],
) -> str:
    """Generate an Obsidian topic note for one cluster."""
    slug = _slugify(cluster.label)
    timestamps = []
    source_files: dict[str, int] = defaultdict(int)
    for idx in cluster.member_indices:
        ts = items[idx].get("timestamp", "")
        if ts and len(ts) >= 10:
            timestamps.append(ts[:10])
        src = items[idx].get("source_file", "")
        if src:
            source_files[src] += 1
    timestamps.sort()

    period = ""
    if timestamps:
        period = f"{timestamps[0]} — {timestamps[-1]}"

    lines: list[str] = []

    # Frontmatter
    lines.append("---")
    lines.append(f"type: thoughtmap-topic")
    lines.append(f"cluster_id: {cluster.cluster_id}")
    lines.append(f"size: {cluster.size}")
    if super_cluster:
        lines.append(f"super_cluster: {super_cluster['label']}")
    lines.append(f"generated: true")
    lines.append(f"tags: [type/thoughtmap-topic, thoughtmap]")
    lines.append("---")
    lines.append("")

    # Title
    lines.append(f"# {cluster.label}")
    lines.append("")
    lines.append(f"> **{cluster.size}** thoughts · {period}")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(summary)
    lines.append("")

    # Super-cluster
    if super_cluster:
        sc_slug = _slugify(super_cluster["label"])
        lines.append(f"**Mega-topic**: [[{sc_slug}|{super_cluster['label']}]]")
        lines.append("")

    # Related topics
    if related:
        lines.append("## Related Topics")
        lines.append("")
        for rel_cluster, sim in related[:6]:
            rel_slug = _slugify(rel_cluster.label)
            lines.append(f"- [[{rel_slug}|{rel_cluster.label}]] (similarity: {sim:.2f})")
        lines.append("")

    # Representative fragments
    lines.append("## Representative Fragments")
    lines.append("")
    for text in cluster.representative_texts[:5]:
        clean = text.replace("\n", " ").strip()
        if len(clean) > 250:
            clean = clean[:250].rsplit(" ", 1)[0] + "..."
        lines.append(f"> {clean}")
        lines.append("")

    # Source notes
    if source_files:
        top_sources = sorted(source_files.items(), key=lambda x: -x[1])[:8]
        lines.append("## Source Notes")
        lines.append("")
        for src, count in top_sources:
            if src.startswith("wispr:"):
                lines.append(f"- `{src}` ({count})")
            else:
                stem = Path(src).stem
                lines.append(f"- [[{stem}]] ({count})")
        lines.append("")

    return "\n".join(lines)


def _generate_super_topic_note(
    super_cluster: dict,
    summary: str,
    member_clusters: list[ClusterInfo],
    cluster_summaries: dict[int, str],
) -> str:
    """Generate an Obsidian note for a super-cluster (mega-topic)."""
    total_size = sum(c.size for c in member_clusters)

    lines: list[str] = []

    lines.append("---")
    lines.append("type: thoughtmap-super-topic")
    lines.append(f"super_id: {super_cluster['super_id']}")
    lines.append(f"clusters: {len(member_clusters)}")
    lines.append(f"size: {total_size}")
    lines.append("generated: true")
    lines.append("tags: [type/thoughtmap-super-topic, thoughtmap]")
    lines.append("---")
    lines.append("")

    lines.append(f"# {super_cluster['label']}")
    lines.append("")
    lines.append(f"> **{len(member_clusters)}** sub-topics · **{total_size}** thoughts")
    lines.append("")

    lines.append("## Overview")
    lines.append("")
    lines.append(summary)
    lines.append("")

    lines.append("## Sub-topics")
    lines.append("")
    for c in sorted(member_clusters, key=lambda c: c.size, reverse=True):
        slug = _slugify(c.label)
        csummary = cluster_summaries.get(c.cluster_id, "")
        short = csummary[:120] + "..." if len(csummary) > 120 else csummary
        lines.append(f"### [[{slug}|{c.label}]] ({c.size})")
        lines.append("")
        if short:
            lines.append(f"> {short}")
            lines.append("")

    return "\n".join(lines)


def _generate_topics_index(
    super_clusters: list[dict],
    super_summaries: dict[int, str],
    clusters: list[ClusterInfo],
    cluster_summaries: dict[int, str],
) -> str:
    """Generate _index.md for the topics directory."""
    total_thoughts = sum(c.size for c in clusters)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines: list[str] = []
    lines.append("---")
    lines.append("type: thoughtmap-topics-index")
    lines.append("generated: true")
    lines.append("tags: [type/thoughtmap-topics-index, thoughtmap]")
    lines.append("---")
    lines.append("")
    lines.append("# ThoughtMap Topics")
    lines.append("")
    lines.append(
        f"> **{len(clusters)}** topics → **{len(super_clusters)}** mega-topics"
        f" · **{total_thoughts}** thoughts"
    )
    lines.append(f"> Generated: {now}")
    lines.append("")

    for sc in sorted(super_clusters, key=lambda s: s.get("total_size", 0), reverse=True):
        sc_slug = _slugify(sc["label"])
        sc_summary = super_summaries.get(sc["super_id"], "")
        short = sc_summary[:150] + "..." if len(sc_summary) > 150 else sc_summary
        member_count = len(sc["member_ids"])
        total = sc.get("total_size", 0)

        lines.append(f"## [[{sc_slug}|{sc['label']}]]")
        lines.append(f"> {member_count} sub-topics · {total} thoughts")
        lines.append("")
        if short:
            lines.append(short)
            lines.append("")

        # List member clusters
        member_clusters = [c for c in clusters if c.cluster_id in sc["member_ids"]]
        for c in sorted(member_clusters, key=lambda c: c.size, reverse=True):
            slug = _slugify(c.label)
            lines.append(f"- [[{slug}|{c.label}]] ({c.size})")
        lines.append("")

    return "\n".join(lines)


# ─── Condensed HTML visualization ───

_CONDENSED_PALETTE = [
    "#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F",
    "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC",
    "#86BCB6", "#D37295", "#FABFD2", "#B6992D", "#499894",
]

_CONDENSED_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ThoughtMap</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a14; color: #e0e0e0; overflow: hidden; height: 100vh; display: flex; flex-direction: column; }
  #topbar { display: flex; align-items: center; gap: 12px; padding: 10px 16px; background: #12121f; border-bottom: 1px solid #2a2a4e; flex-shrink: 0; z-index: 10; position: relative; }
  #breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 14px; flex: 1; min-width: 0; }
  #breadcrumb .crumb { cursor: pointer; color: #7a7aaf; transition: color 0.15s; }
  #breadcrumb .crumb:hover { color: #aaaadf; }
  #breadcrumb .sep { color: #3a3a5e; }
  #breadcrumb .current { color: #e0e0e0; font-weight: 600; cursor: default; }
  #topbar-actions { display: flex; align-items: center; gap: 8px; margin-left: auto; flex-wrap: wrap; justify-content: flex-end; }
  #surface-nav { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  #search-wrap { width: 240px; }
  #search { width: 100%; padding: 6px 10px; background: #1a1a2e; border: 1px solid #3a3a5e; border-radius: 6px; color: #e0e0e0; font-size: 13px; outline: none; }
  #search:focus { border-color: #4E79A7; }
  #main { display: flex; flex: 1; overflow: hidden; position: relative; }
  #graph { flex: 1; background: #0a0a14; position: relative; }
  #sidebar { width: 340px; border-left: 1px solid #2a2a4e; display: flex; flex-direction: column; overflow: hidden; flex-shrink: 0; }
  #info-panel { padding: 14px; border-bottom: 1px solid #2a2a4e; max-height: 50%; overflow-y: auto; }
  #info-panel h3 { font-size: 13px; color: #aaa; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
  #info-content { font-size: 13px; line-height: 1.5; }
  #info-content .empty { color: #555; font-style: italic; }
  #info-content .field { margin-bottom: 6px; }
  #info-content .summary { color: #aaa; font-size: 12px; margin: 8px 0; padding: 8px; background: #12121f; border-radius: 6px; border-left: 3px solid #4E79A7; }
  #info-content .related-item { display: inline-block; background: #2a2a4e; border-radius: 4px; padding: 2px 8px; margin: 2px; font-size: 12px; cursor: pointer; }
  #info-content .related-item:hover { background: #3a3a5e; }
  #info-content .rep-text { margin: 4px 0; padding: 6px 8px; background: #12121f; border-radius: 4px; font-size: 12px; color: #999; }
  .mega-badge { display: inline-block; background: #2a2a4e; border-radius: 4px; padding: 1px 8px; font-size: 11px; margin-left: 6px; }
  #legend-wrap { flex: 1; overflow-y: auto; padding: 12px; }
  #legend-wrap h3 { font-size: 13px; color: #aaa; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.05em; }
  .legend-item { display: flex; align-items: center; gap: 8px; padding: 5px 6px; cursor: pointer; border-radius: 4px; font-size: 12px; }
  .legend-item:hover { background: #2a2a4e; }
  .legend-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
  .legend-dot.mega { border-radius: 3px; width: 14px; height: 14px; }
  .legend-label { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .legend-count { color: #666; font-size: 11px; }
  #stats { padding: 10px 14px; border-top: 1px solid #2a2a4e; font-size: 11px; color: #555; }
  .drill-hint { font-size: 11px; color: #555; margin-top: 4px; }
  #loading-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(10,10,20,0.85); display: none; align-items: center; justify-content: center; z-index: 100; }
  #loading-overlay .spinner { width: 36px; height: 36px; border: 3px solid #30363d; border-top-color: #58a6ff; border-radius: 50%; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .entity-hl { background: rgba(255, 200, 50, 0.25); color: #ffd866; border-radius: 2px; padding: 0 2px; cursor: pointer; border-bottom: 1px dashed #ffd866; }
  .entity-hl:hover { background: rgba(255, 200, 50, 0.45); }
  .entity-hl.person { background: rgba(56, 166, 56, 0.25); color: #6fcf6f; border-color: #6fcf6f; }
  .entity-hl.organization { background: rgba(31, 111, 235, 0.25); color: #6fadff; border-color: #6fadff; }
  .entity-hl.project { background: rgba(137, 87, 229, 0.25); color: #b89eff; border-color: #b89eff; }
  .entity-hl.tool { background: rgba(210, 153, 34, 0.25); color: #e6c44d; border-color: #e6c44d; }
  .entity-hl.location { background: rgba(228, 87, 87, 0.25); color: #f28585; border-color: #f28585; }
  #entity-detail { display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #1a1a2e; border: 1px solid #3a3a5e; border-radius: 10px; padding: 20px 24px; max-width: 440px; width: 90vw; max-height: 70vh; overflow-y: auto; z-index: 1000; box-shadow: 0 8px 32px rgba(0,0,0,0.6); }
  #entity-detail h2 { font-size: 16px; margin-bottom: 4px; }
  #entity-detail .etype { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; }
  #entity-detail .esummary { font-size: 13px; color: #ccc; line-height: 1.6; margin-bottom: 12px; }
  #entity-detail .efield { font-size: 12px; margin-bottom: 6px; color: #aaa; }
  #entity-detail .efield b { color: #e0e0e0; }
  #entity-detail .eclose { position: absolute; top: 12px; right: 14px; background: none; border: none; color: #666; font-size: 18px; cursor: pointer; }
  #entity-detail .eclose:hover { color: #fff; }
  #entity-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); z-index: 999; }
  /* Time filter */
  #time-filter { position: relative; }
  #time-trigger { display: inline-flex; align-items: center; height: 32px; padding: 0 12px; background: #171727; border: 1px solid #303653; border-radius: 999px; color: #9aa3c7; cursor: pointer; font-size: 12px; transition: all 0.15s; }
  #time-trigger:hover,
  #time-trigger[aria-expanded="true"] { border-color: #4E79A7; color: #e0e6ff; background: #1b1c2d; }
  #time-trigger.filtered { border-color: #4E79A7; color: #fff; background: #213552; }
  #time-popover { display: none; position: absolute; top: calc(100% + 8px); right: 0; width: 320px; max-width: calc(100vw - 32px); padding: 12px; background: #141425; border: 1px solid #303653; border-radius: 12px; box-shadow: 0 16px 40px rgba(0,0,0,0.45); z-index: 30; }
  #time-popover.open { display: block; }
  #time-popover .tl { display: block; color: #7a7aaf; font-size: 11px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 10px; }
  .time-presets { display: flex; flex-wrap: wrap; gap: 6px; }
  .tbtn { padding: 5px 10px; background: #1a1a2e; border: 1px solid #3a3a5e; border-radius: 999px; color: #aaa; cursor: pointer; font-size: 12px; transition: all 0.15s; }
  .tbtn:hover { border-color: #4E79A7; color: #ddd; }
  .tbtn.active { background: #4E79A7; border-color: #4E79A7; color: #fff; }
  .custom-label { margin-top: 10px; color: #666f92; font-size: 11px; }
  #custom-range { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 6px; }
  #custom-range input[type=date] { padding: 6px 8px; background: #1a1a2e; border: 1px solid #3a3a5e; border-radius: 6px; color: #e0e0e0; font-size: 11px; }
  #custom-range input[type=date]:focus { border-color: #4E79A7; outline: none; }
  #custom-range.active input[type=date] { border-color: #4E79A7; }
  #time-info { display: block; color: #666f92; font-size: 11px; margin-top: 10px; min-height: 14px; }
  @media (max-width: 900px) {
    #topbar { flex-wrap: wrap; }
    #breadcrumb { width: 100%; }
    #topbar-actions { width: 100%; }
    #search-wrap { flex: 1; }
    #time-popover { left: 0; right: auto; }
  }
  #note-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1001; }
  #note-modal { display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #1a1a2e; border: 1px solid #3a3a5e; border-radius: 10px; padding: 24px; width: 440px; max-width: 90vw; z-index: 1002; box-shadow: 0 8px 32px rgba(0,0,0,0.6); }
  #note-modal h2 { font-size: 16px; margin-bottom: 16px; }
  #note-modal .nclose { position: absolute; top: 12px; right: 14px; background: none; border: none; color: #666; font-size: 18px; cursor: pointer; }
  #note-modal .nclose:hover { color: #fff; }
  #note-modal label { display: block; font-size: 12px; color: #888; margin-bottom: 4px; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
  #note-modal input, #note-modal textarea, #note-modal select { width: 100%; background: #0f0f1a; border: 1px solid #3a3a5e; color: #e0e0e0; padding: 8px 10px; border-radius: 6px; font-size: 13px; font-family: inherit; margin-bottom: 12px; outline: none; }
  #note-modal input:focus, #note-modal textarea:focus, #note-modal select:focus { border-color: #4E79A7; }
  #note-modal textarea { height: 120px; resize: vertical; }
  #note-modal .nbtn { background: #238636; border: none; color: #fff; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 13px; }
  #note-modal .nbtn:hover { background: #2ea043; }
  #note-modal .nbtn:disabled { opacity: 0.5; cursor: not-allowed; }
  #note-modal .nfeedback { font-size: 12px; margin-top: 8px; min-height: 18px; }
  #note-modal .nfeedback.ok { color: #3fb950; }
  #note-modal .nfeedback.err { color: #f85149; }
  .add-note-btn { background: #238636; border: none; color: #fff; padding: 5px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; margin-top: 8px; }
  .add-note-btn:hover { background: #2ea043; }
  #chat-panel { position: absolute; top: 0; left: 0; bottom: 0; width: 420px; background: #161b22; border-right: 1px solid #2a2a4e; display: none; flex-direction: column; z-index: 20; box-shadow: 4px 0 16px rgba(0,0,0,0.4); }
  #chat-panel.open { display: flex; }
  #chat-panel .chat-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px 6px; }
  #chat-panel .chat-header h3 { font-size: 13px; color: #aaa; text-transform: uppercase; letter-spacing: 0.05em; margin: 0; }
  #chat-panel .chat-close { background: none; border: none; color: #888; font-size: 20px; cursor: pointer; padding: 0 4px; line-height: 1; }
  #chat-panel .chat-close:hover { color: #e0e0e0; }
  #chat-bar { display: flex; gap: 6px; padding: 0 14px 8px; }
  #chat-bar input { flex: 1; background: #0f0f1a; border: 1px solid #3a3a5e; color: #e0e0e0; padding: 6px 10px; border-radius: 6px; font-size: 12px; font-family: inherit; outline: none; }
  #chat-bar input:focus { border-color: #4E79A7; }
  #chat-bar button { background: #4E79A7; border: none; color: #fff; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; white-space: nowrap; }
  #chat-bar button:hover { background: #5a8ab8; }
  #chat-bar button:disabled { opacity: 0.5; cursor: not-allowed; }
  .chat-mode-btns { display: flex; gap: 4px; padding: 0 14px 6px; }
  .chat-mode-btns button { background: #1a1a2e; border: 1px solid #3a3a5e; color: #aaa; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 11px; }
  .chat-mode-btns button.active { background: #4E79A7; border-color: #4E79A7; color: #fff; }
  #chat-results { flex: 1; overflow-y: auto; padding: 0 14px 10px; font-size: 12px; line-height: 1.5; }
  .chat-result { background: #12121f; border-radius: 6px; padding: 8px 10px; margin-bottom: 6px; border-left: 3px solid #4E79A7; word-break: break-word; overflow-wrap: break-word; }
  .chat-result .cr-meta { color: #7a7aaf; font-size: 11px; margin-bottom: 4px; word-break: break-all; }
  .chat-result .cr-score { float: right; color: #e5a00d; font-size: 11px; }
  .chat-result .cr-text { color: #ccc; white-space: pre-wrap; word-break: break-word; }
  .chat-scope { color: #888; font-size: 11px; padding: 0 14px 4px; }
  .chat-empty { color: #555; font-style: italic; padding: 8px 0; }

  .surface-trigger { background: #1a1a2e; color: #d7d7f0; border: 1px solid #3a3a5e; border-radius: 999px; padding: 6px 12px; font-size: 12px; cursor: pointer; transition: border-color 0.15s, color 0.15s, background 0.15s; }
  .surface-trigger:hover { border-color: #6a6aaf; color: #fff; }
  .surface-trigger.active { background: #315a8b; border-color: #4E79A7; color: #fff; }
  #graph.doc-surface { padding: 22px 24px 28px; overflow-y: auto; }
  .doc-shell { max-width: 1120px; margin: 0 auto; }
  .doc-intro { color: #a8afca; font-size: 14px; line-height: 1.65; max-width: 72ch; margin-bottom: 18px; }
  .doc-section-label { color: #7a7aaf; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; margin: 18px 0 10px; }
  .doc-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
  .doc-grid.doc-grid-compact { grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
  .doc-card { background: #12121f; border: 1px solid #252541; border-radius: 12px; padding: 14px 15px; cursor: pointer; transition: border-color 0.15s, transform 0.15s, background 0.15s; }
  .doc-card:hover { border-color: #4E79A7; transform: translateY(-1px); background: #151528; }
  .doc-kicker { color: #7a7aaf; font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }
  .doc-title { font-size: 15px; color: #f0f2ff; margin-bottom: 6px; }
  .doc-meta { color: #8d95b8; font-size: 12px; margin-bottom: 8px; line-height: 1.5; }
  .doc-summary { color: #c9cee4; font-size: 13px; line-height: 1.6; }
  .doc-chip-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
  .doc-chip { display: inline-flex; align-items: center; gap: 4px; background: #1b1b2f; border: 1px solid #2d2d4a; border-radius: 999px; padding: 3px 8px; color: #c6ccef; font-size: 11px; }
  .doc-empty { color: #666f92; font-size: 13px; font-style: italic; padding: 18px 0; }
  .doc-columns { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(0, 0.9fr); gap: 18px; align-items: start; }
  .tree-section { background: #10101d; border: 1px solid #252541; border-radius: 12px; padding: 12px 14px; }
  .tree-branch { border-bottom: 1px solid #1e2036; padding: 8px 0; }
  .tree-branch:last-child { border-bottom: 0; }
  .tree-branch summary { list-style: none; cursor: pointer; display: flex; align-items: baseline; gap: 8px; color: #eef1ff; font-size: 14px; }
  .tree-branch summary::-webkit-details-marker { display: none; }
  .tree-branch summary .count { color: #7a7aaf; font-size: 11px; }
  .tree-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin: 8px 0 0 18px; padding: 8px 10px; border-radius: 8px; background: #141425; cursor: pointer; }
  .tree-row:hover { background: #1a1a2e; }
  .tree-row .label { color: #e0e3f4; font-size: 13px; }
  .tree-row .meta { color: #7f87ab; font-size: 11px; }
  .triple-group { margin-bottom: 16px; }
  .triple-list { display: flex; flex-direction: column; gap: 8px; }
  .triple-row { width: 100%; text-align: left; background: #12121f; border: 1px solid #252541; border-radius: 10px; padding: 12px 14px; cursor: pointer; color: #d8ddf0; }
  .triple-row:hover { border-color: #4E79A7; background: #16162a; }
  .triple-main { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; font-size: 13px; line-height: 1.55; }
  .triple-predicate { color: #8fc3ff; font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; }
  .triple-meta { color: #70789d; font-size: 11px; margin-top: 6px; }
  @media (max-width: 1100px) {
    .doc-columns { grid-template-columns: 1fr; }
  }
  #echoes-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.55); z-index: 90; }
  #echoes-overlay.open { display: block; }
  #echoes-panel { display: none; position: fixed; top: 0; right: 0; height: 100vh; width: 560px; max-width: 95vw; background: #0d0d18; border-left: 1px solid #2a2a4e; z-index: 100; box-shadow: -6px 0 24px rgba(0,0,0,0.5); flex-direction: column; }
  #echoes-panel.open { display: flex; }
  #echoes-header { padding: 14px 16px 8px; border-bottom: 1px solid #2a2a4e; display: flex; align-items: center; gap: 10px; }
  #echoes-header h2 { margin: 0; font-size: 15px; color: #e0e0e0; text-transform: uppercase; letter-spacing: 0.05em; }
  #echoes-header .echo-meta { color: #7a7aaf; font-size: 11px; margin-left: auto; }
  #echoes-header .eclose { background: transparent; color: #aaa; border: 0; font-size: 22px; cursor: pointer; line-height: 1; }
  #echoes-controls { padding: 10px 16px; border-bottom: 1px solid #2a2a4e; display: grid; grid-template-columns: auto auto auto 1fr; gap: 8px 12px; align-items: center; font-size: 12px; color: #aaa; }
  #echoes-controls input[type=number] { width: 60px; background: #12121f; color: #e0e0e0; border: 1px solid #2a2a4e; border-radius: 4px; padding: 4px 6px; font-size: 12px; }
  #echoes-controls .seg { display: inline-flex; border: 1px solid #2a2a4e; border-radius: 6px; overflow: hidden; }
  #echoes-controls .seg button { background: #12121f; color: #aaa; border: 0; padding: 4px 8px; font-size: 11px; cursor: pointer; }
  #echoes-controls .seg button.active { background: #4E79A7; color: #fff; }
  #echoes-list { flex: 1; overflow-y: auto; padding: 8px 12px 20px; }
  .echo-card { background: #12121f; border: 1px solid #2a2a4e; border-left: 3px solid #4a4a6e; border-radius: 6px; padding: 10px 12px; margin-bottom: 10px; }
  .echo-card.observe { border-left-color: #2aa36b; }
  .echo-card.discard { border-left-color: #a13d3d; opacity: 0.65; }
  .echo-card .echo-head { display: flex; gap: 8px; align-items: baseline; flex-wrap: wrap; }
  .echo-card .echo-size { color: #e5a00d; font-weight: bold; }
  .echo-card .echo-sim { color: #7a7aaf; font-size: 11px; }
  .echo-card .echo-dates { color: #666; font-size: 11px; margin-left: auto; }
  .echo-card .echo-rep { color: #ddd; font-size: 13px; margin-top: 6px; line-height: 1.45; word-break: break-word; }
  .echo-card .echo-frags { margin-top: 6px; display: none; }
  .echo-card.expanded .echo-frags { display: block; }
  .echo-card .echo-frag { color: #aaa; font-size: 11px; padding: 4px 8px; border-left: 2px solid #2a2a4e; margin: 4px 0; white-space: pre-wrap; word-break: break-word; }
  .echo-card .echo-frag .fm { color: #666; font-size: 10px; }
  .echo-card .echo-actions { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; }
  .echo-card .echo-actions button { background: #1a1a2e; color: #bbb; border: 1px solid #2a2a4e; border-radius: 4px; padding: 4px 10px; font-size: 11px; cursor: pointer; }
  .echo-card .echo-actions button:hover { border-color: #6a6aaf; color: #fff; }
  .echo-card .echo-actions button.active { background: #4E79A7; border-color: #4E79A7; color: #fff; }
  .echo-card .echo-actions button.active.observe { background: #2aa36b; border-color: #2aa36b; }
  .echo-card .echo-actions button.active.discard { background: #a13d3d; border-color: #a13d3d; }
  .echo-card .echo-expand { margin-left: auto; background: transparent; color: #7a7aaf; border: 0; cursor: pointer; font-size: 11px; }
  .echo-card textarea { width: 100%; margin-top: 6px; min-height: 40px; background: #0d0d18; color: #ddd; border: 1px solid #2a2a4e; border-radius: 4px; padding: 6px 8px; font-size: 12px; font-family: inherit; resize: vertical; }
  #echoes-empty { color: #666; text-align: center; padding: 24px 12px; font-style: italic; font-size: 12px; }
</style>
</head>
<body>
<div id="topbar">
  <div id="breadcrumb">
    <span class="current" id="bc-root">ThoughtMap</span>
  </div>
  <div id="topbar-actions">
    <div id="surface-nav">
      <button id="map-trigger" class="surface-trigger" type="button" onclick="navigateToSurface('map')">Map</button>
      <button id="entities-trigger" class="surface-trigger" type="button" onclick="navigateToSurface('entities')" title="Combined entities, topics, and mega-topics graph">Entities</button>
      <button id="glossary-trigger" class="surface-trigger" type="button" onclick="navigateToSurface('glossary')">Glossary</button>
      <button id="taxonomy-trigger" class="surface-trigger" type="button" onclick="navigateToSurface('taxonomy')">Taxonomy</button>
      <button id="echoes-trigger" class="surface-trigger" type="button" onclick="navigateToSurface('echoes')" title="Near-duplicate thought groups">Echoes</button>
      <button id="query-trigger" class="surface-trigger" type="button" onclick="toggleChatPanel()" title="Open context search panel">Query</button>
    </div>
    <div id="search-wrap">
      <input id="search" type="text" placeholder="Search..." autocomplete="off">
    </div>
    <div id="time-filter">
      <button id="time-trigger" type="button" onclick="toggleTimePopover(event)" aria-expanded="false">
        <span class="tf-label" id="time-trigger-label">Time: All Time</span>
      </button>
      <div id="time-popover">
        <span class="tl">Filter thoughts by time</span>
        <div class="time-presets">
          <button class="tbtn active" data-range="all" onclick="setTimeRange('all')">All Time</button>
          <button class="tbtn" data-range="today" onclick="setTimeRange('today')">Today</button>
          <button class="tbtn" data-range="yesterday" onclick="setTimeRange('yesterday')">Yesterday</button>
          <button class="tbtn" data-range="week" onclick="setTimeRange('week')">This Week</button>
          <button class="tbtn" data-range="month" onclick="setTimeRange('month')">This Month</button>
          <button class="tbtn" data-range="year" onclick="setTimeRange('year')">This Year</button>
          <button class="tbtn" data-range="last2y" onclick="setTimeRange('last2y')">Last 2 Years</button>
        </div>
        <div class="custom-label">Custom range</div>
        <div id="custom-range">
          <input type="date" id="date-from" aria-label="From date" onchange="setCustomRange()">
          <input type="date" id="date-to" aria-label="To date" onchange="setCustomRange()">
        </div>
        <span id="time-info"></span>
      </div>
    </div>
  </div>
</div>
<div id="main">
  <div id="loading-overlay"><div class="spinner"></div></div>
  <div id="graph"></div>
  <div id="sidebar">
    <div id="info-panel">
      <h3>Info</h3>
      <div id="info-content"><span class="empty">Click a node to inspect. Double-click to drill down.</span></div>
    </div>
    <div id="legend-wrap">
      <h3 id="legend-title">Mega-Topics</h3>
      <div id="legend"></div>
    </div>
    <div id="stats"></div>
  </div>
  <div id="chat-panel">
    <div class="chat-header">
      <h3>Query</h3>
      <button class="chat-close" onclick="closeChatPanel()">&times;</button>
    </div>
    <div class="chat-scope" id="chat-scope">Select a topic to query</div>
    <div class="chat-mode-btns">
      <button class="active" id="btn-mode-context" onclick="setChatMode('context')">Context Search</button>
      <button id="btn-mode-latest" onclick="setChatMode('latest')">Latest</button>
    </div>
    <div id="chat-bar">
      <input type="text" id="chat-input" placeholder="Type your query..." onkeydown="if(event.key==='Enter')runQuery()">
      <button id="chat-go" onclick="runQuery()">Search</button>
    </div>
    <div id="chat-results"><span class="chat-empty">Results will appear here</span></div>
  </div>
</div>
<div id="entity-overlay" onclick="closeEntityDetail()"></div>
<div id="entity-detail">
  <button class="eclose" onclick="closeEntityDetail()">&times;</button>
  <h2 id="ename"></h2>
  <div class="etype" id="etype"></div>
  <div class="esummary" id="esummary"></div>
  <div id="edetails"></div>
</div>
<div id="echoes-overlay" onclick="closeEchoes()"></div>
<div id="echoes-panel">
  <div id="echoes-header">
    <h2>Echoes</h2>
    <span class="echo-meta" id="echoes-meta"></span>
    <button class="eclose" onclick="closeEchoes()" title="Close">&times;</button>
  </div>
  <div id="echoes-controls">
    <label>Min size <input id="echo-min-size" type="number" min="2" max="100" value="5" onchange="loadEchoes()"></label>
    <label>Min sim <input id="echo-min-sim" type="number" min="0" max="1" step="0.01" value="0.95" onchange="loadEchoes()"></label>
    <div class="seg" role="tablist" aria-label="Status filter">
      <button data-es="all" class="active" onclick="setEchoStatusFilter('all')">All</button>
      <button data-es="observe" onclick="setEchoStatusFilter('observe')">Observe</button>
      <button data-es="discard" onclick="setEchoStatusFilter('discard')">Discard</button>
      <button data-es="neutral" onclick="setEchoStatusFilter('neutral')">Neutral</button>
    </div>
    <span id="echoes-count" style="text-align:right; color:#7a7aaf; font-size:11px;"></span>
  </div>
  <div id="echoes-list"><div id="echoes-empty">Loading&hellip;</div></div>
</div>
<div id="note-overlay" onclick="closeCreateNote()"></div>
<div id="note-modal">
  <button class="nclose" onclick="closeCreateNote()">&times;</button>
  <h2>Add Note</h2>
  <label>Directory</label>
  <select id="note-dir"></select>
  <label>Title</label>
  <input id="note-title" type="text" placeholder="Note title..." autocomplete="off">
  <label>Content</label>
  <textarea id="note-content" placeholder="Write your thought..."></textarea>
  <button class="nbtn" id="note-submit" onclick="submitNote()">Create Note</button>
  <div class="nfeedback" id="note-feedback"></div>
</div>

<script>
const CLUSTERS = __CLUSTERS__;
const SUPER_CLUSTERS = __SUPER_CLUSTERS__;
const EDGES = __EDGES__;
const PALETTE = __PALETTE__;
const ENTITIES = __ENTITIES__;
const GLOSSARY = __GLOSSARY__;
const TAXONOMY = __TAXONOMY__;
const SURFACE_TO_PATH = {
  map: '/',
  entities: '/entities',
  glossary: '/glossary',
  taxonomy: '/taxonomy',
  echoes: '/echoes',
};
const PATH_TO_SURFACE = {
  '/': 'map',
  '/entities': 'entities',
  '/glossary': 'glossary',
  '/taxonomy': 'taxonomy',
  '/echoes': 'echoes',
};

// Time filtering state
let filterFrom = null, filterTo = null;
let activeTimeRange = 'all';

function todayStr() { return new Date().toISOString().substring(0, 10); }
function addDays(d, n) { const r = new Date(d); r.setDate(r.getDate() + n); return r.toISOString().substring(0, 10); }
function startOfWeek(d) { const r = new Date(d); const day = r.getDay(); const diff = day === 0 ? 6 : day - 1; r.setDate(r.getDate() - diff); return r.toISOString().substring(0, 10); }
function startOfMonth(d) { const r = new Date(d); r.setDate(1); return r.toISOString().substring(0, 10); }
function startOfYear(d) { return d.getFullYear() + '-01-01'; }

function describeTimeRange() {
  switch (activeTimeRange) {
    case 'all': return 'Time: All Time';
    case 'today': return 'Time: Today';
    case 'yesterday': return 'Time: Yesterday';
    case 'week': return 'Time: This Week';
    case 'month': return 'Time: This Month';
    case 'year': return 'Time: This Year';
    case 'last2y': return 'Time: Last 2 Years';
    case 'custom': return 'Time: Custom';
    default: return 'Time: Filtered';
  }
}

function syncTimeUi() {
  const trigger = document.getElementById('time-trigger');
  const label = document.getElementById('time-trigger-label');
  const popover = document.getElementById('time-popover');
  const customRange = document.getElementById('custom-range');
  if (label) label.textContent = describeTimeRange();
  if (trigger) {
    trigger.classList.toggle('filtered', activeTimeRange !== 'all');
    trigger.setAttribute('aria-expanded', popover && popover.classList.contains('open') ? 'true' : 'false');
  }
  if (customRange) customRange.classList.toggle('active', activeTimeRange === 'custom');
  document.querySelectorAll('.tbtn').forEach(b => b.classList.toggle('active', b.dataset.range === activeTimeRange));
}

function closeTimePopover() {
  const popover = document.getElementById('time-popover');
  if (!popover) return;
  popover.classList.remove('open');
  syncTimeUi();
}

function toggleTimePopover(event) {
  if (event) event.stopPropagation();
  const popover = document.getElementById('time-popover');
  if (!popover) return;
  popover.classList.toggle('open');
  syncTimeUi();
}

document.addEventListener('click', function(e) {
  const filter = document.getElementById('time-filter');
  if (!filter || filter.contains(e.target)) return;
  closeTimePopover();
});

function setTimeRange(range) {
  activeTimeRange = range;
  const today = new Date();
  switch(range) {
    case 'all': filterFrom = null; filterTo = null; break;
    case 'today': filterFrom = todayStr(); filterTo = todayStr(); break;
    case 'yesterday': filterFrom = addDays(today, -1); filterTo = addDays(today, -1); break;
    case 'week': filterFrom = startOfWeek(today); filterTo = todayStr(); break;
    case 'month': filterFrom = startOfMonth(today); filterTo = todayStr(); break;
    case 'year': filterFrom = startOfYear(today); filterTo = todayStr(); break;
    case 'last2y': filterFrom = (today.getFullYear() - 2) + todayStr().substring(4); filterTo = todayStr(); break;
    case 'custom': break;
  }
  document.getElementById('date-from').value = filterFrom || '';
  document.getElementById('date-to').value = filterTo || '';
  applyTimeFilter();
  closeTimePopover();
}

function setCustomRange() {
  const fromInput = document.getElementById('date-from');
  const toInput = document.getElementById('date-to');
  const from = fromInput.value;
  const to = toInput.value;
  if (!from && !to) {
    activeTimeRange = 'all';
    filterFrom = null;
    filterTo = null;
    applyTimeFilter();
    closeTimePopover();
    return;
  }
  if (from && to) {
    filterFrom = from <= to ? from : to;
    filterTo = from <= to ? to : from;
    activeTimeRange = 'custom';
    fromInput.value = filterFrom;
    toInput.value = filterTo;
    applyTimeFilter();
    closeTimePopover();
  }
}

function clusterOverlaps(c) {
  if (!filterFrom || !filterTo) return true;
  if (!c.date_min || !c.date_max) return false;
  return c.date_max >= filterFrom && c.date_min <= filterTo;
}

function clusterMatchCount(c) {
  // Count how many member dates fall within filter range
  if (!filterFrom || !filterTo || !c.member_dates) return c.size;
  return c.member_dates.filter(d => d >= filterFrom && d <= filterTo).length;
}

function superOverlaps(sc) {
  if (!filterFrom || !filterTo) return true;
  if (!sc.date_min || !sc.date_max) return false;
  return sc.date_max >= filterFrom && sc.date_min <= filterTo;
}

function superMatchCount(sc) {
  if (!filterFrom || !filterTo) return sc.total_size;
  let count = 0;
  sc.member_ids.forEach(cid => { const c = clusterById[cid]; if (c) count += clusterMatchCount(c); });
  return count;
}

function thoughtMatches(t) {
  if (!filterFrom || !filterTo) return true;
  if (!t.timestamp) return false;
  const d = t.timestamp.substring(0, 10);
  return d >= filterFrom && d <= filterTo;
}

function applyTimeFilter() {
  // Update info bar
  const info = document.getElementById('time-info');
  if (!filterFrom) {
    info.textContent = '';
  } else {
    const fClusters = CLUSTERS.filter(clusterOverlaps).length;
    const fThoughts = CLUSTERS.reduce((s, c) => s + clusterMatchCount(c), 0);
    info.textContent = fClusters + '/' + CLUSTERS.length + ' topics · ' + fThoughts + ' thoughts in range';
  }
  syncTimeUi();
  // Clear thoughts cache so filtered thoughts load fresh
  thoughtsCache = {};
  // Re-render current level
  if (currentSurface === 'glossary') renderGlossaryView();
  else if (currentSurface === 'taxonomy') renderTaxonomyView();
  else if (currentSurface === 'entities') buildEntitiesView();
  else if (currentLevel === 0) buildLevel0();
  else if (currentLevel === 1) buildLevel1(currentSuperId);
  else if (currentLevel === 2) drillIntoCluster(currentClusterId);
  else if (currentLevel === 3) drillIntoSubCluster(currentClusterId, currentSubId);
}

let currentLevel = 0;
let currentSuperId = null;
let currentClusterId = null;
let currentSubId = null;
let network = null;
let thoughtsCache = {};
let entityGraphCache = null;
let currentSurface = 'map';
let currentSearchTerm = '';
let selectedGlossarySlug = null;

const clusterById = {};
CLUSTERS.forEach(c => { clusterById[c.cluster_id] = c; });
const superById = {};
SUPER_CLUSTERS.forEach(sc => { superById[sc.super_id] = sc; });
const clusterToSuper = {};
SUPER_CLUSTERS.forEach((sc, idx) => {
  sc._idx = idx;
  sc.member_ids.forEach(cid => { clusterToSuper[cid] = sc; });
});

function esc(s) { return s ? s.replace(/\x3c/g, '&lt;').replace(/>/g, '&gt;') : ''; }

function entityNodeId(name) {
  return 'es_e_' + encodeURIComponent(name || 'entity');
}

function topologyEntityNodeId(name, type) {
  return 'entity:' + String((type || 'other') + '-' + (name || 'entity')).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function visibleClusterIds() {
  return new Set(CLUSTERS.filter(clusterOverlaps).map(c => c.cluster_id));
}

function glossaryEntriesInRange() {
  const visible = visibleClusterIds();
  if (!filterFrom || !filterTo) return (GLOSSARY.entries || []).slice();
  return (GLOSSARY.entries || []).filter(entry => {
    const topics = entry.topics || [];
    if (!topics.length) return false;
    return topics.some(topic => visible.has(topic.cluster_id));
  });
}

function glossaryConceptsInRange() {
  const visible = visibleClusterIds();
  if (!filterFrom || !filterTo) return (GLOSSARY.concepts || []).slice();
  return (GLOSSARY.concepts || []).filter(concept => visible.has(concept.cluster_id));
}

function surfaceFromPath(pathname) {
  return PATH_TO_SURFACE[pathname] || 'map';
}

function setSurfaceRoute(surface, replace) {
  const target = SURFACE_TO_PATH[surface] || '/';
  if (window.location.pathname === target) return;
  if (replace) window.history.replaceState({}, '', target);
  else window.history.pushState({}, '', target);
}

function navigateToSurface(surface, options = {}) {
  const opts = { replace: false, fromHistory: false, ...options };
  if (surface === 'entities') {
    openEntitiesView({ skipRoute: opts.fromHistory, replace: opts.replace });
    return;
  }
  if (surface === 'glossary') {
    openGlossaryView({ skipRoute: opts.fromHistory, replace: opts.replace });
    return;
  }
  if (surface === 'taxonomy') {
    openTaxonomyView({ skipRoute: opts.fromHistory, replace: opts.replace });
    return;
  }
  if (surface === 'echoes') {
    openEchoes({ skipRoute: opts.fromHistory, replace: opts.replace });
    return;
  }
  goToLevel0({ skipRoute: opts.fromHistory, replace: opts.replace });
}

function syncSurfaceButtons() {
  Object.keys(SURFACE_TO_PATH).forEach(surface => {
    const button = document.getElementById(surface + '-trigger');
    if (!button) return;
    button.classList.toggle('active', currentSurface === surface);
  });
}

function updateBreadcrumb() {
  const bc = document.getElementById('breadcrumb');
  let html = '';
  if (currentSurface === 'glossary') {
    html = '<span class="crumb" onclick="navigateToSurface(\\'map\\')">ThoughtMap</span><span class="sep"> › </span><span class="current">Glossary</span>';
  } else if (currentSurface === 'taxonomy') {
    html = '<span class="crumb" onclick="navigateToSurface(\\'map\\')">ThoughtMap</span><span class="sep"> › </span><span class="current">Taxonomy</span>';
  } else if (currentSurface === 'echoes') {
    html = '<span class="crumb" onclick="navigateToSurface(\\'map\\')">ThoughtMap</span><span class="sep"> › </span><span class="current">Echoes</span>';
  } else if (currentSurface === 'entities') {
    html = '<span class="crumb" onclick="navigateToSurface(\\'map\\')">ThoughtMap</span><span class="sep"> › </span><span class="current">Entities Graph</span>';
  } else if (currentLevel === 0) {
    html = '<span class="current">ThoughtMap</span>';
  } else if (currentLevel === 1) {
    const sc = superById[currentSuperId];
    html = '<span class="crumb" onclick="goToLevel0()">ThoughtMap</span><span class="sep"> \u203a </span><span class="current">' + esc(sc.label) + '</span>';
  } else if (currentLevel === 2) {
    const sc = clusterToSuper[currentClusterId];
    const cl = clusterById[currentClusterId];
    html = '<span class="crumb" onclick="goToLevel0()">ThoughtMap</span><span class="sep"> \u203a </span>';
    if (sc) html += '<span class="crumb" onclick="drillIntoSuper(' + sc.super_id + ')">' + esc(sc.label) + '</span><span class="sep"> \u203a </span>';
    html += '<span class="current">' + esc(cl.label) + '</span>';
  } else if (currentLevel === 3) {
    const sc = clusterToSuper[currentClusterId];
    const cl = clusterById[currentClusterId];
    const sub = cl.sub_clusters && cl.sub_clusters.find(s => s.sub_id === currentSubId);
    html = '<span class="crumb" onclick="goToLevel0()">ThoughtMap</span><span class="sep"> \u203a </span>';
    if (sc) html += '<span class="crumb" onclick="drillIntoSuper(' + sc.super_id + ')">' + esc(sc.label) + '</span><span class="sep"> \u203a </span>';
    html += '<span class="crumb" onclick="drillIntoCluster(' + currentClusterId + ')">' + esc(cl.label) + '</span><span class="sep"> \u203a </span>';
    html += '<span class="current">' + esc(sub ? sub.label : 'Thoughts') + '</span>';
  }
  bc.innerHTML = html;
}

function goToLevel0(options = {}) {
  currentSurface = 'map';
  currentLevel = 0; currentSuperId = null; currentClusterId = null; currentSubId = null;
  if (!options.skipRoute) setSurfaceRoute('map', !!options.replace);
  closeEchoes(true);
  syncSurfaceButtons();
  updateBreadcrumb(); buildLevel0();
}

function openEntitiesView(options = {}) {
  currentSurface = 'entities';
  currentLevel = 4;
  currentSuperId = null;
  currentClusterId = null;
  currentSubId = null;
  if (!options.skipRoute) setSurfaceRoute('entities', !!options.replace);
  closeEchoes(true);
  closeChatPanel();
  syncSurfaceButtons();
  updateBreadcrumb();
  buildEntitiesView();
}

function openGlossaryView(options = {}) {
  currentSurface = 'glossary';
  currentLevel = 0;
  if (!options.skipRoute) setSurfaceRoute('glossary', !!options.replace);
  closeEchoes(true);
  closeChatPanel();
  syncSurfaceButtons();
  updateBreadcrumb();
  renderGlossaryView();
}

function openTaxonomyView(options = {}) {
  currentSurface = 'taxonomy';
  currentLevel = 0;
  if (!options.skipRoute) setSurfaceRoute('taxonomy', !!options.replace);
  closeEchoes(true);
  closeChatPanel();
  syncSurfaceButtons();
  updateBreadcrumb();
  renderTaxonomyView();
}

function entityTypeColor(type) {
  if (type === 'person') return '#3fb950';
  if (type === 'organization') return '#58a6ff';
  if (type === 'project') return '#b392f0';
  if (type === 'tool') return '#e3b341';
  if (type === 'location') return '#ff7b72';
  return '#8b949e';
}

function overlapScore(a, b) {
  const setA = new Set(a || []);
  const setB = new Set(b || []);
  if (!setA.size && !setB.size) return 0;
  let inter = 0;
  setA.forEach(v => { if (setB.has(v)) inter++; });
  const union = new Set([...(a || []), ...(b || [])]).size;
  return union ? inter / union : 0;
}

function buildEntitiesView() {
  const visibleClusters = CLUSTERS.filter(clusterOverlaps);
  const clusterSet = new Set(visibleClusters.map(c => c.cluster_id));

  const entities = ENTITIES
    .filter(e => (e.cluster_ids || []).some(cid => clusterSet.has(cid)))
    .sort((a, b) => (b.mention_count || 0) - (a.mention_count || 0))
    .slice(0, 120);

  const nodes = [];
  const edges = [];
  let eid = 0;

  entities.forEach(e => {
    const mentions = e.mention_count || 1;
    const color = entityTypeColor(e.type || 'other');
    const eidNode = entityNodeId(e.name);
    nodes.push({
      id: eidNode,
      label: e.name + '\\n(' + mentions + ')',
      color: { background: color + 'cc', border: color },
      shape: 'dot',
      size: Math.max(10, Math.min(28, 8 + Math.log2(mentions + 1) * 3)),
      font: { size: 10, color: '#f0f0f0', strokeWidth: 1, strokeColor: '#000' },
      borderWidth: 1,
      _type: 'entity',
      _data: e,
    });
  });

  for (let i = 0; i < entities.length; i++) {
    for (let j = i + 1; j < entities.length; j++) {
      const a = entities[i];
      const b = entities[j];
      const clusterJ = overlapScore(a.cluster_ids || [], b.cluster_ids || []);
      const sourceJ = overlapScore(a.source_files || [], b.source_files || []);
      const score = (0.75 * clusterJ) + (0.25 * sourceJ);
      if (score < 0.34) continue;
      edges.push({
        id: 'ee_' + (eid++),
        from: entityNodeId(a.name),
        to: entityNodeId(b.name),
        color: { color: '#9aa3c7', opacity: Math.min(0.65, 0.18 + score * 0.7) },
        width: 0.8 + score * 2.4,
        smooth: { type: 'continuous' },
      });
    }
  }

  entityGraphCache = { entities, visibleClusters, edgesCount: edges.length };
  renderNetwork(nodes, edges, { gravity: -115, spring: 170, central: 0.006, overlap: 0.9 });
  buildLegendEntities(entities);
  document.getElementById('legend-title').textContent = 'Entities Graph';
  document.getElementById('info-content').innerHTML = '<div class="field"><b>Entities view</b></div><div class="field">Entity-only graph</div><div class="field" style="font-size:11px;color:#7a7aaf;">Click a node to inspect. Double-click an entity for full detail.</div>';
  updateStats(entities.length + ' entities · ' + edges.length + ' links');
}

function renderDocumentSurface(innerHtml) {
  const container = document.getElementById('graph');
  if (network) {
    network.destroy();
    network = null;
  }
  container.classList.add('doc-surface');
  container.innerHTML = innerHtml;
}

function matchesSearch(parts) {
  if (!currentSearchTerm) return true;
  return parts.some(part => (part || '').toLowerCase().includes(currentSearchTerm));
}

function showOverviewInfo(title, detail, helper) {
  let html = '<div class="field"><b>' + esc(title) + '</b></div>';
  if (detail) html += '<div class="summary">' + esc(detail) + '</div>';
  if (helper) html += '<div class="field" style="font-size:11px;color:#7a7aaf;">' + esc(helper) + '</div>';
  document.getElementById('info-content').innerHTML = html;
}

function renderGlossaryView() {
  const entries = glossaryEntriesInRange().filter(entry => matchesSearch([
    entry.name,
    entry.summary,
    entry.type,
    ...(entry.aliases || []),
  ]));
  const concepts = glossaryConceptsInRange().filter(concept => matchesSearch([
    concept.name,
    concept.summary,
  ]));
  let html = '<div class="doc-shell">';
  html += '<div class="doc-intro">Canonical terms from the current run: named entities first, then topic labels. The cards stay compact so the view reads like an index, not a report.</div>';
  if (entries.length) {
    html += '<div class="doc-grid">';
    entries.slice(0, 160).forEach(entry => {
      html += '<article class="doc-card" onclick="showGlossaryEntry(\\'' + entry.slug.replace(/'/g, "\\'") + '\\')">';
      html += '<div class="doc-kicker">' + esc(entry.type) + '</div>';
      html += '<div class="doc-title">' + esc(entry.name) + '</div>';
      html += '<div class="doc-meta">' + entry.mention_count + ' mentions · ' + entry.topic_count + ' topics</div>';
      if (entry.summary) html += '<div class="doc-summary">' + esc(entry.summary) + '</div>';
      if (entry.aliases && entry.aliases.length) {
        html += '<div class="doc-chip-row">' + entry.aliases.slice(0, 3).map(alias => '<span class="doc-chip">' + esc(alias) + '</span>').join('') + '</div>';
      }
      html += '</article>';
    });
    html += '</div>';
  } else {
    html += '<div class="doc-empty">No glossary entries match the current search and time filter.</div>';
  }
  if (concepts.length) {
    html += '<div class="doc-section-label">Topic labels</div><div class="doc-grid doc-grid-compact">';
    concepts.slice(0, 60).forEach(concept => {
      html += '<article class="doc-card" onclick="openClusterFromSurface(' + concept.cluster_id + ')">';
      html += '<div class="doc-kicker">Topic</div>';
      html += '<div class="doc-title">' + esc(concept.name) + '</div>';
      html += '<div class="doc-meta">' + concept.mention_count + ' thoughts</div>';
      if (concept.summary) html += '<div class="doc-summary">' + esc(concept.summary) + '</div>';
      html += '</article>';
    });
    html += '</div>';
  }
  html += '</div>';
  renderDocumentSurface(html);
  buildLegendGlossary();
  if (selectedGlossarySlug) showGlossaryEntry(selectedGlossarySlug);
  else showOverviewInfo('Glossary', 'Open a card to inspect aliases, boundaries, and linked topics.', 'Click a topic label to jump back into the map.');
  updateStats(entries.length + ' terms · ' + concepts.length + ' topic labels');
}

function showGlossaryEntry(slug) {
  const entry = (GLOSSARY.entries || []).find(item => item.slug === slug);
  if (!entry) return;
  selectedGlossarySlug = slug;
  let html = '<div class="field"><b>' + esc(entry.name) + '</b></div>';
  html += '<div class="field"><span class="mega-badge">' + esc(entry.type) + ' · ' + entry.mention_count + ' mentions</span></div>';
  if (entry.summary) html += '<div class="summary">' + esc(entry.summary) + '</div>';
  if (entry.aliases && entry.aliases.length) html += '<div class="field"><b>Aliases:</b> ' + entry.aliases.map(alias => esc(alias)).join(', ') + '</div>';
  if (entry.detail) html += '<div class="field"><b>Boundaries:</b><br>' + esc(entry.detail) + '</div>';
  if (entry.topics && entry.topics.length) {
    html += '<div style="margin-top:8px"><b>Topics:</b></div>';
    entry.topics.slice(0, 10).forEach(topic => {
      html += '<span class="related-item" onclick="openClusterFromSurface(' + topic.cluster_id + ')">' + esc(topic.label) + ' (' + topic.mentions + ')</span> ';
    });
  }
  document.getElementById('info-content').innerHTML = html;
}

function renderTaxonomyView() {
  const topicTree = (TAXONOMY.topic_tree || []).filter(root => {
    if (matchesSearch([root.label, root.summary])) return true;
    return (root.children || []).some(child => matchesSearch([child.label, child.summary]));
  });
  const entityTree = (TAXONOMY.entity_tree || []).filter(root => {
    if (matchesSearch([root.label])) return true;
    return (root.children || []).some(branch => {
      if (matchesSearch([branch.label])) return true;
      return (branch.children || []).some(child => matchesSearch([child.label, child.summary]));
    });
  });
  let html = '<div class="doc-shell">';
  html += '<div class="doc-intro">Two parallel hierarchies: topics grouped under mega-topics, and entities grouped by type and breadth. Use it when you want structure first and graph second.</div>';
  html += '<div class="doc-columns">';
  html += '<section class="tree-section"><div class="doc-section-label">Topics</div>';
  topicTree.forEach(root => {
    html += '<details class="tree-branch" open>';
    html += '<summary><span>' + esc(root.label) + '</span><span class="count">' + root.count + ' thoughts</span></summary>';
    (root.children || []).forEach(child => {
      html += '<div class="tree-row" onclick="openClusterFromSurface(' + child.cluster_id + ')"><span class="label">' + esc(child.label) + '</span><span class="meta">' + child.count + ' thoughts</span></div>';
    });
    html += '</details>';
  });
  html += '</section>';
  html += '<section class="tree-section"><div class="doc-section-label">Entities</div>';
  entityTree.forEach(root => {
    html += '<details class="tree-branch" open>';
    html += '<summary><span>' + esc(root.label) + '</span><span class="count">' + root.count + ' terms</span></summary>';
    (root.children || []).forEach(branch => {
      html += '<details class="tree-branch" open><summary><span>' + esc(branch.label) + '</span><span class="count">' + branch.count + '</span></summary>';
      (branch.children || []).forEach(child => {
        html += '<div class="tree-row" onclick="openEntityFromSurface(\\'' + child.slug.replace(/'/g, "\\'") + '\\')"><span class="label">' + esc(child.label) + '</span><span class="meta">' + child.topic_count + ' topics</span></div>';
      });
      html += '</details>';
    });
    html += '</details>';
  });
  html += '</section></div></div>';
  renderDocumentSurface(html);
  buildLegendTaxonomy(topicTree, entityTree);
  showOverviewInfo('Taxonomy', 'Browse topic branches on the left and entity branches on the right.', 'Topic rows jump into the map. Entity rows open the entity detail.');
  updateStats(topicTree.length + ' topic roots · ' + entityTree.length + ' entity roots');
}

function buildTopologyView() {
  const visibleClusters = visibleClusterIds();
  const visibleSuperIds = new Set(SUPER_CLUSTERS.filter(superOverlaps).map(sc => sc.super_id));
  const entityLinks = (TOPOLOGY.edges || []).filter(edge => edge.relation === 'appears_in' && visibleClusters.has(parseInt(String(edge.target).split(':')[1], 10)));
  const entityNodeIds = new Set(entityLinks.map(edge => edge.source));
  const clusterNodes = (TOPOLOGY.nodes || []).filter(node => node.kind === 'cluster' && visibleClusters.has(parseInt(String(node.id).split(':')[1], 10)));
  const superNodes = (TOPOLOGY.nodes || []).filter(node => node.kind === 'super_cluster' && visibleSuperIds.has(parseInt(String(node.id).split(':')[1], 10)));
  const entityNodes = (TOPOLOGY.nodes || []).filter(node => node.kind === 'entity' && entityNodeIds.has(node.id)).sort((a, b) => (b.size || 0) - (a.size || 0)).slice(0, 160);
  const allowed = new Set([...clusterNodes, ...superNodes, ...entityNodes].map(node => node.id));
  const edges = (TOPOLOGY.edges || []).filter(edge => allowed.has(edge.source) && allowed.has(edge.target));
  const nodes = [...superNodes, ...clusterNodes, ...entityNodes].map(node => {
    if (node.kind === 'super_cluster') {
      return {
        id: node.id,
        label: node.label + '\\n(' + (node.size || 0) + ')',
        color: { background: '#7b61c8', border: '#bba8ff' },
        size: Math.max(24, Math.min(56, Math.sqrt(node.size || 1) * 2.4)),
        shape: 'diamond',
        font: { size: 16, color: '#fff', strokeWidth: 3, strokeColor: '#000' },
        borderWidth: 2,
        _type: 'super',
        _data: superById[parseInt(String(node.id).split(':')[1], 10)],
      };
    }
    if (node.kind === 'cluster') {
      const clusterId = parseInt(String(node.id).split(':')[1], 10);
      return {
        id: node.id,
        label: node.label + '\\n(' + (node.size || 0) + ')',
        color: { background: '#2e6ca5', border: '#7db8ef' },
        size: Math.max(16, Math.min(42, Math.sqrt(node.size || 1) * 2.0)),
        shape: 'dot',
        font: { size: 12, color: '#f4f7ff', strokeWidth: 2, strokeColor: '#000' },
        borderWidth: 2,
        _type: 'cluster',
        _data: clusterById[clusterId],
      };
    }
    const entityData = ENTITIES.find(item => topologyEntityNodeId(item.name, item.type) === node.id)
      || ENTITIES.find(item => item.name === (node.entity_name || node.label) && (item.type || 'other') === (node.entity_type || 'other'))
      || { name: node.entity_name || node.label, type: node.entity_type || 'other', summary: node.summary || '', mention_count: node.size || 0, cluster_ids: [] };
    return {
      id: node.id,
      label: node.label + '\\n(' + (node.size || 0) + ')',
      color: { background: entityTypeColor(node.entity_type || 'other') + 'cc', border: entityTypeColor(node.entity_type || 'other') },
      size: Math.max(10, Math.min(30, 8 + Math.log2((node.size || 1) + 1) * 3)),
      shape: 'dot',
      font: { size: 10, color: '#f0f0f0', strokeWidth: 1, strokeColor: '#000' },
      borderWidth: 1,
      _type: 'entity',
      _data: entityData,
    };
  });
  const visEdges = edges.map((edge, index) => ({
    id: 'topo_' + index,
    from: edge.source,
    to: edge.target,
    color: { color: edge.relation === 'related' ? '#7d87b5' : '#505678', opacity: edge.relation === 'related' ? 0.45 : 0.25 },
    width: edge.relation === 'related' ? 1 + ((edge.weight || 0) * 2.4) : 1.2,
    smooth: { type: 'continuous' },
  }));
  topologyViewCache = { nodes };
  renderNetwork(nodes, visEdges, { gravity: -120, spring: 170, central: 0.006, overlap: 0.9 });
  buildLegendTopology(nodes);
  document.getElementById('legend-title').textContent = 'Topology';
  showOverviewInfo('Topology', 'A structural view across mega-topics, topics, and entities linked by containment, similarity, and presence.', 'Double-click a topic to drill into the map, or an entity to open its detail.');
  updateStats(nodes.length + ' nodes · ' + visEdges.length + ' links');
}

function renderOntologyView() {
  const visible = visibleClusterIds();
  const triples = (ONTOLOGY.triples || []).filter(triple => {
    if (!filterFrom || !filterTo) return true;
    if (triple.predicate === 'appears_in') {
      return visible.has(parseInt(String(triple.object).split(':')[1], 10));
    }
    const shared = (((triple.evidence || {}).shared_clusters) || []);
    if (!shared.length) return true;
    return shared.some(clusterId => visible.has(clusterId));
  }).filter(triple => matchesSearch([
    triple.subject_label,
    triple.object_label,
    triple.label,
    triple.predicate,
  ]));
  const groups = {};
  triples.forEach(triple => {
    if (!groups[triple.predicate]) groups[triple.predicate] = [];
    groups[triple.predicate].push(triple);
  });
  let html = '<div class="doc-shell">';
  html += '<div class="doc-intro">A lightweight ontology inferred from the current run. It stays typed and readable: classes, predicates, then concrete triples with evidence instead of a long formal dump.</div>';
  const predicates = Object.keys(groups).sort((a, b) => groups[b].length - groups[a].length);
  predicates.forEach(predicate => {
    html += '<div class="triple-group"><div class="doc-section-label">' + esc(predicate.replace(/_/g, ' ')) + '</div><div class="triple-list">';
    groups[predicate].slice(0, 60).forEach((triple, index) => {
      html += '<button class="triple-row" type="button" onclick="showOntologyTriple(' + index + ', \\'' + predicate.replace(/'/g, "\\'") + '\\')">';
      html += '<div class="triple-main"><span>' + esc(triple.subject_label || triple.label || triple.subject || '') + '</span><span class="triple-predicate">' + esc(predicate) + '</span><span>' + esc(triple.object_label || triple.object || '') + '</span></div>';
      html += '<div class="triple-meta">confidence ' + (triple.confidence || 0).toFixed(3) + '</div>';
      html += '</button>';
    });
    html += '</div></div>';
  });
  if (!predicates.length) html += '<div class="doc-empty">No ontology triples match the current filters.</div>';
  html += '</div>';
  renderDocumentSurface(html);
  window.__ontologyGroups = groups;
  buildLegendOntology(predicates, groups);
  showOverviewInfo('Ontology', 'Read the triples as typed statements over the current map.', 'Open a row to inspect evidence and jump back to related topics.');
  updateStats(triples.length + ' triples · ' + (ONTOLOGY.classes || []).length + ' classes');
}

function showOntologyTriple(index, predicate) {
  const triple = (((window.__ontologyGroups || {})[predicate]) || [])[index];
  if (!triple) return;
  let html = '<div class="field"><b>' + esc(triple.subject_label || triple.label || triple.subject || '') + '</b></div>';
  html += '<div class="field"><span class="mega-badge">' + esc(predicate.replace(/_/g, ' ')) + '</span></div>';
  html += '<div class="summary">' + esc((triple.subject_label || triple.label || triple.subject || '') + ' ' + predicate.replace(/_/g, ' ') + ' ' + (triple.object_label || triple.object || '')) + '</div>';
  html += '<div class="field"><b>Confidence:</b> ' + (triple.confidence || 0).toFixed(3) + '</div>';
  const shared = (((triple.evidence || {}).shared_clusters) || []);
  if (shared.length) {
    html += '<div style="margin-top:8px"><b>Evidence topics:</b></div>';
    shared.slice(0, 8).forEach(clusterId => {
      const cluster = clusterById[clusterId];
      const label = cluster ? cluster.label : ('Cluster ' + clusterId);
      html += '<span class="related-item" onclick="openClusterFromSurface(' + clusterId + ')">' + esc(label) + '</span> ';
    });
  }
  document.getElementById('info-content').innerHTML = html;
}

function buildLegendGlossary() {
  const legend = document.getElementById('legend');
  legend.innerHTML = '';
  const counts = GLOSSARY.type_counts || {};
  Object.keys(counts).sort().forEach(type => {
    const item = document.createElement('div');
    item.className = 'legend-item';
    item.innerHTML = '<div class="legend-dot" style="background:' + entityTypeColor(type) + '"></div><span class="legend-label">' + esc(type) + '</span><span class="legend-count">' + counts[type] + '</span>';
    item.onclick = () => {
      document.getElementById('search').value = type;
      currentSearchTerm = type;
      renderGlossaryView();
    };
    legend.appendChild(item);
  });
  document.getElementById('legend-title').textContent = 'Glossary';
}

function buildLegendTaxonomy(topicTree, entityTree) {
  const legend = document.getElementById('legend');
  legend.innerHTML = '';
  [
    ['Mega-topics', topicTree.length, '#7b61c8'],
    ['Entity roots', entityTree.length, '#4E79A7'],
  ].forEach(meta => {
    const item = document.createElement('div');
    item.className = 'legend-item';
    item.innerHTML = '<div class="legend-dot" style="background:' + meta[2] + '"></div><span class="legend-label">' + meta[0] + '</span><span class="legend-count">' + meta[1] + '</span>';
    legend.appendChild(item);
  });
  document.getElementById('legend-title').textContent = 'Taxonomy';
}

function buildLegendTopology(nodes) {
  const legend = document.getElementById('legend');
  legend.innerHTML = '';
  [
    ['Mega-topics', nodes.filter(node => node._type === 'super').length, '#7b61c8'],
    ['Topics', nodes.filter(node => node._type === 'cluster').length, '#2e6ca5'],
    ['Entities', nodes.filter(node => node._type === 'entity').length, '#59A14F'],
  ].forEach(meta => {
    const item = document.createElement('div');
    item.className = 'legend-item';
    item.innerHTML = '<div class="legend-dot" style="background:' + meta[2] + '"></div><span class="legend-label">' + meta[0] + '</span><span class="legend-count">' + meta[1] + '</span>';
    legend.appendChild(item);
  });
}

function buildLegendOntology(predicates, groups) {
  const legend = document.getElementById('legend');
  legend.innerHTML = '';
  predicates.slice(0, 8).forEach(predicate => {
    const item = document.createElement('div');
    item.className = 'legend-item';
    item.innerHTML = '<div class="legend-dot" style="background:#4E79A7"></div><span class="legend-label">' + esc(predicate.replace(/_/g, ' ')) + '</span><span class="legend-count">' + groups[predicate].length + '</span>';
    item.onclick = () => {
      document.getElementById('search').value = predicate;
      currentSearchTerm = predicate;
      renderOntologyView();
    };
    legend.appendChild(item);
  });
  document.getElementById('legend-title').textContent = 'Ontology';
}

function openClusterFromSurface(clusterId) {
  document.getElementById('search').value = '';
  currentSearchTerm = '';
  setSurfaceRoute('map', false);
  currentSurface = 'map';
  closeEchoes(true);
  syncSurfaceButtons();
  drillIntoCluster(clusterId);
}

function openEntityFromSurface(slug) {
  const entry = (GLOSSARY.entries || []).find(item => item.slug === slug);
  if (!entry) return;
  showEntityDetail(entry.name);
}

function buildLegendEntities(entities) {
  const legend = document.getElementById('legend');
  legend.innerHTML = '';
  const typeOrder = ['person', 'organization', 'project', 'tool', 'location', 'other'];
  const labels = {
    person: 'People',
    organization: 'Organizations',
    project: 'Projects',
    tool: 'Tools',
    location: 'Locations',
    other: 'Other',
  };
  typeOrder.forEach(type => {
    const list = entities.filter(e => (e.type || 'other') === type);
    if (!list.length) return;
    const item = document.createElement('div');
    item.className = 'legend-item';
    item.innerHTML = '<div class="legend-dot" style="background:' + entityTypeColor(type) + '"></div><span class="legend-label"><b>' + labels[type] + '</b></span><span class="legend-count">' + list.length + '</span>';
    item.onclick = () => {
      const first = list[0];
      if (!first || !network) return;
      const nodeId = entityNodeId(first.name);
      try {
        network.focus(nodeId, { scale: 1.1, animation: true });
        network.selectNodes([nodeId]);
      } catch (e) {}
    };
    legend.appendChild(item);
  });
}

function showEntityNodeInfo(e) {
  let h = '<div class="field"><b>' + esc(e.name) + '</b></div>';
  h += '<div class="field"><span class="mega-badge">' + esc((e.type || 'entity') + ' · ' + (e.mention_count || 0) + ' mentions') + '</span></div>';
  if (e.summary) h += '<div class="summary">' + esc(e.summary) + '</div>';
  if (e.cluster_ids && e.cluster_ids.length) {
    h += '<div style="margin-top:8px"><b>Topics:</b></div>';
    e.cluster_ids.slice(0, 12).forEach(cid => {
      const c = clusterById[cid];
      const label = c ? c.label : ('Cluster ' + cid);
      h += '<span class="related-item" onclick="focusOrDrill(' + cid + ')">' + esc(label) + '</span> ';
    });
  }
  h += '<div class="drill-hint">Double-click to open full entity detail.</div>';
  document.getElementById('info-content').innerHTML = h;
}

function buildLevel0() {
  const nodes = [], edges = [];
  let eid = 0;
  const visibleSupers = SUPER_CLUSTERS.filter(superOverlaps);
  visibleSupers.forEach((sc, idx) => {
    const mc = superMatchCount(sc);
    const origIdx = SUPER_CLUSTERS.indexOf(sc);
    nodes.push({
      id: 'sc_' + sc.super_id,
      label: sc.label + '\\n(' + mc + ')',
      color: { background: PALETTE[origIdx % PALETTE.length], border: '#ffffff' },
      size: Math.max(30, Math.min(70, Math.sqrt(mc) * 1.5)),
      font: { size: 18, color: '#ffffff', multi: true, bold: { color: '#ffffff' }, strokeWidth: 3, strokeColor: '#000' },
      shape: 'diamond', borderWidth: 2, _type: 'super', _data: sc,
    });
  });
  const visibleIds = new Set(visibleSupers.map(sc => sc.super_id));
  for (let i = 0; i < visibleSupers.length; i++) {
    for (let j = i + 1; j < visibleSupers.length; j++) {
      const si = new Set(visibleSupers[i].member_ids), sj = new Set(visibleSupers[j].member_ids);
      let count = 0;
      EDGES.forEach(e => { if ((si.has(e.from) && sj.has(e.to)) || (sj.has(e.from) && si.has(e.to))) count++; });
      if (count > 2) edges.push({ id: eid++, from: 'sc_' + visibleSupers[i].super_id, to: 'sc_' + visibleSupers[j].super_id, color: { opacity: 0.4, color: '#6a6a8e' }, width: 1 + Math.min(count * 0.3, 6), label: '' + count, font: { size: 10, color: '#555' }, smooth: { type: 'continuous' } });
    }
  }
  renderNetwork(nodes, edges, { gravity: -200, spring: 250, central: 0.01 });
  buildLegendLevel0();
  document.getElementById('legend-title').textContent = 'Mega-Topics';
  document.getElementById('info-content').innerHTML = '<span class="empty">Double-click a mega-topic to see its topics.</span>';
  updateStats(visibleSupers.length + '/' + SUPER_CLUSTERS.length + ' mega-topics \xb7 ' + CLUSTERS.filter(clusterOverlaps).length + ' topics');
}

function drillIntoSuper(superId) {
  currentSurface = 'map';
  setSurfaceRoute('map', false);
  currentLevel = 1; currentSuperId = superId; currentClusterId = null;
  syncSurfaceButtons();
  updateBreadcrumb(); buildLevel1(superId);
}

function buildLevel1(superId) {
  const sc = superById[superId], scIdx = sc._idx;
  const allMembers = sc.member_ids.map(cid => clusterById[cid]).filter(Boolean);
  const members = allMembers.filter(clusterOverlaps);
  const mset = new Set(members.map(c => c.cluster_id));
  const nodes = [], edges = [];
  let eid = 0;
  const color = PALETTE[scIdx % PALETTE.length];
  members.forEach(c => {
    const mc = clusterMatchCount(c);
    nodes.push({
      id: 'c_' + c.cluster_id,
      label: c.label + '\\n(' + mc + ')',
      color: { background: color + 'bb', border: color },
      size: Math.max(15, Math.min(50, Math.sqrt(mc) * 2.2)),
      font: { size: 13, color: '#e0e0e0', strokeWidth: 2, strokeColor: '#000' },
      shape: 'dot', borderWidth: 1.5, _type: 'cluster', _data: c,
    });
  });
  EDGES.forEach(e => {
    if (mset.has(e.from) && mset.has(e.to)) edges.push({ id: eid++, from: 'c_' + e.from, to: 'c_' + e.to, color: { opacity: Math.max(0.2, (e.similarity - 0.5) * 2), color: '#4a4a6e' }, width: 1 + (e.similarity - 0.5) * 4, smooth: { type: 'continuous' } });
  });
  renderNetwork(nodes, edges, { gravity: -80, spring: 160, central: 0.01 });
  const filteredCount = members.reduce((s, c) => s + clusterMatchCount(c), 0);
  buildLegendLevel1(sc, members, scIdx);
  document.getElementById('legend-title').textContent = sc.label + ' \u2014 Topics';
  document.getElementById('info-content').innerHTML = '<div class="field"><b>' + esc(sc.label) + '</b></div><div class="field">' + members.length + '/' + allMembers.length + ' topics \xb7 ' + filteredCount + ' thoughts</div>' + (sc.summary ? '<div class="summary">' + esc(sc.summary) + '</div>' : '') + '<div class="drill-hint">Double-click a topic to see its thoughts.</div>';
  updateStats(members.length + ' topics in ' + sc.label);
}

async function drillIntoCluster(clusterId) {
  currentSurface = 'map';
  setSurfaceRoute('map', false);
  currentLevel = 2; currentClusterId = clusterId; currentSubId = null;
  syncSurfaceButtons();
  updateBreadcrumb();
  const cl = clusterById[clusterId];
  document.getElementById('info-content').innerHTML = '<div class="field"><b>' + esc(cl.label) + '</b> (' + cl.size + ' thoughts)</div>' + (cl.summary ? '<div class="summary">' + esc(cl.summary) + '</div>' : '') + '<div class="drill-hint">Loading thoughts...</div>';
  if (thoughtsCache[clusterId]) { buildLevel2(clusterId, thoughtsCache[clusterId]); return; }
  showLoading(true);
  try {
    const resp = await fetch('/api/cluster-thoughts/' + clusterId);
    const data = await resp.json();
    thoughtsCache[clusterId] = data.thoughts || [];
    buildLevel2(clusterId, thoughtsCache[clusterId]);
  } catch (e) {
    document.getElementById('info-content').innerHTML += '<div style="color:#f85149;margin-top:8px;">Failed: ' + e.message + '</div>';
  } finally { showLoading(false); }
}

function subClusterMatchCount(sc, thoughts) {
  if (!filterFrom || !filterTo) return sc.size;
  return sc.member_offsets.filter(i => {
    const t = thoughts[i];
    if (!t || !t.timestamp) return false;
    const d = t.timestamp.substring(0, 10);
    return d >= filterFrom && d <= filterTo;
  }).length;
}

function buildLevel2(clusterId, thoughts) {
  const cl = clusterById[clusterId];
  const sc = clusterToSuper[clusterId];
  const scIdx = sc ? sc._idx : 0;
  const color = PALETTE[scIdx % PALETTE.length];
  if (!cl.sub_clusters || cl.sub_clusters.length < 2) {
    buildLevel3(clusterId, null, thoughts);
    return;
  }
  currentLevel = 2;
  syncSurfaceButtons();
  updateBreadcrumb();
  const nodes = [];
  cl.sub_clusters.forEach(sub => {
    const mc = subClusterMatchCount(sub, thoughts);
    const empty = mc === 0;
    const density = sub.density || 0;
    const densityStr = density.toFixed(2);
    const size = Math.max(18, Math.min(60, Math.sqrt(sub.size) * 3.5 + density * 1.5));
    nodes.push({
      id: 'sub_' + sub.sub_id,
      label: sub.label + '\\n(' + mc + ' | d:' + densityStr + ')',
      title: 'Density: ' + densityStr + ' · Thoughts: ' + mc + '/' + sub.size,
      color: { background: empty ? '#1a1a2e' : (color + 'aa'), border: empty ? '#3a3a5e' : color, highlight: { background: color + 'cc', border: color } },
      opacity: empty ? 0.4 : 1.0,
      size: size,
      font: { size: 12, color: empty ? '#555' : '#e0e0e0', strokeWidth: empty ? 0 : 2, strokeColor: '#000' },
      shape: 'dot', borderWidth: empty ? 1 : 2, borderDashes: empty ? [4, 4] : false,
      _type: 'subcluster', _data: { ...sub, _clusterId: clusterId },
    });
  });
  renderNetwork(nodes, [], { gravity: -60, spring: 120, central: 0.02, overlap: 0.8 });
  const totalVisible = cl.sub_clusters.reduce((s, sub) => s + subClusterMatchCount(sub, thoughts), 0);
  buildLegendLevel2SubClusters(cl, thoughts, color);
  document.getElementById('legend-title').textContent = cl.label + ' — Sub-topics';
  document.getElementById('info-content').innerHTML = '<div class="field"><b>' + esc(cl.label) + '</b></div><div class="field">' + cl.sub_clusters.length + ' sub-topics \u00b7 ' + totalVisible + '/' + thoughts.length + ' thoughts</div>' + (cl.summary ? '<div class="summary">' + esc(cl.summary) + '</div>' : '') + '<div class="drill-hint">Double-click a sub-topic to see its thoughts.</div>';
  updateStats(cl.sub_clusters.length + ' sub-topics in ' + cl.label);
}

function buildLegendLevel2SubClusters(cl, thoughts, color) {
  const legend = document.getElementById('legend');
  legend.innerHTML = '';
  (cl.sub_clusters || []).slice().sort((a, b) => subClusterMatchCount(b, thoughts) - subClusterMatchCount(a, thoughts)).forEach(sub => {
    const mc = subClusterMatchCount(sub, thoughts);
    const density = (sub.density || 0).toFixed(2);
    const item = document.createElement('div');
    item.className = 'legend-item';
    item.style.opacity = mc === 0 ? '0.4' : '1';
    item.innerHTML = '<div class="legend-dot" style="background:' + (mc === 0 ? '#3a3a5e' : color + '99') + '"></div><span class="legend-label">' + esc(sub.label) + ' <span style="color:#8a8ab5;font-size:10px;">(d:' + density + ')</span></span><span class="legend-count">' + mc + '</span>';
    item.onclick = () => drillIntoSubCluster(cl.cluster_id, sub.sub_id);
    legend.appendChild(item);
  });
}

function showSubClusterInfo(sub, thoughts) {
  const mc = subClusterMatchCount(sub, thoughts);
  let h = '<div class="field"><b>' + esc(sub.label) + '</b></div><div class="field">' + mc + '/' + sub.size + ' thoughts</div>';
  h += '<div class="field" style="font-size:11px;color:#7a7aaf;">Density: ' + (sub.density || 0).toFixed(2) + '</div>';
  const sample = sub.member_offsets.slice(0, 3).map(i => thoughts[i]).filter(Boolean);
  if (sample.length) {
    h += '<div style="margin-top:8px"><b>Fragments:</b></div>';
    sample.forEach(t => { h += '<div class="rep-text">' + esc((t.text || '').substring(0, 200)) + '</div>'; });
  }
  h += '<div class="drill-hint">Double-click to see thoughts</div>';
  document.getElementById('info-content').innerHTML = h;
}

function drillIntoSubCluster(clusterId, subId) {
  currentSurface = 'map';
  setSurfaceRoute('map', false);
  currentLevel = 3; currentClusterId = clusterId; currentSubId = subId;
  syncSurfaceButtons();
  updateBreadcrumb();
  const thoughts = thoughtsCache[clusterId] || [];
  const cl = clusterById[clusterId];
  const sub = cl.sub_clusters && cl.sub_clusters.find(s => s.sub_id === subId);
  const subThoughts = sub ? sub.member_offsets.map(i => thoughts[i]).filter(Boolean) : thoughts;
  buildLevel3(clusterId, subId, subThoughts);
}

function buildLevel3(clusterId, subId, thoughts) {
  const cl = clusterById[clusterId], sc = clusterToSuper[clusterId];
  const scIdx = sc ? sc._idx : 0;
  const color = PALETTE[scIdx % PALETTE.length];
  const nodes = [], edges = [];
  let eid = 0;
  const filtered = thoughts.filter(thoughtMatches);
  filtered.forEach((t, i) => {
    const preview = (t.text || '').substring(0, 80).replace(/\\n/g, ' ');
    const dateLabel = t.timestamp ? t.timestamp.substring(0, 10) + ' ' : '';
    const rc = t.repeat_count || 1;
    const sz = rc > 1 ? 10 + Math.log2(rc) * 4 : 10;
    nodes.push({ id: 't_' + i, label: dateLabel + preview || '(empty)', color: { background: color + '66', border: color + 'cc' }, size: sz, font: { size: 10, color: '#ccc', strokeWidth: 1, strokeColor: '#000' }, shape: 'dot', borderWidth: 1, _type: 'thought', _data: t });
  });
  const bySource = {};
  filtered.forEach((t, i) => { const k = t.source_file || '__none__'; if (!bySource[k]) bySource[k] = []; bySource[k].push(i); });
  Object.values(bySource).forEach(g => { for (let i = 1; i < g.length; i++) edges.push({ id: eid++, from: 't_' + g[i-1], to: 't_' + g[i], color: { opacity: 0.15, color: color }, width: 0.5, smooth: { type: 'continuous' } }); });
  renderNetwork(nodes, edges, { gravity: -30, spring: 80, central: 0.02, overlap: 1.0 });
  buildLegendLevel2(cl, filtered, color);
  const sub = cl.sub_clusters && subId !== null && cl.sub_clusters.find(s => s.sub_id === subId);
  const titleLabel = sub ? cl.label + ' / ' + sub.label : cl.label;
  document.getElementById('legend-title').textContent = titleLabel;
  document.getElementById('info-content').innerHTML = '<div class="field"><b>' + esc(titleLabel) + '</b> (' + filtered.length + '/' + thoughts.length + ' thoughts)</div>' + (cl.summary ? '<div class="summary">' + esc(cl.summary) + '</div>' : '');
  updateStats(filtered.length + ' thoughts');
}

function renderNetwork(nodesArr, edgesArr, opts) {
  const container = document.getElementById('graph');
  if (network) network.destroy();
  container.classList.remove('doc-surface');
  container.innerHTML = '';
  const nodes = new vis.DataSet(nodesArr), edges = new vis.DataSet(edgesArr);
  network = new vis.Network(container, { nodes, edges }, {
    physics: { enabled: true, solver: 'forceAtlas2Based', forceAtlas2Based: { gravitationalConstant: opts.gravity || -60, centralGravity: opts.central || 0.01, springLength: opts.spring || 150, springConstant: 0.04, damping: 0.4, avoidOverlap: opts.overlap || 0.8 }, stabilization: { iterations: 200, fit: true } },
    interaction: { hover: true, tooltipDelay: 150 }, nodes: { borderWidth: 1.5 }, edges: { smooth: { type: 'continuous' } },
  });
  network.on('click', params => {
    if (!params.nodes.length) return;
    const node = nodes.get(params.nodes[0]);
    if (!node) return;
    if (node._type === 'super') showSuperInfo(node._data);
    else if (node._type === 'cluster') showClusterInfo(node._data);
    else if (node._type === 'subcluster') showSubClusterInfo(node._data, thoughtsCache[node._data._clusterId] || []);
    else if (node._type === 'thought') showThoughtInfo(node._data);
    else if (node._type === 'entity') showEntityNodeInfo(node._data);
  });
  network.on('doubleClick', params => {
    if (!params.nodes.length) return;
    const node = nodes.get(params.nodes[0]);
    if (!node) return;
    if (node._type === 'super') drillIntoSuper(node._data.super_id);
    else if (node._type === 'cluster') drillIntoCluster(node._data.cluster_id);
    else if (node._type === 'subcluster') drillIntoSubCluster(node._data._clusterId, node._data.sub_id);
    else if (node._type === 'entity') showEntityDetail(node._data.name);
  });
}

function showSuperInfo(sc) {
  const mc = superMatchCount(sc);
  let h = '<div class="field"><b>' + esc(sc.label) + '</b></div><div class="field">' + sc.member_ids.length + ' topics \xb7 ' + mc + ' thoughts</div>';
  if (sc.date_min && sc.date_max) h += '<div class="field" style="font-size:11px;color:#7a7aaf;">' + sc.date_min + ' \u2014 ' + sc.date_max + '</div>';
  if (sc.summary) h += '<div class="summary">' + esc(sc.summary) + '</div>';
  h += '<div style="margin-top:8px"><b>Topics:</b></div>';
  sc.member_ids.forEach(cid => { const c = clusterById[cid]; if (c) h += '<span class="related-item" onclick="drillIntoSuper(' + sc.super_id + ')">' + esc(c.label) + ' (' + c.size + ')</span> '; });
  h += '<div class="drill-hint">Double-click to drill in</div>';
  document.getElementById('info-content').innerHTML = h;
  updateChatScope('super', sc.super_id, sc.label);
}

function showClusterInfo(c) {
  const sc = clusterToSuper[c.cluster_id];
  const mc = clusterMatchCount(c);
  let h = '<div class="field"><b>' + esc(c.label) + '</b> (' + mc + ' thoughts)</div>';
  if (sc) h += '<div class="field"><span class="mega-badge">' + esc(sc.label) + '</span></div>';
  if (c.date_min && c.date_max) h += '<div class="field" style="font-size:11px;color:#7a7aaf;">' + c.date_min + ' \u2014 ' + c.date_max + '</div>';
  if (c.summary) h += '<div class="summary">' + esc(c.summary) + '</div>';
  if (c.related && c.related.length) { h += '<div style="margin-top:8px"><b>Related:</b></div>'; c.related.forEach(r => { h += '<span class="related-item" onclick="focusOrDrill(' + r.id + ')">' + esc(r.label) + ' (' + r.similarity.toFixed(2) + ')</span> '; }); }
  if (c.representative_texts) { h += '<div style="margin-top:8px"><b>Fragments:</b></div>'; c.representative_texts.slice(0,3).forEach(t => { h += '<div class="rep-text">' + highlightEntities((t||'').substring(0,200)) + '</div>'; }); }
  h += '<div class="drill-hint">Double-click to see thoughts</div>';
  h += '<button class="add-note-btn" onclick="openCreateNote(' + c.cluster_id + ')">+ Add Note</button>';
  document.getElementById('info-content').innerHTML = h;
  updateChatScope('cluster', c.cluster_id, c.label);
}

function showThoughtInfo(t) {
  let h = '';
  if (t.timestamp) h += '<div class="field" style="color:#7a7aaf;">' + esc(t.timestamp.substring(0,19)) + '</div>';
  if (t.source_file) h += '<div class="field" style="font-size:11px;color:#666;">' + esc(t.source_file) + '</div>';
  if (t.source) h += '<div class="field"><span class="mega-badge">' + esc(t.source) + '</span></div>';
  if (t.repeat_count > 1) h += '<div class="field" style="color:#e5a00d;">\u26a0 Appears in ' + t.repeat_count + ' notes</div>';
  h += '<div style="margin-top:8px;font-size:13px;line-height:1.6;color:#ccc;">' + highlightEntities(t.text||'') + '</div>';
  document.getElementById('info-content').innerHTML = h;
}

function focusOrDrill(clusterId) {
  if (currentLevel === 1 && network) { try { network.focus('c_' + clusterId, {scale:1.2,animation:true}); network.selectNodes(['c_' + clusterId]); return; } catch(e){} }
  drillIntoCluster(clusterId);
}

function buildLegendLevel0() {
  const legend = document.getElementById('legend'); legend.innerHTML = '';
  const visibleSupers = SUPER_CLUSTERS.filter(superOverlaps);
  visibleSupers.forEach((sc) => {
    const origIdx = SUPER_CLUSTERS.indexOf(sc);
    const mc = superMatchCount(sc);
    const item = document.createElement('div'); item.className = 'legend-item';
    item.innerHTML = '<div class="legend-dot mega" style="background:' + PALETTE[origIdx % PALETTE.length] + '"></div><span class="legend-label"><b>' + esc(sc.label) + '</b></span><span class="legend-count">' + mc + '</span>';
    item.onclick = () => drillIntoSuper(sc.super_id);
    legend.appendChild(item);
  });
}

function buildLegendLevel1(sc, members, scIdx) {
  const legend = document.getElementById('legend'); legend.innerHTML = '';
  const color = PALETTE[scIdx % PALETTE.length];
  members.filter(clusterOverlaps).sort((a,b) => clusterMatchCount(b) - clusterMatchCount(a)).forEach(c => {
    const mc = clusterMatchCount(c);
    const item = document.createElement('div'); item.className = 'legend-item';
    item.innerHTML = '<div class="legend-dot" style="background:' + color + '99"></div><span class="legend-label">' + esc(c.label) + '</span><span class="legend-count">' + mc + '</span>';
    item.onclick = () => { if (network) { network.focus('c_' + c.cluster_id, {scale:1.2,animation:true}); network.selectNodes(['c_' + c.cluster_id]); } };
    item.ondblclick = () => drillIntoCluster(c.cluster_id);
    legend.appendChild(item);
  });
}

function buildLegendLevel2(cl, thoughts, color) {
  const legend = document.getElementById('legend'); legend.innerHTML = '';
  const groups = {};
  thoughts.forEach(t => { const s = t.source || 'unknown'; groups[s] = (groups[s]||0) + 1; });
  Object.entries(groups).sort((a,b) => b[1]-a[1]).forEach(([src,count]) => {
    const item = document.createElement('div'); item.className = 'legend-item';
    item.innerHTML = '<div class="legend-dot" style="background:' + color + '66"></div><span class="legend-label">' + esc(src) + '</span><span class="legend-count">' + count + '</span>';
    legend.appendChild(item);
  });
}

function showLoading(show) { const el = document.getElementById('loading-overlay'); if (el) el.style.display = show ? 'flex' : 'none'; }
function updateStats(text) { document.getElementById('stats').textContent = text; }

document.getElementById('search').addEventListener('input', function() {
  currentSearchTerm = this.value.toLowerCase().trim();
  const q = currentSearchTerm;
  if (currentSurface === 'glossary') {
    renderGlossaryView();
    return;
  }
  if (currentSurface === 'taxonomy') {
    renderTaxonomyView();
    return;
  }
  if (q.length < 2) return;
  if (currentSurface === 'map' && currentLevel === 0) {
    const m = SUPER_CLUSTERS.find(sc => sc.label.toLowerCase().includes(q) || (sc.summary && sc.summary.toLowerCase().includes(q)));
    if (m && network) { network.focus('sc_' + m.super_id, {scale:1.2,animation:true}); network.selectNodes(['sc_' + m.super_id]); }
  } else if (currentSurface === 'map' && currentLevel === 1) {
    const sc = superById[currentSuperId];
    const m = sc.member_ids.map(cid => clusterById[cid]).filter(Boolean).find(c => c.label.toLowerCase().includes(q) || (c.summary && c.summary.toLowerCase().includes(q)));
    if (m && network) { network.focus('c_' + m.cluster_id, {scale:1.2,animation:true}); network.selectNodes(['c_' + m.cluster_id]); }
  } else if (currentSurface === 'entities') {
    const m = ENTITIES.find(e => (e.name || '').toLowerCase().includes(q) || (e.summary && e.summary.toLowerCase().includes(q)));
    if (m && network) {
      const nodeId = entityNodeId(m.name);
      try {
        network.focus(nodeId, { scale:1.2, animation:true });
        network.selectNodes([nodeId]);
      } catch (e) {}
    }
  }
});

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    const panel = document.getElementById('echoes-panel');
    if (panel && panel.classList.contains('open')) {
      closeEchoes();
      return;
    }
    const popover = document.getElementById('time-popover');
    if (popover && popover.classList.contains('open')) {
      closeTimePopover();
      return;
    }
  }
  if (document.activeElement === document.getElementById('search')) return;
  if (e.key === 'Escape' || e.key === 'Backspace') {
    if (currentSurface && currentSurface !== 'map' && currentSurface !== 'echoes') navigateToSurface('map');
    else if (currentLevel === 4) goToLevel0();
    else if (currentLevel === 3) drillIntoCluster(currentClusterId);
    else if (currentLevel === 2) { const sc = clusterToSuper[currentClusterId]; if (sc) drillIntoSuper(sc.super_id); else goToLevel0(); }
    else if (currentLevel === 1) goToLevel0();
  }
});

syncTimeUi();
syncSurfaceButtons();
navigateToSurface(surfaceFromPath(window.location.pathname), { fromHistory: true, replace: true });
window.addEventListener('popstate', function() {
  navigateToSurface(surfaceFromPath(window.location.pathname), { fromHistory: true });
});

// Entity highlighting
const _entityIndex = {};
ENTITIES.forEach(e => {
  const names = [e.name, ...(e.aliases || [])];
  names.forEach(n => { if (n && n.length > 1) _entityIndex[n.toLowerCase()] = e; });
});
const _entityNames = Object.keys(_entityIndex).sort((a, b) => b.length - a.length);

function highlightEntities(text) {
  if (!_entityNames.length) return esc(text);
  let safe = esc(text);
  const pattern = _entityNames.map(n => n.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&')).join('|');
  const re = new RegExp('\\\\b(' + pattern + ')\\\\b', 'gi');
  return safe.replace(re, (match) => {
    const e = _entityIndex[match.toLowerCase()];
    const cls = e ? e.type : '';
    const ename = e ? e.name : match;
    return '<span class="entity-hl ' + cls + '" onclick="showEntityDetail(\\'' +
      ename.replace(/'/g, "\\\\'") + '\\')">' + match + '</span>';
  });
}

function showEntityDetail(name) {
  const e = ENTITIES.find(en => en.name === name) || _entityIndex[name.toLowerCase()];
  if (!e) return;
  document.getElementById('ename').textContent = e.name;
  document.getElementById('etype').textContent = e.type + ' \\u00b7 ' + e.mention_count + ' mentions';
  document.getElementById('esummary').textContent = e.summary || '(No summary)';
  let details = '';
  if (e.aliases && e.aliases.length) details += '<div class="efield"><b>Aliases:</b> ' + e.aliases.join(', ') + '</div>';
  if (e.cluster_ids && e.cluster_ids.length) {
    const labels = e.cluster_ids.map(id => { const c = clusterById[id]; return c ? c.label : 'Cluster ' + id; });
    details += '<div class="efield"><b>Clusters:</b> ' + labels.join(', ') + '</div>';
  }
  if (e.boundaries) details += '<div class="efield" style="margin-top:8px"><b>Boundaries:</b><br>' + e.boundaries.replace(/\\n/g, '<br>') + '</div>';
  document.getElementById('edetails').innerHTML = details;
  document.getElementById('entity-overlay').style.display = 'block';
  document.getElementById('entity-detail').style.display = 'block';
}

function closeEntityDetail() {
  document.getElementById('entity-overlay').style.display = 'none';
  document.getElementById('entity-detail').style.display = 'none';
}

let _noteClusterId = null;
let _noteDirs = null;

async function loadDirectories() {
  if (_noteDirs) return _noteDirs;
  try {
    const r = await fetch('/api/directories');
    const d = await r.json();
    _noteDirs = d.directories || [];
    return _noteDirs;
  } catch(e) { return []; }
}

function suggestDirectory(clusterId) {
  const c = clusterById[clusterId];
  if (!c || !_noteDirs) return null;
  const scores = {};
  if (c.representative_texts) {
    c.representative_texts.forEach(t => {
      const m = (t || '').match(/Projects\\/([\\w-]+)\\//i);
      if (m) scores[m[1]] = (scores[m[1]] || 0) + 1;
    });
  }
  const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1]);
  if (sorted.length === 0) return null;
  const best = sorted[0][0].toLowerCase();
  return _noteDirs.find(d => d.toLowerCase().includes(best)) || null;
}

async function openCreateNote(clusterId) {
  _noteClusterId = clusterId;
  const dirs = await loadDirectories();
  const select = document.getElementById('note-dir');
  select.innerHTML = dirs.map(d => '<option value="' + d + '">' + d + '</option>').join('');
  const suggested = suggestDirectory(clusterId);
  if (suggested) select.value = suggested;
  const c = clusterById[clusterId];
  document.getElementById('note-title').value = '';
  document.getElementById('note-content').value = c && c.summary ? c.summary : '';
  document.getElementById('note-feedback').textContent = '';
  document.getElementById('note-feedback').className = 'nfeedback';
  document.getElementById('note-submit').disabled = false;
  document.getElementById('note-overlay').style.display = 'block';
  document.getElementById('note-modal').style.display = 'block';
  document.getElementById('note-title').focus();
}

function closeCreateNote() {
  document.getElementById('note-overlay').style.display = 'none';
  document.getElementById('note-modal').style.display = 'none';
}

async function submitNote() {
  const title = document.getElementById('note-title').value.trim();
  const content = document.getElementById('note-content').value.trim();
  const directory = document.getElementById('note-dir').value;
  const feedback = document.getElementById('note-feedback');
  const btn = document.getElementById('note-submit');
  if (!title || !content) {
    feedback.textContent = 'Title and content are required.';
    feedback.className = 'nfeedback err';
    return;
  }
  btn.disabled = true;
  feedback.textContent = 'Creating...';
  feedback.className = 'nfeedback';
  try {
    const r = await fetch('/api/notes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content, directory }),
    });
    const d = await r.json();
    if (d.ok) {
      feedback.textContent = '\u2713 Created: ' + d.path;
      feedback.className = 'nfeedback ok';
      setTimeout(closeCreateNote, 2000);
    } else {
      feedback.textContent = d.error || 'Failed to create note.';
      feedback.className = 'nfeedback err';
      btn.disabled = false;
    }
  } catch(e) {
    feedback.textContent = 'Network error.';
    feedback.className = 'nfeedback err';
    btn.disabled = false;
  }
}

// ── Chat / Query panel ──
let chatMode = 'context';
let chatScope = null; // { type: 'cluster'|'super', id: int, label: str }

function setChatMode(mode) {
  chatMode = mode;
  document.getElementById('btn-mode-context').className = mode === 'context' ? 'active' : '';
  document.getElementById('btn-mode-latest').className = mode === 'latest' ? 'active' : '';
  const input = document.getElementById('chat-input');
  if (mode === 'latest') {
    input.placeholder = 'Press Search to get latest thoughts';
  } else {
    input.placeholder = 'Type your query...';
  }
}

function updateChatScope(type, id, label) {
  chatScope = { type, id, label };
  document.getElementById('chat-scope').innerHTML = '<b>' + esc(label) + '</b> (' + type + ')';
}

function openChatPanel() {
  document.getElementById('chat-panel').classList.add('open');
  const trigger = document.getElementById('query-trigger');
  if (trigger) trigger.classList.add('active');
}

function toggleChatPanel() {
  const panel = document.getElementById('chat-panel');
  if (!panel) return;
  if (panel.classList.contains('open')) closeChatPanel();
  else openChatPanel();
}

function closeChatPanel() {
  document.getElementById('chat-panel').classList.remove('open');
  const trigger = document.getElementById('query-trigger');
  if (trigger) trigger.classList.remove('active');
}

async function runQuery() {
  if (!chatScope) {
    document.getElementById('chat-results').innerHTML = '<span class="chat-empty">Click a topic or mega-topic first</span>';
    return;
  }
  const queryText = document.getElementById('chat-input').value.trim();
  if (chatMode === 'context' && !queryText) {
    document.getElementById('chat-results').innerHTML = '<span class="chat-empty">Enter a query to search</span>';
    return;
  }
  const btn = document.getElementById('chat-go');
  btn.disabled = true;
  document.getElementById('chat-results').innerHTML = '<span class="chat-empty">Searching...</span>';
  try {
    const body = {
      mode: chatMode,
      scope: chatScope.type === 'super' ? 'super' : 'cluster',
      scope_id: chatScope.id,
      query: queryText,
      n: 10,
    };
    const r = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const d = await r.json();
    if (d.error) {
      document.getElementById('chat-results').innerHTML = '<span class="chat-empty" style="color:#f85149;">' + esc(d.error) + '</span>';
    } else {
      renderChatResults(d);
    }
  } catch(e) {
    document.getElementById('chat-results').innerHTML = '<span class="chat-empty" style="color:#f85149;">Network error</span>';
  } finally {
    btn.disabled = false;
  }
}

function renderChatResults(data) {
  const el = document.getElementById('chat-results');
  if (!data.results || !data.results.length) {
    el.innerHTML = '<span class="chat-empty">No results found</span>';
    return;
  }
  let h = '';
  data.results.forEach((r, i) => {
    const date = r.timestamp ? r.timestamp.substring(0, 10) : '';
    const src = r.source_file || r.source || '';
    const score = r.similarity !== undefined ? r.similarity.toFixed(3) : '';
    h += '<div class="chat-result">';
    if (score) h += '<span class="cr-score">' + score + '</span>';
    h += '<div class="cr-meta">';
    if (date) h += date + ' ';
    if (src) h += '\xb7 ' + esc(src);
    if (r.repeat_count > 1) h += ' \xb7 \xd7' + r.repeat_count;
    h += '</div>';
    h += '<div class="cr-text">' + esc((r.text || '').substring(0, 300)) + '</div>';
    h += '</div>';
  });
  h += '<div style="color:#555;font-size:11px;margin-top:4px;">' + data.count + ' results from ' + data.total + ' thoughts</div>';
  el.innerHTML = h;
}

// ─── Echoes: near-duplicate groups ───
let echoStatusFilter = 'all';

function openEchoes(options = {}) {
  currentSurface = 'echoes';
  if (!options.skipRoute) setSurfaceRoute('echoes', !!options.replace);
  closeChatPanel();
  syncSurfaceButtons();
  updateBreadcrumb();
  document.getElementById('echoes-overlay').classList.add('open');
  document.getElementById('echoes-panel').classList.add('open');
  loadEchoes();
}
function closeEchoes(silent) {
  document.getElementById('echoes-overlay').classList.remove('open');
  document.getElementById('echoes-panel').classList.remove('open');
  if (!silent && currentSurface === 'echoes') goToLevel0();
}
function setEchoStatusFilter(s) {
  echoStatusFilter = s;
  document.querySelectorAll('#echoes-controls .seg button').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-es') === s);
  });
  loadEchoes();
}

async function loadEchoes() {
  const list = document.getElementById('echoes-list');
  const meta = document.getElementById('echoes-meta');
  const countEl = document.getElementById('echoes-count');
  const minSize = parseInt(document.getElementById('echo-min-size').value || '5', 10);
  const minSim = parseFloat(document.getElementById('echo-min-sim').value || '0.95');
  list.innerHTML = '<div id="echoes-empty">Loading&hellip;</div>';
  try {
    const url = '/api/echoes?min_size=' + encodeURIComponent(minSize) +
                '&min_sim=' + encodeURIComponent(minSim) +
                '&status=' + encodeURIComponent(echoStatusFilter);
    const r = await fetch(url);
    const data = await r.json();
    if (data.message) {
      list.innerHTML = '<div id="echoes-empty">' + esc(data.message) + '</div>';
      meta.textContent = '';
      countEl.textContent = '';
      return;
    }
    const thr = data.threshold !== null && data.threshold !== undefined ? data.threshold.toFixed(2) : '?';
    meta.textContent = 'pipeline threshold ' + thr + ' · total ' + (data.total || 0);
    countEl.textContent = (data.count || 0) + ' group(s)';
    renderEchoes(data.echoes || []);
  } catch (e) {
    list.innerHTML = '<div id="echoes-empty" style="color:#f85149;">Failed: ' + esc(e.message) + '</div>';
  }
}

function renderEchoes(groups) {
  const list = document.getElementById('echoes-list');
  if (!groups.length) {
    list.innerHTML = '<div id="echoes-empty">No groups match current filters.</div>';
    return;
  }
  let h = '';
  groups.forEach(g => {
    const status = g.status || 'neutral';
    const dates = (g.date_min || g.date_max) ? (String(g.date_min||'').substring(0,10) + ' → ' + String(g.date_max||'').substring(0,10)) : '';
    const avg = (g.avg_similarity || 0).toFixed(3);
    const mn = (g.min_similarity || 0).toFixed(3);
    const rep = esc((g.representative_text || '').substring(0, 280));
    const note = esc(g.note || '');
    const fragsHtml = (g.examples || []).map(ex => {
      const srcBits = [];
      if (ex.timestamp) srcBits.push(String(ex.timestamp).substring(0,10));
      if (ex.source) srcBits.push(ex.source);
      const meta = srcBits.join(' · ');
      return '<div class="echo-frag">' + esc(ex.text || '') +
             (meta ? '<div class="fm">' + esc(meta) + '</div>' : '') + '</div>';
    }).join('');
    h += '<div class="echo-card ' + status + '" data-key="' + esc(g.echo_key) + '">' +
      '<div class="echo-head">' +
        '<span class="echo-size">' + g.size + ' thoughts</span>' +
        '<span class="echo-sim">avg ' + avg + ' · min ' + mn + '</span>' +
        (dates ? '<span class="echo-dates">' + esc(dates) + '</span>' : '') +
        '<button class="echo-expand" onclick="toggleEcho(this)">details ▾</button>' +
      '</div>' +
      '<div class="echo-rep">' + rep + '</div>' +
      '<div class="echo-frags">' + fragsHtml +
        '<textarea placeholder="Optional note..." onchange="saveEchoNote(this)">' + note + '</textarea>' +
      '</div>' +
      '<div class="echo-actions">' +
        '<button class="echo-btn observe ' + (status === 'observe' ? 'active' : '') + '" onclick="setEcho(this,\\'observe\\')">Observe</button>' +
        '<button class="echo-btn discard ' + (status === 'discard' ? 'active' : '') + '" onclick="setEcho(this,\\'discard\\')">Discard</button>' +
        '<button class="echo-btn neutral ' + (status === 'neutral' ? 'active' : '') + '" onclick="setEcho(this,\\'neutral\\')">Neutral</button>' +
      '</div>' +
    '</div>';
  });
  list.innerHTML = h;
}

function toggleEcho(btn) {
  const card = btn.closest('.echo-card');
  card.classList.toggle('expanded');
  btn.textContent = card.classList.contains('expanded') ? 'details ▴' : 'details ▾';
}

async function setEcho(btn, status) {
  const card = btn.closest('.echo-card');
  const key = card.getAttribute('data-key');
  const textarea = card.querySelector('textarea');
  const note = textarea ? textarea.value : '';
  try {
    const r = await fetch('/api/echoes/' + encodeURIComponent(key), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: status, note: note }),
    });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    card.classList.remove('observe','discard','neutral');
    card.classList.add(status);
    card.querySelectorAll('.echo-actions .echo-btn').forEach(b => {
      b.classList.remove('active');
    });
    btn.classList.add('active');
    // If filter is set and status no longer matches, remove card
    if (echoStatusFilter !== 'all' && echoStatusFilter !== status) {
      card.remove();
      const left = document.querySelectorAll('.echo-card').length;
      document.getElementById('echoes-count').textContent = left + ' group(s)';
      if (!left) {
        document.getElementById('echoes-list').innerHTML =
          '<div id="echoes-empty">No groups match current filters.</div>';
      }
    }
  } catch (e) {
    alert('Failed to save: ' + e.message);
  }
}

async function saveEchoNote(ta) {
  const card = ta.closest('.echo-card');
  const key = card.getAttribute('data-key');
  const activeBtn = card.querySelector('.echo-actions .echo-btn.active');
  const status = activeBtn ? (activeBtn.classList.contains('observe') ? 'observe' :
                              activeBtn.classList.contains('discard') ? 'discard' : 'neutral')
                           : 'neutral';
  try {
    await fetch('/api/echoes/' + encodeURIComponent(key), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: status, note: ta.value }),
    });
  } catch (e) {}
}
</script>
</body>
</html>"""


def _load_json_payload(path: Path, default: dict | list) -> dict | list:
  if not path.exists():
    return default
  try:
    return json.loads(path.read_text(encoding="utf-8"))
  except json.JSONDecodeError:
    return default


def write_condensed_visualization(condensed_json: dict, on_status: Callable[[str], None] | None = None) -> Path:
  """Render the condensed HTML view using the latest persisted side artifacts."""
  def status(message: str) -> None:
    print(message)
    if on_status:
      on_status(message)

  html = _CONDENSED_HTML
  html = html.replace("__CLUSTERS__", json.dumps(condensed_json.get("clusters", [])))
  html = html.replace("__SUPER_CLUSTERS__", json.dumps(condensed_json.get("super_clusters", [])))
  html = html.replace("__EDGES__", json.dumps(condensed_json.get("edges", [])))
  html = html.replace("__PALETTE__", json.dumps(_CONDENSED_PALETTE))
  html = html.replace("__ENTITIES__", json.dumps(_load_json_payload(config.OUTPUT_DIR / "entities.json", [])))
  html = html.replace("__GLOSSARY__", json.dumps(_load_json_payload(config.GLOSSARY_PATH, {"entries": [], "concepts": [], "type_counts": {}})))
  html = html.replace("__TAXONOMY__", json.dumps(_load_json_payload(config.TAXONOMY_PATH, {"topic_tree": [], "entity_tree": [], "stats": {}})))

  viz_path = config.OUTPUT_DIR / "thoughtmap-condensed.html"
  viz_path.write_text(html, encoding="utf-8")
  status(f"  Condensed visualization: {viz_path}")
  return viz_path


# ─── Public API ───

def condense(
    result: ThoughtMapResult,
    on_status: Callable[[str], None] | None = None,
    embeddings_hd: list | None = None,
) -> dict:
    """Run the full condensation pipeline.

    Returns dict with summaries, edges, super_clusters, and output paths.
    """
    def status(msg: str):
        print(msg)
        if on_status:
            on_status(msg)

    clusters = result.clusters
    items = result.items

    # ── 1. Pull model if needed ──
    status(f"  Checking model {config.CONDENSE_MODEL}...")
    try:
        resp = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/show",
            json={"name": config.CONDENSE_MODEL},
            timeout=10,
        )
        if resp.status_code == 404:
            status(f"  Pulling {config.CONDENSE_MODEL} (first time)...")
            pull_resp = requests.post(
                f"{config.OLLAMA_BASE_URL}/api/pull",
                json={"name": config.CONDENSE_MODEL, "stream": False},
                timeout=600,
            )
            pull_resp.raise_for_status()
            status(f"  Model pulled successfully")
    except Exception as e:
        status(f"  Warning: Could not verify model: {e}")

    # ── 2. Summarize & label clusters ──
    status(f"  Summarizing {len(clusters)} clusters with {config.CONDENSE_MODEL}...")
    cluster_summaries: dict[int, str] = {}
    for i, cluster in enumerate(clusters):
        if (i + 1) % 10 == 0 or i == 0:
            status(f"    [{i+1}/{len(clusters)}] {cluster.label}...")
        label, summary = _summarize_cluster(cluster, items)
        cluster.label = label
        cluster_summaries[cluster.cluster_id] = summary

    # ── 3. Compute inter-cluster edges ──
    status("  Computing inter-cluster edges...")
    edges = _compute_cluster_edges(clusters)
    status(f"  Found {len(edges)} edges (threshold={config.CONDENSE_EDGE_THRESHOLD})")

    # ── 4. Build related-topics index from edges ──
    related_map: dict[int, list[tuple[ClusterInfo, float]]] = defaultdict(list)
    cid_to_cluster = {c.cluster_id: c for c in clusters}
    for edge in edges:
        from_id, to_id = edge["from"], edge["to"]
        sim = edge["similarity"]
        if to_id in cid_to_cluster:
            related_map[from_id].append((cid_to_cluster[to_id], sim))
        if from_id in cid_to_cluster:
            related_map[to_id].append((cid_to_cluster[from_id], sim))
    # Sort by similarity
    for cid in related_map:
        related_map[cid].sort(key=lambda x: -x[1])

    # ── 5. Super-cluster ──
    status("  Building super-clusters...")
    super_clusters = _super_cluster(clusters)
    status(f"  Formed {len(super_clusters)} mega-topics")

    # ── 6. Summarize & label super-clusters ──
    status(f"  Summarizing {len(super_clusters)} mega-topics...")
    super_summaries: dict[int, str] = {}
    for sc in super_clusters:
        member_clusters = [cid_to_cluster[cid] for cid in sc["member_ids"] if cid in cid_to_cluster]
        label, summary = _summarize_super_cluster(
            sc["label"], member_clusters, cluster_summaries,
        )
        sc["label"] = label
        super_summaries[sc["super_id"]] = summary

    # ── 7. Generate Obsidian topic notes ──
    status("  Generating Obsidian topic notes...")
    topics_dir = config.TOPICS_DIR
    topics_dir.mkdir(parents=True, exist_ok=True)
    # Clean previous
    for old in topics_dir.glob("*.md"):
        old.unlink()

    # Build super-cluster lookup
    cid_to_super: dict[int, dict] = {}
    for sc in super_clusters:
        for cid in sc["member_ids"]:
            cid_to_super[cid] = sc

    # Cluster topic notes
    for cluster in clusters:
        content = _generate_topic_note(
            cluster=cluster,
            summary=cluster_summaries.get(cluster.cluster_id, ""),
            related=related_map.get(cluster.cluster_id, []),
            super_cluster=cid_to_super.get(cluster.cluster_id),
            items=items,
        )
        slug = _slugify(cluster.label)
        (topics_dir / f"{slug}.md").write_text(content, encoding="utf-8")

    # Super-cluster notes
    for sc in super_clusters:
        member_clusters = [cid_to_cluster[cid] for cid in sc["member_ids"] if cid in cid_to_cluster]
        content = _generate_super_topic_note(
            super_cluster=sc,
            summary=super_summaries.get(sc["super_id"], ""),
            member_clusters=member_clusters,
            cluster_summaries=cluster_summaries,
        )
        slug = _slugify(sc["label"])
        (topics_dir / f"{slug}.md").write_text(content, encoding="utf-8")

    # Index
    index_content = _generate_topics_index(
        super_clusters, super_summaries, clusters, cluster_summaries,
    )
    (topics_dir / "_index.md").write_text(index_content, encoding="utf-8")

    status(f"  Generated {len(clusters) + len(super_clusters) + 1} topic notes in {topics_dir}")

    # ── 8. Generate condensed visualization ──
    status("  Generating condensed visualization...")

    # Pre-compute per-chunk timestamps as ISO date strings for the UI
    chunk_dates: list[str] = []
    for item in items:
        ts = item.get("timestamp", "")
        chunk_dates.append(ts[:10] if ts else "")  # "YYYY-MM-DD" or ""

    # Pre-compute sub-clusters (on all thoughts, time-filter-stable)
    status("  Computing sub-clusters...")
    sub_clusters_cache: dict[int, list[dict]] = {}
    if embeddings_hd is not None:
        embs_list = embeddings_hd if isinstance(embeddings_hd, list) else list(embeddings_hd)
        for c in clusters:
            subs = compute_sub_clusters(c.member_indices, embs_list, items)
            sub_clusters_cache[c.cluster_id] = subs
        total_subs = sum(len(v) for v in sub_clusters_cache.values())
        status(f"  Sub-clusters: {total_subs} across {len(clusters)} clusters")

    clusters_viz = []
    for c in clusters:
        # Compute date range from member chunks
        member_dates = sorted(
            d for idx in c.member_indices
            if 0 <= idx < len(chunk_dates) and (d := chunk_dates[idx])
        )
        subs = sub_clusters_cache.get(c.cluster_id, [])
        clusters_viz.append({
            "cluster_id": c.cluster_id,
            "label": c.label,
            "size": c.size,
            "date_min": member_dates[0] if member_dates else "",
            "date_max": member_dates[-1] if member_dates else "",
            "member_dates": member_dates,
            "summary": cluster_summaries.get(c.cluster_id, ""),
            "representative_texts": c.representative_texts,
            "related": [
                {"id": rel.cluster_id, "label": rel.label, "similarity": round(sim, 3)}
                for rel, sim in related_map.get(c.cluster_id, [])[:5]
            ],
            "sub_clusters": subs,
        })

    super_viz = []
    for sc in super_clusters:
        # Compute date range from member clusters
        sc_dates = []
        for cid in sc["member_ids"]:
            cv = next((cv for cv in clusters_viz if cv["cluster_id"] == cid), None)
            if cv and cv["date_min"]:
                sc_dates.append(cv["date_min"])
            if cv and cv["date_max"]:
                sc_dates.append(cv["date_max"])
        sc_dates.sort()
        super_viz.append({
            "super_id": sc["super_id"],
            "label": sc["label"],
            "member_ids": sc["member_ids"],
            "total_size": sc.get("total_size", 0),
            "summary": super_summaries.get(sc["super_id"], ""),
            "date_min": sc_dates[0] if sc_dates else "",
            "date_max": sc_dates[-1] if sc_dates else "",
        })

    condensed_json = {
        "generated": datetime.now().isoformat(),
        "model": config.CONDENSE_MODEL,
        "clusters": clusters_viz,
        "super_clusters": super_viz,
        "edges": edges,
        "stats": {
            "total_clusters": len(clusters),
            "total_super_clusters": len(super_clusters),
            "total_edges": len(edges),
            "edge_threshold": config.CONDENSE_EDGE_THRESHOLD,
        },
    }
    condensed_path = config.OUTPUT_DIR / "condensed.json"
    condensed_path.write_text(json.dumps(condensed_json, indent=2, ensure_ascii=False), encoding="utf-8")

    # ── 9. Save condensed HTML ──
    write_condensed_visualization(condensed_json, on_status=on_status)

    return condensed_json
