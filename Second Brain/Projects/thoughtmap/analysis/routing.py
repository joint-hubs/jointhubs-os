"""Index routing decisions for ThoughtAtom dry runs."""

from __future__ import annotations

from thoughtmap.analysis.classify import classify_atom
from thoughtmap.core.models import RoutingDecision, ThoughtAtom


def route_atom_to_indexes(atom: ThoughtAtom) -> RoutingDecision:
    """Decide which indexes should receive a ThoughtAtom in dry-run mode."""
    classification = classify_atom(atom)
    reason = "dry-run routing from signal, quality, and confidence"

    if classification.quality == "boilerplate" or classification.signal_type == "generated_output":
        return RoutingDecision(
            atom_id=atom.atom_id,
            index_targets=["discard"],
            suggested_target="discard",
            confidence=classification.confidence,
            reason=reason,
        )

    if classification.confidence < 0.60:
        return RoutingDecision(
            atom_id=atom.atom_id,
            index_targets=["needs_review"],
            suggested_target=classification.suggested_target,
            confidence=classification.confidence,
            reason=reason,
        )

    if classification.confidence < 0.80 or classification.quality != "usable":
        return RoutingDecision(
            atom_id=atom.atom_id,
            index_targets=["needs_review"],
            suggested_target=classification.suggested_target,
            confidence=classification.confidence,
            reason=reason,
        )

    if classification.signal_type == "communication":
        targets = ["communication"]
    elif classification.signal_type == "task":
        targets = ["activity"]
    elif classification.signal_type in {"project_update", "decision"}:
        targets = ["project", "semantic"]
    else:
        targets = [classification.suggested_target or "semantic"]

    return RoutingDecision(
        atom_id=atom.atom_id,
        index_targets=targets,
        suggested_target=classification.suggested_target,
        confidence=classification.confidence,
        reason=reason,
    )


def route_atoms(atoms: list[ThoughtAtom]) -> list[RoutingDecision]:
    """Route multiple atoms in dry-run mode."""
    return [route_atom_to_indexes(atom) for atom in atoms]