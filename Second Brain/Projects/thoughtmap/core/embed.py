"""Embedding via Ollama / OpenAI / Google and ChromaDB storage."""

from __future__ import annotations

import hashlib
import json
import re
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import chromadb
import requests

import thoughtmap.config as config
from thoughtmap.core.chunk import Chunk


# ─── Embedding provider abstraction ───

_OLLAMA_MODEL_READY = False

def _ensure_ollama_model() -> None:
    """Check if the configured Ollama model is available; pull if not."""
    global _OLLAMA_MODEL_READY
    if _OLLAMA_MODEL_READY:
        return

    try:
        resp = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/show",
            json={"name": config.OLLAMA_EMBEDDING_MODEL},
            timeout=30,
        )
        if resp.status_code == 200:
            _OLLAMA_MODEL_READY = True
            return  # Model exists
    except requests.Timeout as exc:
        # The web server already validates model availability during startup.
        # If this probe stalls, let the actual embed call handle it with longer retries.
        print(f"  Warning: Ollama model probe timed out, continuing: {exc}")
        _OLLAMA_MODEL_READY = True
        return
    except requests.ConnectionError:
        raise RuntimeError(
            f"Cannot connect to Ollama at {config.OLLAMA_BASE_URL}. "
            "Is Ollama running?"
        )

    print(f"  Pulling model {config.OLLAMA_EMBEDDING_MODEL}...")
    resp = requests.post(
        f"{config.OLLAMA_BASE_URL}/api/pull",
        json={"name": config.OLLAMA_EMBEDDING_MODEL, "stream": False},
        timeout=1800,  # 30 min for large models
    )
    resp.raise_for_status()
    _OLLAMA_MODEL_READY = True
    print(f"  Model {config.OLLAMA_EMBEDDING_MODEL} ready.")


_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_OLLAMA_EMBED_TIMEOUT_SECONDS = 180
_OLLAMA_EMBED_RETRIES = 2
_OLLAMA_FALLBACK_CHAR_LIMITS = (4000, 2000, 1000, 400)


def _sanitize_embedding_text(text: str, max_chars: int = 4000) -> str:
    """Normalize text so embedding APIs don't choke on malformed payloads."""
    normalized = unicodedata.normalize("NFKC", text or "")
    no_surrogates = "".join(ch for ch in normalized if unicodedata.category(ch) != "Cs")
    no_controls = _CONTROL_CHARS.sub(" ", no_surrogates)
    compact = " ".join(no_controls.split())
    trimmed = compact[:max_chars].strip()
    return trimmed or " "


def _candidate_embedding_texts(text: str) -> list[str]:
    """Generate progressively safer fallbacks for stubborn Ollama inputs."""
    candidates: list[str] = []
    seen: set[str] = set()
    for limit in _OLLAMA_FALLBACK_CHAR_LIMITS:
        candidate = _sanitize_embedding_text(text, max_chars=limit)
        if candidate not in seen:
            seen.add(candidate)
            candidates.append(candidate)
    if " " not in seen:
        candidates.append(" ")
    return candidates


def _fit_embedding_dimensions(embedding: list[float]) -> list[float]:
    """Fit Ollama embeddings to the configured collection dimension."""
    target_dimensions = config.EMBEDDING_DIMENSIONS
    if target_dimensions <= 0 or len(embedding) <= target_dimensions:
        return embedding

    fitted = embedding[:target_dimensions]
    norm = sum(value * value for value in fitted) ** 0.5
    if norm == 0:
        return fitted
    return [value / norm for value in fitted]


def _post_ollama_embed(batch: list[str], timeout: int) -> list[list[float]]:
    """Send one embedding request and validate the response shape."""
    resp = requests.post(
        f"{config.OLLAMA_BASE_URL}/api/embed",
        json={"model": config.OLLAMA_EMBEDDING_MODEL, "input": batch},
        timeout=timeout,
    )
    resp.raise_for_status()

    body = resp.json()
    embeddings = body.get("embeddings")
    if not isinstance(embeddings, list) or len(embeddings) != len(batch):
        raise RuntimeError(
            f"Unexpected Ollama embed response for {config.OLLAMA_EMBEDDING_MODEL}: {body}"
        )
    return [_fit_embedding_dimensions(embedding) for embedding in embeddings]


def _embed_ollama_single(text: str, index: int) -> list[float]:
    """Embed one text with retries and shorter fallbacks for bad payloads."""
    last_error: Exception | None = None

    for candidate_index, candidate in enumerate(_candidate_embedding_texts(text)):
        for attempt in range(_OLLAMA_EMBED_RETRIES + 1):
            try:
                embedding = _post_ollama_embed([candidate], timeout=_OLLAMA_EMBED_TIMEOUT_SECONDS)[0]
                if candidate_index > 0 or attempt > 0:
                    print(
                        f"  Warning: recovered embedding for item {index} "
                        f"using fallback #{candidate_index + 1}"
                    )
                return embedding
            except (requests.ConnectionError, requests.Timeout) as exc:
                last_error = exc
                if attempt < _OLLAMA_EMBED_RETRIES:
                    time.sleep(attempt + 1)
                    continue
                break
            except requests.HTTPError as exc:
                last_error = exc
                status = exc.response.status_code if exc.response is not None else None
                if status is not None and status >= 500 and attempt < _OLLAMA_EMBED_RETRIES:
                    time.sleep(attempt + 1)
                    continue
                break
            except RuntimeError as exc:
                last_error = exc
                break

    preview = repr(_sanitize_embedding_text(text, max_chars=200))
    raise RuntimeError(
        f"Ollama embedding failed for item {index} "
        f"(len={len(text)}, preview={preview}): {last_error}"
    ) from last_error


def _embed_ollama(texts: list[str], batch_size: int | None = None) -> list[list[float]]:
    """Embed via Ollama local API in parallel small batches, with single-item fallback."""
    effective_batch_size = max(1, batch_size or config.OLLAMA_EMBED_BATCH_SIZE)
    concurrency = max(1, config.OLLAMA_EMBED_CONCURRENCY)
    batches = [
        (start, texts[start:start + effective_batch_size])
        for start in range(0, len(texts), effective_batch_size)
    ]

    def embed_one_batch(start: int, batch: list[str]) -> tuple[int, list[list[float]]]:
        try:
            return start, _post_ollama_embed(batch, timeout=_OLLAMA_EMBED_TIMEOUT_SECONDS)
        except Exception as exc:
            print(
                f"  Warning: Ollama batch embedding failed at {start}-{start + len(batch) - 1}; "
                f"falling back to single-item retries ({exc})"
            )
            fallback_embeddings = [
                _embed_ollama_single(text, start + offset)
                for offset, text in enumerate(batch)
            ]
            return start, fallback_embeddings

    if concurrency == 1 or len(batches) <= 1:
        return [
            embedding
            for start, batch in batches
            for embedding in embed_one_batch(start, batch)[1]
        ]

    completed: dict[int, list[list[float]]] = {}
    with ThreadPoolExecutor(max_workers=min(concurrency, len(batches))) as executor:
        futures = [
            executor.submit(embed_one_batch, start, batch)
            for start, batch in batches
        ]
        for future in as_completed(futures):
            start, embeddings = future.result()
            completed[start] = embeddings

    all_embeddings: list[list[float]] = []
    for start, _batch in batches:
        all_embeddings.extend(completed[start])
    return all_embeddings


def _embed_openai(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """Embed via OpenAI Embeddings API."""
    import openai  # pyright: ignore[reportMissingImports]
    client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    all_embs: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        resp = client.embeddings.create(
            model=config.OPENAI_EMBEDDING_MODEL,
            input=batch,
            dimensions=config.EMBEDDING_DIMENSIONS,
        )
        all_embs.extend([d.embedding for d in resp.data])
    return all_embs


def _embed_google(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """Embed via Google Generative AI API."""
    import google.generativeai as genai  # pyright: ignore[reportMissingImports]
    genai.configure(api_key=config.GOOGLE_API_KEY)
    all_embs: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        result = genai.embed_content(
            model=f"models/{config.GOOGLE_EMBEDDING_MODEL}",
            content=batch,
            output_dimensionality=config.EMBEDDING_DIMENSIONS,
        )
        all_embs.extend(result["embedding"])
    return all_embs


_PROVIDERS = {
    "ollama": _embed_ollama,
    "openai": _embed_openai,
    "google": _embed_google,
}


# Max characters per text for embedding (conservative for multi-byte languages)
_MAX_TEXT_CHARS = 4000


def embed_text(text: str) -> list[float]:
    """Get embedding for a single text using the configured provider."""
    return embed_batch([text])[0]


def embed_batch(texts: list[str], batch_size: int | None = None) -> list[list[float]]:
    """Embed a batch of texts using the configured provider."""
    provider = config.EMBEDDING_PROVIDER
    fn = _PROVIDERS.get(provider)
    if fn is None:
        raise ValueError(f"Unknown EMBEDDING_PROVIDER: {provider!r}. Choose: {', '.join(_PROVIDERS)}")
    # Auto-pull Ollama model if needed
    if provider == "ollama":
        _ensure_ollama_model()
    # Truncate overly long texts to fit model context window
    safe_texts = [_sanitize_embedding_text(t, max_chars=_MAX_TEXT_CHARS) for t in texts]
    kwargs = {}
    if batch_size is not None:
        kwargs["batch_size"] = batch_size
    return fn(safe_texts, **kwargs)


# ─── ChromaDB storage ───

def get_chroma_client() -> chromadb.ClientAPI:
    """Get persistent ChromaDB client."""
    config.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(config.CHROMA_DIR))


def get_or_create_collection(client: chromadb.ClientAPI) -> chromadb.Collection:
    """Get or create the thoughtmap collection."""
    return client.get_or_create_collection(
        name=config.CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def chunk_id(chunk: Chunk) -> str:
    """Deterministic ID for a chunk (for dedup in ChromaDB)."""
    if chunk.record_id:
        return chunk.record_id
    content = f"{chunk.segment_id}:{chunk.chunk_index}:{chunk.text[:100]}"
    return hashlib.sha256(content.encode()).hexdigest()[:24]


def chunk_metadata(chunk: Chunk) -> dict:
    """Convert chunk to ChromaDB metadata dict."""
    meta = {
        "timestamp": chunk.timestamp_start,
        "source": chunk.source,
        "source_file": chunk.source_file,
        "token_estimate": chunk.token_estimate,
    }
    if chunk.section:
        meta["section"] = chunk.section
    if chunk.project_tag:
        meta["project_tag"] = chunk.project_tag
    if chunk.language:
        meta["language"] = chunk.language
    if chunk.intent:
        meta["intent"] = chunk.intent
    if chunk.category:
        meta["category"] = chunk.category
    if chunk.wispr_app:
        meta["wispr_app"] = chunk.wispr_app
    if chunk.timestamp_end:
        meta["timestamp_end"] = chunk.timestamp_end
    if chunk.atom_id:
        meta["atom_id"] = chunk.atom_id
    if chunk.parent_segment_id:
        meta["parent_segment_id"] = chunk.parent_segment_id
    if chunk.signal_type:
        meta["signal_type"] = chunk.signal_type
    if chunk.quality:
        meta["quality"] = chunk.quality
    if chunk.confidence is not None:
        meta["confidence"] = float(chunk.confidence)
    return meta


def store_chunks(chunks: list[Chunk], embeddings: list[list[float]]) -> int:
    """Store chunks and embeddings in ChromaDB. Returns count of new items added."""
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    ids = [chunk_id(c) for c in chunks]
    documents = [c.text for c in chunks]
    metadatas = [chunk_metadata(c) for c in chunks]

    # Filter out already-existing IDs
    existing = set()
    try:
        result = collection.get(ids=ids)
        existing = {id_ for id_ in result["ids"]}
    except Exception:
        pass

    seen = set()
    new_ids, new_docs, new_metas, new_embs = [], [], [], []
    for i, id_ in enumerate(ids):
        if id_ not in existing and id_ not in seen:
            seen.add(id_)
            new_ids.append(id_)
            new_docs.append(documents[i])
            new_metas.append(metadatas[i])
            new_embs.append(embeddings[i])

    if new_ids:
        # ChromaDB has a max batch size (~5461); add in chunks
        batch_size = 5000
        for start in range(0, len(new_ids), batch_size):
            end = start + batch_size
            collection.add(
                ids=new_ids[start:end],
                documents=new_docs[start:end],
                metadatas=new_metas[start:end],
                embeddings=new_embs[start:end],
            )

    return len(new_ids)


def _append_loaded_batch(
    result: dict,
    items: list[dict],
    embeddings: list[list[float]],
) -> None:
    """Normalize one ChromaDB batch into clustering payloads."""
    for i, id_ in enumerate(result.get("ids", [])):
        item = {
            "id": id_,
            "text": result["documents"][i],
            **result["metadatas"][i],
        }
        items.append(item)
        embeddings.append(result["embeddings"][i])


def load_all_embeddings(
    ids: list[str] | None = None,
    batch_size: int = 5000,
) -> tuple[list[dict], list[list[float]]]:
    """Load chunks and embeddings from ChromaDB for clustering."""
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    items: list[dict] = []
    embeddings: list[list[float]] = []

    if ids is not None:
        requested_ids = set(ids)
        total = collection.count()
        for offset in range(0, total, batch_size):
            result = collection.get(
                include=["documents", "metadatas", "embeddings"],
                limit=batch_size,
                offset=offset,
            )
            matching_indexes = [
                i for i, id_ in enumerate(result.get("ids", []))
                if id_ in requested_ids
            ]
            if not matching_indexes:
                continue

            filtered_result = {
                "ids": [result["ids"][i] for i in matching_indexes],
                "documents": [result["documents"][i] for i in matching_indexes],
                "metadatas": [result["metadatas"][i] for i in matching_indexes],
                "embeddings": [result["embeddings"][i] for i in matching_indexes],
            }
            _append_loaded_batch(filtered_result, items, embeddings)
        return items, embeddings

    total = collection.count()
    for offset in range(0, total, batch_size):
        result = collection.get(
            include=["documents", "metadatas", "embeddings"],
            limit=batch_size,
            offset=offset,
        )
        _append_loaded_batch(result, items, embeddings)

    return items, embeddings
