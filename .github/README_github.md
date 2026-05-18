# .github

This folder contains VS Code Copilot configuration for the multi-agent assistant.

## Structure

```
.github/
├── agents/           ← AI personas (Planner, Tech Lead, Designer, etc.)
├── skills/           ← Domain knowledge loaded on-demand
├── prompts/          ← Reusable workflows (/commit, /weekly-review)
├── instructions/     ← Auto-applied rules based on file patterns
├── README_github.md  ← High-level map of this folder
└── AGENT_MAINTENANCE.md     ← How to maintain all of the above
```

## Quick Reference

| Component | Purpose | How to Use |
|-----------|---------|------------|
| **Agents** | AI personas with personality | Select from agent dropdown |
| **Skills** | Knowledge packs | Loaded automatically when relevant; see `skills/README.md` for the current catalog |
| **Prompts** | Workflows | Type `/prompt-name` in chat |
| **Instructions** | Rules | Applied automatically by file path |

## Documentation

- [Agent Maintenance Guide](AGENT_MAINTENANCE.md) — How to create and update everything
- [Agents README](agents/README.md) — Available agents and how to create them
- [Skills README](skills/README.md) — Available skills and how to create them
- [Prompts README](prompts/README.md) — Available prompts and how to create them
- [Instructions README](instructions/README.md) — File-specific rules

## External References

- [VS Code: Custom agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
- [VS Code: Prompt files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)
- [VS Code: Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- [VS Code: Custom instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
- [VS Code: MCP servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
- [Anthropic: Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

## Shared vs Local

- Shared configuration that is safe to commit lives directly in `agents/`, `skills/`, `prompts/`, and `instructions/`
- Private or experimental configuration should live in the matching `local/` subfolder
- Local folders are ignored by git, except for their `README.md` files which document the convention

## How It Works

1. **Agents** are personas you select for a session (Planner, Tech Lead, etc.)
2. **Skills** are knowledge that agents load when relevant (daily-log conventions, etc.)
3. **Prompts** are workflows you trigger with `/name` (commit, weekly-review, etc.)
4. **Instructions** apply automatically when editing matching files

The system uses progressive disclosure — only relevant content loads into context.

Current shared skill coverage includes vault conventions, daily and weekly workflows, project context, Obsidian Markdown, Bases, JSON Canvas, Obsidian CLI workflows, design review, strategy, travel planning, and clean web-page extraction.
