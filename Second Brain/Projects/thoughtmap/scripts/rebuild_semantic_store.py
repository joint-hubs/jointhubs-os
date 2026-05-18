"""Dry-run semantic store rebuild planning for ThoughtMap v2."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_PARENT = PROJECT_ROOT.parent
if str(PACKAGE_PARENT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_PARENT))

from thoughtmap.analysis.routing import route_atoms
from thoughtmap.analysis.storage_tiers import (
    build_active_manifest,
    build_prune_plan,
    write_manifest,
    write_prune_plan,
)
from thoughtmap.core.embed import get_chroma_client, get_or_create_collection
from thoughtmap.core.segment.deterministic import atomize_segments_deterministically
from thoughtmap.core.extract import extract_all


def main() -> int:
    atoms = atomize_segments_deterministically(extract_all())
    decisions = route_atoms(atoms)
    manifest = build_active_manifest(atoms, decisions)

    client = get_chroma_client()
    collection = get_or_create_collection(client)
    current_store_ids = collection.get(include=[]).get("ids", [])
    prune_plan = build_prune_plan(manifest, current_store_ids)

    manifest_path = write_manifest(manifest)
    prune_plan_path = write_prune_plan(prune_plan)

    print(f"Wrote {manifest_path}")
    print(f"Wrote {prune_plan_path}")
    print(
        f"Active semantic records: {manifest['counts']['active_semantic']}; "
        f"stale in store: {len(prune_plan['stale_in_store'])}; "
        f"missing from store: {len(prune_plan['missing_from_store'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())