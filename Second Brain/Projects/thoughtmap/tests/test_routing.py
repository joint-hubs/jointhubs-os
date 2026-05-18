from thoughtmap.analysis.routing import route_atom_to_indexes
from thoughtmap.core.models import ThoughtAtom


def make_atom(signal_type: str, quality: str, confidence: float, suggested_target: str | None = None) -> ThoughtAtom:
    return ThoughtAtom(
        atom_id=f"atom-{signal_type}-{quality}-{confidence}",
        parent_segment_id="segment-1",
        text="Example text",
        title="Example title",
        signal_type=signal_type,
        domains=[],
        index_targets=["needs_review"],
        quality=quality,
        confidence=confidence,
        source="obsidian-daily",
        source_file="Second Brain/Operations/Periodic Notes/Daily/2026-04-28.md",
        section="logs",
        timestamp="2026-04-28T10:00:00",
        suggested_target=suggested_target,
    )


def test_boilerplate_routes_to_discard() -> None:
    decision = route_atom_to_indexes(make_atom("generated_output", "boilerplate", 0.95, "discard"))
    assert decision.index_targets == ["discard"]


def test_communication_routes_to_communication() -> None:
    decision = route_atom_to_indexes(make_atom("communication", "usable", 0.87, "communication"))
    assert decision.index_targets == ["communication"]


def test_project_decision_routes_to_project_and_semantic() -> None:
    decision = route_atom_to_indexes(make_atom("decision", "usable", 0.86, "project"))
    assert decision.index_targets == ["project", "semantic"]


def test_task_routes_to_activity() -> None:
    decision = route_atom_to_indexes(make_atom("task", "usable", 0.91, "activity"))
    assert decision.index_targets == ["activity"]


def test_low_confidence_routes_to_needs_review() -> None:
    decision = route_atom_to_indexes(make_atom("thought", "usable", 0.72, "semantic"))
    assert decision.index_targets == ["needs_review"]