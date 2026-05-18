from thoughtmap.analysis.storage_tiers import build_active_manifest, build_prune_plan, semantic_record_id
from thoughtmap.core.models import RoutingDecision, ThoughtAtom


def make_atom(atom_id: str, quality: str = "usable", signal_type: str = "thought") -> ThoughtAtom:
    return ThoughtAtom(
        atom_id=atom_id,
        parent_segment_id="segment-1",
        text=f"text for {atom_id}",
        title=f"title {atom_id}",
        signal_type=signal_type,
        domains=[],
        index_targets=["needs_review"],
        quality=quality,
        confidence=0.9,
        source="obsidian-daily",
        source_file="Second Brain/Operations/Periodic Notes/Daily/2026-04-28.md",
        section="logs",
        timestamp="2026-04-28T10:00:00",
        raw_text=f"raw {atom_id}",
    )


def make_decision(atom_id: str, targets: list[str]) -> RoutingDecision:
    return RoutingDecision(
        atom_id=atom_id,
        index_targets=targets,
        suggested_target=targets[0] if targets else None,
        confidence=0.9,
        reason="test",
    )


def test_active_manifest_keeps_only_semantic_records() -> None:
    atoms = [make_atom("a1"), make_atom("a2", signal_type="task")]
    decisions = [make_decision("a1", ["semantic"]), make_decision("a2", ["activity"])]

    manifest = build_active_manifest(atoms, decisions)

    assert manifest["counts"]["active_semantic"] == 1
    assert manifest["active_records"][0]["record_id"] == semantic_record_id(atoms[0])
    assert manifest["counts"]["cold_or_review_only"] == 1


def test_prune_plan_reports_stale_and_missing_records() -> None:
    atoms = [make_atom("a1"), make_atom("a2")]
    decisions = [make_decision("a1", ["semantic"]), make_decision("a2", ["semantic"])]
    manifest = build_active_manifest(atoms, decisions)

    plan = build_prune_plan(manifest, [semantic_record_id(atoms[0]), "legacy:chunk-1"])

    assert semantic_record_id(atoms[1]) in plan["missing_from_store"]
    assert "legacy:chunk-1" in plan["stale_in_store"]