"""ThoughtMap web server — runs pipeline then serves the interactive visualization.

Start with:  python -m thoughtmap server
Or via Docker Compose (preferred).
"""

from __future__ import annotations

import json
import os
import socketserver
import threading
import time
import traceback
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

import thoughtmap.config as config

# ─── Global pipeline state (read by the HTTP handler) ───

_state = {
    "phase": "starting",       # starting | waiting | pulling | running | done | error
    "message": "Initializing...",
    "step": "",                 # current pipeline step text
    "error": None,
}
_state_lock = threading.Lock()


def _set_state(phase: str, message: str, step: str = ""):
    with _state_lock:
        _state["phase"] = phase
        _state["message"] = message
        _state["step"] = step


def _set_error(message: str):
    with _state_lock:
        _state["phase"] = "error"
        _state["message"] = message
        _state["error"] = message


# ─── Loading page served while the pipeline runs ───

LOADING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ThoughtMap — Loading</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0d1117; color: #c9d1d9;
    display: flex; align-items: center; justify-content: center;
    height: 100vh;
  }
  .card {
    background: #161b22; border: 1px solid #30363d; border-radius: 12px;
    padding: 48px 56px; text-align: center; max-width: 480px;
  }
  h1 { font-size: 28px; margin-bottom: 8px; }
  .subtitle { color: #8b949e; font-size: 14px; margin-bottom: 32px; }
  .spinner {
    width: 48px; height: 48px; border: 3px solid #30363d;
    border-top-color: #58a6ff; border-radius: 50%;
    animation: spin 1s linear infinite; margin: 0 auto 24px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  #status { font-size: 15px; color: #c9d1d9; margin-bottom: 8px; min-height: 22px; }
  #step { font-size: 13px; color: #8b949e; min-height: 18px; }
  .error { color: #f85149; }
  .done { color: #3fb950; }
</style>
</head>
<body>
<div class="card">
  <h1>ThoughtMap</h1>
  <p class="subtitle">Personal Thought Vector Visualization</p>
  <div class="spinner" id="spinner"></div>
  <div id="status">Initializing...</div>
  <div id="step"></div>
</div>
<script>
async function poll() {
  try {
    const r = await fetch('/api/status');
    const d = await r.json();
    document.getElementById('status').textContent = d.message;
    document.getElementById('step').textContent = d.step || '';

    if (d.phase === 'done') {
      document.getElementById('spinner').style.display = 'none';
      document.getElementById('status').className = 'done';
      document.getElementById('status').textContent = 'Ready! Redirecting...';
      setTimeout(() => { window.location.href = '/'; }, 800);
      return;
    }
    if (d.phase === 'error') {
      document.getElementById('spinner').style.display = 'none';
      document.getElementById('status').className = 'error';
      return;
    }
  } catch (e) { /* server may not be ready yet */ }
  setTimeout(poll, 1500);
}
poll();
</script>
</body>
</html>
"""


# ─── HTTP Request Handler ───

class ThoughtMapHandler(SimpleHTTPRequestHandler):
    """Serves loading page during pipeline, then the visualization."""

    _spa_routes = {
        "/",
        "/index.html",
        "/entities",
        "/glossary",
        "/taxonomy",
        "/echoes",
        "/annotate",
    }

    def __init__(self, *args, output_dir: str, **kwargs):
        self._output_dir = output_dir
        super().__init__(*args, directory=output_dir, **kwargs)

    def do_GET(self):
        request_path = urlparse(self.path).path

        # Status API endpoint
        if self.path == "/api/status":
            with _state_lock:
                payload = json.dumps(_state)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(payload.encode())
            return

        # Re-run trigger
        if self.path == "/api/rerun":
            t = threading.Thread(target=_run_pipeline, daemon=True)
            t.start()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return

        # Search API — semantic search over chunks
        if self.path.startswith("/api/search"):
            self._handle_search()
            return

        # Clusters list API
        if self.path.startswith("/api/clusters") and not self.path.startswith("/api/clusters/"):
            self._handle_clusters()
            return

        # Single cluster API
        if self.path.startswith("/api/clusters/"):
            self._handle_cluster_detail()
            return

        # Cluster thoughts API — all chunks for a cluster
        if self.path.startswith("/api/cluster-thoughts/"):
            self._handle_cluster_thoughts()
            return

        # Entities list API
        if self.path == "/api/entities" or self.path.startswith("/api/entities?"):
            self._handle_entities()
            return

        # Single entity detail API
        if self.path.startswith("/api/entities/"):
            self._handle_entity_detail()
            return

        # Directories list API (for note creation)
        if self.path == "/api/directories":
            self._handle_directories()
            return

        # Echoes list API
        if self.path == "/api/echoes" or self.path.startswith("/api/echoes?"):
            self._handle_echoes_list()
            return

        # Annotation UI — serve standalone HTML page
        if request_path == "/annotate":
            self._handle_annotation_ui()
            return

        # Annotation tasks API
        if self.path == "/api/annotations/tasks" or self.path.startswith("/api/annotations/tasks?"):
            self._handle_annotation_tasks()
            return

        # Annotation stats API
        if self.path == "/api/annotations/stats":
            self._handle_annotation_stats()
            return

        # Root path
        if request_path in self._spa_routes:
            with _state_lock:
                phase = _state["phase"]

            if phase == "done":
                viz = Path(self._output_dir) / "thoughtmap-condensed.html"
                if viz.exists():
                    self.path = "/thoughtmap-condensed.html"
                    return super().do_GET()
                # Fallback to original if condensed not available
                viz = Path(self._output_dir) / "thoughtmap.html"
                if viz.exists():
                    self.path = "/thoughtmap.html"
                    return super().do_GET()

            # Otherwise serve loading page
            content = LOADING_HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
            return

        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/notes":
            self._handle_create_note()
            return
        if self.path == "/api/query":
            self._handle_query()
            return
        if self.path.startswith("/api/echoes/"):
            self._handle_echo_catalog()
            return
        if self.path.startswith("/api/annotations/tasks/"):
            self._handle_annotation_save()
            return
        if self.path == "/api/annotations/generate":
            self._handle_annotation_generate()
            return
        self.send_error(404)

    def _json_response(self, data: dict | list, status_code: int = 200):
        payload = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(payload)

    def _handle_search(self):
        """GET /api/search?q=...&n=10 — semantic search over ChromaDB."""
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        query = params.get("q", [""])[0]
        n_results = min(int(params.get("n", ["10"])[0]), 50)

        if not query:
            self._json_response({"error": "Missing ?q= parameter"}, 400)
            return

        try:
            from thoughtmap.core.embed import get_chroma_client, embed_text
            client = get_chroma_client()
            collection = client.get_collection(name=config.CHROMA_COLLECTION)
        except Exception as e:
            self._json_response({"error": f"ChromaDB error: {e}"}, 500)
            return

        try:
            query_embedding = embed_text(query)
        except Exception as e:
            self._json_response({"error": f"Embedding failed: {e}"}, 500)
            return

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        items = []
        for i in range(len(results["ids"][0])):
            meta = results["metadatas"][0][i] or {}
            items.append({
                "text": results["documents"][0][i],
                "source_file": meta.get("source_file", ""),
                "source": meta.get("source", ""),
                "timestamp": meta.get("timestamp", ""),
                "section": meta.get("section", ""),
                "project_tag": meta.get("project_tag", ""),
                "category": meta.get("category", ""),
                "distance": round(results["distances"][0][i], 4),
            })

        self._json_response({"results": items, "query": query, "count": len(items)})

    def _handle_clusters(self):
        """GET /api/clusters?domain=... — list all clusters."""
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        domain = params.get("domain", [""])[0].lower()

        clusters_path = Path(self._output_dir) / "clusters.json"
        if not clusters_path.exists():
            self._json_response({"error": "No clusters.json found"}, 404)
            return

        with open(clusters_path, "r", encoding="utf-8") as f:
            clusters = json.load(f)

        items = []
        for c in clusters:
            label = c.get("label", "")
            if domain and domain not in label.lower():
                continue
            items.append({
                "cluster_id": c["cluster_id"],
                "label": label,
                "size": c["size"],
            })

        items.sort(key=lambda x: x["size"], reverse=True)
        self._json_response({"clusters": items, "count": len(items)})

    def _handle_cluster_detail(self):
        """GET /api/clusters/<id> — get cluster detail."""
        try:
            cluster_id = int(self.path.split("/api/clusters/")[1].split("?")[0])
        except (ValueError, IndexError):
            self._json_response({"error": "Invalid cluster ID"}, 400)
            return

        clusters_path = Path(self._output_dir) / "clusters.json"
        if not clusters_path.exists():
            self._json_response({"error": "No clusters.json found"}, 404)
            return

        with open(clusters_path, "r", encoding="utf-8") as f:
            clusters = json.load(f)

        for c in clusters:
            if c["cluster_id"] == cluster_id:
                self._json_response({
                    "cluster_id": c["cluster_id"],
                    "label": c.get("label", ""),
                    "size": c["size"],
                    "representative_texts": c.get("representative_texts", []),
                })
                return

        self._json_response({"error": f"Cluster {cluster_id} not found"}, 404)

    def _handle_cluster_thoughts(self):
        """GET /api/cluster-thoughts/<id> — all chunks belonging to a cluster."""
        try:
            cluster_id = int(self.path.split("/api/cluster-thoughts/")[1].split("?")[0])
        except (ValueError, IndexError):
            self._json_response({"error": "Invalid cluster ID"}, 400)
            return

        clusters_path = Path(self._output_dir) / "clusters.json"
        chunks_path = Path(self._output_dir) / "chunks.json"
        if not clusters_path.exists() or not chunks_path.exists():
            self._json_response({"error": "Data files not found"}, 404)
            return

        with open(clusters_path, "r", encoding="utf-8") as f:
            clusters = json.load(f)
        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        cluster = None
        for c in clusters:
            if c["cluster_id"] == cluster_id:
                cluster = c
                break

        if cluster is None:
            self._json_response({"error": f"Cluster {cluster_id} not found"}, 404)
            return

        member_indices = cluster.get("member_indices", [])
        thoughts = []
        for idx in member_indices:
            if 0 <= idx < len(chunks):
                ch = chunks[idx]
                thoughts.append({
                    "idx": idx,
                    "text": ch.get("text", "")[:500],
                    "timestamp": ch.get("timestamp", ""),
                    "source": ch.get("source", ""),
                    "source_file": ch.get("source_file", ""),
                    "section": ch.get("section", ""),
                    "repeat_count": ch.get("repeat_count", 1),
                })

        self._json_response({
            "cluster_id": cluster_id,
            "label": cluster.get("label", ""),
            "size": cluster.get("size", 0),
            "thoughts": thoughts,
            "count": len(thoughts),
        })

    def _load_entities(self):
        """Load entities.json from output directory."""
        entities_path = Path(self._output_dir) / "entities.json"
        if not entities_path.exists():
            return None
        with open(entities_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _handle_entities(self):
        """GET /api/entities — list all entities."""
        entities = self._load_entities()
        if entities is None:
            self._json_response({"error": "No entities.json found"}, 404)
            return

        items = []
        for e in entities:
            items.append({
                "name": e.get("name", ""),
                "type": e.get("type", ""),
                "aliases": e.get("aliases", []),
                "mention_count": e.get("mention_count", 0),
                "cluster_ids": e.get("cluster_ids", []),
                "summary": e.get("summary", ""),
                "boundaries": e.get("boundaries", ""),
            })
        items.sort(key=lambda x: x["mention_count"], reverse=True)
        self._json_response({"entities": items, "count": len(items)})

    def _handle_entity_detail(self):
        """GET /api/entities/<name> — get entity detail by URL-encoded name."""
        try:
            from urllib.parse import unquote
            entity_name = unquote(self.path.split("/api/entities/")[1].split("?")[0])
        except (IndexError,):
            self._json_response({"error": "Invalid entity name"}, 400)
            return

        entities = self._load_entities()
        if entities is None:
            self._json_response({"error": "No entities.json found"}, 404)
            return

        entity_name_lower = entity_name.lower()
        for e in entities:
            if e.get("name", "").lower() == entity_name_lower or \
               e.get("normalized", "").lower() == entity_name_lower:
                self._json_response(e)
                return

        self._json_response({"error": f"Entity '{entity_name}' not found"}, 404)

    def _handle_directories(self):
        """GET /api/directories — list available target directories for notes."""
        sb_dir = Path(os.environ.get(
            "THOUGHTMAP_SECOND_BRAIN_DIR", str(config.SECOND_BRAIN_DIR)
        ))
        dirs = []
        for area in ("Projects", "Personal"):
            area_dir = sb_dir / area
            if area_dir.exists():
                for d in sorted(area_dir.iterdir()):
                    if d.is_dir() and not d.name.startswith('.') \
                       and d.name not in config.SECOND_BRAIN_EXCLUDE_DIRS:
                        dirs.append(f"{area}/{d.name}")
        self._json_response({"directories": dirs})

    def _handle_create_note(self):
        """POST /api/notes — create an Obsidian note in the Second Brain."""
        import re
        from datetime import date

        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 100_000:
            self._json_response({"error": "Payload too large"}, 413)
            return

        try:
            body = json.loads(self.rfile.read(content_length))
        except (json.JSONDecodeError, ValueError):
            self._json_response({"error": "Invalid JSON"}, 400)
            return

        title = str(body.get("title", "")).strip()
        content = str(body.get("content", "")).strip()
        directory = str(body.get("directory", "")).strip()

        if not title or not content or not directory:
            self._json_response(
                {"error": "title, content and directory are required"}, 400,
            )
            return

        # Sanitize filename — strip characters illegal on Windows / in URLs
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title).strip()
        if not safe_title:
            self._json_response({"error": "Invalid title after sanitization"}, 400)
            return

        sb_dir = Path(os.environ.get(
            "THOUGHTMAP_SECOND_BRAIN_DIR", str(config.SECOND_BRAIN_DIR)
        )).resolve()
        target_dir = (sb_dir / directory).resolve()

        # Path-traversal guard
        if not str(target_dir).startswith(str(sb_dir)):
            self._json_response({"error": "Invalid directory path"}, 400)
            return
        if not target_dir.is_dir():
            self._json_response(
                {"error": f"Directory not found: {directory}"}, 404,
            )
            return

        filepath = target_dir / f"{safe_title}.md"
        counter = 1
        while filepath.exists():
            filepath = target_dir / f"{safe_title} ({counter}).md"
            counter += 1

        today = date.today().isoformat()
        md = f"---\ncreated: {today}\nsource: thoughtmap\n---\n\n# {title}\n\n{content}\n"
        filepath.write_text(md, encoding="utf-8")

        rel_path = str(filepath.relative_to(sb_dir)).replace("\\", "/")
        self._json_response({"ok": True, "path": rel_path, "filename": filepath.name})

    def _handle_query(self):
        """POST /api/query — query thoughts in a cluster or super-cluster.

        Body JSON:
          mode: "latest" | "context"
          scope: "cluster" | "super"
          scope_id: int (cluster_id or super_id)
          query: str (required when mode="context")
          n: int (max results, default 10)
        """
        import numpy as np

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 50_000:
            self._json_response({"error": "Payload too large"}, 413)
            return

        try:
            body = json.loads(self.rfile.read(content_length))
        except (json.JSONDecodeError, ValueError):
            self._json_response({"error": "Invalid JSON"}, 400)
            return

        mode = body.get("mode", "latest")
        scope = body.get("scope", "cluster")
        scope_id = body.get("scope_id")
        query_text = str(body.get("query", "")).strip()
        n = min(int(body.get("n", 10)), 50)

        if scope_id is None:
            self._json_response({"error": "scope_id is required"}, 400)
            return
        if mode == "context" and not query_text:
            self._json_response({"error": "query is required for mode=context"}, 400)
            return

        # Load data
        chunks_path = Path(self._output_dir) / "chunks.json"
        clusters_path = Path(self._output_dir) / "clusters.json"
        condensed_path = Path(self._output_dir) / "condensed.json"
        if not chunks_path.exists() or not clusters_path.exists():
            self._json_response({"error": "Data files not found"}, 404)
            return

        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        with open(clusters_path, "r", encoding="utf-8") as f:
            clusters = json.load(f)

        # Resolve member indices for the requested scope
        if scope == "super":
            if not condensed_path.exists():
                self._json_response({"error": "condensed.json not found"}, 404)
                return
            with open(condensed_path, "r", encoding="utf-8") as f:
                condensed = json.load(f)
            sc = next(
                (s for s in condensed.get("super_clusters", [])
                 if s["super_id"] == scope_id),
                None,
            )
            if sc is None:
                self._json_response({"error": f"Super-cluster {scope_id} not found"}, 404)
                return
            member_indices = set()
            for cid in sc["member_ids"]:
                cl = next((c for c in clusters if c["cluster_id"] == cid), None)
                if cl:
                    member_indices.update(cl.get("member_indices", []))
            scope_label = sc["label"]
        else:
            cl = next((c for c in clusters if c["cluster_id"] == scope_id), None)
            if cl is None:
                self._json_response({"error": f"Cluster {scope_id} not found"}, 404)
                return
            member_indices = set(cl.get("member_indices", []))
            scope_label = cl.get("label", "")

        # Gather the subset of chunks
        subset = []
        for idx in member_indices:
            if 0 <= idx < len(chunks):
                ch = chunks[idx]
                subset.append({
                    "idx": idx,
                    "text": ch.get("text", ""),
                    "timestamp": ch.get("timestamp", ""),
                    "source": ch.get("source", ""),
                    "source_file": ch.get("source_file", ""),
                    "section": ch.get("section", ""),
                    "repeat_count": ch.get("repeat_count", 1),
                })

        if mode == "latest":
            # Sort by timestamp descending, return top N
            subset.sort(key=lambda x: x["timestamp"] or "", reverse=True)
            results = subset[:n]
            self._json_response({
                "mode": "latest",
                "scope": scope,
                "scope_label": scope_label,
                "results": results,
                "count": len(results),
                "total": len(subset),
            })
        else:
            # mode == "context": vectorize query, similarity search on subset
            try:
                from thoughtmap.core.embed import embed_text, load_all_embeddings
                query_embedding = np.array(embed_text(query_text))
            except Exception as e:
                self._json_response({"error": f"Embedding failed: {e}"}, 500)
                return

            # Load all embeddings and pick the subset
            try:
                all_items, all_embeddings = load_all_embeddings()
            except Exception as e:
                self._json_response({"error": f"Failed to load embeddings: {e}"}, 500)
                return

            # Build index mapping: chunk idx → embedding idx
            # chunks.json is the deduplicated list; all_embeddings is the raw ChromaDB load
            # We need to match by text since dedup may have reordered
            subset_embeddings = []
            subset_matched = []
            text_to_emb = {}
            for i, item in enumerate(all_items):
                key = (item.get("text", "") or "").strip()
                if key not in text_to_emb:
                    text_to_emb[key] = all_embeddings[i]

            for s in subset:
                key = (s["text"] or "").strip()
                emb = text_to_emb.get(key)
                if emb is not None:
                    subset_embeddings.append(emb)
                    subset_matched.append(s)

            if not subset_embeddings:
                self._json_response({
                    "mode": "context",
                    "scope": scope,
                    "scope_label": scope_label,
                    "query": query_text,
                    "results": [],
                    "count": 0,
                    "total": len(subset),
                })
                return

            # Cosine similarity
            emb_matrix = np.array(subset_embeddings)
            norms = np.linalg.norm(emb_matrix, axis=1)
            norms[norms == 0] = 1
            normed = emb_matrix / norms[:, np.newaxis]
            q_norm = query_embedding / (np.linalg.norm(query_embedding) or 1)
            similarities = normed @ q_norm

            top_indices = np.argsort(similarities)[::-1][:n]
            results = []
            for i in top_indices:
                item = subset_matched[i].copy()
                item["similarity"] = round(float(similarities[i]), 4)
                item["text"] = item["text"][:500]
                results.append(item)

            self._json_response({
                "mode": "context",
                "scope": scope,
                "scope_label": scope_label,
                "query": query_text,
                "results": results,
                "count": len(results),
                "total": len(subset),
            })

    def _handle_echoes_list(self):
        """GET /api/echoes?min_size=5&min_sim=0.95&status=all|observe|discard|neutral

        Returns near-duplicate thought groups merged with catalog state.
        """
        from thoughtmap.analysis.echoes import load_catalog

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        try:
            min_size = max(2, int(params.get("min_size", ["5"])[0]))
        except ValueError:
            min_size = 5
        try:
            min_sim = float(params.get("min_sim", ["0"])[0])
        except ValueError:
            min_sim = 0.0
        status_filter = params.get("status", ["all"])[0].lower()

        echoes_path = Path(self._output_dir) / "echoes.json"
        if not echoes_path.exists():
            self._json_response({
                "echoes": [],
                "count": 0,
                "threshold": None,
                "min_group_size": None,
                "message": "echoes.json not found — run the pipeline first",
            })
            return

        with open(echoes_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        catalog = load_catalog()
        groups = payload.get("echoes", [])
        merged = []
        for g in groups:
            if g["size"] < min_size:
                continue
            if g.get("min_similarity", 0) < min_sim:
                continue
            entry = catalog.get(g["echo_key"], {})
            status_value = entry.get("status", "neutral")
            if status_filter != "all" and status_value != status_filter:
                continue
            merged.append({
                **g,
                "status": status_value,
                "note": entry.get("note", ""),
                "catalog_updated": entry.get("updated"),
            })

        self._json_response({
            "echoes": merged,
            "count": len(merged),
            "total": len(groups),
            "threshold": payload.get("threshold"),
            "min_group_size": payload.get("min_group_size"),
            "generated_at": payload.get("generated_at"),
            "filters": {"min_size": min_size, "min_sim": min_sim, "status": status_filter},
        })

    def _handle_echo_catalog(self):
        """POST /api/echoes/<key> — set catalog status/note for a group."""
        from thoughtmap.analysis.echoes import set_catalog_entry

        try:
            echo_key_val = self.path.split("/api/echoes/")[1].split("?")[0]
        except IndexError:
            self._json_response({"error": "Missing echo key"}, 400)
            return
        if not echo_key_val or len(echo_key_val) > 64:
            self._json_response({"error": "Invalid echo key"}, 400)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 20_000:
            self._json_response({"error": "Payload too large"}, 413)
            return
        try:
            body = json.loads(self.rfile.read(content_length) or b"{}")
        except (json.JSONDecodeError, ValueError):
            self._json_response({"error": "Invalid JSON"}, 400)
            return

        status_value = str(body.get("status", "neutral")).lower()
        note = body.get("note")
        if note is not None:
            note = str(note)[:2000]
        try:
            entry = set_catalog_entry(echo_key_val, status=status_value, note=note)
        except ValueError as e:
            self._json_response({"error": str(e)}, 400)
            return
        self._json_response({"ok": True, "echo_key": echo_key_val, "entry": entry})

    # ── Annotation handlers ──────────────────────────────────────────────────

    def _handle_annotation_ui(self):
        """GET /annotate — serve the standalone annotation HTML page."""
        html_path = Path(__file__).parent / "annotate.html"
        if not html_path.exists():
            self._json_response({"error": "annotate.html not found"}, 404)
            return
        content = html_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content)

    def _handle_annotation_tasks(self):
        """GET /api/annotations/tasks?status=pending&limit=50&offset=0 — list tasks."""
        from thoughtmap.annotation.store import load_tasks, load_annotations

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        status_filter = params.get("status", ["all"])[0].lower()
        try:
            limit = min(int(params.get("limit", ["100"])[0]), 500)
            offset = max(0, int(params.get("offset", ["0"])[0]))
        except ValueError:
            limit, offset = 100, 0

        tasks = load_tasks()
        annotations = load_annotations()

        items = []
        for tid, task in tasks.items():
            ann = annotations.get(tid)
            status = "annotated" if ann else "pending"
            if status_filter != "all" and status != status_filter:
                continue
            entry = {**task, "status": status}
            if ann:
                entry["annotation"] = ann
            items.append(entry)

        # Uncertain types first, then by mention_count desc
        items.sort(key=lambda t: (
            0 if t.get("current_type") in {"location", "concept", "other"} else 1,
            -(t.get("mention_count") or 0),
        ))

        total = len(items)
        page = items[offset:offset + limit]
        self._json_response({
            "tasks": page,
            "total": total,
            "offset": offset,
            "limit": limit,
        })

    def _handle_annotation_stats(self):
        """GET /api/annotations/stats — annotation progress summary."""
        from thoughtmap.annotation.store import annotation_stats
        self._json_response(annotation_stats())

    def _handle_annotation_save(self):
        """POST /api/annotations/tasks/<task_id> — save one annotation."""
        from thoughtmap.annotation.store import save_annotation, load_tasks

        try:
            task_id = self.path.split("/api/annotations/tasks/")[1].split("?")[0]
        except IndexError:
            self._json_response({"error": "Missing task_id"}, 400)
            return
        if not task_id or len(task_id) > 64:
            self._json_response({"error": "Invalid task_id"}, 400)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 20_000:
            self._json_response({"error": "Payload too large"}, 413)
            return
        try:
            body = json.loads(self.rfile.read(content_length) or b"{}")
        except (json.JSONDecodeError, ValueError):
            self._json_response({"error": "Invalid JSON"}, 400)
            return

        decision = str(body.get("decision", "")).strip().lower()
        valid_decisions = {"verify", "reject", "retype", "merge", "alias", "unsure"}
        if decision not in valid_decisions:
            self._json_response(
                {"error": f"decision must be one of: {', '.join(sorted(valid_decisions))}"},
                400,
            )
            return

        entity_type = body.get("entity_type")
        if entity_type is not None:
            entity_type = str(entity_type).strip().lower()
            valid_types = {"person", "organization", "project", "tool", "location", "concept", "other"}
            if entity_type not in valid_types:
                self._json_response(
                    {"error": f"entity_type must be one of: {', '.join(sorted(valid_types))}"},
                    400,
                )
                return

        canonical_name = body.get("canonical_name")
        if canonical_name is not None:
            canonical_name = str(canonical_name).strip()[:200]

        reason = str(body.get("reason", "")).strip()[:500]

        # Validate task exists
        tasks = load_tasks()
        if task_id not in tasks:
            self._json_response({"error": f"Task '{task_id}' not found"}, 404)
            return

        record = save_annotation(
            task_id=task_id,
            decision=decision,
            entity_type=entity_type,
            canonical_name=canonical_name,
            reason=reason,
        )
        self._json_response({"ok": True, "annotation": record})

    def _handle_annotation_generate(self):
        """POST /api/annotations/generate — generate tasks from entities.json."""
        from thoughtmap.annotation.generate import generate_entity_tasks
        from thoughtmap.annotation.store import upsert_tasks

        content_length = int(self.headers.get("Content-Length", 0))
        body = {}
        if content_length > 0:
            try:
                body = json.loads(self.rfile.read(min(content_length, 4096)) or b"{}")
            except (json.JSONDecodeError, ValueError):
                pass

        min_mentions = max(1, int(body.get("min_mentions", 3)))
        only_uncertain = bool(body.get("only_uncertain", False))

        try:
            tasks = generate_entity_tasks(
                min_mentions=min_mentions,
                only_uncertain=only_uncertain,
            )
            added = upsert_tasks(tasks)
        except FileNotFoundError as e:
            self._json_response({"error": str(e)}, 404)
            return
        except Exception as e:
            self._json_response({"error": f"Generation failed: {e}"}, 500)
            return

        self._json_response({
            "ok": True,
            "generated": len(tasks),
            "added": added,
        })

    def log_message(self, format, *args):
        # Suppress noisy request logs; status polls are frequent
        if "/api/status" in str(args[0]):
            return
        super().log_message(format, *args)


# ─── Ollama readiness check ───

def _wait_for_ollama():
    """Wait for Ollama to be reachable and ensure the model is available."""
    _set_state("waiting", "Waiting for Ollama...", "Connecting to embedding server")

    for attempt in range(120):  # up to ~4 minutes
        try:
            resp = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if resp.ok:
                break
        except (requests.ConnectionError, requests.Timeout):
            pass
        time.sleep(2)
    else:
        raise RuntimeError(
            f"Ollama not reachable at {config.OLLAMA_BASE_URL} after 4 minutes"
        )

    # Check if model is already pulled
    resp = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=10)
    resp.raise_for_status()
    model_names = [m.get("name", "") for m in resp.json().get("models", [])]
    if config.EMBEDDING_MODEL not in model_names:
        _set_state("pulling", f"Pulling {config.EMBEDDING_MODEL}...",
                    "First run — downloading embedding model (~274 MB)")
        pull_resp = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/pull",
            json={"name": config.EMBEDDING_MODEL, "stream": False},
            timeout=600,
        )
        pull_resp.raise_for_status()

    _set_state("running", "Ollama ready", "Model loaded")


# ─── Pipeline runner (background thread) ───

def _run_pipeline():
    """Orchestrate: wait for Ollama → run pipeline → mark done."""
    try:
        _wait_for_ollama()

        # If we're already serving previous results, stay in "done" until
        # the pipeline actually needs to do heavy work (embedding).
        _set_state("running", "Running pipeline...", "Checking for new data...")

        def on_status(msg: str):
            with _state_lock:
                _state["step"] = msg
                _state["message"] = "Updating ThoughtMap output..."

        from thoughtmap.run import main
        result = main(on_status=on_status)

        if result is None:
            _set_state("done", "Pipeline finished (limited data)", "")
        else:
            _set_state("done", "Pipeline complete", "")

    except Exception as e:
        traceback.print_exc()
        _set_error(f"Pipeline failed: {e}")


# ─── Entry point ───

def serve():
    """Start the ThoughtMap server: run pipeline in background, serve results."""
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    port = config.SERVER_PORT
    handler = partial(ThoughtMapHandler, output_dir=str(config.OUTPUT_DIR))

    has_previous = (config.OUTPUT_DIR / "thoughtmap-condensed.html").exists() or (config.OUTPUT_DIR / "thoughtmap.html").exists()
    if has_previous:
        print("Previous output found — running refresh in background.")

    pipeline_thread = threading.Thread(target=_run_pipeline, daemon=True)
    pipeline_thread.start()

    # Start HTTP server (blocks)
    with socketserver.ThreadingTCPServer(("0.0.0.0", port), handler) as httpd:
        httpd.allow_reuse_address = True
        print(f"\n  ThoughtMap server: http://localhost:{port}")
        print(f"  Output directory:  {config.OUTPUT_DIR}")
        print()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")


def serve_static():
    """Serve the generated ThoughtMap output without re-running the pipeline."""
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    viz = config.OUTPUT_DIR / "thoughtmap-condensed.html"
    if not viz.exists():
        viz = config.OUTPUT_DIR / "thoughtmap.html"
    if not viz.exists():
        raise RuntimeError(
            f"Static UI not found in {config.OUTPUT_DIR}. Run the pipeline once first."
        )

    port = config.SERVER_PORT
    handler = partial(SimpleHTTPRequestHandler, directory=str(config.OUTPUT_DIR))

    with socketserver.ThreadingTCPServer(("0.0.0.0", port), handler) as httpd:
        httpd.allow_reuse_address = True
        print(f"\n  ThoughtMap static UI: http://localhost:{port}/{viz.name}")
        print(f"  Serving from:        {config.OUTPUT_DIR}")
        print()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")


if __name__ == "__main__":
    serve()
