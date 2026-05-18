"""Structured LLM response parsing for ThoughtAtom generation."""

from __future__ import annotations

import json

from thoughtmap.core.models import DomainAssignment, TextSegment, ThoughtAtom
from thoughtmap.core.segment.validate import InvalidStructuredOutput, build_thought_atom, make_review_atom, minimal_embed_cleanup


def _coerce_domains(payload: list[dict] | None) -> list[DomainAssignment]:
    if not payload:
        return []
    domains: list[DomainAssignment] = []
    for item in payload:
        domain_id = str(item.get("id", "")).strip()
        if not domain_id:
            continue
        domains.append(DomainAssignment(id=domain_id, confidence=float(item.get("confidence", 0.0))))
    return domains


def parse_llm_atom_response(segment: TextSegment, response_text: str) -> list[ThoughtAtom]:
    """Parse JSON-like LLM output into ThoughtAtoms or raise on invalid data."""
    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise InvalidStructuredOutput(f"Invalid JSON from LLM: {exc}") from exc

    if isinstance(payload, dict):
        payload = payload.get("atoms", [])
    if not isinstance(payload, list) or not payload:
        raise InvalidStructuredOutput("LLM payload must contain a non-empty atoms list")

    atoms: list[ThoughtAtom] = []
    for item in payload:
        if not isinstance(item, dict):
            raise InvalidStructuredOutput("Each LLM atom must be an object")
        raw_text = str(item.get("raw_text") or item.get("text") or "").strip()
        cleaned_text = minimal_embed_cleanup(str(item.get("text") or raw_text))
        if not raw_text or not cleaned_text:
            raise InvalidStructuredOutput("LLM atom is missing text")
        atoms.append(build_thought_atom(
            segment=segment,
            raw_text=raw_text,
            text=cleaned_text,
            title=str(item.get("title") or cleaned_text[:80]).strip(),
            signal_type=str(item.get("signal_type") or "thought").strip(),
            quality=str(item.get("quality") or "needs_review").strip(),
            confidence=float(item.get("confidence", 0.0)),
            index_targets=[str(target) for target in item.get("index_targets") or ["needs_review"]],
            suggested_target=item.get("suggested_target"),
            source_offsets=item.get("source_offsets"),
            domains=_coerce_domains(item.get("domains")),
            summary=item.get("summary"),
            language=item.get("language") or segment.language,
        ))
    return atoms


def llm_atomize_from_response(segment: TextSegment, response_text: str) -> list[ThoughtAtom]:
    """Parse LLM output and fail closed into review atoms on schema errors."""
    try:
        return parse_llm_atom_response(segment, response_text)
    except InvalidStructuredOutput as exc:
        return [make_review_atom(segment, str(exc))]