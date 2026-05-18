"""Human-facing curation surfaces backed by the durable entity registry."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import thoughtmap.config as config
from thoughtmap.core.models import RoutingDecision, ThoughtAtom


def render_entity_curation_board(registry: dict) -> str:
    """Render the current entity registry as a markdown curation board."""
    entities = registry.get("entities", {}) or {}
    decisions = registry.get("decisions", {}) or {}

    lines = [
        "---",
        "type: thoughtmap-entity-curation",
        "status: active",
        "generated: true",
        "---",
        "",
        "# ThoughtMap Entity Curation",
        "",
        "This board reflects durable manual truth from entity_registry.json.",
        "This file is currently a readable mirror, not the primary editing surface.",
        "For now, record manual entity decisions in `data/curation/entity_registry.json` or through a dedicated workflow.",
        "",
        "## Verified Entities",
    ]

    if not entities:
        lines.append("- No verified entities yet.")
    else:
        for entity_id, entity in sorted(entities.items(), key=lambda item: str(item[1].get("canonical_name", "")).lower()):
            canonical_name = str(entity.get("canonical_name", entity_id))
            entity_type = str(entity.get("type", "unknown"))
            aliases = ", ".join(entity.get("aliases", [])) or "-"
            lines.append(f"- {canonical_name} [{entity_type}]")
            lines.append(f"  entity_id: {entity_id}")
            lines.append(f"  aliases: {aliases}")

    lines.extend(["", "## Manual Decisions"])
    if not decisions:
        lines.append("- No manual decisions yet.")
    else:
        for candidate_key, decision in sorted(decisions.items(), key=lambda item: item[0]):
            action = str(decision.get("action", "unknown"))
            target = str(decision.get("target_entity_id", "-"))
            reason = str(decision.get("reason", ""))
            lines.append(f"- {candidate_key}: {action} -> {target}")
            if reason:
                lines.append(f"  reason: {reason}")

    return "\n".join(lines) + "\n"


def write_entity_curation_board(registry: dict, path: Path | None = None) -> Path:
    """Write the entity curation board to the configured Obsidian path."""
    board_path = path or config.ENTITY_CURATION_BOARD_PATH
    board_path.parent.mkdir(parents=True, exist_ok=True)
    board_path.write_text(render_entity_curation_board(registry), encoding="utf-8")
    return board_path


def render_segment_curation_board(atoms: list[ThoughtAtom], decisions: list[RoutingDecision]) -> str:
    """Render a review-first board for uncertain or non-semantic atoms."""
    decision_by_atom = {decision.atom_id: decision for decision in decisions}
    lines = [
        "---",
        "type: thoughtmap-segment-curation",
        "status: active",
        "generated: true",
        "---",
        "",
        "# ThoughtMap Segment Curation",
        "",
        "This is a diagnostic review surface for the ThoughtAtom prototype.",
        "It is not meant for reviewing thousands of cards by hand.",
        "",
        "## How To Use",
        "- Look for patterns, not individual perfection: repeated timestamps, dataview output, JSON blobs, headings, or one-word fragments.",
        "- If many cards of the same kind are wrong, fix the splitter/classifier rules instead of moving cards manually.",
        "- Manual moves in this file are not yet consumed by the pipeline. Durable curation sync is a later phase.",
        "- Use `atom_id` only when you need to report a concrete example to the developer.",
        "",
        "## Needs Review",
    ]

    review_atoms = [
        atom for atom in atoms
        if "needs_review" in decision_by_atom.get(atom.atom_id, RoutingDecision(atom.atom_id, [], None, 0.0, "")).index_targets
    ]
    if not review_atoms:
        lines.append("- No uncertain atoms in the current prototype run.")
    else:
        for atom in review_atoms[:200]:
            decision = decision_by_atom[atom.atom_id]
            lines.append(f"- [{atom.signal_type}] {atom.title}")
            lines.append(f"  atom_id: {atom.atom_id}")
            lines.append(f"  source: {atom.source}")
            lines.append(f"  confidence: {decision.confidence:.2f}")
            lines.append(f"  quality: {atom.quality}")
            lines.append(f"  suggested_target: {decision.suggested_target or '-'}")
            preview = " ".join((atom.text or "").split())[:240]
            if preview:
                lines.append(f"  preview: {preview}")

    lines.extend([
        "",
        "## What To Fix In Code",
        "- If this board contains many bare timestamps, make `_infer_quality` classify them as boilerplate/discard.",
        "- If this board contains dataview or generated file-list text, improve markdown cleanup/exclusions before atomization.",
        "- If this board contains huge JSON blobs, route them away from `semantic` and consider source exclusion.",
    ])

    return "\n".join(lines) + "\n"


def write_segment_curation_board(atoms: list[ThoughtAtom], decisions: list[RoutingDecision], path: Path | None = None) -> Path:
    board_path = path or config.SEGMENT_CURATION_BOARD_PATH
    board_path.parent.mkdir(parents=True, exist_ok=True)
    board_path.write_text(render_segment_curation_board(atoms, decisions), encoding="utf-8")
    return board_path


def render_domain_curation_board(atoms: list[ThoughtAtom]) -> str:
    """Render domain assignments and emerging labels for manual review."""
    domain_counter: Counter[str] = Counter()
    for atom in atoms:
        if atom.domains:
            for domain in atom.domains:
                domain_counter[domain.id] += 1
        else:
            domain_counter["unassigned"] += 1

    lines = [
        "---",
        "type: thoughtmap-domain-curation",
        "status: active",
        "generated: true",
        "---",
        "",
        "# ThoughtMap Domain Curation",
        "",
        "Current domain assignments from the latest prototype run.",
        "",
        "## Domain Counts",
    ]
    for domain_id, count in sorted(domain_counter.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- {domain_id}: {count}")
    return "\n".join(lines) + "\n"


def write_domain_curation_board(atoms: list[ThoughtAtom], path: Path | None = None) -> Path:
    board_path = path or config.DOMAIN_CURATION_BOARD_PATH
    board_path.parent.mkdir(parents=True, exist_ok=True)
    board_path.write_text(render_domain_curation_board(atoms), encoding="utf-8")
    return board_path