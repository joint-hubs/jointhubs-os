"""ThoughtMap — personal thought vector storage and visualization."""

from __future__ import annotations

from importlib import import_module

__all__ = [
	"config",
	"main",
	"AtomClassification",
	"Chunk",
	"DomainAssignment",
	"RoutingDecision",
	"TextSegment",
	"ThoughtAtom",
	"ClusterInfo",
	"ThoughtMapResult",
	"Entity",
	"extract_all",
	"chunk_all",
	"merge_similar_chunks",
	"embed_batch",
	"store_chunks",
	"load_all_embeddings",
	"cluster_all",
	"condense",
	"extract_entities",
	"generate_report",
	"save_report",
	"generate_cluster_indices",
	"generate_viz",
	"serve",
	"serve_static",
]

_EXPORTS = {
	"config": "thoughtmap.config",
	"main": "thoughtmap.run.main",
	"AtomClassification": "thoughtmap.core.models.AtomClassification",
	"Chunk": "thoughtmap.core.chunk.Chunk",
	"DomainAssignment": "thoughtmap.core.models.DomainAssignment",
	"RoutingDecision": "thoughtmap.core.models.RoutingDecision",
	"TextSegment": "thoughtmap.core.models.TextSegment",
	"ThoughtAtom": "thoughtmap.core.models.ThoughtAtom",
	"ClusterInfo": "thoughtmap.core.cluster.ClusterInfo",
	"ThoughtMapResult": "thoughtmap.core.cluster.ThoughtMapResult",
	"Entity": "thoughtmap.analysis.ner.Entity",
	"extract_all": "thoughtmap.core.extract.extract_all",
	"chunk_all": "thoughtmap.core.chunk.chunk_all",
	"merge_similar_chunks": "thoughtmap.core.chunk.merge_similar_chunks",
	"embed_batch": "thoughtmap.core.embed.embed_batch",
	"store_chunks": "thoughtmap.core.embed.store_chunks",
	"load_all_embeddings": "thoughtmap.core.embed.load_all_embeddings",
	"cluster_all": "thoughtmap.core.cluster.cluster_all",
	"condense": "thoughtmap.analysis.condense.condense",
	"extract_entities": "thoughtmap.analysis.ner.extract_entities",
	"generate_report": "thoughtmap.analysis.report.generate_report",
	"save_report": "thoughtmap.analysis.report.save_report",
	"generate_cluster_indices": "thoughtmap.analysis.index.generate_cluster_indices",
	"generate_viz": "thoughtmap.web.viz.generate_viz",
	"serve": "thoughtmap.web.server.serve",
	"serve_static": "thoughtmap.web.server.serve_static",
}


def __getattr__(name: str):
	target = _EXPORTS.get(name)
	if target is None:
		raise AttributeError(f"module 'thoughtmap' has no attribute {name!r}")

	if "." not in target:
		value = import_module(target)
	else:
		module_name, attr_name = target.rsplit(".", 1)
		module = import_module(module_name)
		value = getattr(module, attr_name)

	globals()[name] = value
	return value
