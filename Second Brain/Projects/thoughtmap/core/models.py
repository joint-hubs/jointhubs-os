"""Shared typed models for the ThoughtMap pipeline.

These models are the compatibility bridge between the v1 chunk pipeline and the
v2 thought-atom pipeline. Keep them lightweight and data-focused.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime


def _normalize_text_for_identity(text: str) -> str:
    return " ".join(text.split())


def build_segment_id(source: str, source_file: str, timestamp: datetime | None, text: str) -> str:
    """Create a stable segment ID from source identity and normalized text."""
    stamp = timestamp.isoformat() if timestamp else ""
    payload = f"{source}|{source_file}|{stamp}|{_normalize_text_for_identity(text)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


@dataclass
class TextSegment:
    """A raw text segment extracted from a source, before chunking or atomization."""

    text: str
    timestamp: datetime
    source: str
    source_file: str
    section: str | None = None
    project_tag: str | None = None
    language: str | None = None
    wispr_app: str | None = None
    wispr_duration: float | None = None
    wispr_word_count: int | None = None
    intent: str | None = None
    category: str | None = None
    segment_id: str = field(init=False)

    def __post_init__(self) -> None:
        self.segment_id = build_segment_id(
            source=self.source,
            source_file=self.source_file,
            timestamp=self.timestamp,
            text=self.text,
        )


@dataclass(frozen=True)
class DomainAssignment:
    """A proposed domain label for a thought atom."""

    id: str
    confidence: float


@dataclass(frozen=True)
class ThoughtAtom:
    """Atomic semantic unit produced from a source segment."""

    atom_id: str
    parent_segment_id: str
    text: str
    title: str
    signal_type: str
    domains: list[DomainAssignment]
    index_targets: list[str]
    quality: str
    confidence: float
    source: str
    source_file: str
    section: str | None
    timestamp: str | None
    project_tag: str | None = None
    intent: str | None = None
    category: str | None = None
    wispr_app: str | None = None
    raw_text: str | None = None
    summary: str | None = None
    language: str | None = None
    suggested_target: str | None = None
    curation_state: str = "auto"
    source_offsets: dict[str, int] | None = None
    evidence_notes: list[str] | None = None


@dataclass(frozen=True)
class RoutingDecision:
    """Structured routing output for a thought atom."""

    atom_id: str
    index_targets: list[str]
    suggested_target: str | None
    confidence: float
    reason: str


@dataclass(frozen=True)
class AtomClassification:
    """Read-only classification snapshot for routing and reporting."""

    atom_id: str
    signal_type: str
    quality: str
    confidence: float
    domains: list[DomainAssignment]
    source: str
    source_file: str
    section: str | None
    suggested_target: str | None