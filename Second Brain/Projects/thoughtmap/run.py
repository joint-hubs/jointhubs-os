"""ThoughtMap CLI — run the full pipeline."""

from __future__ import annotations

import json
import sys
import time
from typing import Callable


def main(on_status: Callable[[str], None] | None = None):
    """Run the full ThoughtMap pipeline.

    Args:
        on_status: Optional callback for status updates (used by web server).

    Returns:
        ThoughtMapResult or None if not enough data.

    Raises:
        RuntimeError: If no segments or chunks produced.
    """
    import numpy as np
    import thoughtmap.config as config
    from thoughtmap.analysis.condense import condense, write_condensed_visualization
    from thoughtmap.analysis.curation import write_domain_curation_board, write_segment_curation_board
    from thoughtmap.analysis.entities.registry import load_entity_registry
    from thoughtmap.analysis.index import generate_cluster_indices
    from thoughtmap.analysis.kanban import generate_kanban_artifacts, sync_kanban_curation
    from thoughtmap.analysis.ner import extract_entities
    from thoughtmap.analysis.report import save_report
    from thoughtmap.analysis.reports.curation_report import write_curation_report
    from thoughtmap.analysis.semantic_layers import generate_semantic_artifacts
    from thoughtmap.analysis.routing import route_atoms
    from thoughtmap.analysis.storage_tiers import (
        build_active_manifest,
        build_prune_plan,
        write_manifest,
        write_prune_plan,
    )
    from thoughtmap.core.chunk import chunk_all, chunk_atoms
    from thoughtmap.core.cluster import cluster_all
    from thoughtmap.core.embed import (
        chunk_id as compute_chunk_id,
        embed_batch,
        get_chroma_client,
        get_or_create_collection,
        load_all_embeddings,
        store_chunks,
    )
    from thoughtmap.core.extract import extract_all
    from thoughtmap.core.segment.deterministic import atomize_segments_deterministically
    from thoughtmap.web.viz import generate_viz

    total_steps = 10

    def status(msg: str):
        print(msg)
        if on_status:
            on_status(msg)

    status("=" * 60)
    status("ThoughtMap — Personal Thought Vector Pipeline")
    status("=" * 60)

    # ─── Step 1: Extract ───
    status(f"[1/{total_steps}] Extracting text from all sources...")
    t0 = time.time()
    segments = extract_all()
    source_counts = {}
    for s in segments:
        source_counts[s.source] = source_counts.get(s.source, 0) + 1
    status(f"  Found {len(segments)} segments in {time.time() - t0:.1f}s")
    for src, cnt in sorted(source_counts.items()):
        status(f"    {src}: {cnt}")
    intent_notes = sum(1 for s in segments if s.intent == "note")
    status(f"  Wispr entries matched as intentional notes: {intent_notes}")

    if not segments:
        raise RuntimeError("No segments found. Check your data source paths in config.py.")

    atoms = []
    decisions = []
    manifest = {"active_records": [], "cold_records": [], "counts": {}}

    # ─── Step 2: Prepare embedding records ───
    status(f"[2/{total_steps}] Preparing embedding records...")
    t0 = time.time()
    if config.ENABLE_ATOM_PIPELINE:
        atoms = atomize_segments_deterministically(segments)
        decisions = route_atoms(atoms)
        manifest = build_active_manifest(atoms, decisions)
        semantic_atom_ids = {
            record["atom_id"] for record in manifest.get("active_records", [])
        }
        semantic_atoms = [atom for atom in atoms if atom.atom_id in semantic_atom_ids]
        chunks = chunk_atoms(semantic_atoms)
        status(
            f"  Atom pipeline enabled: {len(atoms)} thought atoms, "
            f"{len(semantic_atoms)} semantic atoms, {len(chunks)} embedding records "
            f"in {time.time() - t0:.1f}s"
        )
    else:
        chunks = chunk_all(segments)
        status(
            f"  Atom pipeline disabled; using stable v1 chunking: "
            f"{len(chunks)} chunks in {time.time() - t0:.1f}s"
        )

    if not chunks:
        raise RuntimeError("No semantic chunks produced. Routing may have filtered everything out.")

    # ─── Check for new data ───
    status("Checking ChromaDB for existing chunks...")
    client = get_chroma_client()
    collection = get_or_create_collection(client)
    existing_count = collection.count()

    # Build ID→chunk index and find which are truly new
    id_to_idx: dict[str, int] = {}
    for i, c in enumerate(chunks):
        cid = compute_chunk_id(c)
        if cid not in id_to_idx:  # first occurrence wins (dedup)
            id_to_idx[cid] = i

    all_ids = list(id_to_idx.keys())
    existing_ids: set[str] = set()
    if existing_count > 0:
        for batch_start in range(0, len(all_ids), 5000):
            batch = all_ids[batch_start:batch_start + 5000]
            try:
                result = collection.get(ids=batch)
                existing_ids.update(result["ids"])
            except Exception:
                pass

    new_ids = [cid for cid in all_ids if cid not in existing_ids]
    status(f"  {existing_count} records in store, {len(new_ids)} new semantic records, {len(all_ids) - len(new_ids)} already stored")

    if new_ids:
        # Filter to only the new semantic records — no point embedding what already exists
        new_indices = [id_to_idx[cid] for cid in new_ids]
        new_chunks = [chunks[i] for i in new_indices]

        # ─── Step 3: Embed (only new) ───
        status(f"[3/{total_steps}] Embedding {len(new_chunks)} new semantic records via {config.EMBEDDING_PROVIDER}:{config.EMBEDDING_MODEL}...")
        t0 = time.time()
        new_texts = [c.text for c in new_chunks]
        new_embeddings = embed_batch(new_texts)
        status(f"  Embedded in {time.time() - t0:.1f}s")

        # ─── Step 4: Active manifest and prune plan ───
        status(f"[4/{total_steps}] Writing semantic manifest and prune dry-run...")
        t0 = time.time()
        if config.ENABLE_ATOM_PIPELINE:
            prune_plan = build_prune_plan(manifest, collection.get(include=[]).get("ids", []))
            manifest_path = write_manifest(manifest)
            prune_plan_path = write_prune_plan(prune_plan)
            status(
                f"  Manifest: {manifest_path.name}; prune plan: {prune_plan_path.name} "
                f"({time.time() - t0:.1f}s)"
            )
        else:
            status(f"  Atom manifest skipped; v1 chunking remains active ({time.time() - t0:.1f}s)")

        # ─── Step 5: Store (only new) ───
        status(f"[5/{total_steps}] Storing new semantic records in ChromaDB...")
        added = store_chunks(new_chunks, new_embeddings)
        status(f"  Added {added} new semantic records to vector store")
    else:
        status(f"[3/{total_steps}] No new semantic records — skipping embedding")
        status(f"[4/{total_steps}] Writing semantic manifest and prune dry-run...")
        t0 = time.time()
        if config.ENABLE_ATOM_PIPELINE:
            prune_plan = build_prune_plan(manifest, collection.get(include=[]).get("ids", []))
            manifest_path = write_manifest(manifest)
            prune_plan_path = write_prune_plan(prune_plan)
            status(
                f"  Manifest: {manifest_path.name}; prune plan: {prune_plan_path.name} "
                f"({time.time() - t0:.1f}s)"
            )
        else:
            status(f"  Atom manifest skipped; v1 chunking remains active ({time.time() - t0:.1f}s)")
        status(f"[5/{total_steps}] No new semantic records — skipping storage")

    # Load only records that actually produced embedding chunks.
    active_record_ids = [compute_chunk_id(chunk) for chunk in chunks]
    items, all_embeddings = load_all_embeddings(ids=active_record_ids)
    status(f"  Active semantic corpus: {len(items)} records from manifest")

    # ─── Deduplicate exact-match texts ───
    seen_texts: dict[str, int] = {}  # normalized text → index in deduped list
    deduped_items: list[dict] = []
    deduped_embeddings: list[list[float]] = []
    dup_count = 0
    for i, item in enumerate(items):
        key = item.get("text", "").strip()
        if key in seen_texts:
            # Increment repeat count on the first occurrence
            idx = seen_texts[key]
            deduped_items[idx]["repeat_count"] = deduped_items[idx].get("repeat_count", 1) + 1
            src = item.get("source_file", "")
            if src:
                sources = deduped_items[idx].get("repeat_sources", "")
                if src not in sources:
                    deduped_items[idx]["repeat_sources"] = (sources + "|" + src) if sources else src
            dup_count += 1
        else:
            seen_texts[key] = len(deduped_items)
            item["repeat_count"] = 1
            item["repeat_sources"] = item.get("source_file", "")
            deduped_items.append(item)
            deduped_embeddings.append(all_embeddings[i])

    if dup_count > 0:
        status(f"  Deduplicated: {dup_count} exact duplicates removed → {len(deduped_items)} unique chunks")
    items = deduped_items
    all_embeddings = deduped_embeddings

    if len(items) < 5:
        status("Not enough data for meaningful clustering (need at least 5 chunks).")
        status("Run again after accumulating more notes.")
        config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (config.OUTPUT_DIR / "chunks.json").write_text(
            json.dumps([{"text": c.text, **{k: v for k, v in vars(c).items() if k != "text"}}
                        for c in chunks], indent=2, default=str),
            encoding="utf-8",
        )
        return None

    # ─── Step 6: Cluster + Output ───
    status(f"[6/{total_steps}] Clustering {len(items)} chunks (UMAP + HDBSCAN)...")
    t0 = time.time()
    result = cluster_all(items, all_embeddings)
    status(f"  Found {len(result.clusters)} clusters, {result.noise_count} unclustered ({time.time() - t0:.1f}s)")

    # God nodes
    status("  God Nodes (dominant topics):")
    for i, god in enumerate(result.god_nodes[:5], 1):
        status(f"    {i}. {god.label} ({god.size} chunks)")

    # ─── Step 7: Condense ───
    status(f"[7/{total_steps}] Condensing {len(result.clusters)} clusters → topic notes + condensed viz...")
    t0 = time.time()
    condensed = condense(result, on_status=on_status, embeddings_hd=all_embeddings)
    n_topics = condensed["stats"]["total_clusters"]
    n_super = condensed["stats"]["total_super_clusters"]
    n_edges = condensed["stats"]["total_edges"]
    status(f"  Condensed in {time.time() - t0:.1f}s: {n_topics} topics, {n_super} mega-topics, {n_edges} edges")

    # ─── Step 8: Named entities ───
    status("  Syncing manual ThoughtMap Intake curation...")
    sync_kanban_curation(on_status=status)
    if config.ENABLE_ATOM_PIPELINE:
        write_segment_curation_board(atoms, decisions)
        write_domain_curation_board(atoms)
    else:
        status("  Atom curation boards skipped; run scripts/prototype_thought_atoms.py for review surfaces")

    entities = []
    if config.NER_ENABLED:
        status(f"[8/{total_steps}] Extracting named entities...")
        t0 = time.time()
        entities = extract_entities(result, items, on_status=status, embeddings=all_embeddings)
        status(f"  Found {len(entities)} entities in {time.time() - t0:.1f}s")
    else:
        status(f"[8/{total_steps}] NER disabled — skipping")
    if config.ENABLE_ATOM_PIPELINE:
        write_curation_report(atoms, decisions, load_entity_registry())

    # ─── Step 9: Semantic layers ───
    status(f"[9/{total_steps}] Generating glossary, taxonomy, topology, and ontology...")
    t0 = time.time()
    generate_semantic_artifacts(entities, condensed, on_status=status)
    write_condensed_visualization(condensed, on_status=status)
    status(f"  Semantic layers generated in {time.time() - t0:.1f}s")

    # ─── Step 10: Reports and artifacts ───
    status(f"[10/{total_steps}] Generating report, indices, visualizations, and kanban artifacts...")

    report_path = save_report(result, entities=entities)
    status(f"  Report: {report_path}")

    viz_path = generate_viz(result)
    status(f"  Visualization: {viz_path}")

    index_dir = generate_cluster_indices(result, np.array(all_embeddings))
    idx_count = len(list(index_dir.glob("*.md")))
    status(f"  Domain indices: {idx_count} files in {index_dir}")

    kanban_paths = generate_kanban_artifacts(entities=entities, on_status=status)
    status(f"  Kanban JSON: {kanban_paths['json']}")
    status(f"  Kanban board: {kanban_paths['board']}")

    # ─── Echoes: near-duplicate thought groups ───
    try:
        from thoughtmap.analysis.echoes import (
            compute_echoes,
            save_echoes,
            ECHO_DEFAULT_THRESHOLD,
            ECHO_MIN_GROUP_SIZE,
        )
        t0 = time.time()
        echoes = compute_echoes(
            items,
            all_embeddings,
            threshold=ECHO_DEFAULT_THRESHOLD,
            min_group_size=ECHO_MIN_GROUP_SIZE,
        )
        save_echoes(echoes, ECHO_DEFAULT_THRESHOLD, ECHO_MIN_GROUP_SIZE)
        big = sum(1 for g in echoes if g["size"] >= 5)
        status(
            f"  Echoes: {len(echoes)} groups (>= {ECHO_MIN_GROUP_SIZE} members) "
            f"at cos >= {ECHO_DEFAULT_THRESHOLD}, "
            f"{big} with >= 5 members ({time.time() - t0:.1f}s)"
        )
    except Exception as e:
        status(f"  Echoes: skipped ({e})")

    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    (config.OUTPUT_DIR / "chunks.json").write_text(
        json.dumps(list(result.items), indent=2, default=str), encoding="utf-8"
    )

    clusters_json = [
        {
            "cluster_id": c.cluster_id,
            "label": c.label,
            "size": c.size,
            "centroid_2d": c.centroid,
            "representative_texts": c.representative_texts,
            "member_indices": c.member_indices,
        }
        for c in result.clusters
    ]
    (config.OUTPUT_DIR / "clusters.json").write_text(
        json.dumps(clusters_json, indent=2, default=str), encoding="utf-8"
    )

    status("=" * 60)
    status("Done. Open thoughtmap.html to explore your thoughts.")
    status("=" * 60)

    return result


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
