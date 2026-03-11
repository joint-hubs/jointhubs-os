# Prompts Directory

Prompt files are reusable, on-demand prompts for common development workflows.

## Shared vs Local

- Shared prompts that are safe to commit live directly in `.github/prompts/`
- Private or experimental prompts should live in `.github/prompts/local/`
- `.github/prompts/local/` is ignored by git, so personal workflows can stay local

## How to Use

Type `/` in chat followed by the prompt name:
- `/daily-kickoff` — Start your day
- `/session-end` — Wrap up work
- `/weekly-review` — Friday synthesis

## Available Prompts

### Session Management

| Prompt | Purpose | Best Time |
|--------|---------|-----------|
| [daily-kickoff](daily-kickoff.prompt.md) | Check context, set priorities | Morning / session start |
| [session-end](session-end.prompt.md) | Log progress, plan tomorrow | End of work block |
| [quick-capture](quick-capture.prompt.md) | Add entry to today's log | Anytime |

### Planning & Review

| Prompt | Purpose | Best Time |
|--------|---------|-----------|
| [weekly-review](weekly-review.prompt.md) | Synthesize the week | Friday afternoon |
| [deep-work](deep-work.prompt.md) | Start protected focus time | When you need focus |

### Project Work

| Prompt | Purpose | Best Time |
|--------|---------|-----------|
| [new-project](new-project.prompt.md) | Scaffold a new project | Project inception |
| [context-update](context-update.prompt.md) | Update project CONTEXT.md | After significant progress |
| [project-status](project-status.prompt.md) | Get overview of all projects | Planning sessions |

### Development

| Prompt | Purpose | Best Time |
|--------|---------|-----------|
| [commit](commit.prompt.md) | Generate commit message | After changes |
| [design-review](design-review.prompt.md) | Review interface design | Before implementation |
| [breakdown](breakdown.prompt.md) | Break task into implementation plan | Before complex work |
| [new-scraper](new-scraper.prompt.md) | Scaffold a web scraper | When building a scraper |

### Power Modes

| Prompt | Purpose | Best Time |
|--------|---------|----------|
| [beast-mode](beast-mode.prompt.md) | Autonomous problem solving | Complex multi-step tasks |

## Local-Only Prompts

If a prompt is personal, machine-specific, or experimental, keep it in `.github/prompts/local/`.

Current local examples:

| Prompt | Purpose |
|--------|---------|
| `plan-week` | Weekly planning workflow kept local |
| `remember` | Personal memory capture workflow |
## Prompts vs Agents vs Skills

| Type | When Used | Example |
|------|-----------|---------|
| **Agents** | Persona you work with for a session | Planner, Tech Lead |
| **Skills** | Knowledge loaded on-demand by agents | daily-log conventions |
| **Prompts** | One-shot workflows you trigger | `/weekly-review` |

## Creating New Prompts

1. Decide whether the prompt is `shared` or `local`
2. Create file: `.github/prompts/{name}.prompt.md` for shared prompts, or `.github/prompts/local/{name}.prompt.md` for private prompts
3. Add frontmatter with `name`, `description`, `agent`, `tools`
4. Write the prompt instructions
5. Update this README only for shared prompts

See [Maintenance Guide](../AGENT_MAINTENANCE.md) for details.
