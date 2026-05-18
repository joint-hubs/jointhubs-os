---
applyTo: "Second Brain/Projects/thoughtmap/**"
---

# ThoughtMap Instructions

> Auto-loaded when working in `Second Brain/Projects/thoughtmap/`

## Project Rules

1. Read `CONTEXT.md` before making architectural changes
2. Keep the root package lean: `config.py`, `run.py`, `__main__.py`, `__init__.py`
3. Put pipeline stages in `core/`, post-processing in `analysis/`, and HTTP/UI code in `web/`
4. Use full package imports everywhere: `thoughtmap.core.*`, `thoughtmap.analysis.*`, `thoughtmap.web.*`
5. Preserve local-first defaults; any cloud provider must remain explicit and opt-in

## Data Boundaries

- ThoughtMap itself is local-first: Ollama, ChromaDB, local markdown, local SQLite
- External Obsidian Vault and Wispr Flow are optional local sources when configured
- GitHub Copilot usage is separate from ThoughtMap runtime and may use cloud-hosted models

## NER Rules

- Use spaCy for entity extraction
- Use Ollama for entity summaries
- Persist regex cache in `data/entities_cache.json`
- Write entity outputs to `Second Brain/Operations/thoughtmap-out/entities/`

## Verification

After major changes:
- validate imports from `thoughtmap.core`, `thoughtmap.analysis`, and `thoughtmap.web`
- verify Docker still starts with `python -m thoughtmap server`
- verify outputs still land in `Second Brain/Operations/thoughtmap-out/`