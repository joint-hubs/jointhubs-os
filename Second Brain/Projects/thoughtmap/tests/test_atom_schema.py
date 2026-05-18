import json
from dataclasses import asdict
from datetime import datetime

from thoughtmap.core.models import TextSegment
from thoughtmap.core.segment.deterministic import atomize_segment_deterministically
from thoughtmap.core.segment.llm import llm_atomize_from_response


def make_segment(text: str) -> TextSegment:
    return TextSegment(
        text=text,
        timestamp=datetime(2026, 4, 28, 12, 0),
        source="wispr-flow",
        source_file="wispr:test-1",
        section="logs",
        wispr_app="Obsidian",
    )


def test_thought_atom_ids_are_stable_for_unchanged_input() -> None:
    segment = make_segment("Need to compare routing decisions with current chunk output.")

    first = atomize_segment_deterministically(segment)
    second = atomize_segment_deterministically(segment)

    assert [atom.atom_id for atom in first] == [atom.atom_id for atom in second]


def test_invalid_llm_output_produces_needs_review() -> None:
    segment = make_segment("This mixed segment should fail closed if the schema is broken.")

    atoms = llm_atomize_from_response(segment, "not valid json")

    assert len(atoms) == 1
    assert atoms[0].quality == "needs_review"
    assert atoms[0].index_targets == ["needs_review"]


def test_atom_json_round_trip_preserves_required_fields() -> None:
    segment = make_segment("Need to map this thought into an atom with stable fields.")
    atom = atomize_segment_deterministically(segment)[0]

    payload = json.loads(json.dumps(asdict(atom)))

    assert payload["atom_id"] == atom.atom_id
    assert payload["parent_segment_id"] == atom.parent_segment_id
    assert payload["text"] == atom.text
    assert payload["title"] == atom.title
    assert payload["confidence"] == atom.confidence


def test_atom_preserves_segment_metadata_needed_by_downstream_outputs() -> None:
    segment = TextSegment(
        text="Need to preserve project and Wispr metadata through atomization.",
        timestamp=datetime(2026, 4, 28, 12, 0),
        source="wispr-flow",
        source_file="wispr:test-2",
        section="logs",
        project_tag="fenix",
        intent="note",
        category="communication",
        wispr_app="Obsidian",
    )

    atom = atomize_segment_deterministically(segment)[0]

    assert atom.project_tag == "fenix"
    assert atom.intent == "note"
    assert atom.category == "communication"
    assert atom.wispr_app == "Obsidian"