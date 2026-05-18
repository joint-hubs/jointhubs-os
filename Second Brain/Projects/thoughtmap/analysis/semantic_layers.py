"""Generate semantic layer artifacts for glossary, taxonomy, topology, and ontology."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from datetime import datetime
from typing import Callable

import thoughtmap.config as config
from thoughtmap.analysis.ner import Entity


def _status(on_status: Callable[[str], None] | None, message: str) -> None:
    if on_status:
        on_status(message)


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", (value or "").lower().strip())
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    return normalized or "item"


def _dedupe_preserve(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def _truncate(text: str, limit: int = 220) -> str:
    if not text:
        return ""
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def _compact_boundaries(text: str) -> str:
    if not text:
        return ""
    compact = re.sub(r"(?:^|\s)(CENTER|EDGES):\s*", "", text)
    compact = re.sub(r"\s+", " ", compact).strip()
    return _truncate(compact, limit=260)


def _jaccard(values_a: list[int] | list[str], values_b: list[int] | list[str]) -> float:
    set_a = set(values_a or [])
    set_b = set(values_b or [])
    if not set_a and not set_b:
        return 0.0
    union = len(set_a | set_b)
    if union == 0:
        return 0.0
    return len(set_a & set_b) / union


def _entity_overlap_score(entity_a: Entity, entity_b: Entity) -> float:
    cluster_score = _jaccard(entity_a.cluster_ids, entity_b.cluster_ids)
    source_score = _jaccard(entity_a.source_files, entity_b.source_files)
    return (0.75 * cluster_score) + (0.25 * source_score)


def _semantic_entity_group_key(entity: Entity) -> tuple[str, str]:
    return ((entity.type or "other").lower(), entity.normalized or _slugify(entity.name))


def _semantic_entity_ref(entity: Entity) -> str:
    return f"{(entity.type or 'other').lower()}-{_slugify(entity.name)}"


def _merge_entities_for_semantics(entities: list[Entity]) -> list[Entity]:
    grouped: dict[tuple[str, str], list[Entity]] = defaultdict(list)
    for entity in entities:
        grouped[_semantic_entity_group_key(entity)].append(entity)

    merged_entities: list[Entity] = []
    for members in grouped.values():
        ordered = sorted(
            members,
            key=lambda item: (
                -(item.mention_count or 0),
                item.name.lower(),
                item.first_seen or "",
                tuple(sorted(item.cluster_ids)),
                tuple(sorted(item.source_files)),
            ),
        )
        if len(ordered) == 1:
            merged_entities.append(ordered[0])
            continue

        primary = ordered[0]
        alias_values = _dedupe_preserve([
            alias
            for item in ordered
            for alias in [item.name, *item.aliases]
            if alias
        ])
        aliases = [alias for alias in alias_values if alias != primary.name]

        cluster_ids = sorted({cluster_id for item in ordered for cluster_id in item.cluster_ids})
        source_files = _dedupe_preserve([
            source_file
            for item in ordered
            for source_file in item.source_files
            if source_file
        ])
        chunk_indices = sorted({chunk_index for item in ordered for chunk_index in item.chunk_indices})

        cluster_mentions: dict[int, int] = defaultdict(int)
        cluster_labels: dict[int, str] = {}
        for item in ordered:
            for cluster_id, mentions in item.cluster_mentions.items():
                cluster_mentions[int(cluster_id)] += mentions
            for cluster_id, label in item.cluster_labels.items():
                cluster_labels[int(cluster_id)] = label

        merged_entities.append(Entity(
            name=primary.name,
            type=primary.type,
            aliases=aliases,
            normalized=primary.normalized,
            cluster_ids=cluster_ids,
            source_files=source_files,
            mention_count=sum(item.mention_count for item in ordered),
            summary=next((item.summary for item in ordered if item.summary), primary.summary),
            first_seen=min((item.first_seen for item in ordered if item.first_seen), default=primary.first_seen),
            boundaries=next((item.boundaries for item in ordered if item.boundaries), primary.boundaries),
            area_context=next((item.area_context for item in ordered if item.area_context), primary.area_context),
            distinctive_signature=next(
                (item.distinctive_signature for item in ordered if item.distinctive_signature),
                primary.distinctive_signature,
            ),
            chunk_indices=chunk_indices,
            cluster_mentions=dict(sorted(cluster_mentions.items())),
            cluster_labels=dict(sorted(cluster_labels.items())),
        ))

    return sorted(merged_entities, key=lambda item: (item.name.lower(), item.type.lower()))


def _cluster_lookup(condensed: dict) -> dict[int, dict]:
    return {
        int(cluster.get("cluster_id", -1)): cluster
        for cluster in condensed.get("clusters", [])
        if cluster.get("cluster_id") is not None
    }


def _super_lookup(condensed: dict) -> tuple[dict[int, dict], dict[int, dict]]:
    super_by_id: dict[int, dict] = {}
    cluster_to_super: dict[int, dict] = {}
    for super_cluster in condensed.get("super_clusters", []):
        super_id = int(super_cluster.get("super_id", -1))
        super_by_id[super_id] = super_cluster
        for cluster_id in super_cluster.get("member_ids", []):
            cluster_to_super[int(cluster_id)] = super_cluster
    return super_by_id, cluster_to_super


def _topic_refs(entity: Entity, clusters_by_id: dict[int, dict]) -> list[dict]:
    refs: list[dict] = []
    for cluster_id in entity.cluster_ids:
        cluster = clusters_by_id.get(cluster_id)
        refs.append({
            "cluster_id": cluster_id,
            "label": cluster.get("label", f"Cluster {cluster_id}") if cluster else f"Cluster {cluster_id}",
            "mentions": entity.cluster_mentions.get(cluster_id, 0),
        })
    refs.sort(key=lambda item: (-item["mentions"], item["label"].lower()))
    return refs


def build_glossary(entities: list[Entity], condensed: dict) -> dict:
    clusters_by_id = _cluster_lookup(condensed)
    entries: list[dict] = []
    type_counts: dict[str, int] = defaultdict(int)

    for entity in sorted(entities, key=lambda item: item.name.lower()):
        topics = _topic_refs(entity, clusters_by_id)
        entry = {
            "slug": _semantic_entity_ref(entity),
            "name": entity.name,
            "type": entity.type,
            "summary": _truncate(entity.summary or _compact_boundaries(entity.boundaries), limit=260),
            "detail": _compact_boundaries(entity.boundaries),
            "aliases": _dedupe_preserve(entity.aliases),
            "mention_count": entity.mention_count,
            "first_seen": entity.first_seen,
            "topic_count": len(topics),
            "topics": topics,
            "source_count": len(entity.source_files),
            "sources": entity.source_files[:12],
        }
        entries.append(entry)
        type_counts[entity.type] += 1

    concepts = [
        {
            "slug": f"topic-{cluster['cluster_id']}",
            "name": cluster.get("label", f"Cluster {cluster['cluster_id']}"),
            "type": "topic",
            "summary": _truncate(cluster.get("summary", ""), limit=220),
            "mention_count": cluster.get("size", 0),
            "cluster_id": cluster.get("cluster_id"),
            "date_min": cluster.get("date_min", ""),
            "date_max": cluster.get("date_max", ""),
        }
        for cluster in sorted(
            condensed.get("clusters", []),
            key=lambda value: (-value.get("size", 0), value.get("label", "").lower()),
        )
    ]

    return {
        "generated": datetime.now().isoformat(),
        "count": len(entries),
        "type_counts": dict(sorted(type_counts.items())),
        "entries": entries,
        "concepts": concepts,
    }


def _entity_bucket(entity: Entity) -> str:
    breadth = len(entity.cluster_ids)
    if breadth >= 6:
        return "hub"
    if breadth >= 3:
        return "cross-topic"
    if breadth == 2:
        return "multi-topic"
    return "single-topic"


def build_taxonomy(entities: list[Entity], condensed: dict) -> dict:
    topic_tree: list[dict] = []
    clusters_by_id = _cluster_lookup(condensed)

    for super_cluster in sorted(
        condensed.get("super_clusters", []),
        key=lambda value: (-value.get("total_size", 0), value.get("label", "").lower()),
    ):
        children = []
        for cluster_id in super_cluster.get("member_ids", []):
            cluster = clusters_by_id.get(int(cluster_id))
            if not cluster:
                continue
            children.append({
                "id": f"topic-{cluster['cluster_id']}",
                "cluster_id": cluster["cluster_id"],
                "label": cluster.get("label", f"Cluster {cluster['cluster_id']}"),
                "count": cluster.get("size", 0),
                "summary": _truncate(cluster.get("summary", ""), limit=200),
            })
        children.sort(key=lambda item: (-item["count"], item["label"].lower()))
        topic_tree.append({
            "id": f"mega-{super_cluster['super_id']}",
            "super_id": super_cluster["super_id"],
            "label": super_cluster.get("label", f"Mega-topic {super_cluster['super_id']}"),
            "count": super_cluster.get("total_size", 0),
            "summary": _truncate(super_cluster.get("summary", ""), limit=220),
            "children": children,
        })

    bucket_order = ["hub", "cross-topic", "multi-topic", "single-topic"]
    bucket_labels = {
        "hub": "Hub entities",
        "cross-topic": "Cross-topic",
        "multi-topic": "Multi-topic",
        "single-topic": "Single-topic",
    }
    entity_tree: list[dict] = []
    for entity_type in ["person", "organization", "project", "tool", "location"]:
        typed = [entity for entity in entities if entity.type == entity_type]
        if not typed:
            continue
        buckets: dict[str, list[Entity]] = defaultdict(list)
        for entity in typed:
            buckets[_entity_bucket(entity)].append(entity)
        children = []
        for bucket in bucket_order:
            members = sorted(
                buckets.get(bucket, []),
                key=lambda item: (-item.mention_count, item.name.lower()),
            )
            if not members:
                continue
            children.append({
                "id": f"{entity_type}-{bucket}",
                "label": bucket_labels[bucket],
                "count": len(members),
                "children": [
                    {
                        "id": f"entity-{_slugify(entity.name)}",
                        "slug": _semantic_entity_ref(entity),
                        "label": entity.name,
                        "mentions": entity.mention_count,
                        "topic_count": len(entity.cluster_ids),
                        "summary": _truncate(entity.summary, limit=180),
                    }
                    for entity in members
                ],
            })
        entity_tree.append({
            "id": entity_type,
            "label": entity_type.capitalize(),
            "count": len(typed),
            "children": children,
        })

    return {
        "generated": datetime.now().isoformat(),
        "topic_tree": topic_tree,
        "entity_tree": entity_tree,
        "stats": {
            "topic_roots": len(topic_tree),
            "entity_roots": len(entity_tree),
        },
    }


def build_topology(entities: list[Entity], condensed: dict) -> dict:
    clusters_by_id = _cluster_lookup(condensed)
    super_by_id, cluster_to_super = _super_lookup(condensed)

    nodes: list[dict] = []
    edges: list[dict] = []

    for super_cluster in condensed.get("super_clusters", []):
        nodes.append({
            "id": f"super:{super_cluster['super_id']}",
            "kind": "super_cluster",
            "label": super_cluster.get("label", f"Mega-topic {super_cluster['super_id']}"),
            "size": super_cluster.get("total_size", 0),
            "summary": _truncate(super_cluster.get("summary", ""), limit=180),
        })

    for cluster in condensed.get("clusters", []):
        nodes.append({
            "id": f"cluster:{cluster['cluster_id']}",
            "kind": "cluster",
            "label": cluster.get("label", f"Cluster {cluster['cluster_id']}"),
            "size": cluster.get("size", 0),
            "summary": _truncate(cluster.get("summary", ""), limit=180),
        })
        super_cluster = cluster_to_super.get(int(cluster["cluster_id"]))
        if super_cluster:
            edges.append({
                "id": f"contains:{super_cluster['super_id']}:{cluster['cluster_id']}",
                "source": f"super:{super_cluster['super_id']}",
                "target": f"cluster:{cluster['cluster_id']}",
                "relation": "contains",
                "weight": 1.0,
            })

    for entity in entities:
        entity_ref = _semantic_entity_ref(entity)
        nodes.append({
            "id": f"entity:{entity_ref}",
            "kind": "entity",
            "entity_type": entity.type,
            "entity_name": entity.name,
            "label": entity.name,
            "size": entity.mention_count,
            "summary": _truncate(entity.summary, limit=180),
        })
        for cluster_id in entity.cluster_ids:
            if cluster_id not in clusters_by_id:
                continue
            edges.append({
                "id": f"appears:{entity_ref}:{cluster_id}",
                "source": f"entity:{entity_ref}",
                "target": f"cluster:{cluster_id}",
                "relation": "appears_in",
                "weight": float(max(entity.cluster_mentions.get(cluster_id, 1), 1)),
            })

    for edge in condensed.get("edges", []):
        edges.append({
            "id": f"related:{edge['from']}:{edge['to']}",
            "source": f"cluster:{edge['from']}",
            "target": f"cluster:{edge['to']}",
            "relation": "related",
            "weight": float(edge.get("similarity", 0.0)),
        })

    for index, entity_a in enumerate(entities):
        for entity_b in entities[index + 1 :]:
            score = _entity_overlap_score(entity_a, entity_b)
            if score < config.SEMANTIC_ENTITY_EDGE_MIN:
                continue
            edges.append({
                "id": f"co:{_slugify(entity_a.name)}:{_slugify(entity_b.name)}",
                "source": f"entity:{_slugify(entity_a.name)}",
                "target": f"entity:{_slugify(entity_b.name)}",
                "relation": "co_occurs_with",
                "weight": round(score, 3),
            })

    return {
        "generated": datetime.now().isoformat(),
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "nodes": len(nodes),
            "edges": len(edges),
            "entity_edge_threshold": config.SEMANTIC_ENTITY_EDGE_MIN,
        },
    }


def _ordered_predicate(entity_a: Entity, entity_b: Entity) -> tuple[Entity, str, Entity]:
    types = frozenset({entity_a.type, entity_b.type})
    if types == {"person", "project"}:
        subject = entity_a if entity_a.type == "person" else entity_b
        obj = entity_b if subject is entity_a else entity_a
        return subject, "works_on", obj
    if types == {"project", "tool"}:
        subject = entity_a if entity_a.type == "project" else entity_b
        obj = entity_b if subject is entity_a else entity_a
        return subject, "uses", obj
    if types == {"person", "organization"}:
        subject = entity_a if entity_a.type == "person" else entity_b
        obj = entity_b if subject is entity_a else entity_a
        return subject, "affiliated_with", obj
    if types == {"organization", "project"}:
        subject = entity_a if entity_a.type == "organization" else entity_b
        obj = entity_b if subject is entity_a else entity_a
        return subject, "supports", obj
    if "location" in types and len(types) == 2:
        obj = entity_a if entity_a.type == "location" else entity_b
        subject = entity_b if obj is entity_a else entity_a
        return subject, "located_in", obj
    if entity_a.type == entity_b.type:
        subject, obj = sorted([entity_a, entity_b], key=lambda item: item.name.lower())
        return subject, "related_to", obj
    subject, obj = sorted([entity_a, entity_b], key=lambda item: item.name.lower())
    return subject, "associated_with", obj


def build_ontology(entities: list[Entity], condensed: dict) -> dict:
    clusters_by_id = _cluster_lookup(condensed)
    _, cluster_to_super = _super_lookup(condensed)
    classes = [
        {"id": "Entity", "label": "Entity", "parent": None, "description": "Named item extracted from notes and transcripts."},
        {"id": "Person", "label": "Person", "parent": "Entity", "description": "Human individual mentioned in the corpus."},
        {"id": "Organization", "label": "Organization", "parent": "Entity", "description": "Company, team, or institution."},
        {"id": "Project", "label": "Project", "parent": "Entity", "description": "Initiative, workstream, or product."},
        {"id": "Tool", "label": "Tool", "parent": "Entity", "description": "Software, framework, or operational tool."},
        {"id": "Location", "label": "Location", "parent": "Entity", "description": "Place or geography."},
        {"id": "Cluster", "label": "Topic", "parent": None, "description": "Topic cluster discovered in embedding space."},
        {"id": "SuperCluster", "label": "Mega-topic", "parent": None, "description": "Higher-level grouping of related topics."},
    ]
    predicates = [
        {"id": "instance_of", "domain": "Entity", "range": "Class"},
        {"id": "appears_in", "domain": "Entity", "range": "Cluster"},
        {"id": "belongs_to", "domain": "Cluster", "range": "SuperCluster"},
        {"id": "related_to", "domain": "Entity", "range": "Entity"},
        {"id": "works_on", "domain": "Person", "range": "Project"},
        {"id": "uses", "domain": "Project", "range": "Tool"},
        {"id": "affiliated_with", "domain": "Person", "range": "Organization"},
        {"id": "supports", "domain": "Organization", "range": "Project"},
        {"id": "located_in", "domain": "Entity", "range": "Location"},
        {"id": "associated_with", "domain": "Entity", "range": "Entity"},
    ]

    triples: list[dict] = []
    for entity in entities:
        class_id = entity.type.capitalize() if entity.type else "Entity"
        entity_ref = _semantic_entity_ref(entity)
        triples.append({
            "subject": f"entity:{entity_ref}",
            "predicate": "instance_of",
            "object": class_id,
            "label": entity.name,
            "confidence": 1.0,
        })
        for cluster_id in entity.cluster_ids:
            cluster = clusters_by_id.get(cluster_id)
            if not cluster:
                continue
            triples.append({
                "subject": f"entity:{entity_ref}",
                "predicate": "appears_in",
                "object": f"cluster:{cluster_id}",
                "object_label": cluster.get("label", f"Cluster {cluster_id}"),
                "confidence": 1.0,
                "evidence": {
                    "mentions": entity.cluster_mentions.get(cluster_id, 0),
                },
            })
            super_cluster = cluster_to_super.get(cluster_id)
            if super_cluster:
                triples.append({
                    "subject": f"cluster:{cluster_id}",
                    "predicate": "belongs_to",
                    "object": f"super:{super_cluster['super_id']}",
                    "object_label": super_cluster.get("label", f"Mega-topic {super_cluster['super_id']}"),
                    "confidence": 1.0,
                })

    pair_triples: list[dict] = []
    for index, entity_a in enumerate(entities):
        for entity_b in entities[index + 1 :]:
            score = _entity_overlap_score(entity_a, entity_b)
            if score < config.ONTOLOGY_ENTITY_EDGE_MIN:
                continue
            subject, predicate, obj = _ordered_predicate(entity_a, entity_b)
            shared_clusters = sorted(set(entity_a.cluster_ids) & set(entity_b.cluster_ids))[:8]
            shared_sources = _dedupe_preserve([
                source for source in entity_a.source_files if source in set(entity_b.source_files)
            ])[:6]
            pair_triples.append({
                "subject": f"entity:{_semantic_entity_ref(subject)}",
                "predicate": predicate,
                "object": f"entity:{_semantic_entity_ref(obj)}",
                "subject_label": subject.name,
                "object_label": obj.name,
                "confidence": round(min(0.97, 0.45 + score), 3),
                "evidence": {
                    "shared_clusters": shared_clusters,
                    "shared_sources": shared_sources,
                },
            })

    pair_triples.sort(key=lambda triple: (-triple["confidence"], triple["predicate"], triple["subject_label"], triple["object_label"]))
    triples.extend(pair_triples[: config.ONTOLOGY_MAX_TRIPLES])

    return {
        "generated": datetime.now().isoformat(),
        "classes": classes,
        "predicates": predicates,
        "triples": triples,
        "stats": {
            "classes": len(classes),
            "predicates": len(predicates),
            "triples": len(triples),
            "entity_edge_threshold": config.ONTOLOGY_ENTITY_EDGE_MIN,
        },
    }


def generate_semantic_artifacts(
    entities: list[Entity],
    condensed: dict,
    on_status: Callable[[str], None] | None = None,
) -> dict[str, dict]:
    """Generate and persist semantic layer outputs for the current run."""
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    semantic_entities = _merge_entities_for_semantics(entities)
    _status(on_status, f"  Semantic entities: {len(semantic_entities)} canonicalized from {len(entities)} raw")

    glossary = build_glossary(semantic_entities, condensed)
    config.GLOSSARY_PATH.write_text(json.dumps(glossary, indent=2, ensure_ascii=False), encoding="utf-8")
    _status(on_status, f"  Glossary: {config.GLOSSARY_PATH}")

    taxonomy = build_taxonomy(semantic_entities, condensed)
    config.TAXONOMY_PATH.write_text(json.dumps(taxonomy, indent=2, ensure_ascii=False), encoding="utf-8")
    _status(on_status, f"  Taxonomy: {config.TAXONOMY_PATH}")

    topology = build_topology(semantic_entities, condensed)
    config.TOPOLOGY_PATH.write_text(json.dumps(topology, indent=2, ensure_ascii=False), encoding="utf-8")
    _status(on_status, f"  Topology: {config.TOPOLOGY_PATH}")

    ontology = build_ontology(semantic_entities, condensed)
    config.ONTOLOGY_PATH.write_text(json.dumps(ontology, indent=2, ensure_ascii=False), encoding="utf-8")
    _status(on_status, f"  Ontology: {config.ONTOLOGY_PATH}")

    return {
        "glossary": glossary,
        "taxonomy": taxonomy,
        "topology": topology,
        "ontology": ontology,
    }