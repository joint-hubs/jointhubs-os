"""Hot/cold storage planning for ThoughtMap semantic store migration."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import thoughtmap.config as config
from thoughtmap.core.models import RoutingDecision, ThoughtAtom


def semantic_record_id(atom: ThoughtAtom) -> str:
    """Stable active-store record ID for semantic atom embeddings."""
    return f"atom:{atom.atom_id}"


def build_active_manifest(atoms: list[ThoughtAtom], decisions: list[RoutingDecision]) -> dict:
    """Build the active semantic manifest from dry-run routing decisions."""
    decisions_by_atom = {decision.atom_id: decision for decision in decisions}
    active_records = []
    cold_records = []

    for atom in atoms:
        decision = decisions_by_atom.get(atom.atom_id)
        if decision is None:
            continue

        record = {
            "record_id": semantic_record_id(atom),
            "atom_id": atom.atom_id,
            "parent_segment_id": atom.parent_segment_id,
            "source": atom.source,
            "source_file": atom.source_file,
            "section": atom.section,
            "timestamp": atom.timestamp,
            "signal_type": atom.signal_type,
            "quality": atom.quality,
            "confidence": atom.confidence,
            "index_targets": decision.index_targets,
            "suggested_target": decision.suggested_target,
            "text": atom.text,
            "raw_text": atom.raw_text,
        }

        if "semantic" in decision.index_targets:
            active_records.append(record)
        else:
            cold_records.append(record)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "active_records": active_records,
        "cold_records": cold_records,
        "counts": {
            "active_semantic": len(active_records),
            "cold_or_review_only": len(cold_records),
        },
    }


def build_prune_plan(manifest: dict, current_store_ids: list[str]) -> dict:
    """Compute a dry-run prune plan by comparing active records to current store IDs."""
    active_ids = {record["record_id"] for record in manifest.get("active_records", [])}
    current_ids = set(current_store_ids)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "active_manifest_count": len(active_ids),
        "current_store_count": len(current_ids),
        "missing_from_store": sorted(active_ids - current_ids),
        "stale_in_store": sorted(current_ids - active_ids),
        "kept_in_store": sorted(active_ids & current_ids),
    }


def write_manifest(manifest: dict, path: Path | None = None) -> Path:
    """Persist the active manifest JSON to the output directory."""
    manifest_path = path or (config.OUTPUT_DIR / "prototypes" / "thought_atom_manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest_path


def write_prune_plan(plan: dict, path: Path | None = None) -> Path:
    """Persist the Chroma prune dry-run report JSON."""
    plan_path = path or (config.OUTPUT_DIR / "prototypes" / "chroma_prune_plan.json")
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    return plan_path