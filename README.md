# Jointhubs OS

<p align="center">
  <img src=".github/assets/jointhubs.png" alt="Jointhubs OS" width="450">
</p>

You write notes every day. Meeting notes, project decisions, late-night ideas, health logs, financial tracking. Over months and years, it adds up — hundreds of files, thousands of thoughts.

But you can't *see* them. You know the insight is in there somewhere. You just don't know where, or what connects to what.

**Jointhubs OS** is an open-source system that turns your notes into something you can work with:

1. **A Second Brain** — structured notes in Obsidian that agents can read and write
2. **ThoughtMap** — a pipeline that embeds your notes, clusters them into topics, and generates an interactive 2D map of everything you think about
3. **AI agents** — specialized personas in VS Code Copilot that maintain context across sessions, using your notes as memory

The whole thing runs locally. Your notes stay on your machine. ThoughtMap uses Ollama for embeddings — no cloud calls unless you opt in.

It is already useful before the system is "finished". Even in its current state, the stack can turn daily notes, reviews, and voice transcripts into a working planning surface: recurring reviews, entity tracking, project memory, and a map of what keeps showing up across your week.

---

## What does ThoughtMap actually show you?

ThoughtMap takes all your notes, splits them into chunks, embeds them with a local model, and clusters them by meaning. The output is an interactive HTML visualization where:

- **Clusters** are the topics you think about most — your "god nodes"
- **Bridges** are ideas that connect otherwise separate topics
- **Orphans** are thoughts that don't belong anywhere yet
- **Entities** are people, projects, tools that appear across your knowledge base

You see the shape of your thinking. Where you're deep, where you're shallow, what's connected, what's isolated.

Run it nightly and your map evolves with you.

**ThoughtMap maps whatever you point it at.** By default it reads the notes in this repo. But you can plug in your existing Obsidian vault, a folder of markdown files, or [Wispr Flow](https://wispr.flow) voice transcripts — ThoughtMap picks up all three and merges them into one unified map.

> **Set up and run ThoughtMap** → [ThoughtMap README](Second%20Brain/Projects/thoughtmap/README.md)

---

## How the system works

```
┌─────────────────────────────────────────────────────────┐
│                   VS Code + Copilot                     │
│                                                         │
│   Agents: Tech Lead · Planner · Journal · Designer ...  │
│       │                                                 │
│       │ read / write                                    │
│       ▼                                                 │
│   ┌─────────────────────────────────────────────────┐   │
│   │              Second Brain/                      │   │
│   │                                                 │   │
│   │   Operations/  ── Personal/ ── Projects/        │   │
│   │       │                           │             │   │
│   │   thoughtmap-out/          thoughtmap/           │   │
│   │   (your map)               (the pipeline)       │   │
│   └─────────────────────────────────────────────────┘   │
│       │                                                 │
│       │ MCP                                             │
│       ▼                                                 │
│   Ollama (local) · ChromaDB · Google Workspace · ...    │
└─────────────────────────────────────────────────────────┘
```

Agents maintain continuity through daily logs. They read yesterday's notes, pick up context, and keep working where you left off.

---

## Explore the system

The best way to understand Jointhubs OS is to walk through it. Each area has its own README that explains what it does and links to its neighbors.

**Start here:** [Build your Second Brain →](Second%20Brain/README.md)

### [Second Brain](Second%20Brain/README.md) — the knowledge layer

Your notes, organized into three areas. This is where agents read and write. This is what ThoughtMap maps.
- [Operations](Second%20Brain/Operations/README.md) — system output, daily journals, docs, ThoughtMap output
- [Personal](Second%20Brain/Personal/README.md) — health, finances, events, learning
- [Projects](Second%20Brain/Projects/README.md) — active work, each with a `CONTEXT.md`

### [Agents](.github/agents/README.md) — who does the work

Specialized AI personas you select in Copilot Chat. A Tech Lead thinks differently than a Journal agent. Each brings a distinct mindset.

### [Skills](.github/skills/README.md) — what agents know

Domain knowledge that agents load on demand. How to write daily logs, how to do weekly reviews, how to navigate your vault, how to query ThoughtMap.

### [Prompts](.github/prompts/README.md) — one-command workflows

Type `/daily-kickoff` or `/weekly-review` in Copilot Chat to run a full workflow in one shot.

### [Instructions](.github/instructions/README.md) — rules by context

Directory-scoped rules that activate automatically. Working in `Projects/`? Project rules apply. Working in `Health/`? Health rules apply.

### [Automation](.github/automation/README.md) — scheduled pipelines

ThoughtMap nightly, graphify weekly. Set up once, runs in the background.

---

## Quick Start

```bash
# 1. Fork & clone
git clone https://github.com/YOUR_USERNAME/jointhubs-os.git
cd jointhubs-os

# 2. Open as an Obsidian vault
#    The repo IS your vault — open this folder in Obsidian

# 3. Run ThoughtMap
cd "Second Brain/Projects/thoughtmap"
cp .env.example .env          # set your vault path
docker compose up --build     # open http://localhost:8585

# 4. Open in VS Code with Copilot
#    Pick an agent in Copilot Chat → start working
```

> **Detailed setup:** [Repo Init Guide](Second%20Brain/Operations/Docs/repo-init/README.md) · [AI Development Guide](Second%20Brain/Operations/Docs/ai-development/README.md)

---

## Privacy

- **ThoughtMap runs locally** — Ollama embeddings, local clustering, no cloud calls
- **Cloud embeddings are opt-in** — OpenAI/Google only if you configure API keys
- **Copilot is separate** — VS Code Copilot sends context to cloud model providers, but the ThoughtMap pipeline itself does not
- **One CDN request** — the visualization loads `vis-network.js` from CDN (vendorable)

## Public-Safe Fork Workflow

If you want to use this repo as your own operating system and still contribute upstream, keep a hard boundary between `shared framework` and `personal operating data`.

**Safe to commit upstream:**
- framework code, docs, templates, shared prompts, shared agents, shared skills
- generic examples that do not reference real people, private projects, or local machine paths

**Keep local only:**
- personal notes and journals
- communication logs, daily execution boards, generated reviews, and ThoughtMap output built from your own notes
- machine-specific prompts, instructions, and experiments in `.github/*/local/`

Recommended flow:

1. Commit only public-safe files to your fork.
2. Push your branch or `main` to `origin`.
3. Open a Pull Request from your fork into `upstream`.
4. Keep personal workflows and note content in ignored paths or local-only prompt/instruction folders.

Before pushing, run a quick audit:

```bash
git status --short --ignored
git diff --cached
```

---

## Customization

The vault structure (`Operations / Personal / Projects`) is the backbone — agents, skills, and ThoughtMap all depend on it. Keep the top-level areas, customize everything inside them.

You can freely add agents, skills, prompts, and instructions. Every layer has a `local/` subfolder for private files that won't be committed:
- `.github/agents/local/` · `.github/skills/local/` · `.github/prompts/local/` · `.github/instructions/local/`

If a workflow includes your real name, private contacts, or absolute file-system paths, treat it as local by default and move it under the matching `local/` folder before opening a PR.

When you change your note conventions, update the matching skill so agents can still find things. See [Second Brain README](Second%20Brain/README.md) for details.

---

## Contributing

Open source under MIT. New agents, skills, and prompts welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
