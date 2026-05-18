"""Durable manual entity registry for ThoughtMap v2."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

import thoughtmap.config as config


def _default_registry() -> dict[str, Any]:
    return {
        "version": 1,
        "updated_at": "",
        "entities": {},
        "decisions": {},
    }


def ensure_entity_registry(path: Path | None = None) -> dict[str, Any]:
    """Ensure the durable entity registry exists on disk."""
    registry_path = path or config.ENTITY_REGISTRY_PATH
    registry = load_entity_registry(registry_path)
    if registry_path.exists():
        return registry
    save_entity_registry(registry, registry_path)
    return registry


def load_entity_registry(path: Path | None = None) -> dict[str, Any]:
    """Load the durable entity registry, falling back to an empty schema."""
    registry_path = path or config.ENTITY_REGISTRY_PATH
    if not registry_path.exists():
        return _default_registry()
    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _default_registry()

    registry = _default_registry()
    registry["version"] = int(payload.get("version", 1) or 1)
    registry["updated_at"] = str(payload.get("updated_at", "") or "")
    registry["entities"] = payload.get("entities", {}) or {}
    registry["decisions"] = payload.get("decisions", {}) or {}
    return registry


def save_entity_registry(registry: dict[str, Any], path: Path | None = None) -> None:
    """Persist the durable entity registry atomically."""
    registry_path = path or config.ENTITY_REGISTRY_PATH
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    payload = deepcopy(registry)
    payload["updated_at"] = datetime.now().isoformat(timespec="seconds")
    with NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=registry_path.parent) as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        temp_path = Path(handle.name)
    temp_path.replace(registry_path)


def _normalize_candidate_key(name: str) -> str:
    try:
        from thoughtmap.analysis.ner import normalize_entity
        return normalize_entity(name)
    except Exception:
        return " ".join(name.lower().split())


def _entity_id(name: str, entity_type: str) -> str:
    normalized = _normalize_candidate_key(name).replace(" ", "-") or "entity"
    return f"{entity_type}:{normalized}"


def apply_kanban_alias_overrides_to_registry(registry: dict[str, Any], overrides: dict[str, dict]) -> dict[str, Any]:
    """Promote harvested intake alias overrides into the durable registry format."""
    if not overrides:
        return registry

    updated = deepcopy(registry)
    entities = updated.setdefault("entities", {})
    decisions = updated.setdefault("decisions", {})

    for alias_key, override in overrides.items():
        canonical_name = str(override.get("name", "")).strip()
        entity_type = str(override.get("type", "person") or "person")
        if not canonical_name:
            continue

        entity_id = _entity_id(canonical_name, entity_type)
        entity_entry = entities.setdefault(entity_id, {
            "canonical_name": canonical_name,
            "type": entity_type,
            "aliases": [],
            "status": "verified",
            "source": "manual",
            "notes": "",
        })
        entity_entry["canonical_name"] = canonical_name
        entity_entry["type"] = entity_type
        entity_entry["status"] = entity_entry.get("status") or "verified"
        entity_entry["source"] = entity_entry.get("source") or "manual"

        aliases = list(entity_entry.get("aliases", []))
        for alias in override.get("aliases", []):
            alias_text = str(alias).strip()
            if alias_text and alias_text != canonical_name and alias_text not in aliases:
                aliases.append(alias_text)
        entity_entry["aliases"] = sorted(aliases, key=str.lower)

        decisions[_normalize_candidate_key(alias_key)] = {
            "action": "alias",
            "target_entity_id": entity_id,
            "reason": "Imported from ThoughtMap Intake curation.",
        }

    return updated