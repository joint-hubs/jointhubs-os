# Obsidian Vault Navigation Skill

> How to navigate and work with the Jointhubs vault structure

## Vault Structure

The vault is organized into four main areas:

```
/
├── Operations/           # Day-to-day operations
│   ├── Periodic Notes/   # Daily, Weekly, Monthly, Quarterly
│   │   ├── Daily/        # YYYY-MM-DD.md
│   │   └── Weekly/       # YYYY-Www.md
│   └── Meetings/         # Meeting notes
├── Personal/             # Personal life tracking
│   ├── Health/           # Training, nutrition logs
│   ├── Finances/         # Financial tracking
│   ├── Events/           # Personal events
│   └── Classes/          # Learning & courses
├── Projects/             # Professional projects
│   └── project-name/     # Each project gets a folder
└── Templater/            # Templates for new notes
```

---

## File Naming Conventions

| Note Type | Format | Example | Location |
|-----------|--------|---------|----------|
| Daily | `YYYY-MM-DD.md` | `2025-12-30.md` | `Operations/Periodic Notes/Daily/` |
| Weekly | `YYYY-Www.md` | `2025-W52.md` | `Operations/Periodic Notes/Weekly/` |
| Monthly | `YYYY-MM.md` | `2025-12.md` | `Operations/Periodic Notes/Monthly/` |
| Quarterly | `YYYY-Qq.md` | `2025-Q4.md` | `Operations/Periodic Notes/Quarterly/` |
| Meetings | Descriptive | `Client Kickoff.md` | `Operations/Meetings/` |
| Projects | Folder name | `fenix/` | `Projects/` |

---

## Daily Note Structure

Daily notes use Templater and have this structure:

```markdown
---
date: YYYY-MM-DD
week: YYYY-Www
year: YYYY
tags:
  - daily
type: notes
---

# helpers
- Links to frequently used notes (training-log, nutrition-log, etc.)

## ideation
- Workflow for capturing ideas

## 🎯 Focus (from last weekly review)
![[YYYY-Www#Next]]  ← Embeds weekly commitments

## Dziennik
- Journal entries, thoughts, observations

## Logs
YYYY-MM-DD HH:mm - Activity description

## ToDo
```tasks query block```

## Files created/modified today
```dataview queries```
```

### Key Sections to Read

| Section | What It Contains |
|---------|------------------|
| `## 🎯 Focus` | Weekly priorities (embedded from weekly note) |
| `## Dziennik` | Journal - thoughts, mood, observations |
| `## Logs` | Timestamped activity log |
| `## ToDo` | Tasks query showing pending items |

---

## Weekly Note Structure

Weekly notes aggregate daily notes and set priorities:

```markdown
---
week: YYYY-Www
year: YYYY
tags: weekly
type: notes
---

## Next
> Commitments for this week (3-5 items max)
- [ ] Task 1
- [ ] Task 2

## Last Week
![[Previous-Week#Next]]  ← Shows what was planned last week

## Wins
> What went well?

## History
![[Monday#Dziennik]]
![[Tuesday#Dziennik]]
... (embeds each day's journal)

## Tasks
### Closed this week
```tasks done query```

### Still open
```tasks not done query```
```

### Key Sections

| Section | Purpose |
|---------|---------|
| `## Next` | THIS WEEK'S PRIORITIES - most important |
| `## Last Week` | Review of previous week's commitments |
| `## History` | Embedded journals from each day |
| `## Tasks` | Task completion tracking |

---

## Tasks Plugin Usage

Tasks are managed with the Obsidian Tasks plugin:

### Task Format
```markdown
- [ ] Task description ⏫ 📅 2025-12-30
```

### Priority Markers
- `⏫` — Highest priority
- `🔼` — High priority  
- `🔽` — Low priority
- (no marker) — Medium priority

### Task Display in Daily Notes

Tasks are displayed grouped by priority and start date:

```tasks
not done
due after 2024-01-01
sort by priority
group by priority
group by function task.start.format("YYYY-MM-DD dddd")
```

---

## Hashtag System

Project and context tags used throughout the vault:

| Tag | Meaning |
|-----|---------|
| `#fenix` | Fenix project work |
| `#neurohubs` | Neurohubs project work |
| `#globallogic` | Day job (GlobalLogic) |
| `#daily` | Daily note |
| `#weekly` | Weekly note |
| `#monthly` | Monthly review |
| `#quarterly` | Quarterly review |
| `#meeting` | Meeting notes |
| `#project` | Project documentation |

---

## Health Tracking (Personal/Health/)

Three key files for health tracking:

| File | Purpose |
|------|---------|
| `training-log.md` | Gym sessions - exercises, weights, reps, PRs |
| `nutrition-log.md` | Daily macros - protein, carbs, fat, calories |
| `food-database.md` | Reference table for food macros |

### Training Log Format
- Summary section with weekly volume and PRs
- Daily sessions in tables: Exercise, Set, Weight, Reps, Notes

### Nutrition Log Format
- Daily summary table with macros, steps, rating
- Detailed meal breakdowns per day

---

## Quick Navigation

### Find Today's Note
```
Operations/Periodic Notes/Daily/[YYYY-MM-DD].md
```

### Find This Week's Review
```
Operations/Periodic Notes/Weekly/[YYYY-Www].md
```

### Find Active Projects
```
Projects/[project-name]/
```

### Find Recent Meetings
```
Operations/Meetings/
```

### Find Health Data
```
Personal/Health/training-log.md
Personal/Health/nutrition-log.md
```

---

## Templates (Templater/)

Available templates for creating new notes:

| Template | Use For |
|----------|---------|
| `Daily.md` | New daily note |
| `Weekly.md` | New weekly review |
| `Monthly.md` | Monthly review |
| `Quarterly.md` | Quarterly review |
| `Meeting.md` | Meeting notes |
| `Project.md` | New project |
| `Finances.md` | Monthly finances |
| `Event.md` | Personal events |
| `Class.md` | Learning/courses |
