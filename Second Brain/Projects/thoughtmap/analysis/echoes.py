"""Echoes — near-duplicate thought groups.

Finds groups of thoughts whose pairwise cosine similarity is above a
threshold (default 0.95). These are "echoes" — the same thought said
multiple ways, often across days, sources, or after rewording.

Goal: surface repeating ideas so they can be catalogued as
  - observe   → worth watching, a recurring signal
  - discard   → noise, filler, not interesting
  - neutral   → no opinion yet (default)
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Iterable

import numpy as np

import thoughtmap.config as config


ECHO_DEFAULT_THRESHOLD = 0.95
ECHO_MIN_GROUP_SIZE = 3  # pipeline computes down to 3; UI filters higher
CATALOG_FILE = config.DATA_DIR / "echo_catalog.json"


# ─── Helpers ───

def _normalize(embeddings: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1e-10, norms)
    return embeddings / norms


def echo_key(chunk_ids: Iterable[str]) -> str:
    """Stable identifier for a group, invariant to member order.

    Uses sorted chunk IDs so that reruns produce the same key as long as the
    same set of chunks ends up in the same group.
    """
    payload = "\n".join(sorted(chunk_ids))
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


# ─── Core grouping ───

def _union_find_groups(
    similarities: np.ndarray,
    threshold: float,
) -> list[list[int]]:
    """Group indices into connected components where sim[i,j] >= threshold."""
    n = similarities.shape[0]
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    # Upper triangle: i < j
    ij = np.argwhere(np.triu(similarities >= threshold, k=1))
    for i, j in ij:
        union(int(i), int(j))

    groups: dict[int, list[int]] = {}
    for i in range(n):
        root = find(i)
        groups.setdefault(root, []).append(i)
    return list(groups.values())


def compute_echoes(
    items: list[dict],
    embeddings: list[list[float]] | np.ndarray,
    threshold: float = ECHO_DEFAULT_THRESHOLD,
    min_group_size: int = ECHO_MIN_GROUP_SIZE,
) -> list[dict]:
    """Compute near-duplicate groups across ALL thoughts.

    Returns a list of groups (largest first), each with:
      - echo_key: stable hash of sorted chunk IDs
      - size: number of members
      - avg_similarity, min_similarity: within-group cosine stats
      - representative_text: member closest to the group centroid
      - member_indices: positions within `items`
      - member_chunk_ids: chunk IDs (stable across runs)
      - examples: up to 5 short text previews
      - date_min / date_max: timestamp span
      - sources: unique source tags present in the group
    """
    if len(items) < min_group_size or len(items) != len(embeddings):
        return []

    arr = np.asarray(embeddings, dtype=np.float32)
    normed = _normalize(arr)

    # Full similarity matrix — fine up to ~10k items (100M floats = 400MB).
    # For larger corpora this should be chunked; guard here and early-return.
    if normed.shape[0] > 12000:
        # Safety guard — skip to avoid OOM on huge corpora
        return []

    sim = normed @ normed.T
    groups_idx = _union_find_groups(sim, threshold)

    results: list[dict] = []
    for member_indices in groups_idx:
        if len(member_indices) < min_group_size:
            continue

        member_indices_sorted = sorted(member_indices)
        group_embs = normed[member_indices_sorted]
        centroid = group_embs.mean(axis=0)
        centroid /= max(np.linalg.norm(centroid), 1e-10)
        dists = 1.0 - (group_embs @ centroid)
        rep_local = int(np.argmin(dists))
        rep_global = member_indices_sorted[rep_local]

        # Within-group similarity stats (upper triangle only)
        sub_sim = sim[np.ix_(member_indices_sorted, member_indices_sorted)]
        n = len(member_indices_sorted)
        iu = np.triu_indices(n, k=1)
        pair_sims = sub_sim[iu] if n > 1 else np.array([1.0])
        avg_sim = float(pair_sims.mean()) if pair_sims.size else 1.0
        min_sim = float(pair_sims.min()) if pair_sims.size else 1.0

        # Collect member metadata
        member_chunk_ids: list[str] = []
        timestamps: list[str] = []
        sources: set[str] = set()
        source_files: set[str] = set()
        examples: list[dict] = []
        for gi in member_indices_sorted:
            it = items[gi]
            cid = it.get("id") or it.get("chunk_id") or ""
            if cid:
                member_chunk_ids.append(cid)
            ts = it.get("timestamp")
            if ts:
                timestamps.append(str(ts))
            src = it.get("source")
            if src:
                sources.add(str(src))
            sf = it.get("source_file")
            if sf:
                source_files.add(str(sf))
            if len(examples) < 5:
                text = (it.get("text") or "").strip().replace("\n", " ")
                examples.append({
                    "idx": gi,
                    "text": text[:220],
                    "timestamp": ts,
                    "source": src,
                    "source_file": sf,
                })

        key = echo_key(member_chunk_ids) if member_chunk_ids else f"idx-{rep_global}"
        rep_text = (items[rep_global].get("text") or "").strip().replace("\n", " ")

        results.append({
            "echo_key": key,
            "size": len(member_indices_sorted),
            "avg_similarity": round(avg_sim, 4),
            "min_similarity": round(min_sim, 4),
            "threshold": round(float(threshold), 4),
            "representative_text": rep_text[:280],
            "representative_idx": rep_global,
            "member_indices": member_indices_sorted,
            "member_chunk_ids": member_chunk_ids,
            "examples": examples,
            "date_min": min(timestamps) if timestamps else None,
            "date_max": max(timestamps) if timestamps else None,
            "sources": sorted(sources),
            "source_files": sorted(source_files),
        })

    # Largest first, then most-similar first
    results.sort(key=lambda g: (-g["size"], -g["avg_similarity"]))
    return results


def save_echoes(
    echoes: list[dict],
    threshold: float,
    min_group_size: int,
) -> Path:
    """Write echoes.json to OUTPUT_DIR."""
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = config.OUTPUT_DIR / "echoes.json"
    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "threshold": threshold,
        "min_group_size": min_group_size,
        "count": len(echoes),
        "echoes": echoes,
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


# ─── Catalog state ───

def load_catalog() -> dict:
    """Load per-group catalog state. Keyed by echo_key."""
    if not CATALOG_FILE.exists():
        return {}
    try:
        return json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_catalog(catalog: dict) -> None:
    CATALOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_FILE.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def set_catalog_entry(
    key: str,
    status: str = "neutral",
    note: str | None = None,
) -> dict:
    """Update catalog entry for a group. Status: observe | discard | neutral."""
    if status not in {"observe", "discard", "neutral"}:
        raise ValueError(f"invalid status: {status}")
    catalog = load_catalog()
    entry = catalog.get(key, {})
    entry["status"] = status
    if note is not None:
        entry["note"] = note
    entry["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    catalog[key] = entry
    save_catalog(catalog)
    return entry
