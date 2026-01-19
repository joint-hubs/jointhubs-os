---
applyTo: '{path/pattern}/**'
---

# {Directory/Context} Instructions

> These instructions apply to all files matching: `{path/pattern}/**`

## Context

{What is this directory for? What kind of work happens here?}

## Rules

1. {Rule 1}
2. {Rule 2}
3. {Rule 3}

## Conventions

{Naming conventions, file structure, patterns to follow}

## Related

- `.github/skills/{relevant-skill}.md`

---

## How to Create Your Own Instructions

Instructions are **directory-scoped** — they apply to specific paths.

### Steps

1. **Copy this template** to: `{context-name}.instructions.md`
2. **Set the applyTo pattern** — Use glob syntax
3. **Define rules** — What should agents always do here?
4. **Add conventions** — Naming, structure, patterns

### Pattern Examples

```yaml
applyTo: 'Projects/**'           # All projects
applyTo: 'Projects/my-app/**'    # Specific project
applyTo: '**/*.py'               # All Python files
applyTo: 'Operations/**'         # Operations directory
```

### Tips

- **Keep it short** — Instructions load every time, don't bloat
- **Rules, not guidance** — These are constraints, not suggestions
- **Reference skills** — Point to detailed knowledge elsewhere
