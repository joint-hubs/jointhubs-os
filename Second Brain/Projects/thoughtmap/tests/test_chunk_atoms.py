from thoughtmap.core.chunk import chunk_atom
from thoughtmap.core.models import ThoughtAtom


def make_atom(atom_id: str = "atom-1") -> ThoughtAtom:
    return ThoughtAtom(
        atom_id=atom_id,
        parent_segment_id="segment-1",
        text="Semantic atom text for embedding.",
        title="Semantic atom title",
        signal_type="thought",
        domains=[],
        index_targets=["semantic"],
        quality="usable",
        confidence=0.91,
        source="obsidian-daily",
        source_file="Second Brain/Operations/Periodic Notes/Daily/2026-04-28.md",
        section="logs",
        timestamp="2026-04-28T10:00:00",
        project_tag="thoughtmap",
        intent="note",
        category="note-taking",
        wispr_app="Obsidian",
        raw_text="Semantic atom text for embedding.",
    )


def test_chunk_atom_creates_single_store_record_with_atom_metadata() -> None:
    chunk = chunk_atom(make_atom())

    assert chunk is not None
    assert chunk.record_id == "atom:atom-1"
    assert chunk.atom_id == "atom-1"
    assert chunk.parent_segment_id == "segment-1"
    assert chunk.project_tag == "thoughtmap"
    assert chunk.intent == "note"
    assert chunk.category == "note-taking"
    assert chunk.signal_type == "thought"