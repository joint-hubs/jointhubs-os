"""Post-clustering analysis helpers for ThoughtMap."""

from thoughtmap.analysis.condense import condense
from thoughtmap.analysis.index import generate_cluster_indices
from thoughtmap.analysis.report import generate_report, save_report

try:
    from thoughtmap.analysis.ner import Entity, extract_entities
except ModuleNotFoundError as exc:
    Entity = None  # type: ignore[assignment]

    def extract_entities(*args, **kwargs):
        raise ModuleNotFoundError(
            "thoughtmap.analysis.ner dependencies are not installed; "
            "NER is required for extract_entities()"
        ) from exc

__all__ = [
    "Entity",
    "condense",
    "extract_entities",
    "generate_cluster_indices",
    "generate_report",
    "save_report",
]