"""Generate domain-grouped index notes from ThoughtMap clusters.

Instead of one file per cluster (hundreds of noisy files), groups clusters
by domain (project, topic area) and generates one rich note per domain
plus a master _index.md.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

import thoughtmap.config as config
from thoughtmap.core.cluster import ClusterInfo, ThoughtMapResult

# ─── Output directory ───

INDEX_DIR = config.OUTPUT_DIR / "clusters"

# ─── Domain classification ───

DOMAIN_RULES: list[tuple[str, str, str]] = [
    # (path_contains, domain_key, display_name)
    ("Projects/fenix", "fenix", "Fenix"),
    ("Projects/neurohubs", "neurohubs", "Neurohubs"),
    ("Projects/jointhubs", "jointhubs", "Jointhubs"),
    ("Projects/avatar", "avatar", "Avatar"),
    ("Projects/office_ai", "office-ai", "Office AI"),
    ("Projects/home-finance", "home-finance", "Home Finance"),
    ("Projects/thoughtmap", "thoughtmap", "ThoughtMap"),
    ("Projects/Global", "global", "Global Work"),
    ("Personal/Health", "health", "Health"),
    ("Personal/Finances/stocks", "stocks", "Stocks"),
    ("Personal/Finances", "finance", "Finance"),
    ("Personal/Events", "events", "Events"),
    ("Personal/daily", "daily-reflections", "Daily Reflections"),
    ("Operations/Periodic", "periodic", "Periodic Notes"),
    ("Operations/Meetings", "meetings", "Meetings"),
    ("Operations/", "operations", "Operations"),
    ("wispr:", "voice-notes", "Voice Notes"),
]

BOILERPLATE_MARKERS = [
    "warranty", "noninfringement", "copyright holder",
    "provided as is", "without warranty", "mit license",
    "redistribute", "indemnify", "tort", "license shall",
    "archive anthropic active", "archive amazon active",
    "google zapisywanie brainstoriming",
    "software is provided", "implied warranties",
    "apache license", "bsd license", "gnu general",
]


# ─── Helpers ───

def _classify_source(source_file: str) -> tuple[str, str]:
    """Classify a source file path into (domain_key, display_name)."""
    normalized = source_file.replace("\\", "/")
    for pattern, key, name in DOMAIN_RULES:
        if pattern in normalized:
            return key, name
    return "misc", "Miscellaneous"


def _classify_cluster_domain(
    cluster: ClusterInfo,
    items: list[dict],
) -> tuple[str, str]:
    """Determine the dominant domain of a cluster by source file majority."""
    domain_counts: dict[str, int] = defaultdict(int)
    domain_names: dict[str, str] = {}
    for idx in cluster.member_indices:
        src = items[idx].get("source_file", "")
        key, name = _classify_source(src)
        domain_counts[key] += 1
        domain_names[key] = name
    if not domain_counts:
        return "misc", "Miscellaneous"
    dominant = max(domain_counts, key=lambda k: domain_counts[k])
    return dominant, domain_names[dominant]


def _is_boilerplate(cluster: ClusterInfo, items: list[dict]) -> bool:
    """Check if a cluster is mostly boilerplate (license, warranty, template)."""
    if cluster.size < 3:
        return True
    sample_indices = cluster.member_indices[:min(cluster.size, 10)]
    hits = 0
    for idx in sample_indices:
        text = items[idx].get("text", "").lower()
        if any(marker in text for marker in BOILERPLATE_MARKERS):
            hits += 1
    return hits / len(sample_indices) > 0.5


def _extract_timestamps(cluster: ClusterInfo, items: list[dict]) -> list[str]:
    """Extract sorted YYYY-MM-DD timestamps from a cluster."""
    timestamps = []
    for idx in cluster.member_indices:
        ts = items[idx].get("timestamp", "")
        if ts and len(ts) >= 10:
            timestamps.append(ts[:10])
    return sorted(timestamps)


def _compute_trend(timestamps: list[str]) -> str:
    """Compute trend: ↗ growing / → stable / ↘ fading."""
    if len(timestamps) < 4:
        return "→"
    months: dict[str, int] = defaultdict(int)
    for ts in timestamps:
        months[ts[:7]] += 1
    sorted_months = sorted(months.keys())
    if len(sorted_months) < 2:
        return "→"
    mid = len(sorted_months) // 2
    earlier = sum(months[m] for m in sorted_months[:mid])
    later = sum(months[m] for m in sorted_months[mid:])
    if later > earlier * 1.5:
        return "↗"
    elif earlier > later * 1.5:
        return "↘"
    return "→"


def _build_timeline(timestamps: list[str], width: int = 10) -> list[str]:
    """Build ASCII timeline bars by month."""
    if not timestamps:
        return []
    months: dict[str, int] = defaultdict(int)
    for ts in timestamps:
        if len(ts) >= 7:
            months[ts[:7]] += 1
    if not months:
        return []
    sorted_months = sorted(months.keys())
    max_count = max(months.values())
    lines = []
    for month in sorted_months:
        count = months[month]
        bar_len = max(1, round(count / max_count * width))
        bar = "█" * bar_len + "░" * (width - bar_len)
        lines.append(f"{month} {bar} {count}")
    return lines


def _get_centroid_quote(
    cluster: ClusterInfo,
    items: list[dict],
    embeddings_hd: np.ndarray,
) -> dict:
    """Get the single most representative quote (nearest to centroid)."""
    member_embs = embeddings_hd[cluster.member_indices]
    centroid = member_embs.mean(axis=0)
    dists = np.linalg.norm(member_embs - centroid, axis=1)
    center_local = int(np.argmin(dists))
    center_global = cluster.member_indices[center_local]
    item = items[center_global]
    return {
        "text": item.get("text", ""),
        "source_file": item.get("source_file", ""),
        "timestamp": item.get("timestamp", ""),
    }


def _top_source_notes(
    cluster: ClusterInfo,
    items: list[dict],
    max_notes: int = 5,
) -> list[str]:
    """Get top source file wikilinks by chunk count."""
    counts: dict[str, int] = defaultdict(int)
    for idx in cluster.member_indices:
        src = items[idx].get("source_file", "")
        if src:
            counts[src] += 1
    ranked = sorted(counts.items(), key=lambda x: -x[1])[:max_notes]
    return [_to_wikilink(src) for src, _ in ranked]


def _to_wikilink(source_file: str) -> str:
    """Convert a source file path to an Obsidian wikilink."""
    if source_file.startswith("wispr:"):
        return f"`{source_file}`"
    p = Path(source_file)
    return f"[[{p.stem}]]"


def _format_quote(text: str, max_len: int = 250) -> str:
    """Format a quote for display, truncating if needed."""
    clean = text.replace("\n", " ").strip()
    if len(clean) > max_len:
        clean = clean[:max_len].rsplit(" ", 1)[0] + "..."
    return clean


# ─── Domain note generation ───

def _generate_domain_note(
    domain_key: str,
    display_name: str,
    clusters: list[ClusterInfo],
    items: list[dict],
    embeddings_hd: np.ndarray,
    all_domain_keys: list[str],
) -> str:
    """Generate a rich markdown note for one domain with all its clusters."""
    # Aggregate stats
    total_chunks = sum(c.size for c in clusters)
    all_timestamps: list[str] = []
    for c in clusters:
        all_timestamps.extend(_extract_timestamps(c, items))
    all_timestamps.sort()

    period = ""
    if all_timestamps:
        period = f"{all_timestamps[0][:7]} — {all_timestamps[-1][:7]}"
    trend = _compute_trend(all_timestamps)

    # Sort clusters by size descending
    clusters_sorted = sorted(clusters, key=lambda c: c.size, reverse=True)

    lines: list[str] = []

    # Frontmatter
    lines.append("---")
    lines.append(f"domain: {domain_key}")
    lines.append(f"clusters: {len(clusters)}")
    lines.append(f"chunks: {total_chunks}")
    lines.append("type: thoughtmap-domain")
    lines.append("generated: true")
    lines.append(f"tags: [type/thoughtmap-domain, thoughtmap, {domain_key}]")
    lines.append("---")
    lines.append("")

    # Title
    lines.append(f"# {display_name}")
    lines.append("")
    trend_label = {"↗": "growing", "↘": "fading", "→": "stable"}[trend]
    lines.append(
        f"> **{len(clusters)}** clusters · **{total_chunks}** thoughts"
        f" · {period} · {trend} {trend_label}"
    )
    lines.append("")

    # Timeline
    timeline = _build_timeline(all_timestamps)
    if timeline:
        lines.append("## Timeline")
        lines.append("")
        lines.append("```")
        for tl in timeline:
            lines.append(tl)
        lines.append("```")
        lines.append("")

    # Clusters
    lines.append("## Clusters")
    lines.append("")

    for cluster in clusters_sorted:
        quote = _get_centroid_quote(cluster, items, embeddings_hd)
        ts_list = _extract_timestamps(cluster, items)
        c_trend = _compute_trend(ts_list)
        sources = _top_source_notes(cluster, items, max_notes=4)

        lines.append(f"### {cluster.label} ({cluster.size} thoughts) {c_trend}")
        lines.append("")
        quote_text = _format_quote(quote["text"])
        lines.append(f"> {quote_text}")
        ts_display = quote["timestamp"][:10] if quote["timestamp"] else ""
        src_link = _to_wikilink(quote["source_file"]) if quote["source_file"] else ""
        if ts_display or src_link:
            lines.append(f"> — {src_link} · {ts_display}")
        lines.append("")
        if sources:
            lines.append(f"**Sources**: {', '.join(sources)}")
            lines.append("")

    # Related domains
    other_domains = [k for k in all_domain_keys if k != domain_key]
    if other_domains:
        lines.append("## Related Domains")
        lines.append("")
        for dk in other_domains[:8]:
            lines.append(f"- [[{dk}]]")
        lines.append("")

    return "\n".join(lines)


# ─── Master index ───

def _generate_master_index(
    domain_summaries: list[dict],
    result: ThoughtMapResult,
    boilerplate_count: int,
) -> str:
    """Generate the _index.md master overview."""
    total_chunks = sum(d["chunk_count"] for d in domain_summaries)
    total_clusters = sum(d["cluster_count"] for d in domain_summaries)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines: list[str] = []
    lines.append("---")
    lines.append("type: thoughtmap-index")
    lines.append("generated: true")
    lines.append("tags: [type/thoughtmap-index, thoughtmap]")
    lines.append("---")
    lines.append("")
    lines.append("# ThoughtMap Index")
    lines.append("")
    lines.append(
        f"> **{total_chunks}** thoughts → **{total_clusters}** meaningful clusters"
        f" across **{len(domain_summaries)}** domains"
    )
    lines.append(f"> Last run: {now} · Filtered: {boilerplate_count} boilerplate clusters")
    lines.append("")

    # Domain table
    lines.append("## Domains")
    lines.append("")
    lines.append("| Domain | Clusters | Thoughts | Trend | Period |")
    lines.append("|--------|----------|----------|-------|--------|")
    for d in domain_summaries:
        link = f"[[{d['key']}|{d['name']}]]"
        lines.append(
            f"| {link} | {d['cluster_count']} | {d['chunk_count']}"
            f" | {d['trend']} | {d['period']} |"
        )
    lines.append("")

    # God Nodes
    lines.append("## God Nodes (Largest Topics)")
    lines.append("")
    for i, god in enumerate(result.god_nodes[:7], 1):
        lines.append(f"{i}. **{god.label}** ({god.size} thoughts)")
    lines.append("")

    return "\n".join(lines)


# ─── Public API ───

def generate_cluster_indices(result: ThoughtMapResult, embeddings_hd: np.ndarray) -> Path:
    """Generate domain-grouped index notes. Returns the output directory."""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    # Clean ALL previous output (cluster-*.md and domain files)
    for old in INDEX_DIR.glob("*.md"):
        old.unlink()

    # Filter boilerplate clusters
    meaningful: list[ClusterInfo] = []
    boilerplate_count = 0
    for cluster in result.clusters:
        if _is_boilerplate(cluster, result.items):
            boilerplate_count += 1
        else:
            meaningful.append(cluster)

    # Group by domain
    domain_clusters: dict[str, list[ClusterInfo]] = defaultdict(list)
    domain_names: dict[str, str] = {}
    for cluster in meaningful:
        key, name = _classify_cluster_domain(cluster, result.items)
        domain_clusters[key].append(cluster)
        domain_names[key] = name

    # Sort domains by total chunk count
    domain_order = sorted(
        domain_clusters.keys(),
        key=lambda k: sum(c.size for c in domain_clusters[k]),
        reverse=True,
    )

    # Generate per-domain notes
    domain_summaries: list[dict] = []
    for domain_key in domain_order:
        clusters = domain_clusters[domain_key]
        display_name = domain_names[domain_key]

        content = _generate_domain_note(
            domain_key, display_name, clusters,
            result.items, embeddings_hd,
            all_domain_keys=domain_order,
        )
        (INDEX_DIR / f"{domain_key}.md").write_text(content, encoding="utf-8")

        # Collect summary
        all_ts: list[str] = []
        for c in clusters:
            all_ts.extend(_extract_timestamps(c, result.items))
        all_ts.sort()
        period = f"{all_ts[0][:7]} — {all_ts[-1][:7]}" if all_ts else ""

        domain_summaries.append({
            "key": domain_key,
            "name": display_name,
            "cluster_count": len(clusters),
            "chunk_count": sum(c.size for c in clusters),
            "trend": _compute_trend(all_ts),
            "period": period,
        })

    # Generate master index
    index_content = _generate_master_index(domain_summaries, result, boilerplate_count)
    (INDEX_DIR / "_index.md").write_text(index_content, encoding="utf-8")

    return INDEX_DIR
