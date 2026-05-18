"""Read-only ThoughtAtom prototype for ThoughtMap v2 Phase 1."""

from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_PARENT = PROJECT_ROOT.parent
if str(PACKAGE_PARENT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_PARENT))

import thoughtmap.config as config
from thoughtmap.analysis.curation import write_domain_curation_board, write_segment_curation_board
from thoughtmap.analysis.entities.registry import ensure_entity_registry, load_entity_registry
from thoughtmap.analysis.reports.curation_report import write_curation_report
from thoughtmap.analysis.reports.routing_report import build_routing_report
from thoughtmap.analysis.routing import route_atoms
from thoughtmap.core.extract import extract_all
from thoughtmap.core.models import TextSegment, ThoughtAtom
from thoughtmap.core.segment.deterministic import atomize_segments_deterministically

MAX_SAMPLE_SEGMENTS = 20
PER_SOURCE_LIMITS = {
    "obsidian-daily": 8,
    "jointhubs-review": 4,
    "wispr-flow": 8,
    "review-file": 4,
}


def _is_review_file(segment: TextSegment) -> bool:
    normalized_path = segment.source_file.replace("\\", "/").lower()
    return "/operations/reviews/" in normalized_path or "/operations/weekly-reviews/" in normalized_path


def _split_markdown_sections(text: str) -> list[tuple[str | None, str]]:
    pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    if not matches:
        return [(None, text.strip())] if text.strip() else []

    sections: list[tuple[str | None, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        if content:
            sections.append((match.group(1).strip(), content))
    return sections


def expand_review_segments(segments: list[TextSegment]) -> list[TextSegment]:
    """Shrink review-file samples into section-sized prototype segments."""
    expanded: list[TextSegment] = []
    for segment in segments:
        if segment.source != "second-brain" or not _is_review_file(segment):
            expanded.append(segment)
            continue

        sections = _split_markdown_sections(segment.text)
        if not sections:
            expanded.append(segment)
            continue

        for section_name, content in sections:
            if len(content) < 40:
                continue
            expanded.append(TextSegment(
                text=content,
                timestamp=segment.timestamp,
                source=segment.source,
                source_file=segment.source_file,
                section=section_name,
                project_tag=segment.project_tag,
                language=segment.language,
                wispr_app=segment.wispr_app,
                wispr_duration=segment.wispr_duration,
                wispr_word_count=segment.wispr_word_count,
                intent=segment.intent,
                category=segment.category,
            ))
    return expanded


def select_phase1_sample(segments: list[TextSegment]) -> list[TextSegment]:
    """Pick recent daily, review, and Wispr segments for the prototype."""
    selected: list[TextSegment] = []
    counts: Counter[str] = Counter()

    for segment in sorted(segments, key=lambda item: item.timestamp, reverse=True):
        bucket: str | None = None
        if segment.source == "obsidian-daily":
            bucket = "obsidian-daily"
        elif segment.source == "jointhubs-review":
            bucket = "jointhubs-review"
        elif segment.source == "wispr-flow":
            bucket = "wispr-flow"
        elif segment.source == "second-brain" and _is_review_file(segment):
            bucket = "review-file"

        if bucket is None:
            continue
        if counts[bucket] >= PER_SOURCE_LIMITS[bucket]:
            continue

        selected.append(segment)
        counts[bucket] += 1
        if len(selected) >= MAX_SAMPLE_SEGMENTS:
            break

    return sorted(selected, key=lambda item: item.timestamp)
def main() -> int:
    segments = extract_all()
    sample_segments = select_phase1_sample(expand_review_segments(segments))
    atoms = atomize_segments_deterministically(sample_segments)
    decisions = route_atoms(atoms)
    generated_at = datetime.now().isoformat()

    output_dir = config.OUTPUT_DIR / "prototypes"
    output_dir.mkdir(parents=True, exist_ok=True)

    thought_atoms_path = output_dir / "thought_atoms.json"
    routing_report_path = output_dir / "routing_report.json"

    thought_atoms_path.write_text(
        json.dumps([asdict(atom) for atom in atoms], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    routing_report_path.write_text(
        json.dumps(build_routing_report(sample_segments, atoms, decisions, generated_at), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    registry = ensure_entity_registry()
    write_segment_curation_board(atoms, decisions)
    write_domain_curation_board(atoms)
    write_curation_report(atoms, decisions, load_entity_registry())

    print(f"Selected {len(sample_segments)} segments and produced {len(atoms)} thought atoms")
    print(f"Wrote {thought_atoms_path}")
    print(f"Wrote {routing_report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())