---
type: note
status: active
tags: [type/docs, area/ai-development, area/references]
created: 2026-03-11
updated: 2026-03-11
---

# AI Development References

Zebrane źródła, które tłumaczą jak działają agents, skills, prompt files, instructions i MCP.

## Najlepszy punkt startowy

Jeśli chcesz zrozumieć cały stack bez zgadywania, idź w tej kolejności:

1. [VS Code: Custom agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
2. [VS Code: Prompt files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)
3. [VS Code: Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
4. [VS Code: Custom instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
5. [VS Code: MCP servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
6. [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

## Oficjalne źródła VS Code

| Temat | Link | Po co czytać |
|-------|------|--------------|
| Custom agents | [Custom agents in VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-agents) | Format `.agent.md`, tools, handoffs, locations, security |
| Prompt files | [Use prompt files in VS Code](https://code.visualstudio.com/docs/copilot/customization/prompt-files) | Format `.prompt.md`, agent/tool precedence, slash workflows |
| Agent Skills | [Use Agent Skills in VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-skills) | Różnica skill vs instructions, progressive loading, standard |
| Custom instructions | [Use custom instructions in VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-instructions) | `.github/copilot-instructions.md`, `*.instructions.md`, `AGENTS.md` |
| MCP servers | [Add and manage MCP servers in VS Code](https://code.visualstudio.com/docs/copilot/customization/mcp-servers) | `mcp.json`, trust model, workspace vs user config, debugging |

## Oficjalne źródła Anthropic

| Temat | Link | Po co czytać |
|-------|------|--------------|
| Skills overview | [Anthropic: Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) | Jak działa progressive loading i filesystem-based skills |
| Agent design | [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | Kiedy agent ma sens, a kiedy lepszy jest prosty workflow |
| Skill guide PDF | [The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) | Dłuższe, praktyczne guidance do authoringu skills |

## Dodatkowe materiały warte uwagi

| Temat | Link | Uwaga |
|-------|------|-------|
| Agent Skills standard | [agentskills.io](https://agentskills.io/) | Przydatne, jeśli chcesz myśleć o skillach bardziej przenośnie niż tylko pod VS Code |
| Anthropic reference skills | [anthropics/skills](https://github.com/anthropics/skills) | Dobre przykłady struktury i zakresu skilli |
| Awesome Copilot | [github/awesome-copilot](https://github.com/github/awesome-copilot) | Praktyczne community examples dla promptów, agents i instructions |
| MCP spec | [Model Context Protocol](https://modelcontextprotocol.io/) | Warto przeczytać, jeśli budujesz własny serwer lub klienta MCP |

## Materiały społecznościowe

- [Reddit: difference between skills, instructions, prompts](https://www.reddit.com/r/GithubCopilot/comments/1r8pwqx/difference_between_skills_instructions_prompts/)

Ten wątek jest sensowny jako intuicja użytkowników i skrót myślowy, ale nie traktuj go jako źródła nadrzędnego nad dokumentacją VS Code albo Anthropic.

## Jak czytać te źródła praktycznie

- Gdy projektujesz `.agent.md`, czytaj głównie VS Code Custom agents i tylko pomocniczo Anthropic.
- Gdy projektujesz `SKILL.md`, czytaj razem VS Code Agent Skills i Anthropic Agent Skills overview.
- Gdy projektujesz workflow `/prompt`, czytaj Prompt files i sprawdzaj precedence tools vs agent.
- Gdy ustawiasz reguły repo, trzymaj się Custom instructions.
- Gdy wychodzisz poza repo i potrzebujesz narzędzi, przechodź do MCP docs i specyfikacji MCP.