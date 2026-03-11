# Vault Structure Reference

Detailed structure of the Jointhubs Obsidian vault.

## Top-Level Layout

```
/
├── .github/                    # Agent & AI configuration
│   ├── agents/                 # Agent definitions (.agent.md)
│   ├── skills/                 # Domain knowledge (SKILL.md)
│   ├── prompts/                # Reusable prompt workflows (.prompt.md)
│   ├── instructions/           # Path-scoped rules (.instructions.md)
│   └── README_github.md        # High-level map of AI configuration
│
└── Second Brain/               # All notes live here
    ├── Operations/             # Day-to-day operations
    ├── Personal/               # Life tracking
    └── Projects/               # Professional work
```

## Operations Directory

```
Second Brain/Operations/
├── Periodic Notes/
│   ├── Daily/                  # YYYY-MM-DD.md
│   │   ├── 2026-01-19.md
│   │   ├── 2026-01-20.md
│   │   └── ...
│   ├── Weekly/                 # YYYY-Www.md
│   │   ├── 2026-W03.md
│   │   └── ...
│   └── Monthly/                # YYYY-MM.md (optional)
│       └── ...
└── Meetings/                   # Meeting notes
    ├── 2026-01-20-standup.md
    └── ...
```

## Personal Directory

```
Second Brain/Personal/
├── Classes/                    # Learning & courses
├── Events/                     # Personal events
├── Finances/                   # Financial tracking
├── Health/                     # Health logs
│   ├── nutrition-log.md
│   ├── training-log.md
│   ├── food-database.md
│   └── routines.md
└── Profile/                    # Personal branding
    ├── cv.md
    ├── linkedin-post-drafts.md
    └── ME.md
```

## Projects Directory

```
Second Brain/Projects/
├── {project-name}/             # Each project is a folder
│   ├── README.md               # What is this project?
│   ├── CONTEXT.md              # Past / Current / Future state
│   └── deep_work/              # Focus session notes (optional)
│
<!-- CUSTOMIZE: Add your own projects -->
├── my-app/                     # Example project
├── research/                   # Example project
└── ideas/                      # Idea parking lot
```

## File Naming Conventions

| Type | Format | Example |
|------|--------|---------|
| Daily note | `YYYY-MM-DD.md` | `2026-01-20.md` |
| Weekly note | `YYYY-Www.md` | `2026-W03.md` |
| Monthly note | `YYYY-MM.md` | `2026-01.md` |
| Meeting | `YYYY-MM-DD-{topic}.md` | `2026-01-20-standup.md` |
| Project folder | `kebab-case/` | `my-project/` |
