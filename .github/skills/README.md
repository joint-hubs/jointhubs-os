# Skills Directory

Agent Skills are folders of instructions and resources that AI agents load on-demand.

## Available Skills

| Skill | Purpose | Trigger Phrases |
|-------|---------|-----------------|
| [daily-log](daily-log/) | Daily note as agent memory | "daily log", "session start" |
| [weekly-review](weekly-review/) | Weekly reflection process | "weekly review", "Friday review" |
| [project-context](project-context/) | Project state management | "CONTEXT.md", "project status" |
| [session-rituals](session-rituals/) | Planning & review sessions | "planning session", "kickoff" |
| [obsidian-vault](obsidian-vault/) | Vault conventions | "file naming", "frontmatter" |
| [focus-support](focus-support/) | Focus and deep work | "can't focus", "deep work" |

## How Skills Work

Skills use **progressive disclosure**:

1. **Discovery** — Agent reads `name` and `description` from SKILL.md frontmatter
2. **Loading** — When relevant, full SKILL.md loads into context
3. **Resources** — Templates and scripts load only when referenced

This means many skills with minimal context cost.

## Skill Structure

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── template.md       # Optional: template
├── scripts/          # Optional: automation scripts
└── examples/         # Optional: example files
```

## Creating Skills

1. Create folder: `.github/skills/{skill-name}/`
2. Add `SKILL.md` with frontmatter:

```yaml
---
name: skill-name
description: |
  What this skill does.
  Use when: "trigger phrase 1", "trigger phrase 2".
---
```

3. Add instructions in the body
4. Add resources (templates, scripts) as needed
5. Update this README

## Templates

Skills can include templates as resources.

Templates live in the skill folder. If you use Obsidian Templater (or another system), copy the template into your own templates folder.

## Related

- [Agent Skills Spec](https://agentskills.io/)
- [VS Code Skills Docs](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
