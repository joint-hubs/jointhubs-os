# Projects

Professional project documentation.

## Structure

Each project gets its own folder:

```
Projects/
├── project-name/
│   ├── README.md       # Project overview
│   ├── notes.md        # Working notes
│   └── ...
```

## Project Template

Use `Templater/Project.md` to create new projects. It includes:
- Status and priority
- Goals and milestones
- Links to resources
- Decision log
- Task queries filtered by project tag

## Hashtags

Use hashtags to connect notes across the vault:
- `#fenix` — Fenix project
- `#neurohubs` — Neurohubs project
- `#globallogic` — Day job work

Add your own project tags and update:
- `.github/instructions/assistant.instructions.md`
- `.github/skills/obsidian-vault.md`

## Task Integration

Tasks tagged with project hashtags will appear in:
- Daily notes (via Tasks plugin query)
- Project README (via filtered task query)
- Weekly reviews (grouped by project)
