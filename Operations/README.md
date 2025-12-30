# Operations

This folder contains day-to-day operational notes.

## Structure

```
Operations/
├── Periodic Notes/       # Regular reviews and planning
│   ├── Daily/            # Daily notes (YYYY-MM-DD.md)
│   ├── Weekly/           # Weekly reviews (YYYY-Www.md)
│   ├── Monthly/          # Monthly reviews (YYYY-MM.md)
│   └── Quarterly/        # Quarterly reviews (YYYY-Qq.md)
└── Meetings/             # Meeting notes
```

## Daily Notes

Daily notes are the backbone of Jointhubs. They capture:
- **Focus** — Weekly priorities embedded from `#Next`
- **Dziennik** — Journal entries (thoughts, mood, observations)
- **Logs** — Timestamped activity log
- **ToDo** — Tasks query grouped by priority

Use the `Templater/Daily.md` template to create new daily notes.

## Weekly Notes

Weekly notes set priorities and aggregate daily journals:
- **Next** — 3-5 commitments for the week (gets embedded in daily notes)
- **History** — Embedded `#Dziennik` sections from each day
- **Tasks** — Completed and open tasks

Use the `Templater/Weekly.md` template for weekly reviews.

## Meetings

Meeting notes capture:
- Agenda and attendees
- Discussion notes
- Action items
- Follow-up dates

Use the `Templater/Meeting.md` template.
