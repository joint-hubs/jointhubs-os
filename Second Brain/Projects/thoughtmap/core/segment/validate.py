"""Validation and fail-closed helpers for ThoughtAtom generation."""

from __future__ import annotations

import hashlib
from dataclasses import asdict

from thoughtmap.core.models import DomainAssignment, ThoughtAtom, TextSegment


class InvalidStructuredOutput(ValueError):
    """Raised when structured LLM output cannot be trusted."""


def minimal_embed_cleanup(text: str) -> str:
    """Apply the guide's allowed minimal cleanup before embedding."""
    cleaned = text.replace("\r\n", "\n")
    cleaned = cleaned.replace("\t", " ")
    cleaned = cleaned.replace("%%tm:", " %%tm:")
    cleaned = "\n".join(line.rstrip() for line in cleaned.splitlines())
    cleaned = cleaned.replace("**", "")
    cleaned = cleaned.replace("`", "")
    cleaned = cleaned.replace("[[", "")
    cleaned = cleaned.replace("]]", "")
    cleaned = cleaned.replace("- [ ] ", "")
    cleaned = cleaned.replace("- [x] ", "")
    cleaned = cleaned.replace("- [X] ", "")
    cleaned = "\n".join(line for line in cleaned.splitlines() if not line.strip().startswith("%%tm:id="))
    cleaned = "\n".join(line.strip() for line in cleaned.splitlines())
    cleaned = "\n\n".join(block for block in cleaned.split("\n\n") if block.strip())
    return " ".join(cleaned.split())


def build_atom_id(parent_segment_id: str, raw_text: str, source_offsets: dict[str, int] | None = None) -> str:
    """Build a stable atom ID from parent segment identity and exact evidence text."""
    offsets = source_offsets or {}
    payload = f"{parent_segment_id}|{offsets.get('start','')}|{offsets.get('end','')}|{' '.join(raw_text.split())}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def build_thought_atom(
    *,
    segment: TextSegment,
    raw_text: str,
    text: str,
    title: str,
    signal_type: str,
    quality: str,
    confidence: float,
    index_targets: list[str],
    source_offsets: dict[str, int] | None = None,
    domains: list[DomainAssignment] | None = None,
    suggested_target: str | None = None,
    summary: str | None = None,
    language: str | None = None,
    evidence_notes: list[str] | None = None,
) -> ThoughtAtom:
    """Create a ThoughtAtom with stable identity and normalized metadata."""
    atom = ThoughtAtom(
        atom_id=build_atom_id(segment.segment_id, raw_text, source_offsets),
        parent_segment_id=segment.segment_id,
        text=text,
        title=title,
        signal_type=signal_type,
        domains=domains or [],
        index_targets=index_targets,
        quality=quality,
        confidence=max(0.0, min(1.0, confidence)),
        source=segment.source,
        source_file=segment.source_file,
        section=segment.section,
        timestamp=segment.timestamp.isoformat() if segment.timestamp else None,
        project_tag=segment.project_tag,
        intent=segment.intent,
        category=segment.category,
        wispr_app=segment.wispr_app,
        raw_text=raw_text,
        summary=summary,
        language=language or segment.language,
        suggested_target=suggested_target,
        source_offsets=source_offsets,
        evidence_notes=evidence_notes,
    )
    validate_atom(atom)
    return atom


def make_review_atom(segment: TextSegment, reason: str, raw_text: str | None = None) -> ThoughtAtom:
    """Fail closed when structured output is uncertain or invalid."""
    evidence = raw_text if raw_text is not None else segment.text
    cleaned = minimal_embed_cleanup(evidence)
    title = cleaned.split(".", 1)[0][:80].strip() or "Needs review"
    return build_thought_atom(
        segment=segment,
        raw_text=evidence,
        text=cleaned,
        title=title,
        signal_type="thought",
        quality="needs_review",
        confidence=0.0,
        index_targets=["needs_review"],
        source_offsets={"start": 0, "end": len(evidence)},
        evidence_notes=[reason],
    )


def validate_atom(atom: ThoughtAtom) -> None:
    """Validate the minimum schema required by Phase 1."""
    if not atom.atom_id:
        raise InvalidStructuredOutput("ThoughtAtom is missing atom_id")
    if not atom.parent_segment_id:
        raise InvalidStructuredOutput("ThoughtAtom is missing parent_segment_id")
    if not atom.text.strip():
        raise InvalidStructuredOutput("ThoughtAtom text is empty")
    if not atom.title.strip():
        raise InvalidStructuredOutput("ThoughtAtom title is empty")
    if atom.confidence < 0.0 or atom.confidence > 1.0:
        raise InvalidStructuredOutput("ThoughtAtom confidence must be between 0 and 1")
    if not atom.index_targets:
        raise InvalidStructuredOutput("ThoughtAtom must have at least one index target")


def atom_to_dict(atom: ThoughtAtom) -> dict:
    """Serialize ThoughtAtom dataclasses into JSON-safe dictionaries."""
    return asdict(atom)