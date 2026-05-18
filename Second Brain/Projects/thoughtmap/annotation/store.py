"""Annotation store — append/load/update annotation records in JSONL.

All annotations are written to:
  data/annotations/annotations.jsonl

The file is newline-delimited JSON.  Each line is one annotation record.
When multiple records share the same task_id, the last one wins (latest update).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

import thoughtmap.config as config

# ── Paths ──────────────────────────────────────────────────────────────────────

def _annotations_path() -> Path:
    p = config.DATA_DIR / "annotations" / "annotations.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _tasks_path() -> Path:
    p = config.DATA_DIR / "annotations" / "tasks.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


# ── Low-level JSONL helpers ────────────────────────────────────────────────────

def _iter_jsonl(path: Path) -> Iterator[dict]:
    if not path.exists():
        return
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    pass


def _append_jsonl(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


# ── Task store ─────────────────────────────────────────────────────────────────

def load_tasks() -> dict[str, dict]:
    """Return all tasks keyed by task_id (last write wins)."""
    tasks: dict[str, dict] = {}
    for rec in _iter_jsonl(_tasks_path()):
        tid = rec.get("task_id")
        if tid:
            tasks[tid] = rec
    return tasks


def save_task(task: dict) -> None:
    """Append a task record (or update — last write wins at read time)."""
    _append_jsonl(_tasks_path(), task)


def upsert_tasks(tasks: list[dict]) -> int:
    """Write tasks that don't already exist.  Returns count of new tasks added."""
    existing = load_tasks()
    added = 0
    for t in tasks:
        tid = t.get("task_id")
        if tid and tid not in existing:
            _append_jsonl(_tasks_path(), t)
            added += 1
    return added


# ── Annotation store ───────────────────────────────────────────────────────────

def load_annotations() -> dict[str, dict]:
    """Return all annotations keyed by task_id (last write wins)."""
    annotations: dict[str, dict] = {}
    for rec in _iter_jsonl(_annotations_path()):
        tid = rec.get("task_id")
        if tid:
            annotations[tid] = rec
    return annotations


def save_annotation(task_id: str, decision: str, entity_type: str | None,
                    canonical_name: str | None, reason: str,
                    annotator: str = "user") -> dict:
    """Append one annotation record and return it."""
    record = {
        "task_id": task_id,
        "decision": decision,           # verify | reject | retype | merge | alias | unsure
        "entity_type": entity_type,     # person | organization | project | tool | location | concept | other
        "canonical_name": canonical_name,
        "reason": reason,
        "annotator": annotator,         # "user" or "model:<name>"
        "annotated_at": datetime.now(timezone.utc).isoformat(),
    }
    _append_jsonl(_annotations_path(), record)
    return record


# ── Stats ──────────────────────────────────────────────────────────────────────

def annotation_stats() -> dict:
    tasks = load_tasks()
    annotations = load_annotations()
    annotated_ids = set(annotations.keys())

    by_decision: dict[str, int] = {}
    for ann in annotations.values():
        d = ann.get("decision", "unknown")
        by_decision[d] = by_decision.get(d, 0) + 1

    by_type_correction: dict[str, int] = {}
    for ann in annotations.values():
        if ann.get("decision") == "retype" and ann.get("entity_type"):
            k = ann["entity_type"]
            by_type_correction[k] = by_type_correction.get(k, 0) + 1

    total = len(tasks)
    done = len(annotated_ids)
    pending = total - done

    return {
        "total_tasks": total,
        "annotated": done,
        "pending": pending,
        "progress_pct": round(done / total * 100, 1) if total else 0,
        "by_decision": by_decision,
        "by_type_correction": by_type_correction,
    }
