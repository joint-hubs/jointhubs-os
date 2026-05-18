"""MCP server exposing ThoughtMap to Copilot agents via the Docker container's HTTP API.

No local ChromaDB dependency — all queries go through the always-running
ThoughtMap Docker container at http://localhost:8585.

Usage (stdio):
    python infra/mcp-chromadb/server.py

Environment variables:
    THOUGHTMAP_API_URL     — ThoughtMap container API base URL
                             Default: http://localhost:8585
    THOUGHTMAP_CLUSTERS    — Path to clusters.json (for cluster_distances/text_distance)
                             Default: Second Brain/Operations/thoughtmap-out/clusters.json
    OLLAMA_BASE_URL        — Ollama API base URL (for embeddings in cluster_distances)
                             Default: http://localhost:11434
    OLLAMA_EMBEDDING_MODEL — Embedding model name
                             Default: qwen3-embedding:8b
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests
from mcp.server.fastmcp import FastMCP

# ─── Resolve paths ───

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent  # infra/mcp-chromadb -> repo root

THOUGHTMAP_API_URL = os.environ.get("THOUGHTMAP_API_URL", "http://localhost:8585")

CLUSTERS_PATH = Path(os.environ.get(
    "THOUGHTMAP_CLUSTERS",
    str(_REPO_ROOT / "Second Brain" / "Operations" / "thoughtmap-out" / "clusters.json"),
))

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "qwen3-embedding:8b")

# ─── Math helpers ───

def _cosine_distance(a: list[float], b: list[float]) -> float:
    """Cosine distance between two vectors (0 = identical, 2 = opposite)."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 1.0
    return 1.0 - dot / (norm_a * norm_b)

# ─── HTTP helpers ───

def _api_get(path: str, params: dict | None = None) -> dict:
    """GET request to the ThoughtMap container API."""
    resp = requests.get(f"{THOUGHTMAP_API_URL}{path}", params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _load_clusters() -> list[dict]:
    """Load cluster data from the pipeline output."""
    if not CLUSTERS_PATH.exists():
        return []
    with open(CLUSTERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _embed_query(text: str) -> list[float]:
    """Embed a query string via Ollama (same model as the pipeline)."""
    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/embed",
        json={"model": OLLAMA_EMBEDDING_MODEL, "input": [text]},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["embeddings"][0]


def _embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed multiple texts via Ollama."""
    all_embs: list[list[float]] = []
    for text in texts:
        all_embs.append(_embed_query(text))
    return all_embs


# ─── Cluster centroid cache ───

_cluster_centroids: dict[int, list[float]] | None = None


def _get_cluster_centroids() -> dict[int, list[float]]:
    """Compute HD centroids for all clusters by averaging representative text embeddings.

    Cached after first call. Uses representative_texts from clusters.json.
    """
    global _cluster_centroids
    if _cluster_centroids is not None:
        return _cluster_centroids

    clusters = _load_clusters()
    if not clusters:
        return {}

    _cluster_centroids = {}
    for c in clusters:
        reps = c.get("representative_texts", [])
        if not reps:
            continue
        # Truncate to 500 chars each to keep embedding fast
        reps_trimmed = [t[:500] for t in reps]
        embs = _embed_batch(reps_trimmed)
        # Average to get centroid
        dim = len(embs[0])
        centroid = [0.0] * dim
        for emb in embs:
            for j in range(dim):
                centroid[j] += emb[j]
        n = len(embs)
        centroid = [v / n for v in centroid]
        _cluster_centroids[c["cluster_id"]] = centroid

    return _cluster_centroids


# ─── MCP server ───

mcp = FastMCP(
    "ThoughtMap",
    instructions=(
        "Semantic search over the user's personal knowledge base — notes, "
        "journal entries, project docs, and voice transcripts. Use "
        "search_thoughts for finding relevant context. Use list_clusters "
        "and get_cluster to explore discovered topic groups."
    ),
)


@mcp.tool()
def search_thoughts(query: str, n_results: int = 10) -> list[dict]:
    """Search the user's personal knowledge base by semantic similarity.

    Returns the most relevant text chunks from notes, journal entries,
    project documents, and voice transcripts.

    Args:
        query: Natural language search query (e.g., "project blockers",
               "investment thesis", "health goals")
        n_results: Number of results to return (default 10, max 50)
    """
    n_results = min(max(1, n_results), 50)

    try:
        data = _api_get("/api/search", params={"q": query, "n": str(n_results)})
    except requests.ConnectionError:
        return [{"error": "ThoughtMap container not running. Start it with: docker compose up -d (in Second Brain/Projects/thoughtmap/)"}]
    except Exception as e:
        return [{"error": f"ThoughtMap API error: {e}"}]

    if "error" in data:
        return [{"error": data["error"]}]

    return data.get("results", [])


@mcp.tool()
def list_clusters(domain: str | None = None) -> list[dict]:
    """List all discovered thought clusters from the knowledge base.

    Each cluster is a group of semantically related notes/thoughts
    discovered by the ThoughtMap pipeline.

    Args:
        domain: Optional — filter by domain keyword (e.g., "fenix", "health").
                Case-insensitive partial match on the cluster label.
    """
    try:
        params = {}
        if domain:
            params["domain"] = domain
        data = _api_get("/api/clusters", params=params)
    except requests.ConnectionError:
        return [{"error": "ThoughtMap container not running."}]
    except Exception as e:
        return [{"error": f"ThoughtMap API error: {e}"}]

    if "error" in data:
        return [{"error": data["error"]}]

    return data.get("clusters", [])


@mcp.tool()
def get_cluster(cluster_id: int) -> dict:
    """Get details of a specific thought cluster including representative texts.

    Args:
        cluster_id: The cluster ID from list_clusters
    """
    try:
        data = _api_get(f"/api/clusters/{cluster_id}")
    except requests.ConnectionError:
        return {"error": "ThoughtMap container not running."}
    except Exception as e:
        return {"error": f"ThoughtMap API error: {e}"}

    return data


@mcp.tool()
def cluster_distances(cluster_id: int, top_n: int = 10) -> dict:
    """Compute cosine distances from one cluster to all others.

    Returns the nearest and farthest clusters, useful for understanding
    how topics relate to each other in the knowledge base.

    Args:
        cluster_id: The cluster to measure from (use list_clusters to find IDs)
        top_n: Number of nearest and farthest clusters to return (default 10)
    """
    top_n = min(max(1, top_n), 50)
    clusters = _load_clusters()
    if not clusters:
        return {"error": "No clusters found. Run the ThoughtMap pipeline first."}

    # Verify cluster exists
    target = None
    for c in clusters:
        if c["cluster_id"] == cluster_id:
            target = c
            break
    if target is None:
        return {"error": f"Cluster {cluster_id} not found."}

    try:
        centroids = _get_cluster_centroids()
    except Exception as e:
        return {"error": f"Failed to compute centroids (is Ollama running?): {e}"}

    if cluster_id not in centroids:
        return {"error": f"No centroid for cluster {cluster_id} (no representative texts)."}

    ref = centroids[cluster_id]
    id_to_label = {c["cluster_id"]: c.get("label", "") for c in clusters}
    id_to_size = {c["cluster_id"]: c["size"] for c in clusters}

    distances = []
    for cid, centroid in centroids.items():
        if cid == cluster_id:
            continue
        dist = _cosine_distance(ref, centroid)
        distances.append({
            "cluster_id": cid,
            "label": id_to_label.get(cid, ""),
            "size": id_to_size.get(cid, 0),
            "distance": round(dist, 4),
        })

    distances.sort(key=lambda x: x["distance"])

    return {
        "from_cluster": {
            "cluster_id": cluster_id,
            "label": target.get("label", ""),
            "size": target["size"],
        },
        "nearest": distances[:top_n],
        "farthest": list(reversed(distances[-top_n:])),
    }


@mcp.tool()
def text_distance(text_a: str, text_b: str) -> dict:
    """Compute semantic distance between two pieces of text.

    Embeds both texts using the same model as the knowledge base and
    returns their cosine distance (0 = identical meaning, ~1 = unrelated).

    Args:
        text_a: First text to compare
        text_b: Second text to compare
    """
    try:
        emb_a = _embed_query(text_a)
        emb_b = _embed_query(text_b)
    except Exception as e:
        return {"error": f"Embedding failed (is Ollama running?): {e}"}

    dist = _cosine_distance(emb_a, emb_b)
    return {
        "distance": round(dist, 4),
        "similarity": round(1.0 - dist, 4),
        "text_a_preview": text_a[:100],
        "text_b_preview": text_b[:100],
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
