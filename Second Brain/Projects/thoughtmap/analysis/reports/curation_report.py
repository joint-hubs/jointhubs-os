"""Curation report for ThoughtMap v2 manual-truth surfaces."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import thoughtmap.config as config
from thoughtmap.core.models import RoutingDecision, ThoughtAtom


def render_curation_report(atoms: list[ThoughtAtom], decisions: list[RoutingDecision], registry: dict) -> str:
    decision_counter = Counter(target for decision in decisions for target in decision.index_targets)
    quality_counter = Counter(atom.quality for atom in atoms)
    entities = registry.get("entities", {}) or {}
    manual_decisions = registry.get("decisions", {}) or {}

    lines = [
        "# ThoughtMap Curation Report",
        "",
        f"- Thought atoms reviewed: {len(atoms)}",
        f"- Durable registry entities: {len(entities)}",
        f"- Durable registry decisions: {len(manual_decisions)}",
        "",
        "## Routing Counts",
    ]
    for target, count in sorted(decision_counter.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- {target}: {count}")

    lines.extend(["", "## Quality Counts"])
    for quality, count in sorted(quality_counter.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- {quality}: {count}")

    lines.extend([
        "",
        "## Surfaces",
        f"- Entity board: {config.ENTITY_CURATION_BOARD_PATH.as_posix()}",
        f"- Segment board: {config.SEGMENT_CURATION_BOARD_PATH.as_posix()}",
        f"- Domain board: {config.DOMAIN_CURATION_BOARD_PATH.as_posix()}",
        f"- Registry: {config.ENTITY_REGISTRY_PATH.as_posix()}",
    ])
    return "\n".join(lines) + "\n"


def write_curation_report(atoms: list[ThoughtAtom], decisions: list[RoutingDecision], registry: dict, path: Path | None = None) -> Path:
    report_path = path or config.CURATION_REPORT_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_curation_report(atoms, decisions, registry), encoding="utf-8")
    return report_path