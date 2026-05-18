# Automation

> ← [Back to Jointhubs OS](../../README.md)

Scheduled tasks that keep ThoughtMap and graphify outputs fresh without manual intervention.

## What Runs

| Task | Schedule | What It Does | Runtime |
|------|----------|--------------|---------|
| **jointhubs-ThoughtMap** | Nightly 2:00 AM | Starts Docker Compose, runs the full pipeline (extract → chunk → embed → cluster → viz), leaves containers running | ~2-3 min |
| **jointhubs-Graphify** | Weekly Sunday 3:00 AM | Runs graphify on active project folders, incremental (only changed files) | ~1-5 min |

## Install

Run as Administrator:

```powershell
powershell -ExecutionPolicy Bypass -File ".github\automation\install-schedules.ps1"
```

Verify:

```powershell
Get-ScheduledTask -TaskName "jointhubs-*" | Format-Table TaskName, State
```

## Uninstall

```powershell
powershell -ExecutionPolicy Bypass -File ".github\automation\uninstall-schedules.ps1"
```

## Manual Run

```powershell
# Run ThoughtMap now
Start-ScheduledTask -TaskName "jointhubs-ThoughtMap"

# Run graphify now
Start-ScheduledTask -TaskName "jointhubs-Graphify"

# Or run scripts directly
.github\automation\thoughtmap-nightly.ps1
.github\automation\graphify-weekly.ps1
```

## Logs

Both scripts log to `Second Brain/Operations/automation-logs/`:

```
automation-logs/
├── thoughtmap-2026-04-13_020000.log
├── thoughtmap-2026-04-14_020000.log
├── graphify-2026-04-13_030000.log
└── ...
```

Logs auto-rotate: ThoughtMap keeps last 30, graphify keeps last 12.

## Prerequisites

- **Docker Desktop** must be running (for ThoughtMap)
- **Python** with `graphifyy` package installed (for graphify)
- Machine must be awake at scheduled time (tasks use `StartWhenAvailable` — if missed, runs at next wake)

## Graphify Project List

The weekly graphify refresh processes these folders under `Second Brain/Projects/`:

- `thoughtmap` — vector pipeline code
- `office_ai` — Asystent Urzędnika
- `fenix` — Fenix project
- `neurohubs` — Neurohubs project

To add/remove projects, edit the `$Projects` array in `graphify-weekly.ps1`.

## Notes

- The graphify weekly script uses **AST extraction + cached semantic data only** — no LLM calls. This means it's free to run but won't pick up new semantic connections in docs/papers until you run `/graphify` interactively.
- ThoughtMap nightly spins up Docker containers, so Docker Desktop must be running or set to auto-start.
- Both scripts are idempotent — safe to run multiple times.

---

## Navigation

| Where | What |
|-------|------|
| ← [Jointhubs OS](../../README.md) | System overview |
| → [ThoughtMap](../../Second%20Brain/Projects/thoughtmap/README.md) | The pipeline these scripts run |
| → [Operations](../../Second%20Brain/Operations/README.md) | Where output lands |
