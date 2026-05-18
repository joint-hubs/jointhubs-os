"""Generate REPORT.md with cluster summaries, god nodes, and metrics."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import thoughtmap.config as config
from thoughtmap.core.cluster import ThoughtMapResult

if TYPE_CHECKING:
    from thoughtmap.analysis.ner import Entity


def generate_report(result: ThoughtMapResult, entities: list[Entity] | None = None) -> str:
    """Generate a markdown report from clustering results."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = len(result.items)
    n_clusters = len(result.clusters)

    # Compute source breakdown
    source_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    intent_counts: dict[str, int] = {"note": 0, "unmatched": 0}
    for item in result.items:
        src = item.get("source", "unknown")
        source_counts[src] = source_counts.get(src, 0) + 1
        cat = item.get("category")
        if cat:
            category_counts[cat] = category_counts.get(cat, 0) + 1
        if item.get("intent") == "note":
            intent_counts["note"] += 1
        elif item.get("source") == "wispr-flow":
            intent_counts["unmatched"] += 1

    lines = [
        f"# ThoughtMap Report — {now}",
        "",
        "## Summary",
        f"- **{total}** chunks · **{n_clusters}** topic clusters · **{result.noise_count}** unclustered",
        "",
        "### Sources",
        "| Source | Chunks |",
        "|--------|--------|",
    ]
    for src, count in sorted(source_counts.items()):
        lines.append(f"| {src} | {count} |")

    if category_counts:
        lines.extend([
            "",
            "### Wispr Flow Categories",
            "| Category | Chunks |",
            "|----------|--------|",
        ])
        for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            lines.append(f"| {cat} | {count} |")
        lines.append(f"| **Matched as intentional notes** | **{intent_counts['note']}** |")

    if entities:
        top_entities = []
        for entity_type, limit in [
            ("person", 3),
            ("organization", 3),
            ("project", 3),
            ("tool", 1),
            ("location", 1),
        ]:
            typed_entities = [entity for entity in entities if entity.type == entity_type]
            top_entities.extend(sorted(typed_entities, key=lambda entity: entity.mention_count, reverse=True)[:limit])
        lines.extend([
            "",
            "### Named Entities",
            f"- **{len(entities)}** entities discovered across the knowledge base",
            "",
            "| Entity | Type | Mentions | Clusters |",
            "|--------|------|----------|----------|",
        ])
        for entity in top_entities:
            lines.append(
                f"| {entity.name} | {entity.type} | {entity.mention_count} | {len(entity.cluster_ids)} |"
            )

    # God nodes
    lines.extend(["", "## God Nodes (dominant topics)", ""])
    for i, god in enumerate(result.god_nodes, 1):
        lines.append(f"### {i}. {god.label}")
        lines.append(f"- **{god.size}** chunks in this cluster")
        lines.append(f"- Representative samples:")
        for text in god.representative_texts[:3]:
            preview = text[:150].replace("\n", " ")
            lines.append(f'  - "{preview}..."')
        lines.append("")

    # All clusters
    lines.extend(["## All Clusters", ""])
    for cluster in result.clusters:
        lines.append(f"### Cluster {cluster.cluster_id} — \"{cluster.label}\"")
        lines.append(f"- Size: {cluster.size} chunks")
        lines.append(f"- Centroid 2D: ({cluster.centroid[0]:.2f}, {cluster.centroid[1]:.2f})")
        lines.append("")

    # Bridges
    if result.bridge_items:
        lines.extend(["## Bridge Thoughts", ""])
        lines.append("These chunks sit between two topic clusters — potential connections.")
        lines.append("")
        for bridge in result.bridge_items[:10]:
            preview = bridge.get("text", "")[:120].replace("\n", " ")
            between = " ↔ ".join(bridge.get("bridge_between", []))
            lines.append(f'- "{preview}..." — bridges **{between}**')
        lines.append("")

    return "\n".join(lines)


def save_report(result: ThoughtMapResult, entities: list[Entity] | None = None) -> Path:
    """Generate and save REPORT.md to thoughtmap-out."""
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report = generate_report(result, entities=entities)
    path = config.OUTPUT_DIR / "REPORT.md"
    path.write_text(report, encoding="utf-8")
    return path
