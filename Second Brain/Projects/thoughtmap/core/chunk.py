"""Smart chunking — sentence-boundary-aware splitting with overlap and semantic merge."""

from __future__ import annotations

import re
from dataclasses import dataclass

from thoughtmap.core.models import TextSegment, ThoughtAtom


@dataclass
class Chunk:
    """A processed text chunk ready for embedding."""
    text: str
    token_estimate: int
    timestamp_start: str     # ISO format
    timestamp_end: str | None
    source: str
    source_file: str
    section: str | None
    project_tag: str | None
    language: str | None
    intent: str | None       # "note" or None
    category: str | None     # "coding" | "browsing" | etc.
    wispr_app: str | None
    chunk_index: int         # position within the parent segment
    segment_id: str          # hash of original segment for dedup
    record_id: str | None = None
    atom_id: str | None = None
    parent_segment_id: str | None = None
    signal_type: str | None = None
    quality: str | None = None
    confidence: float | None = None


# ─── Text cleanup ───

_MARKDOWN_ARTIFACTS = re.compile(
    r"```[\s\S]*?```"        # code blocks
    r"|!\[\[.*?\]\]"         # obsidian embeds
    r"|\[\[.*?\]\]"          # wikilinks → keep text inside
    r"|^#+\s+"               # heading markers
    r"|^[-*]\s+\[.\]\s+"    # task markers
    r"|^>\s+"                # blockquote markers
    r"|---+"                 # horizontal rules
, re.MULTILINE)

_DATAVIEW_BLOCK = re.compile(r"```(?:dataview|tasks)[\s\S]*?```", re.MULTILINE)
_WIKILINK = re.compile(r"\[\[(.*?)(?:\|.*?)?\]\]")
_HTML_TAGS = re.compile(r"<[^>]+>")
_MULTI_WHITESPACE = re.compile(r"\s{2,}")
_BROKEN_WORD = re.compile(r"(\w)-\n(\w)")


def clean_text(text: str) -> str:
    """Clean markdown artifacts, fix broken words, normalize whitespace."""
    # Remove dataview/tasks blocks entirely
    text = _DATAVIEW_BLOCK.sub("", text)
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Resolve wikilinks to their display text
    text = _WIKILINK.sub(r"\1", text)
    # Strip HTML tags
    text = _HTML_TAGS.sub("", text)
    # Fix broken words at line boundaries
    text = _BROKEN_WORD.sub(r"\1\2", text)
    # Remove heading/list markers
    text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[-*]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^>\s+", "", text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r"^---+\s*$", "", text, flags=re.MULTILINE)
    # Normalize whitespace
    text = _MULTI_WHITESPACE.sub(" ", text)
    return text.strip()


# ─── Sentence splitting ───

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-ZĄĆĘŁŃÓŚŹŻ])")


def split_sentences(text: str) -> list[str]:
    """Split text into sentences, keeping boundaries clean."""
    sentences = _SENTENCE_END.split(text)
    return [s.strip() for s in sentences if s.strip()]


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~0.75 tokens per word for mixed en/pl content."""
    words = len(text.split())
    return int(words * 1.3)  # conservative: 1.3 tokens per word


# ─── Chunking ───

def chunk_segment(
    segment: TextSegment,
    target_tokens: int = 200,
    min_tokens: int = 40,
    overlap_sentences: int = 2,
) -> list[Chunk]:
    """Chunk a text segment with sentence-boundary-aware splitting and overlap."""
    import hashlib
    seg_id = hashlib.sha256(f"{segment.source}:{segment.source_file}:{segment.timestamp}".encode()).hexdigest()[:16]

    cleaned = clean_text(segment.text)
    if not cleaned or estimate_tokens(cleaned) < min_tokens:
        # Too short to chunk — keep as-is if non-trivial
        if cleaned and len(cleaned.split()) >= 3:
            return [Chunk(
                text=cleaned, token_estimate=estimate_tokens(cleaned),
                timestamp_start=segment.timestamp.isoformat(),
                timestamp_end=None, source=segment.source,
                source_file=segment.source_file, section=segment.section,
                project_tag=segment.project_tag, language=segment.language,
                intent=segment.intent, category=segment.category,
                wispr_app=segment.wispr_app, chunk_index=0, segment_id=seg_id,
            )]
        return []

    sentences = split_sentences(cleaned)
    if not sentences:
        return []

    # If entire segment fits in one chunk, return as-is
    total_tokens = estimate_tokens(cleaned)
    if total_tokens <= target_tokens * 1.3:
        return [Chunk(
            text=cleaned, token_estimate=total_tokens,
            timestamp_start=segment.timestamp.isoformat(),
            timestamp_end=None, source=segment.source,
            source_file=segment.source_file, section=segment.section,
            project_tag=segment.project_tag, language=segment.language,
            intent=segment.intent, category=segment.category,
            wispr_app=segment.wispr_app, chunk_index=0, segment_id=seg_id,
        )]

    # Multi-chunk: sliding window over sentences
    chunks: list[Chunk] = []
    i = 0
    chunk_idx = 0
    while i < len(sentences):
        # Accumulate sentences until we hit target
        chunk_sentences: list[str] = []
        token_count = 0
        j = i
        while j < len(sentences) and token_count < target_tokens:
            chunk_sentences.append(sentences[j])
            token_count += estimate_tokens(sentences[j])
            j += 1

        chunk_text = " ".join(chunk_sentences)
        if estimate_tokens(chunk_text) >= min_tokens:
            chunks.append(Chunk(
                text=chunk_text, token_estimate=estimate_tokens(chunk_text),
                timestamp_start=segment.timestamp.isoformat(),
                timestamp_end=None, source=segment.source,
                source_file=segment.source_file, section=segment.section,
                project_tag=segment.project_tag, language=segment.language,
                intent=segment.intent, category=segment.category,
                wispr_app=segment.wispr_app, chunk_index=chunk_idx,
                segment_id=seg_id,
            ))
            chunk_idx += 1

        # Advance by (consumed - overlap) sentences
        advance = max(1, len(chunk_sentences) - overlap_sentences)
        i += advance

    return chunks


def chunk_all(segments: list[TextSegment], target_tokens: int = 200,
              min_tokens: int = 40, overlap_sentences: int = 2) -> list[Chunk]:
    """Chunk all segments."""
    import thoughtmap.config as config
    chunks: list[Chunk] = []
    for seg in segments:
        chunks.extend(chunk_segment(
            seg,
            target_tokens=target_tokens or config.CHUNK_TARGET_TOKENS,
            min_tokens=min_tokens or config.CHUNK_MIN_TOKENS,
            overlap_sentences=overlap_sentences or config.CHUNK_OVERLAP_SENTENCES,
        ))
    return chunks


def chunk_atom(atom: ThoughtAtom) -> Chunk | None:
    """Convert a semantic ThoughtAtom into a single embedding-ready chunk.

    Thought atoms are already the semantic unit, so production migration keeps a
    one-to-one atom→record mapping instead of re-windowing them again.
    """
    cleaned = clean_text(atom.text)
    if not cleaned or len(cleaned.split()) < 3:
        return None

    return Chunk(
        text=cleaned,
        token_estimate=estimate_tokens(cleaned),
        timestamp_start=atom.timestamp or "",
        timestamp_end=None,
        source=atom.source,
        source_file=atom.source_file,
        section=atom.section,
        project_tag=atom.project_tag,
        language=atom.language,
        intent=atom.intent,
        category=atom.category,
        wispr_app=atom.wispr_app,
        chunk_index=0,
        segment_id=atom.parent_segment_id,
        record_id=f"atom:{atom.atom_id}",
        atom_id=atom.atom_id,
        parent_segment_id=atom.parent_segment_id,
        signal_type=atom.signal_type,
        quality=atom.quality,
        confidence=atom.confidence,
    )


def chunk_atoms(atoms: list[ThoughtAtom]) -> list[Chunk]:
    """Convert semantic ThoughtAtoms into embedding-ready chunks."""
    chunks: list[Chunk] = []
    for atom in atoms:
        chunk = chunk_atom(atom)
        if chunk is not None:
            chunks.append(chunk)
    return chunks


def merge_similar_chunks(chunks: list[Chunk], embeddings: list[list[float]],
                         threshold: float = 0.85) -> tuple[list[Chunk], list[list[float]]]:
    """Merge chunks that are semantically too similar (cosine > threshold).

    This is called AFTER embedding, so we have vectors to compare.
    Merges adjacent chunks from the same segment.
    """
    import numpy as np

    if len(chunks) < 2:
        return chunks, embeddings

    merged_chunks: list[Chunk] = []
    merged_embeddings: list[list[float]] = []
    skip = set()

    emb_array = np.array(embeddings)
    # Normalize for cosine similarity
    norms = np.linalg.norm(emb_array, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normalized = emb_array / norms

    for i in range(len(chunks)):
        if i in skip:
            continue
        current_chunk = chunks[i]
        current_emb = emb_array[i]

        # Check next chunk if from same segment
        if (i + 1 < len(chunks)
                and i + 1 not in skip
                and chunks[i + 1].segment_id == current_chunk.segment_id):
            sim = float(np.dot(normalized[i], normalized[i + 1]))
            if sim >= threshold:
                # Merge: concatenate text, average embedding
                merged_text = current_chunk.text + " " + chunks[i + 1].text
                merged_emb = ((current_emb + emb_array[i + 1]) / 2).tolist()
                current_chunk = Chunk(
                    text=merged_text,
                    token_estimate=current_chunk.token_estimate + chunks[i + 1].token_estimate,
                    timestamp_start=current_chunk.timestamp_start,
                    timestamp_end=chunks[i + 1].timestamp_start,
                    source=current_chunk.source,
                    source_file=current_chunk.source_file,
                    section=current_chunk.section,
                    project_tag=current_chunk.project_tag,
                    language=current_chunk.language,
                    intent=current_chunk.intent,
                    category=current_chunk.category,
                    wispr_app=current_chunk.wispr_app,
                    chunk_index=current_chunk.chunk_index,
                    segment_id=current_chunk.segment_id,
                )
                current_emb = merged_emb
                skip.add(i + 1)

        merged_chunks.append(current_chunk)
        merged_embeddings.append(current_emb if isinstance(current_emb, list) else current_emb.tolist())

    return merged_chunks, merged_embeddings
