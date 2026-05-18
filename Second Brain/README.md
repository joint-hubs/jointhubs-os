# Second Brain

> ← [Back to Jointhubs OS](../README.md)

This is your knowledge base — the layer that AI agents read, write, and learn from. Everything in Jointhubs OS revolves around these notes.

## Getting Started

You already have notes. Maybe in Obsidian, maybe in a folder of markdown files, maybe as voice memos. You don't need to start from scratch.

### Bring your existing knowledge

ThoughtMap can ingest what you already have:

- **Your Obsidian vault** — point ThoughtMap at your existing vault path in `.env` and it reads everything
- **Wispr Flow transcripts** — if you use [Wispr Flow](https://wispr.flow) for voice notes, ThoughtMap picks up your local SQLite history automatically
- **Any markdown folder** — any directory with `.md` files works as a source

Run ThoughtMap once and you get a map of everything you've been thinking about — clusters, entities, connections, gaps. See [ThoughtMap README](Projects/thoughtmap/README.md) for setup.

### Then grow it

The map shows you the shape of your knowledge. From there:

- **Create notes** for topics that are thin or missing — ThoughtMap shows you the gaps
- **Start projects** in `Projects/` — each gets a `CONTEXT.md` that tracks past, present, future
- **Keep a journal** — daily notes in `Operations/Periodic Notes/Daily/` become agent memory across sessions
- **Track your health** — nutrition, training, sleep in `Personal/Health/`. You're not just your projects

Use Obsidian to write, or dictate with Wispr Flow — everything feeds back into ThoughtMap. Run it nightly and watch your map evolve.

## Structure

```
Second Brain/
├── Operations/       ← System output: logs, docs, ThoughtMap results
├── Personal/         ← You: health, finances, events, learning
└── Projects/         ← Your work: each project has CONTEXT.md
```

| Area | What Lives Here | README |
|------|----------------|--------|
| **[Operations](Operations/README.md)** | Daily notes, meeting records, ThoughtMap output, setup docs | The daily rhythm |
| **[Personal](Personal/README.md)** | Health tracking, finances, events, learning | Taking care of yourself |
| **[Projects](Projects/README.md)** | Project folders with `CONTEXT.md` state tracking | Building things |

## The Agent Contract

Agents only know what you teach them. When you change your note structure, update the matching files so agents can still find things:

| You Changed | Update This |
|-------------|-------------|
| Folder paths | [`.github/skills/obsidian-vault/SKILL.md`](../.github/skills/obsidian-vault/SKILL.md) |
| Daily log format | [`.github/skills/daily-log/SKILL.md`](../.github/skills/daily-log/SKILL.md) |
| Project structure | [`.github/skills/project-context/SKILL.md`](../.github/skills/project-context/SKILL.md) |
| Directory rules | [`.github/instructions/`](../.github/instructions/README.md) |

## About the Structure

The `Operations / Personal / Projects` layout is not a suggestion — it's the foundation that agents, skills, instructions, and ThoughtMap all rely on. Renaming or reorganizing these top-level folders means updating every skill, instruction, and agent that references them.

**What you can freely customize:**
- Create any projects inside `Projects/`
- Add any categories inside `Personal/` (Health, Finances, etc.)
- Choose your own daily note format, tags, and templates
- Add or remove skills, agents, and instructions

**What you should keep:**
- The three top-level areas: `Operations/`, `Personal/`, `Projects/`
- The `CONTEXT.md` pattern inside projects
- Daily notes in `Operations/Periodic Notes/Daily/`

---

## Navigation

| Where | What |
|-------|------|
| ← [Jointhubs OS](../README.md) | System overview |
| → [Operations](Operations/README.md) | Daily rhythm, docs, ThoughtMap output |
| → [Personal](Personal/README.md) | Health, finances, events |
| → [Projects](Projects/README.md) | Active work and ThoughtMap pipeline |
| → [Agents](../.github/agents/README.md) | AI personas |
| → [Skills](../.github/skills/README.md) | Domain knowledge |
