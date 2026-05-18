from datetime import datetime

from thoughtmap.core.models import TextSegment
from thoughtmap.core.segment.deterministic import atomize_segment_deterministically, split_segment_blocks


def make_segment(text: str, section: str = "dziennik") -> TextSegment:
    return TextSegment(
        text=text,
        timestamp=datetime(2026, 4, 28, 10, 30),
        source="obsidian-daily",
        source_file="Second Brain/Operations/Periodic Notes/Daily/2026-04-28.md",
        section=section,
    )


def test_splitter_handles_headings_bullets_timestamps_and_blank_lines() -> None:
    segment = make_segment(
        "## Focus\nLaunch ThoughtMap v2\n\n"
        "2026-04-28 10:00 - Call Konrad about Fenix\n"
        "- [ ] Prepare routing prototype\n"
        "- Compare atom quality with current chunks\n\n"
        "Reflection paragraph about semantic splitting."
    )

    blocks = split_segment_blocks(segment)

    assert len(blocks) == 5
    assert blocks[0].kind == "heading"
    assert blocks[1].kind == "timestamp"
    assert blocks[2].kind == "task"
    assert blocks[3].kind == "bullet"
    assert blocks[4].kind == "paragraph"


def test_mixed_daily_section_creates_multiple_atoms() -> None:
    segment = make_segment(
        "2026-04-28 09:15 - Need to follow up with Artur about the live demo.\n"
        "- [ ] Draft the implementation prototype.\n\n"
        "Research whether Wispr notes should remain separate from semantic memory."
    )

    atoms = atomize_segment_deterministically(segment)

    assert len(atoms) == 3
    assert {atom.signal_type for atom in atoms} >= {"communication", "task", "research"}