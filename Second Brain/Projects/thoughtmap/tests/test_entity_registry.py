from thoughtmap.analysis.entities.registry import apply_kanban_alias_overrides_to_registry
from thoughtmap.analysis.entities.resolve import apply_manual_entity_decisions
from thoughtmap.analysis.ner import Entity, normalize_entity


def make_entity(name: str, entity_type: str = "person", aliases: list[str] | None = None) -> Entity:
    return Entity(
        name=name,
        type=entity_type,
        aliases=aliases or [],
        normalized=normalize_entity(name),
        cluster_ids=[1],
        source_files=["Second Brain/Operations/Reviews/2026-04-27-review.md"],
        mention_count=3,
        summary="",
        first_seen="2026-04-27",
    )


def test_rejected_entity_stays_rejected() -> None:
    registry = {
        "entities": {},
        "decisions": {
            normalize_entity("Acceptance Criteria"): {
                "action": "reject",
                "target_entity_id": None,
                "reason": "Generic concept, not a named entity.",
            }
        },
    }
    resolved = apply_manual_entity_decisions([make_entity("Acceptance Criteria", "organization")], registry)
    assert resolved == []


def test_alias_resolves_to_canonical_name() -> None:
    registry = apply_kanban_alias_overrides_to_registry(
        {"entities": {}, "decisions": {}},
        {
            normalize_entity("P. Vinci"): {
                "name": "Pietro Vinci",
                "type": "person",
                "aliases": ["P. Vinci", "Pietro"],
            }
        },
    )
    resolved = apply_manual_entity_decisions([make_entity("P. Vinci")], registry)
    assert len(resolved) == 1
    assert resolved[0].name == "Pietro Vinci"
    assert "P. Vinci" in resolved[0].aliases


def test_retype_changes_entity_type() -> None:
    registry = {
        "entities": {},
        "decisions": {
            normalize_entity("Fenix"): {
                "action": "retype",
                "target_entity_id": "project:fenix",
                "reason": "Treat as project, not organization.",
            }
        },
    }
    resolved = apply_manual_entity_decisions([make_entity("Fenix", "organization")], registry)
    assert resolved[0].type == "project"


def test_merge_collapses_two_entities() -> None:
    registry = {
        "entities": {
            "person:konrad-bujak": {
                "canonical_name": "Konrad Bujak",
                "type": "person",
                "aliases": ["Konrad", "K. Bujak"],
                "status": "verified",
                "source": "manual",
                "notes": "",
            }
        },
        "decisions": {
            normalize_entity("K. Bujak"): {
                "action": "merge",
                "target_entity_id": "person:konrad-bujak",
                "reason": "Merge short form into canonical person.",
            }
        },
    }
    resolved = apply_manual_entity_decisions([
        make_entity("K. Bujak"),
        make_entity("Konrad Bujak", aliases=["Konrad"]),
    ], registry)
    assert len(resolved) == 1
    assert resolved[0].name == "Konrad Bujak"
    assert "K. Bujak" in resolved[0].aliases


def test_manual_registry_beats_automatic_entity_shape() -> None:
    registry = {
        "entities": {
            "tool:cursor": {
                "canonical_name": "Cursor",
                "type": "tool",
                "aliases": [],
                "status": "verified",
                "source": "manual",
                "notes": "",
            }
        },
        "decisions": {
            normalize_entity("Cursor"): {
                "action": "verify",
                "target_entity_id": "tool:cursor",
                "reason": "Manual tool classification wins over automatic guess.",
            }
        },
    }
    resolved = apply_manual_entity_decisions([make_entity("Cursor", "organization")], registry)
    assert resolved[0].type == "tool"