Dear note takers,

I'd like to present AI-first data model

if you understand these:
- meeting notes - capturing contents during conversation
- project decisions - capturing contexts of the thoughts and ideas
- health logs - capturing contexts of healthy living
- financial tracking - capturing contexts of wealthy living
- brainstorming sessions - capturing contexts of any idea

Over months and years, it adds up. Hundreds of files, thousands of thoughts lost over time.

now you can track your thoughts

jointhubs-os runs the whole thing locally

It is already useful before the system is "finished". Even in its current state, the stack can turn daily notes, reviews, and voice transcripts into a working planning surface: recurring reviews, entity tracking, project memory, and a map of what keeps showing up across your week.

---

## What does ThoughtMap actually show you?

ThoughtMap takes every note in your filesystem, splits it into chunks, embeds each chunk with a local model, and clusters them by meaning. The result is an interactive map of your own head that you can browse from the outside in.

### 1. The whole brain, at a glance

![ThoughtMap — mega-topics map](.github/assets/High%20level.png)

Every diamond is an **auto-generated mega-topic** built from my entire knowledge base — Obsidian notes, daily logs, voice transcripts, project docs — clustered purely from embedding similarity, not from tags or folders you maintained by hand. Size = how much you actually think about it. Edges = how often ideas bridge between two clusters.

### 2. Drill into one branch

![ThoughtMap — topics inside one mega-topic](.github/assets/mid%20level.png)

Double-click a mega-topic and it opens into its individual topics, laid out by semantic proximity. The right-hand panel summarizes what the cluster is really covering. You can now see which topics are the gravitational center of a domain and which ones sit on its outer edge.

### 3. What's hot *this month*

![ThoughtMap — sub-topics filtered by the timeline](.github/assets/low%20level.png)

Double-click again to enter a single topic, then flip the **timeline filter** to *This Month*. Only sub-topics with thoughts from the active time window stay solid — everything else dims out. The remaining lit-up node is, very literally, the hot topic of the month inside that branch of your brain.

This is how ThoughtMap answers *"what am I actually working on right now, inside this domain?"* without you having to grep through daily notes.

### 4. Echoes — the thoughts you keep having

![ThoughtMap — echoes panel](.github/assets/echoes.png)

Echoes are **near-duplicate thought groups**: distinct chunks that say roughly the same thing, grouped by embedding similarity. Each group shows how many times the idea recurred, how tightly it clusters, and the date range it spans.

Use it to spot templates you should extract, ideas you keep re-deriving without ever writing them down properly, and noise you can mark *Discard* so future runs ignore it.

### 5. Glossary — does the model actually understand you?

![ThoughtMap — glossary of entities](.github/assets/glossary.png)

The Glossary lists every **entity** ThoughtMap extracted — projects, organizations, people, locations, tools — with mention counts, topic reach, a short auto-generated summary, and source files. Its job is **trust verification**: if the cards look right to you at a glance, the pipeline understood your knowledge base. If they look wrong, that's a signal the upstream extraction stages need attention.

### 6. Taxonomy — the same check, from the other side

![ThoughtMap — taxonomy view](.github/assets/taxonomy.png)

Taxonomy puts the **topic tree** and the **entity roots** side by side. Glossary asks "are the entities correct?"; Taxonomy asks "do the topics and the entities line up against each other the way they should?" Together they let you sanity-check the entire map by eye.

---

Together those six views gave me the first Thought Model. It runs on my machine every day because i dont turn off the computer. And if im forced to do so i can just restart the containers. Its scheduled nightly.

**ThoughtMap maps whatever you point it at.** By default it reads the notes in this repo. But you can plug in your existing Obsidian vault, a folder of markdown files, or [Wispr Flow](https://wisprflow.ai/) voice transcripts — my ThoughtMap picks up all three and merges them into one unified map.

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
│   │   thoughtmap-out/          thoughtmap/          │   │
│   │   (your map)               (the pipeline)       │   │
│   └─────────────────────────────────────────────────┘   │
│       │                                                 │
│       │ MCP                                             │
│       ▼                                                 │
│   Ollama (local) · ChromaDB · Google Workspace · ...    │
└─────────────────────────────────────────────────────────┘
```

Agents maintain continuity through daily logs. They read yesterday's notes, pick up context, and keep working where you left off.

But you should be the lead of the note.
---

## Explore the system

The best way to understand the repo is connect with creator.
Mateusz Stachowicz
https://www.linkedin.com/in/mtstch/

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
