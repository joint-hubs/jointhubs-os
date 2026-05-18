"""Machine-readable routing report for the ThoughtAtom prototype."""

from __future__ import annotations

from collections import Counter

from thoughtmap.analysis.classify import classify_atoms
from thoughtmap.core.models import RoutingDecision, TextSegment, ThoughtAtom


def build_routing_report(sample_segments: list[TextSegment], atoms: list[ThoughtAtom], decisions: list[RoutingDecision], generated_at: str) -> dict:
    """Summarize dry-run routing outcomes for inspection."""
    by_source = Counter(atom.source for atom in atoms)
    by_signal = Counter(item.signal_type for item in classify_atoms(atoms))
    by_quality = Counter(item.quality for item in classify_atoms(atoms))
    by_target = Counter(target for decision in decisions for target in decision.index_targets)
    by_suggested_target = Counter((decision.suggested_target or "none") for decision in decisions)
    decision_by_atom = {decision.atom_id: decision for decision in decisions}

    return {
        "generated_at": generated_at,
        "sample_segment_count": len(sample_segments),
        "thought_atom_count": len(atoms),
        "segments": [
            {
                "segment_id": segment.segment_id,
                "timestamp": segment.timestamp.isoformat(),
                "source": segment.source,
                "source_file": segment.source_file,
                "section": segment.section,
            }
            for segment in sample_segments
        ],
        "counts": {
            "by_source": dict(by_source),
            "by_signal_type": dict(by_signal),
            "by_quality": dict(by_quality),
            "by_target": dict(by_target),
            "by_suggested_target": dict(by_suggested_target),
        },
        "needs_review_atoms": [
            {
                "atom_id": atom.atom_id,
                "title": atom.title,
                "source": atom.source,
                "source_file": atom.source_file,
                "suggested_target": decision_by_atom[atom.atom_id].suggested_target,
                "evidence_notes": atom.evidence_notes or [],
            }
            for atom in atoms
            if "needs_review" in decision_by_atom[atom.atom_id].index_targets
        ],
    }