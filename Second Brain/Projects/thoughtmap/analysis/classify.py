"""Structured classification helpers for ThoughtAtom dry runs."""

from __future__ import annotations

from thoughtmap.core.models import AtomClassification, ThoughtAtom


def classify_atom(atom: ThoughtAtom) -> AtomClassification:
    """Project the atom's current interpretation into a routing-ready snapshot."""
    return AtomClassification(
        atom_id=atom.atom_id,
        signal_type=atom.signal_type,
        quality=atom.quality,
        confidence=atom.confidence,
        domains=atom.domains,
        source=atom.source,
        source_file=atom.source_file,
        section=atom.section,
        suggested_target=atom.suggested_target,
    )


def classify_atoms(atoms: list[ThoughtAtom]) -> list[AtomClassification]:
    """Classify multiple atoms without side effects."""
    return [classify_atom(atom) for atom in atoms]