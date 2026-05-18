# Skills Directory

> ← [Back to Jointhubs OS](../../README.md)

Agent Skills are folders of instructions and resources that AI agents load on-demand.

## Shared vs Local

- Shared skills that are safe to commit live in `.github/skills/{skill-name}/`
- Private or experimental skills should live in `.github/skills/local/{skill-name}/`
- `.github/skills/local/` is ignored by git, so you can keep personal playbooks and unstable skills there

## Available Skills

| Skill | Purpose | Trigger Phrases |
|-------|---------|-----------------|
| [daily-log](daily-log/) | Daily note as agent memory | "daily log", "session start" |
| [weekly-review](weekly-review/) | Weekly reflection process | "weekly review", "Friday review" |
| [project-context](project-context/) | Project state management | "CONTEXT.md", "project status" |
| [obsidian-vault](obsidian-vault/) | Vault conventions | "file naming", "frontmatter" |
| [obsidian-markdown](obsidian-markdown/) | Obsidian Flavored Markdown syntax | "wikilinks", "callouts", "embeds", "OFM" |
| [obsidian-bases](obsidian-bases/) | Obsidian Bases (.base files) | "bases", "table view", "card view", "filter notes" |
| [json-canvas](json-canvas/) | JSON Canvas (.canvas files) | "canvas", "mind map", "flowchart", "visual canvas" |
| [obsidian-cli](obsidian-cli/) | Obsidian CLI vault operations | "obsidian cli", "vault from terminal", "plugin dev" |
| [firecrawl](firecrawl/) | Managed markdown-first crawling and site mapping | "firecrawl", "crawl docs", "scrape website to markdown" |
| [design-review](design-review/) | Product and UX critique | "review design", "check accessibility" |
| [strategic-thinking](strategic-thinking/) | Decision frameworks and trade-offs | "options", "decision", "trade-offs" |
| [agentic-engineering](agentic-engineering/) | Building and evolving the agent system | "custom agents", "skills", "instructions" |
| [travel-research](travel-research/) | Travel planning and accommodation research | "find hotel", "compare flights" |
| [thoughtmap](thoughtmap/) | ThoughtMap pipeline, MCP vector search, cluster analysis | "search thoughts", "clusters", "knowledge base", "vector search" |

## Domain Skills In This Repo

These are useful but more specialized than the vault conventions and session-tracking skills:

| Skill | Purpose |
|-------|---------|
| [obsidian-markdown](obsidian-markdown/) | Obsidian Flavored Markdown syntax reference |
| [obsidian-bases](obsidian-bases/) | Obsidian Bases (.base files) with views and formulas |
| [json-canvas](json-canvas/) | JSON Canvas (.canvas files) for visual thinking |
| [obsidian-cli](obsidian-cli/) | Obsidian CLI for vault operations and plugin dev |
| [firecrawl](firecrawl/) | Managed markdown-first scraping, crawling, and site mapping |
| [agentic-engineering](agentic-engineering/) | Building and evolving the agent system |
| [design-review](design-review/) | Product and UX critique |
| [strategic-thinking](strategic-thinking/) | Decision frameworks and trade-offs |
| [travel-research](travel-research/) | Travel planning and accommodation research |
| [thoughtmap](thoughtmap/) | ThoughtMap pipeline, MCP vector search, cluster analysis |

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

1. Decide whether the skill is `shared` or `local`
2. Create folder: `.github/skills/{skill-name}/` for shared skills, or `.github/skills/local/{skill-name}/` for private skills
3. Add `SKILL.md` with frontmatter:

```yaml
---
name: skill-name
description: |
  What this skill does.
  Use when: "trigger phrase 1", "trigger phrase 2".
---
```

4. Add instructions in the body
5. Add resources (templates, scripts) as needed
6. Update this README only for shared skills

## When To Keep A Skill Local

- The skill contains sensitive client or personal context
- The workflow is still changing quickly
- The skill is useful only for your local vault or machine

Promote it into the shared area only when the content is reusable and safe to publish.

## Templates

Skills can include templates as resources.

Templates live in the skill folder. If you use Obsidian Templater (or another system), copy the template into your own templates folder.

## Related

- [Agent Skills Spec](https://agentskills.io/)
- [VS Code Skills Docs](https://code.visualstudio.com/docs/copilot/customization/agent-skills)

---

## Navigation

| Where | What |
|-------|------|
| ← [Jointhubs OS](../../README.md) | System overview |
| → [Agents](../agents/README.md) | Who uses these skills |
| → [Instructions](../instructions/README.md) | Rules vs knowledge |
| → [Prompts](../prompts/README.md) | One-command workflows |
| → [Second Brain](../../Second%20Brain/README.md) | The notes skills describe |
