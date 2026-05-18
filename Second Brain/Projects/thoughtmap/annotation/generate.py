"""Generate annotation tasks from ThoughtMap output.

Currently supports:
  - entity_type_resolution  (from entities.json)

Run:
  python -m thoughtmap.annotation.generate --task-type entity_type_resolution
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import thoughtmap.config as config
from thoughtmap.annotation.store import upsert_tasks

# ── Helpers ────────────────────────────────────────────────────────────────────

def _task_id(entity_name: str, task_type: str) -> str:
    """Stable deterministic ID for a task."""
    raw = f"{task_type}:{entity_name}".encode()
    return hashlib.sha1(raw).hexdigest()[:20]  # noqa: S324 — not crypto


def _entities_path() -> Path:
    return config.OUTPUT_DIR / "entities.json"


# ── Entity type resolution task generator ─────────────────────────────────────

_VALID_TYPES = {
    "person", "organization", "project", "tool",
    "location", "concept", "other",
}

# Heuristics: types that are frequently confused / worth reviewing
_UNCERTAIN_TYPES = {"location", "concept", "other"}

# Minimum mentions to bother annotating (noise filter)
_MIN_MENTIONS = 3


def generate_entity_tasks(
    *,
    min_mentions: int = _MIN_MENTIONS,
    only_uncertain: bool = False,
) -> list[dict]:
    """Generate entity_type_resolution tasks from entities.json."""
    path = _entities_path()
    if not path.exists():
        raise FileNotFoundError(f"entities.json not found at {path}")

    raw: list[dict] = json.loads(path.read_text(encoding="utf-8"))

    tasks = []
    for ent in raw:
        name = ent.get("name", "")
        if not name:
            continue
        mention_count = ent.get("mention_count", 0)
        if mention_count < min_mentions:
            continue
        ent_type = ent.get("type", "other")
        if only_uncertain and ent_type not in _UNCERTAIN_TYPES:
            continue

        # Pick a few representative source files as evidence context
        source_files = ent.get("source_files", [])
        evidence_sources = source_files[:5]

        task = {
            "task_id": _task_id(name, "entity_type_resolution"),
            "task_type": "entity_type_resolution",
            "status": "pending",
            "entity_name": name,
            "current_type": ent_type,
            "aliases": ent.get("aliases", []),
            "normalized": ent.get("normalized", ""),
            "mention_count": mention_count,
            "cluster_ids": ent.get("cluster_ids", []),
            "summary": ent.get("summary", ""),
            "boundaries": ent.get("boundaries", ""),
            "evidence_sources": evidence_sources,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        tasks.append(task)

    # Sort: uncertain types first, then by mention count descending
    tasks.sort(
        key=lambda t: (
            0 if t["current_type"] in _UNCERTAIN_TYPES else 1,
            -t["mention_count"],
        )
    )
    return tasks


# ── CLI entry point ────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate annotation tasks")
    parser.add_argument(
        "--task-type",
        choices=["entity_type_resolution"],
        default="entity_type_resolution",
        help="Which task type to generate (default: entity_type_resolution)",
    )
    parser.add_argument(
        "--min-mentions",
        type=int,
        default=_MIN_MENTIONS,
        help=f"Minimum mention count to include (default: {_MIN_MENTIONS})",
    )
    parser.add_argument(
        "--only-uncertain",
        action="store_true",
        help="Only generate tasks for uncertain/confused types (location, concept, other)",
    )
    args = parser.parse_args()

    if args.task_type == "entity_type_resolution":
        tasks = generate_entity_tasks(
            min_mentions=args.min_mentions,
            only_uncertain=args.only_uncertain,
        )
        added = upsert_tasks(tasks)
        print(f"Generated {len(tasks)} tasks, {added} new tasks added to store.")


if __name__ == "__main__":
    main()
