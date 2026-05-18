"""Apply durable manual entity decisions to current entity candidates."""

from __future__ import annotations

from copy import deepcopy


def _normalize_candidate_key(name: str) -> str:
    try:
        from thoughtmap.analysis.ner import normalize_entity
        return normalize_entity(name)
    except Exception:
        return " ".join(name.lower().split())


def _merge_lists_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        merged.append(value)
    return merged


def apply_manual_entity_decisions(entities: list, registry: dict) -> list:
    """Apply reject, alias, retype, merge, and verify decisions to entity candidates."""
    if not entities:
        return []

    decisions = registry.get("decisions", {}) or {}
    registry_entities = registry.get("entities", {}) or {}
    resolved = [deepcopy(entity) for entity in entities]
    entity_by_id = {entity_id: data for entity_id, data in registry_entities.items()}

    kept = []
    for entity in resolved:
        normalized_forms = {_normalize_candidate_key(entity.name)}
        normalized_forms.update(_normalize_candidate_key(alias) for alias in getattr(entity, "aliases", []) if alias)

        matched_decision = None
        for candidate_key in normalized_forms:
            if candidate_key in decisions:
                matched_decision = decisions[candidate_key]
                break

        if matched_decision is None:
            kept.append(entity)
            continue

        action = matched_decision.get("action")
        target_entity_id = matched_decision.get("target_entity_id")
        target = entity_by_id.get(target_entity_id, {}) if target_entity_id else {}

        if action == "reject":
            continue

        if action in {"alias", "verify"} and target:
            previous_name = entity.name
            entity.name = target.get("canonical_name", entity.name)
            entity.type = target.get("type", entity.type)
            entity.normalized = _normalize_candidate_key(entity.name)
            entity.aliases = _merge_lists_preserve_order([
                *getattr(entity, "aliases", []),
                previous_name,
                *target.get("aliases", []),
            ])
            kept.append(entity)
            continue

        if action == "retype":
            if target.get("type"):
                entity.type = target["type"]
            elif isinstance(target_entity_id, str) and ":" in target_entity_id:
                entity.type = target_entity_id.split(":", 1)[0]
            kept.append(entity)
            continue

        if action == "merge" and target:
            previous_name = entity.name
            entity.name = target.get("canonical_name", entity.name)
            entity.type = target.get("type", entity.type)
            entity.normalized = _normalize_candidate_key(entity.name)
            entity.aliases = _merge_lists_preserve_order([
                *getattr(entity, "aliases", []),
                previous_name,
                *target.get("aliases", []),
            ])
            kept.append(entity)
            continue

        kept.append(entity)

    deduped = []
    by_key = {}
    for entity in kept:
        key = (getattr(entity, "type", ""), _normalize_candidate_key(getattr(entity, "name", "")))
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = entity
            deduped.append(entity)
            continue

        existing.aliases = _merge_lists_preserve_order([
            *getattr(existing, "aliases", []),
            *getattr(entity, "aliases", []),
        ])
        existing.source_files = sorted(set(getattr(existing, "source_files", []) + getattr(entity, "source_files", [])))
        existing.cluster_ids = sorted(set(getattr(existing, "cluster_ids", []) + getattr(entity, "cluster_ids", [])))
        existing.mention_count = max(getattr(existing, "mention_count", 0), getattr(entity, "mention_count", 0))
    return deduped