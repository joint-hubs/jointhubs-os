# Daily Review — Cloud Desktop Scheduled Task

You are running the end-of-day review for the user. Today's date is {TODAY_DATE}. Run every step carefully and save a complete review note at the end.

Assume these placeholders are configured for the user's environment:
- `{REPO_ROOT}` — root of the `jointhubs-os` repository
- `{SECOND_BRAIN}` — `{REPO_ROOT}/Second Brain`
- `{PERSONAL_VAULT_ROOT}` — optional external Obsidian vault root
- `{PERSONAL_DAILY}` — optional personal daily-notes folder inside the external vault
- `{WISPR_DB}` — optional path to `flow.sqlite`

**Core rules:**
1. **Token efficiency over completeness.** Every browsing action costs tokens. Prefer MCP → API → file-based tracking → browser (last resort). Never screenshot a feed or timeline.
2. **Delta-only reading.** Use the thread-state file (Step 0b) to track last-seen IDs/timestamps per channel. Only fetch what changed since last run.
3. **ThoughtMap-out is your compass.** Use pre-computed entities, clusters, and topics before semantic querying. They cost ~zero tokens and already encode the knowledge structure.
4. **Build a compact ThoughtMap context pack early.** After Step 1, convert the warm-set retrieval into: Prior decisions, Open threads, Reusable assets, Freshest relevant source, Gaps / conflicts. Use that pack through Steps 2-9 instead of carrying raw search results.

**Tool preference ladder:**
- Gmail / Tasks / Calendar / Drive → **Google Workspace MCP** (`mcp_googleworkspa_*` tools) if available in this runtime
- If MCP unavailable → Google APIs via Python scripts
- Browser automation → only for channels with no API (Discord DMs, LinkedIn) and only for deltas
- At the start of Step 2, test MCP availability with one call; if it fails, log it and fall back

---

## STEP 0 — Load previous reviews + build message watermark

### 0a — Read previous reviews
Read the last 3 daily review files from:
`{SECOND_BRAIN}/Operations/Reviews/`

Files: `{YESTERDAY_DATE}-review.md`, `{2_DAYS_AGO}-review.md`, `{3_DAYS_AGO}-review.md` (up to 5 days back if gaps exist).

Extract:
- **Carry-forward items** — unresolved action items, blockers, open questions
- **Recurring themes** — patterns across days (anything appearing 3+ times = trend)
- **People tracker** — which people had pending responses or open threads

### 0b — Load / initialize thread-state file

Maintain a single state file that tracks last-seen message markers per channel and per thread. This is the mechanism that makes subsequent steps cheap.

**Path:** `{SECOND_BRAIN}/Personal/peers/thread-state.json`

Schema:
```json
{
  "updated": "2026-04-21T19:30:00",
  "channels": {
    "gmail": {
      "last_history_id": "123456",
      "last_message_date": "2026-04-21T18:42:00Z",
      "threads": {
        "<thread-id>": {
          "last_message_id": "...",
          "last_seen": "2026-04-21T18:42:00Z",
          "status": "pending-reply | answered | closed",
          "priority": "critical | important | info",
          "subject": "...",
          "counterparty": "..."
        }
      }
    },
    "discord": {
      "last_scan": "2026-04-21T19:00:00Z",
      "dms": { "<user>": { "last_message_ts": "...", "status": "..." } },
      "servers": { "jointhubs": { "<channel>": { "last_message_ts": "..." } } }
    },
    "linkedin": { "last_scan": "2026-04-21", "notes": "derived from email notifications only" }
  },
  "folder_sizes": { "<path>": { "size_mb": 0, "files": 0, "checked": "..." } }
}
```

**Rules:**
- If the file does not exist, create it with empty channels and establish baselines in later steps.
- Treat it as **read-write**. Update in place at the end of each step that touched a channel.
- The watermark from this file is law: never re-summarize threads whose `last_seen` ≥ their actual latest message.
- Only open a thread in browser/MCP if its `status` is `pending-reply` or the thread is new.

---

## STEP 1 — Load ThoughtMap-out as the knowledge compass

ThoughtMap-out is the pre-computed semantic map of the user's knowledge base. Use it as your primary navigation index — it replaces the old graphify scan and costs near-zero tokens.

**Root:** `{SECOND_BRAIN}/Operations/thoughtmap-out/`

### 1a — Read the overview

Read `REPORT.md` (top of file is enough):
- Total chunks, clusters, and unclustered count — gauge knowledge-base scope
- **Sources** table — which inputs are fresh vs. stale (e.g., low wispr-flow count = the user hasn't recorded recently)
- **Named Entities** top list — most-mentioned people, orgs, projects, tools (this is your active-context roster)
- **God Nodes** — the 5 largest clusters, i.e. what the user's mind is most focused on
- **Bridge Thoughts** — cross-domain connections (these are the ideas worth revisiting today)

### 1b — Staleness check

Check the REPORT.md build timestamp. If >7 days old, flag: "ThoughtMap is stale, consider rebuild." If >14 days, treat entity/cluster data as advisory only and lean harder on ChromaDB query (Step 9).

### 1c — Lazy indexes to keep handy (don't read yet, reference as needed)

| File / Folder | Read when… |
|---------------|------------|
| `entities/_entity-index.md` | A name appears in today's inputs — look up quick context |
| `entities/person/<slug>.md` | Preparing to message someone — see boundaries, clusters, source files |
| `entities/project/<slug>.md` | Logging project work — see which clusters it spans |
| `topics/<slug>.md` | A theme appears today — find related topics and representative fragments |
| `clusters.json` | Need machine-readable cluster metadata (size, centroid, members) |
| `condensed.json` | Looking for inter-cluster similarity and bridge thoughts |
| `entities.json` | Need all entities + area-context metrics in one scan |

**Rule:** Do not dump entire JSON files into context. Grep/filter for the entity or cluster you need.

### 1d — Seed today's entity list

From the people, projects, and topics appearing in carry-forward (Step 0a), pre-load their entity notes if they exist. These become the "warm set" used by Steps 2–9.

### 1e — Run a small semantic warm set

For the 3-6 highest-signal anchors from carry-forward, `REPORT.md`, top entities, and likely active projects:
- run a short semantic bundle using the exact phrasing when available,
- then `"<anchor> current status"`,
- then `"<anchor> open questions"` or `"<anchor> next step"`.

Keep strong hits when possible (`distance < 0.40`) and read the top 1-2 backing source files for the best matches.

This is not the full historical synthesis yet. The goal here is only to establish the **warm set** for the rest of the review.

### 1f — Build today's ThoughtMap context pack

Before Step 2, distill the warm set into a compact working memory block:

```markdown
## ThoughtMap Context Pack

**Prior decisions**:
- [max 5 bullets, source-backed]

**Open threads**:
- [max 5 bullets]

**Reusable assets**:
- [max 5 bullets]

**Freshest relevant source**:
- [1-3 bullets with date + file]

**Gaps / conflicts**:
- [max 3 bullets]
```

Rules:
- every field should point to a concrete source where possible,
- if evidence is weak or mixed, record it under `Gaps / conflicts`,
- use this pack as the working context for Steps 2-9 instead of dragging raw search hits forward.

---

## STEP 2 — Gmail scan (MCP-first, delta-only)

### 2a — Probe MCP availability

Try a lightweight call to the Google Workspace MCP (tools prefixed `mcp_googleworkspa_*`). If it responds, use it for all Gmail/Tasks/Calendar/Drive steps. If unavailable in this Claude Desktop runtime, fall back to:
1. Google API via Python (creds at standard location), OR
2. Gmail web UI in browser — but **only** open threads flagged `pending-reply` in thread-state, or threads newer than `last_history_id`.

Log which path was used: `Gmail source: MCP | API | browser`.

### 2b — Fetch deltas only

Using the `last_history_id` or `last_message_date` from thread-state (Step 0b):
- MCP / API: request messages `after:{last_message_date}` (add 1-second margin)
- If no watermark exists: fetch last 96h as baseline

**Scope filter:**
- Skip: newsletters, automated notifications (GitHub, LinkedIn, CI), calendar invites already in Calendar step — unless explicitly action-required
- Keep: direct human replies, project-keyword matches (Fenix, Neurohubs, Asystent Urzędnika, jointhubs, GlobalLogic)
- Keep: anything from people in the ThoughtMap entity roster (Step 1d)

### 2c — Update thread-state

For each new message: record thread ID, counterparty, subject, date, status (`pending-reply` / `answered` / `closed`), priority. Bump `last_history_id` and `last_message_date`.

### 2d — Log to review

Only include new or status-changed threads in the review table:
`| Sender | Subject | Date | Priority | Response needed? |`

Priority: 🔴 critical · 🟡 important · ℹ️ informational. **Do not screenshot Gmail under any condition.**

---

## STEP 3 — Google Calendar + time-block planning

### 3a — Review past & current
Check today's calendar events and tasks and any events and tasks from the past week that may need follow-ups.

### 3b — Week-ahead scan + free time mapping
Check the next 7 days. For each day, map:
- Blocked time (meetings, events)
- **GlobalLogic working hours: 09:00–16:00 Mon–Fri** (treat as soft-block — sometimes available for own work, but don't schedule important own-work there by default)
- Free time blocks available for task scheduling

Output a simple availability grid:
```
| Day        | GL Hours    | Meetings     | Free blocks (own work) |
|------------|-------------|--------------|------------------------|
| Wed 15 Apr | 09:00-16:00 | 14:00 standup| 07:00-09:00, 16:00-19:00 |
```

### 3c — Google Tasks: full sync
Pull all tasks from Google Tasks (all lists). For each task:
- Note: title, due date, status, list name, notes
- Cross-reference with carry-forward items from Step 0 — deduplicate
- Flag overdue tasks (due date < today) as 🔴
- Flag tasks without due dates that have been sitting >7 days

Merge into the master task list used in Step 11.

**Task creation:** When creating new action items in later steps (11, 9d), also create corresponding Google Tasks with due dates so they appear in Calendar.

---

## STEP 4 — Obsidian vault: daily note + modified files + task scan

The user may create notes in **both** vaults. Always scan both.

**Vault roots:**
- Repo vault: `{SECOND_BRAIN}` (read + write)
- Personal vault: `{PERSONAL_VAULT_ROOT}` (READ-ONLY)

### 4a — Read today's daily notes

Check both vault locations — the user may use either or both:
- Personal vault: `{PERSONAL_DAILY}/{TODAY_DATE}.md`
- Repo vault: `{SECOND_BRAIN}/Operations/Periodic Notes/Daily/{TODAY_DATE}.md`
- Repo vault (alt location): `{SECOND_BRAIN}/Operations/Reviews/{TODAY_DATE}.md`

### 4b — Scan for modified files (last 24h)

Recursive modified-file scan in both vaults, excluding `.git`, `.obsidian`, `node_modules`, `__pycache__`, `data/chroma`, `graphify-out`, `thoughtmap-out` (regenerated output, not authored content).

PowerShell:
```powershell
Get-ChildItem -Path "{PERSONAL_VAULT_ROOT}", "{SECOND_BRAIN}" -Recurse -File -Include *.md -ErrorAction SilentlyContinue |
  Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-24) -and $_.FullName -notmatch '\\\.(git|obsidian)\\|\\thoughtmap-out\\|\\graphify-out' } |
  Select-Object FullName, LastWriteTime | Sort-Object LastWriteTime -Descending
```

Summarize what changed. **Cross-reference with ThoughtMap entities/clusters** — if a changed file appears as a `source_file` in an entity note or a representative chunk in a cluster, flag as higher signal.

### 4c — Scan for Obsidian Tasks in vault notes

Search all recently modified `.md` files (and today's daily note) for **Obsidian Tasks plugin** tasks. These are NOT regular checkboxes — they are identifiable by emoji markers for dates and priority.

**Regex pattern** (use on each `.md` file content):
```
^- \[.\] .+(📅|🛫|⏳|➕).*(⏫|🔼|🔺|🔽)|^- \[.\] .+(⏫|🔼|🔺|🔽).*(📅|🛫|⏳|➕)
```

This matches lines like:
```
- [ ] jointhubs-os release 📅 2026-04-15 🛫 2026-04-15 🔺 ➕ 2026-04-15
- [x] update CONTEXT.md 📅 2026-04-10 ⏫
- [ ] call Anna Buchwald 🛫 2026-04-16 📅 2026-04-18 🔼 ➕ 2026-04-12
```

**Emoji legend:**
| Emoji | Meaning |
|-------|---------|
| `📅`  | Date stamp (usually when the task was **written/saved** — NOT a deadline) |
| `🛫`  | Date stamp (usually when recording started — NOT a start date constraint) |
| `⏳`  | Date stamp (recording/scheduled note timestamp) |
| `➕`  | Created date (when the task line was added to the note) |
| `⏫`  | Highest priority |
| `🔼`  | High priority |
| `🔺`  | Medium priority |
| `🔽`  | Low priority |

> **Important:** In the user's vault, date emojis (`📅`, `🛫`, `⏳`, `➕`) record *when the task was written or saved* — they are NOT deadlines or scheduling constraints. **Urgency is determined solely by the priority emoji.** Do not interpret any date emoji as a due date unless the task text itself explicitly states a deadline (e.g., "by Friday", "before demo").

**Rules:**
- A valid Obsidian Task must have **at least one date emoji** AND **a priority emoji** — ignore plain `- [ ]` checkboxes without these markers
- `- [ ]` = open task, `- [x]` = completed task
- Extract: task name, status (open/done), all dates, priority, source file path
- Note which file each task lives in — this tells you where the user defined it

**Where to search (both vaults, all subdirectories):**
1. Personal Obsidian Vault: `{PERSONAL_VAULT_ROOT}` — all folders, not just Daily/Weekly
2. Repo Second Brain: `{SECOND_BRAIN}` — all folders including Projects/, Personal/, Operations/
3. Project CONTEXT.md files (tasks often embedded there)
4. Today's and this week's notes in both vaults

Use `grep_search` with the regex above across both roots in parallel. Exclude `thoughtmap-out/`, `graphify-out/`, `.git/`, `.obsidian/`.

**Output as table:**
```
| Task | Priority | Recorded (📅/➕) | Status | Source file |
|------|----------|--------------------|--------|-------------|
```

The date column records when the task was written — it is not a deadline. Sort by priority emoji, not by date.

These tasks feed into Step 11a — they represent commitments the user wrote directly in the notes and must be cross-referenced with Google Tasks to avoid duplication or orphaning.

---

## STEP 5 — Folder health: size & change monitoring

Monitor key directories for growth, unexpected changes, or bloat. Run a quick size scan:

**Directories to monitor:**
- `{REPO_ROOT}/..` — all sibling repos (list each subfolder with size)
- `{SECOND_BRAIN}` — vault inside repo
- `{PERSONAL_VAULT_ROOT}` — main Obsidian vault

**For each directory, report:**
```
| Folder                          | Size    | Files | Change vs last review |
|---------------------------------|---------|-------|-----------------------|
| GitHub\jointhubs-os             | 245 MB  | 1,203 | +12 MB (+8 files)     |
| GitHub\jointhubs-fenix\office   | 89 MB   | 412   | no change             |
| Obsidian Vault                  | 310 MB  | 2,100 | +3 MB (+5 files)      |
```

**Flag if:**
- Any folder grew >50 MB since last review (possible large file committed or generated output left behind)
- A repo folder has uncommitted changes (dirty working tree)
- `node_modules`, `__pycache__`, `.venv`, or `data/` folders are unusually large

Use PowerShell: `Get-ChildItem -Directory | ForEach-Object { $size = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum; [PSCustomObject]@{Name=$_.Name; SizeMB=[math]::Round($size/1MB,1)} }`

Compare with the `folder_sizes` map in `thread-state.json` (Step 0b). Update that map with today's values at the end of this step.

---

## STEP 6 — Discord (thread-state driven, minimal browsing)

Discord has no stable public API for user accounts, so browser is the only path. Minimize it aggressively.

### 6a — Plan the visit from thread-state

Before opening Chrome, decide what to check:
1. Read `channels.discord` from `thread-state.json` (Step 0b)
2. List DMs with `status: pending-reply` or unknown — these are the only ones to open
3. List jointhubs server channels whose `last_message_ts` is >24h old — check once for activity, no deeper scan

If nothing is `pending-reply` and last scan was <12h ago: **skip Discord entirely** and note: "Discord skipped — no pending threads, last scan <12h."

### 6b — Minimal browsing protocol

If opening Chrome:
- Open Discord in an already-authenticated tab if possible
- Navigate directly to each pending DM / channel (one URL per target, no sidebar scrolling)
- Read text via `read_page` — **never** `screenshot_page` a chat feed
- Capture only: last message text (truncated to 300 chars), timestamp, sender. Stop reading once you hit a message older than `last_message_ts`.

### 6c — Update thread-state

For each checked conversation, update `last_message_ts`, `status`, and add a summary line to the review only if status changed or new message arrived.

**Do NOT** read or summarize messages from any other server. If Chrome unavailable, skip and log it.

---

## STEP 7 — LinkedIn (file-based tracking only)

**Do NOT open LinkedIn in browser.** Instead, maintain a communication log file:
`{SECOND_BRAIN}/Personal/peers/linkedin-tracker.md`

If the file exists, read it. If not, create it with this structure:

```markdown
---
type: communication-tracker
platform: linkedin
updated: {TODAY_DATE}
---

# LinkedIn Communication Tracker

## Active Threads
| Contact | Last message from them | Last message from me | Status | Topic |
|---------|----------------------|---------------------|--------|-------|

## Pending Outreach
| Contact | Purpose | Priority | Added |
|---------|---------|----------|-------|
```

Cross-reference with peer notes in `Second Brain/Personal/peers/` and any LinkedIn mentions from Gmail notifications or previous reviews. Update the tracker with any new information found indirectly.

---

## STEP 8 — Communication map (per-person, cross-channel)

Build or update a communication overview file:
`{SECOND_BRAIN}/Personal/peers/communication-map.md`

Structure:

```markdown
---
type: communication-map
updated: {TODAY_DATE}
---

# Communication Map

## Active contacts (last 2 weeks)
| Person | Channels | Last contact | Open thread? | Peer note exists? |
|--------|----------|-------------|-------------|-------------------|
| Anna Buchwald | Discord, Email | 2026-04-08 | ⌛ waiting | ❌ create |
```

For each person appearing in today's scan:
- Note which channel(s) the conversation is on
- Flag if peer note (`Second Brain/Personal/peers/`) is missing → suggest creating it
- Track response age — if >5 days without response, flag 🔴

---

## STEP 9 — ThoughtMap ChromaDB: semantic memory recall

Query the ThoughtMap ChromaDB vector database to enrich today's review with historical context. This is your long-term memory — use it to connect today's topics with past thinking, decisions, and patterns.

### 9a — Extract today's key topics

From today's ThoughtMap context pack and Steps 0-8, identify the **5-8 most significant topics, names, or concepts** discussed today. Examples:
- Project names: "Fenix demo", "Asystent Urzędnika deployment"
- People: "Anna Buchwald", "Artur Povodor"
- Technical topics: "RAG pipeline", "Docker security"
- Decisions or blockers: "pricing strategy", "AWS billing"

### 9b — Query ChromaDB

For each key topic, run a semantic similarity search against the ThoughtMap collection.

**Database location:** `{SECOND_BRAIN}/Projects/thoughtmap/data/chroma/`
**Collection name:** `thoughtmap`

**Query method — run this Python script** (requires the thoughtmap venv):

```python
import chromadb

client = chromadb.PersistentClient(
  path=r"{SECOND_BRAIN}/Projects/thoughtmap/data/chroma"
)
collection = client.get_collection("thoughtmap")

queries = [
    "Fenix demo preparation",
    "Anna Buchwald collaboration",
    # ... add today's key topics here
]

for q in queries:
    results = collection.query(
        query_texts=[q],
        n_results=5,
        include=["documents", "metadatas", "distances"]
    )
    print(f"\n--- {q} ---")
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        if dist < 0.65:  # cosine distance threshold — only relevant results
            print(f"  [{meta.get('timestamp','?')[:10]}] (dist={dist:.3f}) {doc[:200]}")
```

**If Ollama is not running** (embedding model needed for query), fall back to reading the pre-built cluster files:
`{SECOND_BRAIN}/Operations/thoughtmap-out/clusters/*.md`

Scan cluster titles for topic matches and read the relevant cluster files for context.

### 9c — Analyze historical context

For each topic with ChromaDB results:
1. **History exists** — What was said before about this topic? When? What was decided?
2. **Pattern detection** — Does this topic keep recurring without resolution? Flag it.
3. **Connections** — Do results from different queries overlap? That's a cross-domain signal.
4. **Staleness** — If the most recent chunk is >30 days old, the topic may have drifted.

### 9d — Generate context-aware suggestions

Based on historical context, produce for each active topic:
- **Previously explored** — "This was discussed on [date], decision was [X]" or "You considered [Y] but didn't pursue it"
- **Recurring without closure** — "This topic appeared [N] times in the last month without being resolved"
- **New direction proposals** — Based on what's in the history + what happened today, suggest 1-2 concrete next steps or angles not yet explored

For high-signal topics, express the synthesis as a mini context pack:
- **Prior decisions**
- **Open threads**
- **Reusable assets**
- **Freshest relevant source**
- **Gaps / conflicts**

Output this as a dedicated section in the review (see Step 14 template).

---

## STEP 10 — Day reflection + analysis

Based on everything gathered, write an honest end-of-day reflection:

### 🏆 Co poszło dobrze (What went well)
- 3-5 concrete wins, achievements, or positive signals from today
- Include small wins (answered a long-pending email, shipped a commit, had a good call)

### ⚡ Winy dnia (Today's shortcomings)
- What didn't get done that should have?
- Where was time wasted or focus lost?
- Any dropped balls or missed commitments?
- Be specific and honest, not vague

### 🔭 Na co zwrócić uwagę (Watch-outs for the future)
- Patterns that could become problems if ignored
- Deadlines approaching
- Relationships that need attention
- Technical debt or process gaps spotted

### 💡 Co mogłem zrobić lepiej (What could I have done better)
- Specific, actionable improvements — not generic advice
- Reference today's actual events
- 1-3 items max

---

## STEP 11 — Task migration + scheduling

### 11a — Collect all open tasks
Gather tasks from:
- Today's carry-forward list
- New action items from Steps 2-8
- Incomplete tasks from today's daily note
- **Obsidian Tasks found in Step 4b** (vault notes with 📅/🛫/⏳ + priority emoji)
- Google Tasks

Cross-reference Obsidian Tasks (Step 4b) with Google Tasks (Step 3c) — deduplicate by matching task names. If an Obsidian Task has no matching Google Task and is still open, flag it for Google Tasks creation in Step 11e so it appears in Calendar. **Do not use the Obsidian Task date emojis as due dates when creating Google Tasks** — assign a due date based on priority and context instead (e.g., `⏫` → today/tomorrow, `🔼` → this week, `🔺/🔽` → next available slot).

### 11b — Triage and prioritize
For each task, assign:
- Priority: 🔴 critical · 🟡 important · ⚪ low
- Estimated time: (15m / 30m / 1h / 2h / half-day)
- Deadline if known

### 11c — Schedule into calendar free blocks

**First, split tasks into two buckets before scheduling:**

**Maintenance window bucket** — tasks that are: purely operational, require no creative energy, and take <15 min each (e.g. password resets, sending a ready draft, security alerts, quick acks). If today is Monday, schedule these as a batch at 08:00–09:00. On other days, group them at the start of the first available 30-min slot before GL hours. Do NOT scatter them across the day as individual priority items.

**Focus work bucket** — everything else: project work, demos, analysis, creative output. Schedule these in the best available deep-work blocks.

Using the availability grid from Step 3b, suggest concrete time blocks:

```
🔧 Maintenance window (batch — Mon 08:00–09:00 or first available slot):
- reset AWS password (2 min)
- send Pietro email (1 min)
- [any other <15 min operational items]

📅 Focus schedule:
- Wed 15 Apr, 16:30-17:30 → 🔴 Prepare Fenix demo (1h)
- Wed 15 Apr, 17:30-18:00 → 🟡 Reply to Anna Buchwald (30m)
- Thu 16 Apr, 07:00-08:00 → 🟡 Review SCE paper (1h)
```

Rules:
- **09:00-16:00 Mon-Fri = GlobalLogic** — only schedule own-work there if explicitly low-load day
- Prefer morning blocks (before 09:00) for deep work
- Prefer evening blocks (16:00-19:00) for calls and communication
- Don't overload any single day — max 3h of scheduled own-work outside GL hours
- Weekend blocks only for 🔴 critical items
- A task that has been carry-forward for 3+ weeks AND takes <15 min belongs in maintenance window, not in focus schedule

### 11d — Tasks that need calendar events
If a task requires a specific time (call, meeting, deadline), suggest creating a Google Calendar event with exact details.

### 11e — Plan Google Tasks for the future
For tasks that don't fit in the next 3 days, create Google Tasks with appropriate due dates. Group by project/context. Ensure every action item from the review has either:
- A time block in the suggested schedule (next 3 days), OR
- A Google Task with a due date (further out)

No task should be orphaned — everything gets tracked somewhere.

### 11f — Schedule Wispr Flow recording sessions
Based on the ThoughtMap analysis (Step 9) and today's open questions, identify **1-2 topics** that would benefit from a 15-30 minute voice deep-dive. These are topics where:
- There's a gap in documented thinking (ChromaDB has surface-level chunks but no depth)
- A decision is stalled because the reasoning hasn't been articulated
- Multiple threads converge and need synthesis
- A recurring carry-forward item needs unblocking through reflection

For each proposed session, create:
```
🎙️ Wispr Recording Session
- Topic: [specific question or theme]
- Guiding questions: [2-3 questions to answer during recording]
- Context to review first: [links to relevant notes/files]
- Suggested slot: [date, time block from availability grid]
- Expected output: [what note should be created/updated in Second Brain]
```

Schedule these in free blocks — preferably morning (07:00-09:00) when thinking is freshest. Max 1 session per day.

---

## STEP 12 — Process Wispr Flow transcripts

Check for new Wispr Flow transcriptions that haven't been processed yet.

**How to detect new transcripts:**
Wispr Flow saves transcriptions to the SQLite database at:
`{WISPR_DB}`

ThoughtMap already extracts these during its pipeline. Check for recent chunks in ChromaDB with `source: wispr-flow` and `timestamp > {YESTERDAY_DATE}`.

Alternatively, check today's daily note in Obsidian — Wispr transcriptions often appear there as raw text blocks.

**Processing rules:**
1. **Identify the topic** — What was the recording about? Match against existing Second Brain notes.
2. **Route the content:**
   - If the transcript answers a previously scheduled recording session (from a prior review's `🎙️ Wispr Recording Session`) → create or update the designated Second Brain note
   - If it's a standalone reflection → extract key points into today's daily review under a `## Wispr Insights` section
   - If it covers a specific project → update or create a note in the relevant `Second Brain/Projects/{project}/` folder
   - If it's about a person → update their peer note in `Second Brain/Personal/peers/`
3. **Extract structured data:**
   - Decisions made → log with date
   - Action items mentioned → add to task list (Step 11)
   - Questions raised → add to Follow-Up Questions
   - New ideas → note under the relevant project or create a new note
4. **Link back** — Add `[[{note_name}]]` wikilinks in the daily review pointing to any notes created/updated from transcripts

**Note creation format** (when creating new Second Brain notes from transcripts):
```markdown
---
type: insight
source: wispr-flow
date: {TODAY_DATE}
project: [project-tag]
status: active
---

# [Topic Title]

## Context
[Why this recording was made — link to the review that scheduled it]

## Key Points
[Extracted from transcript]

## Decisions
[Any decisions articulated]

## Open Questions
[Remaining unknowns]

## Next Steps
[Action items]
```

---

## STEP 13 — Peer network check

Cross-reference all people mentioned today with `Second Brain/Personal/peers/`:
- If a significant person has no peer note → flag: "Create peer note for [name]"
- If a peer note exists but is outdated (last updated >30 days ago) → flag for update
- Read relevant peer notes for context on active relationships

---

## STEP 14 — ThoughtMap entity & cluster insights

Using the ThoughtMap-out data loaded in Step 1 and the topics identified in Step 9a, produce structural insights:

1. **Entity activation map** — which entities from today's inputs (people, projects, orgs) had signals in which channels? Cross-reference with their entity notes (`entities/{type}/<slug>.md`) to see if today's events fall within their usual Topic Boundaries or represent a new edge.
2. **Cluster coverage** — which clusters did today's activity touch? Reference cluster IDs from `clusters.json` or topic notes.
3. **Silent god nodes** — any of the top-5 clusters from REPORT.md that had NO signal today? Flag as attention gaps if silent 3+ days running.
4. **New bridges** — did today's inputs connect two clusters that weren't related in `condensed.json`? That's a potentially novel connection — log it for possible extraction into a new note.
5. **Staleness** — if REPORT.md build date is >7 days old OR vault had >20 new/modified notes since build, flag: "ThoughtMap rebuild recommended."

---

## STEP 15 — Save output

Save the review to:
`{SECOND_BRAIN}/Operations/Reviews/{TODAY_DATE}-review.md`

```markdown
---
date: {TODAY_DATE}
type: daily-review
---

# Daily Review — {TODAY_DATE}

## Summary
[3-5 bullet points of the most important things today]

## ThoughtMap Snapshot
[From REPORT.md: build date, top 3 god nodes, top 5 entities by mention, any stale flag]

## Gmail
[New messages since watermark, formatted as table]

## Calendar
[Today's events + week-ahead availability grid]

## Modified Files (last 24h)
[Changed files with graph cross-reference flags]

## Folder Health
[Size table for monitored directories with change vs last review]

## Discord
[New messages since watermark, by contact]

## LinkedIn (tracked)
[Updates from linkedin-tracker.md, no direct browsing]

## Communication Map Updates
[Per-person cross-channel summary, new contacts flagged]

## Carry-Forward
| Sprawa | Od kiedy | Dni | Status |
|--------|----------|-----|--------|
[Tracked items with age in days and emoji priority]

## 🏆 Co poszło dobrze
[3-5 wins]

## ⚡ Winy dnia
[Honest shortcomings]

## 🔭 Na co zwrócić uwagę
[Watch-outs and patterns]

## 💡 Co mogłem zrobić lepiej
[Specific improvements]

## Action Items
[Prioritized, numbered list with 🔴/🟡/⚪]

## Google Tasks
[Full task list synced from Google Tasks — overdue flagged, new tasks created]

## 📅 Suggested Schedule (next 3 days)
[Time-blocked task suggestions mapped to free calendar slots]

## 🎙️ Wispr Recording Sessions (planned)
[1-2 proposed voice deep-dive sessions with topic, guiding questions, and suggested time slot]

## Wispr Insights (processed)
[Key points extracted from today's Wispr transcripts, with links to created/updated notes]

## 🧠 ThoughtMap Memory
[Per-topic historical context from ChromaDB]

### Previously explored
[Topics that were already discussed, with dates and decisions]

### Recurring without closure
[Topics appearing repeatedly without resolution — with count and first mention date]

### New directions
[1-3 concrete suggestions based on history + today's context]

## ThoughtMap Insights
[Entity activation map, silent god nodes, new bridges, staleness flag]

## Follow-Up Questions
[2-4 questions for the user to think about or act on]

## Tips & Observations
[1-2 proactive suggestions based on weekly patterns]
```

If any section was unavailable (Chrome offline, API blocked), note it clearly rather than leaving blank.

---

## Operational rules

1. **Tool ladder** — Google Workspace MCP → Google API → file-based tracker → browser. Probe MCP once at Step 2a; if unavailable, note it and descend. Never re-probe within the same run.
2. **Zero-screenshot default** — Never screenshot a feed, inbox, timeline, or chat. Screenshots are allowed only for a single element when text extraction genuinely fails, and must be justified in the output.
3. **Delta-only reading** — `thread-state.json` is the single source of truth for what's already been seen. Never re-summarize a thread whose `last_seen` ≥ its actual latest message. Update the state file after every channel touched.
4. **ThoughtMap routing before semantic grounding** — For entity and topic lookups, read pre-computed notes in `thoughtmap-out/entities/` and `thoughtmap-out/topics/` first, then build a small semantic warm set and compact context pack for active anchors. Use deeper ChromaDB work in Step 9 for historical synthesis, not as the first or only move.
5. **Dual-vault scanning** — Always scan both `{PERSONAL_VAULT_ROOT}` and `{SECOND_BRAIN}` for daily notes, Obsidian Tasks, and modified files. Personal vault is read-only.
6. **Time awareness** — GlobalLogic 09:00-16:00 Mon-Fri is soft-blocked. Own-work deep focus: 07:00-09:00 and 16:00-20:00.
7. **Polish/English** — Section headers in English; body content may mix Polish and English if that matches the user's notes.
8. **Peer tracking** — Every person mentioned anywhere gets cross-referenced with `Second Brain/Personal/peers/` and with `thoughtmap-out/entities/person/`. Missing peer note → flag for creation.
9. **Google Tasks sync** — Every action item must be tracked: either a time block in Step 11c or a Google Task with due date in Step 11e. No orphans.
10. **Wispr Flow discipline** — Max 1 proposed recording session per day. Pick topics where voice articulation unlocks progress faster than writing. When processing transcripts, prefer updating existing notes over creating new ones; always wikilink back from the daily review.
11. **Second Brain note creation** — Follow vault conventions: frontmatter with `type`/`status`/`date`, correct folder, wikilinks to related notes and to relevant `thoughtmap-out/entities/` or `topics/` files.
12. **State hygiene** — At the end of the run, `thread-state.json` must reflect reality: updated watermarks, updated folder sizes, updated thread statuses. This is the contract with tomorrow's run.
