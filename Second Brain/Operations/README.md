# Operations

> ← [Back to Second Brain](../README.md)

This is where the system writes and where you keep your daily rhythm. You won't browse here often — but agents read it constantly for context, and ThoughtMap output lands here.

## Structure

```
Second Brain/Operations/
├── Docs/                 # Setup guides and reference docs
├── Periodic Notes/       # Your journal and planning
│   ├── Daily/            # Daily notes (YYYY-MM-DD.md)
│   ├── Weekly/           # Weekly reviews (YYYY-Www.md)
│   ├── Monthly/          # Monthly reviews (YYYY-MM.md)
│   └── Quarterly/        # Quarterly reviews (YYYY-Qq.md)
├── Meetings/             # Meeting notes
└── thoughtmap-out/       # ThoughtMap pipeline output
```

## ThoughtMap Output

When you run ThoughtMap, results land in `thoughtmap-out/`:
- `thoughtmap.html` — interactive 2D visualization of your knowledge
- `REPORT.md` — cluster summaries, god nodes, source breakdown
- `entities/` — profiles of people, projects, tools across your notes
- `clusters/` — topic group descriptions
- `chunks.json`, `clusters.json` — machine-readable data

Open `thoughtmap.html` in a browser to explore your knowledge map. See [ThoughtMap README](../Projects/thoughtmap/README.md) for how to run the pipeline.

## Daily Notes

Daily notes are agent memory — the bridge between sessions. They capture:
- **Focus** — weekly priorities embedded from the weekly note
- **Journal** — thoughts, observations, reflections
- **Logs** — timestamped activity log
- **Tasks** — grouped by priority

Keep a journal. Write notes. Use Wispr Flow instead of typing if that's easier — everything gets collected and fed back into ThoughtMap regardless of whether you type in Obsidian, dictate while coding in VS Code, or write in any other context.

## Weekly Notes

Weekly notes set priorities and synthesize daily journals:
- **Next** — 3-5 commitments for the week
- **History** — embedded journal sections from each day
- **Tasks** — completed and outstanding

## Docs

Setup and reference guides:
- [Docs index](Docs/README.md)
- [Repo Init](Docs/repo-init/README.md) — environment, MCP, vault setup
- [AI Development](Docs/ai-development/README.md) — building agents, skills, prompts

## Meetings

Meeting notes with agenda, discussion, action items, follow-ups.

---

## Navigation

| Where | What |
|-------|------|
| ← [Second Brain](../README.md) | Knowledge layer overview |
| → [Personal](../Personal/README.md) | Health, finances, events |
| → [Projects](../Projects/README.md) | Active work |
| → [ThoughtMap](../Projects/thoughtmap/README.md) | The pipeline that generates thoughtmap-out/ |
| → [Automation](../../.github/automation/README.md) | Scheduled ThoughtMap + graphify runs |
