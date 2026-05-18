"""Deterministic splitters for the read-only ThoughtAtom prototype."""

from __future__ import annotations

import re
from dataclasses import dataclass

from thoughtmap.core.models import DomainAssignment, TextSegment, ThoughtAtom
from thoughtmap.core.segment.validate import build_thought_atom, minimal_embed_cleanup

_HEADING_PATTERN = re.compile(r"^#{1,6}\s+")
_BULLET_PATTERN = re.compile(r"^(?:[-*+]\s+|\d+\.\s+)")
_CHECKBOX_PATTERN = re.compile(r"^(?:[-*+]\s+)?\[(?: |x|X)\]\s+")
_TIMESTAMP_PATTERN = re.compile(r"^(?:\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}|\d{2}:\d{2})\b")
_TABLE_ROW_PATTERN = re.compile(r"^\s*\|.+\|\s*$")
_URL_PATTERN = re.compile(r"https?://\S+")
_PUNCT_ONLY_PATTERN = re.compile(r"^[\W_]+$")
_BARE_TIME_PATTERN = re.compile(r"^\d{1,2}:\d{2}\s*(?:[a-ząćęłńóśźż-]{0,24})?$", re.IGNORECASE)
_JSONISH_PATTERN = re.compile(r"^\s*[\[{].{40,}[\]}]\s*$", re.DOTALL)


@dataclass(frozen=True)
class SegmentBlock:
    """A deterministic evidence span inside a TextSegment."""

    raw_text: str
    start: int
    end: int
    kind: str


def _classify_line(line: str) -> str:
    stripped = line.strip()
    if not stripped:
        return "blank"
    if _HEADING_PATTERN.match(stripped):
        return "heading"
    if _TIMESTAMP_PATTERN.match(stripped):
        return "timestamp"
    if _CHECKBOX_PATTERN.match(stripped):
        return "task"
    if _BULLET_PATTERN.match(stripped):
        return "bullet"
    if _TABLE_ROW_PATTERN.match(stripped):
        return "table"
    return "text"


def split_segment_blocks(segment: TextSegment) -> list[SegmentBlock]:
    """Split a source segment by headings, bullets, timestamps, and blank lines."""
    lines = segment.text.splitlines(keepends=True)
    blocks: list[SegmentBlock] = []
    current_lines: list[str] = []
    current_start = 0
    current_kind = "paragraph"
    offset = 0

    def flush() -> None:
        nonlocal current_lines, current_start, current_kind
        if not current_lines:
            return
        raw_text = "".join(current_lines).strip()
        if raw_text:
            blocks.append(SegmentBlock(raw_text=raw_text, start=current_start, end=current_start + len(raw_text), kind=current_kind))
        current_lines = []

    for line in lines:
        line_kind = _classify_line(line)
        stripped = line.strip()

        if line_kind == "blank":
            flush()
            offset += len(line)
            continue

        starts_new_block = line_kind in {"heading", "timestamp", "task", "bullet", "table"}
        if starts_new_block:
            flush()
            current_start = offset + max(0, len(line) - len(line.lstrip()))
            current_kind = line_kind
            current_lines = [stripped]
        else:
            if not current_lines:
                current_start = offset
                current_kind = "paragraph"
            current_lines.append(stripped)

        offset += len(line)

    flush()
    return blocks


def _infer_domains(segment: TextSegment, text: str) -> list[DomainAssignment]:
    domains: list[DomainAssignment] = []
    if segment.project_tag:
        domains.append(DomainAssignment(id=segment.project_tag.lower(), confidence=0.92))

    normalized_path = segment.source_file.replace("\\", "/").lower()
    project_match = re.search(r"/projects/([^/]+)/", normalized_path)
    if project_match:
        project_id = project_match.group(1)
        if all(existing.id != project_id for existing in domains):
            domains.append(DomainAssignment(id=project_id, confidence=0.82))

    for candidate in ("fenix", "jointhubs", "neurohubs", "thoughtmap"):
        if candidate in text.lower() and all(existing.id != candidate for existing in domains):
            domains.append(DomainAssignment(id=candidate, confidence=0.68))

    return domains


def _infer_signal_type(segment: TextSegment, block: SegmentBlock, cleaned_text: str) -> str:
    lowered = cleaned_text.lower()
    if block.kind == "table":
        return "generated_output"
    if segment.category == "communication" or any(token in lowered for token in ("reply", "message", "email", "call", "follow up", "odpisa", "wiadomo")):
        return "communication"
    if block.kind == "task" or any(token in lowered for token in ("todo", "to do", "next step", "follow-up", "zrobi", "trzeba", "do zrobienia")):
        return "task"
    if any(token in lowered for token in ("decision", "decide", "ustal", "decyzj")):
        return "decision"
    if segment.source == "jointhubs-review" or any(token in lowered for token in ("blocker", "milestone", "status", "update", "postęp")):
        return "project_update"
    if _URL_PATTERN.search(cleaned_text) or any(token in lowered for token in ("research", "check", "read", "sprawd", "poszuk")):
        return "research"
    return "thought"


def _infer_quality(signal_type: str, cleaned_text: str) -> str:
    lowered = cleaned_text.lower().strip()
    if signal_type == "generated_output":
        return "boilerplate"
    if _BARE_TIME_PATTERN.fullmatch(cleaned_text.strip()):
        return "boilerplate"
    if _JSONISH_PATTERN.match(cleaned_text):
        return "boilerplate"
    if _PUNCT_ONLY_PATTERN.fullmatch(cleaned_text):
        return "boilerplate"
    if lowered in {"file created", "file updated", "file deleted", "created", "updated", "deleted"}:
        return "boilerplate"
    if len(cleaned_text) < 15:
        return "needs_review"
    if cleaned_text.count("|") >= 3:
        return "boilerplate"
    return "usable"


def _infer_confidence(block: SegmentBlock, quality: str, cleaned_text: str) -> float:
    if quality == "boilerplate":
        return 0.95
    if quality == "needs_review":
        return 0.45
    if block.kind in {"timestamp", "task", "bullet", "heading"}:
        return 0.86
    if len(cleaned_text) > 500:
        return 0.72
    return 0.82


def _route_targets(signal_type: str, quality: str, confidence: float) -> tuple[list[str], str | None]:
    if quality == "boilerplate" or signal_type == "generated_output":
        return ["discard"], "discard"

    if signal_type == "communication":
        suggested = "communication"
    elif signal_type == "task":
        suggested = "activity"
    elif signal_type in {"project_update", "decision"}:
        suggested = "project"
    else:
        suggested = "semantic"

    if confidence >= 0.80 and quality == "usable":
        if signal_type in {"project_update", "decision"}:
            return ["project", "semantic"], suggested
        return [suggested], suggested

    if confidence >= 0.60:
        return ["needs_review"], suggested

    return ["needs_review"], suggested if quality != "boilerplate" else "discard"


def _make_title(cleaned_text: str) -> str:
    words = cleaned_text.split()
    if not words:
        return "Untitled atom"
    title = " ".join(words[:8]).strip(" ,.;:-")
    return title[:80] or "Untitled atom"


def atomize_segment_deterministically(segment: TextSegment) -> list[ThoughtAtom]:
    """Produce initial ThoughtAtoms using only deterministic rules."""
    atoms: list[ThoughtAtom] = []
    for block in split_segment_blocks(segment):
        cleaned_text = minimal_embed_cleanup(block.raw_text)
        if not cleaned_text:
            continue
        signal_type = _infer_signal_type(segment, block, cleaned_text)
        quality = _infer_quality(signal_type, cleaned_text)
        confidence = _infer_confidence(block, quality, cleaned_text)
        index_targets, suggested_target = _route_targets(signal_type, quality, confidence)
        atoms.append(build_thought_atom(
            segment=segment,
            raw_text=block.raw_text,
            text=cleaned_text,
            title=_make_title(cleaned_text),
            signal_type=signal_type,
            quality=quality,
            confidence=confidence,
            index_targets=index_targets,
            suggested_target=suggested_target,
            source_offsets={"start": block.start, "end": block.end},
            domains=_infer_domains(segment, cleaned_text),
        ))
    return atoms


def atomize_segments_deterministically(segments: list[TextSegment]) -> list[ThoughtAtom]:
    """Atomize multiple segments without side effects."""
    atoms: list[ThoughtAtom] = []
    for segment in segments:
        atoms.extend(atomize_segment_deterministically(segment))
    return atoms