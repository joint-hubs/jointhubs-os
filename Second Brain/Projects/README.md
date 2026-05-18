# Projects

> ← [Back to Second Brain](../README.md)

This is where you build things. Each project gets its own folder with a `CONTEXT.md` that tracks where the project has been, where it is, and where it's going.

ThoughtMap is one of the projects that lives here — it's the pipeline that maps your entire knowledge base. But you can have as many projects as you need. The same patterns and components are reusable across all of them.

## Structure

```
Second Brain/Projects/
├── thoughtmap/         # ThoughtMap pipeline (Docker + Python)
├── your-project/       # Your project
│   ├── README.md       # Project overview
│   ├── CONTEXT.md      # Past / Current / Future state
│   └── ...
└── another-project/
    └── ...
```

## Starting a Project

1. Create a folder: `Second Brain/Projects/your-project/`
2. Add `README.md` — project overview
3. Add `CONTEXT.md` — use the template from `.github/skills/project-context/`
4. Start working — agents read your `CONTEXT.md` for state

ThoughtMap will pick up your project notes in the next run and cluster them with the rest of your knowledge. You'll see how each project relates to your other thinking.

## ThoughtMap

The [ThoughtMap pipeline](thoughtmap/README.md) lives here as a project. It processes all your notes — from this repo, your external Obsidian vault, Wispr Flow transcripts — and generates an interactive visualization in `Operations/thoughtmap-out/`.

From the map, you can discover gaps, identify connections between projects, and create new notes to fill what's missing.

## CONTEXT.md Pattern

Every project uses `CONTEXT.md` with three sections:
- **Past** — How we got here, key decisions
- **Current** — Where we are, active work
- **Future** — Where we're going, next steps

Agents read this to understand project state instantly.

## Tags

Use hashtags to connect notes across the vault. Add your own project tags and update `.github/instructions/assistant.instructions.md` so agents recognize them.

---

## Navigation

| Where | What |
|-------|------|
| ← [Second Brain](../README.md) | Knowledge layer overview |
| → [ThoughtMap](thoughtmap/README.md) | The pipeline: setup, run, configure |
| → [Operations](../Operations/README.md) | Where ThoughtMap output lands |
| → [Personal](../Personal/README.md) | Health, finances, events |
