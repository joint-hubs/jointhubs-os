# Project Status Review — Cloud Desktop Scheduled Task

You are preparing a weekly project status report for Mateusz Stachowicz (Stachu). He runs three active projects: **Fenix**, **Neurohubs**, and **Asystent Urzędnika**. Your job is to synthesize all available signals from the past 7 days into a structured per-project report and save it.

Today's date is the run date. "Past 7 days" = 7 days ago through today.

**Output vault:** `C:\Users\mateu\Documents\GitHub\jointhubs-os` (read + write)
**Personal vault:** `C:\Users\mateu\Documents\Obsidian Vault` (READ-ONLY)

**Key principle:** Derive project activity from daily reviews, CONTEXT.md files, folder scans, Gmail, Calendar, Google Tasks, and ThoughtMap — NOT from GitHub API (blocked by proxy).

---

## STEP 0 — Load previous project status (baseline)

Read the most recent file from:
`C:\Users\mateu\Documents\GitHub\jointhubs-os\Second Brain\Operations\weekly-status\`

Files use format `YYYYMMDD_project_status.md`. Read the latest one fully.

Extract per project:
- Status (🟢/🟡/🔴) and summary
- What was planned "na ten tydzień"
- Open blockers
- Risks flagged
- **Consecutive weeks** each blocker has appeared

If no previous file exists, note "Pierwszy raport — brak historii".

---

## STEP 1 — Load this week's daily reviews

Read all daily review files from the past 7 days:
`C:\Users\mateu\Documents\GitHub\jointhubs-os\Second Brain\Personal\daily\`

For each day, look for `{YYYY-MM-DD}-review.md` and `{YYYY-MM-DD}.md`.

Extract per project (Fenix / Neurohubs / Asystent):
- Mentions in Summary, Action Items, Gmail, Discord, Calendar sections
- Meetings attended
- Commits or technical work mentioned
- Communication with project-specific people
- Carry-forward items related to each project
- ThoughtMap Memory entries mentioning each project
- Google Tasks created/completed per project

Build a **per-project timeline** of the week's events.

---

## STEP 2 — Load Obsidian Vault daily notes (context only)

READ-ONLY from: `C:\Users\mateu\Documents\Obsidian Vault\10. Operations\Daily\`

For each day, read `{YYYY-MM-DD}.md`. Extract project-related content (Dziennik, ideation, ToDo) that wasn't in the jointhubs-os reviews.

---

## STEP 3 — Read project CONTEXT.md files

Read all three project memory files:
- `Second Brain/Projects/fenix/CONTEXT.md`
- `Second Brain/Projects/neurohubs/CONTEXT.md`
- `Second Brain/Projects/office_ai/CONTEXT.md`

Extract:
- Current status and active tasks
- Blockers and next milestone
- Decision history (recent decisions that affect this week)
- Key people per project

---

## STEP 4 — Google Calendar: project meetings

Check calendar for the past 7 days. Filter for events relevant to the three projects.

**Keywords:** Fenix, neurohubs, asystent, office, urzędnik, jointhubs, pitch, demo, feedback, beta, sprint, review, standup, call, meeting.

**Key people:** Anna Parot, Stan Betin, Konrad Bujak, Dr Orchowski, Artur Povodor, Dima Hakman, Kamil Kania, Kamil Berych, Anna Buchwald, Jakub Żerebecki.

Save: date, title, attendees, duration. Assign each meeting to a project.

Also check next 7 days for upcoming project meetings.

---

## STEP 5 — Gmail: project-related emails

Search Gmail for the past 7 days (`after:YYYY/MM/DD`):

- `(fenix OR "fenix-hubs" OR "fenix platform" OR "fenix-platform") after:YYYY/MM/DD`
- `(neurohubs OR "neuro hubs" OR EEG OR "Dr Orchowski" OR "Anna Buchwald") after:YYYY/MM/DD`
- `(asystent OR urzędnik OR "office assistant" OR "jointhubs-fenix" OR "Kamil Berych" OR Lubliniec) after:YYYY/MM/DD`
- `(github OR "pull request" OR CI OR "failed" OR "joint-hubs") after:YYYY/MM/DD`

For each match: subject, sender, date, 2-3 line summary. Assign to a project.
Skip newsletters/automated unless actionable (CI failure, new issue, security alert).

---

## STEP 6 — Google Tasks: project task tracking

Pull all Google Tasks. For each task:
- Assign to a project (by keyword or list name)
- Check status: completed / open / overdue
- Note age of overdue tasks

```
| Task | Project | Due | Status | Age |
|------|---------|-----|--------|-----|
```

---

## STEP 7 — Folder health: project repos

Scan project-related directories for size and change signals:

**Directories to check:**
- `C:\Users\mateu\Documents\GitHub\jointhubs-os\Second Brain\Projects\fenix\`
- `C:\Users\mateu\Documents\GitHub\jointhubs-os\Second Brain\Projects\neurohubs\`
- `C:\Users\mateu\Documents\GitHub\jointhubs-os\Second Brain\Projects\office_ai\`
- Any other GitHub repos under `C:\Users\mateu\Documents\GitHub\` matching project names

For each:
```
| Folder | Size | Δ week | Files modified (7d) | Key changes |
|--------|------|--------|--------------------|----|
```

This replaces GitHub API — folder changes signal active development.

---

## STEP 8 — ThoughtMap ChromaDB: project pattern analysis

Query ChromaDB for each project to surface historical patterns and trajectory.

**Database:** `C:\Users\mateu\Documents\GitHub\jointhubs-os\Second Brain\Projects\thoughtmap\data\chroma\`
**Collection:** `thoughtmap`

```python
import chromadb

client = chromadb.PersistentClient(
    path=r"C:\Users\mateu\Documents\GitHub\jointhubs-os\Second Brain\Projects\thoughtmap\data\chroma"
)
collection = client.get_collection("thoughtmap")

project_queries = [
    # Fenix
    "Fenix demo GTM launch",
    "Fenix value proposition sales",
    "Fenix CI deployment issues",
    # Neurohubs
    "Neurohubs EEG clinical partner",
    "Neurohubs NIF data standard",
    "Neurohubs grant funding",
    # Asystent
    "Asystent Urzędnika Lubliniec deployment",
    "office AI RAG pipeline",
    "Kamil Berych municipality",
]

for q in project_queries:
    results = collection.query(
        query_texts=[q],
        n_results=8,
        include=["documents", "metadatas", "distances"]
    )
    print(f"\n--- {q} ---")
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        if dist < 0.65:
            ts = meta.get('timestamp', '?')[:10]
            src = meta.get('source', '?')
            print(f"  [{ts}] ({src}, dist={dist:.3f}) {doc[:250]}")
```

**Fallback:** Read cluster files from `Second Brain/Operations/thoughtmap-out/clusters/*.md`

**Per-project analysis:**
- **Momentum trajectory** — is this project accelerating, stable, or losing momentum over 4 weeks?
- **Recurring blockers** — same blocker appearing in multiple weeks of ChromaDB data
- **Untapped connections** — ChromaDB results linking this project to people/resources not yet engaged
- **Decision history** — past decisions that may need revisiting based on current state

---

## STEP 9 — Graphify graphs: project community mapping

Scan for `graphify-out/GRAPH_REPORT.md` files. Currently known:
- `Second Brain/Projects/jointhubs/graphify-out-strategic/` — cross-project graph
- `Second Brain/Projects/office_ai/graphify-out/` — Asystent-specific graph

For each graph, identify:
- Which communities map to which projects
- Cross-project bridges (e.g., people or concepts connecting Fenix ↔ Neurohubs)
- Staleness check (build date vs. folder changes)

**Confidence:** `EXTRACTED` = reliable · `INFERRED` = verify · `AMBIGUOUS` = flag only

---

## STEP 10 — Peer network: project-level contacts

Read peer notes from `Second Brain/Personal/peers/` for people active in project contexts this week.

Per project, build a contacts table:
```
| Person | Role | Last contact | Channel | Status | Peer note? |
|--------|------|-------------|---------|--------|------------|
```

Flag: missing peer notes for active project contacts, >7 day response gaps.

---

## STEP 11 — Wispr Flow: project insights

Check if any Wispr recording sessions this week produced project-related content:
- Search daily reviews for completed Wispr sessions
- Check ChromaDB for recent `source: wispr-flow` entries mentioning project keywords
- Check if new notes were created in project folders from transcript processing

Also check if any project topics were proposed as Wispr sessions but not completed.

---

## STEP 12 — Write the project status report

Synthesize everything **IN POLISH**. Use the template below.

Save to:
`C:\Users\mateu\Documents\GitHub\jointhubs-os\Second Brain\Operations\weekly-status\{YYYYMMDD}_project_status.md`

Create the `weekly-status` folder if it doesn't exist.

```markdown
---
date: {TODAY_DATE}
tags: [weekly-status, projects, fenix, neurohubs, asystent-urzednika]
type: status-report
week: {YYYY-W{WW}}
previous_report: {FILENAME_OF_LAST_REPORT or "brak"}
---

# 📋 Tygodniowy Status Projektów — {TODAY_DATE}

> Raport wygenerowany automatycznie. Źródła: daily reviews (X/7 dni), CONTEXT.md (3 projekty), Google Calendar, Gmail, Google Tasks, ThoughtMap ChromaDB, graphify, peer notes, folder scan.

---

## 📈 Porównanie z poprzednim tygodniem

| Projekt | Poprzedni tydz. | Ten tydz. | Trend | Uzasadnienie |
|---------|-----------------|-----------|-------|-------------|
| Fenix | 🟢/🟡/🔴 | 🟢/🟡/🔴 | ↑/→/↓ | [1-liner why] |
| Neurohubs | 🟢/🟡/🔴 | 🟢/🟡/🔴 | ↑/→/↓ | [1-liner why] |
| Asystent Urzędnika | 🟢/🟡/🔴 | 🟢/🟡/🔴 | ↑/→/↓ | [1-liner why] |

### Realizacja planu z poprzedniego tygodnia
{Per project: co było zaplanowane vs co zrobione ✅/❌/⏳}

### Blokery powtarzające się (2+ tygodnie)
| Bloker | Projekt | Tygodni open | Eskalacja |
|--------|---------|-------------|-----------|
[Items with week count, flagged 🔴 if >3 weeks]

---

## 🔥 Fenix

**Status:** 🟢/🟡/🔴 — [1-sentence summary]

### Spotkania tygodnia
| Data | Temat | Uczestnicy | Czas |
|------|-------|------------|------|

### Aktywność techniczna (z daily reviews + folder scan)
- Pliki zmienione: {count in fenix folders}
- Kluczowe zmiany: {from daily reviews and folder delta}
- CI/GitHub signals: {from Gmail notifications}

### Emaile i komunikacja
{Summarized from daily reviews — per-person threads}

### Google Tasks — Fenix
| Task | Due | Status |
|------|-----|--------|

### Kontakty aktywne
| Osoba | Rola | Ostatni kontakt | Kanał | Dług odpowiedzi |
|-------|------|----------------|-------|-----------------|

### ThoughtMap — kontekst historyczny
- Trajectory: [accelerating/stable/losing momentum]
- Recurring unresolved: [themes from ChromaDB appearing 3+ weeks]
- Untapped: [connections or angles not yet explored]

### Blokery
{lista z wiekiem w tygodniach}

### Na ten tydzień
1. {konkretne zadanie 1}
2. {konkretne zadanie 2}
3. {konkretne zadanie 3}

---

## 🧠 Neurohubs

**Status:** 🟢/🟡/🔴 — [1-sentence summary]

### Spotkania tygodnia
| Data | Temat | Uczestnicy | Czas |
|------|-------|------------|------|

### Aktywność techniczna
{From daily reviews + folder scan}

### Granty i deadliny
| Grant | Deadline | Status | Następny krok |
|-------|----------|--------|---------------|

### Emaile i komunikacja
{Summarized from daily reviews}

### Google Tasks — Neurohubs
| Task | Due | Status |
|------|-----|--------|

### Kontakty aktywne
| Osoba | Rola | Ostatni kontakt | Kanał | Dług odpowiedzi |
|-------|------|----------------|-------|-----------------|

### ThoughtMap — kontekst historyczny
[Same structure as Fenix]

### Blokery
{lista z wiekiem}

### Na ten tydzień
1. ...
2. ...
3. ...

---

## 🏛️ Asystent Urzędnika

**Status:** 🟢/🟡/🔴 — [1-sentence summary]

### Spotkania tygodnia
| Data | Temat | Uczestnicy | Czas |
|------|-------|------------|------|

### Aktywność techniczna
{From daily reviews + folder scan + office_ai/ changes}

### Wdrożenie Lubliniec — dashboard
| Milestone | Status | ETA |
|-----------|--------|-----|
| Spec sprzętu | ✅/⏳/❌ | |
| Deployment packaging | ✅/⏳/❌ | |
| E2E testing | ✅/⏳/❌ | |
| Szkolenie | ✅/⏳/❌ | |

### Emaile i komunikacja
{Summarized from daily reviews}

### Google Tasks — Asystent
| Task | Due | Status |
|------|-----|--------|

### Kontakty aktywne
| Osoba | Rola | Ostatni kontakt | Kanał | Dług odpowiedzi |
|-------|------|----------------|-------|-----------------|

### ThoughtMap — kontekst historyczny
[Same structure as Fenix]

### Blokery
{lista z wiekiem}

### Na ten tydzień
1. ...
2. ...
3. ...

---

## 🔗 Cross-project insights

### Graphify bridge nodes
[People, concepts, or resources connecting multiple projects — from graph analysis]

### ThoughtMap cross-project themes
[ChromaDB results that appear in queries for different projects — signal convergence]

### Shared blockers
[Blockers affecting more than one project — e.g., AWS billing, GitHub PAT]

### Resource conflicts
[Same person/time needed by multiple projects — scheduling conflict]

---

## 📁 Folder Health — project repos

| Folder | Rozmiar | Δ tydzień | Pliki zmienione (7d) |
|--------|---------|-----------|---------------------|
[Per project folder + any external repos]

---

## 🎙️ Wispr Flow — projekt-related sessions

| Sesja | Projekt | Zrealizowana? | Notatka? |
|-------|---------|--------------|----------|
[This week's project-related recording sessions]

### Proponowane sesje na przyszły tydzień
[1-2 project deep-dive topics where voice articulation would help]

---

## 🎯 Priorytety na przyszły tydzień (cross-project)

1. {priorytet 1 — projekt + konkretne zadanie}
2. {priorytet 2}
3. {priorytet 3}

---

## ⚠️ Ryzyka i decyzje

| Ryzyko | Projekt | Powaga | Tygodni | Wymagana decyzja? |
|--------|---------|--------|---------|-------------------|
[Risk matrix with aging + explicit decision callouts]

---

## 📊 Podsumowanie tygodnia

| Projekt | Spotkania | Emaile | Tasks done | Tasks open | Pliki Δ | Status |
|---------|-----------|--------|------------|------------|---------|--------|
| Fenix | X | X | X | X | X | 🟢/🟡/🔴 |
| Neurohubs | X | X | X | X | X | 🟢/🟡/🔴 |
| Asystent | X | X | X | X | X | 🟢/🟡/🔴 |
```

---

## STEP 13 — Update CONTEXT.md files (if warranted)

After writing the status report, check if any project CONTEXT.md needs updating based on this week's signals:

- New milestone reached → update Current section
- Major decision made → add to Decision History
- Status changed (🟢→🟡 or worse) → update status field
- New blocker emerged → add to blockers

**Only update if there's a concrete, factual change** — not speculative. Add a timestamped entry, don't rewrite existing content.

---

## Operational rules

1. **Polish output** — content in Polish, section headers can mix English/Polish.
2. **No GitHub API** — derive all repo activity from daily reviews, folder scans, and Gmail CI notifications. Never call api.github.com.
3. **No browser automation for Drive/Canva** — derive document activity from daily reviews and Gmail notifications. If a specific document is mentioned in reviews, reference it.
4. **Personal vault is READ-ONLY** — never write to `C:\Users\mateu\Documents\Obsidian Vault\`.
5. **Blocker aging is mandatory** — every blocker must show how many consecutive weeks it has been unresolved. >3 weeks = 🔴.
6. **Concrete not generic** — every status, meeting, task, and risk must reference specific dates, people, or events.
7. **"Na ten tydzień" = exactly 3 items per project** — force prioritization.
8. **Cross-project section required** — always look for shared blockers, resource conflicts, and bridge connections.
9. **CONTEXT.md updates are conservative** — only update with verified factual changes, never speculative status.
10. **ChromaDB is context, not authority** — use for trajectory and pattern analysis, verify against source files.
11. **Trend justification required** — every ↑/→/↓ in the comparison table must have a 1-line reason.
