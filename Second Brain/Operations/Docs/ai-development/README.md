---
type: note
status: active
tags: [type/docs, area/ai-development]
created: 2026-03-11
updated: 2026-03-11
---

# AI Development

Przewodniki dla osób, które chcą rozwijać własnych agentów, skills, prompty, instrukcje i serwery MCP w ekosystemie Jointhubs OS.

## Spis treści

| Dokument | Co znajdziesz |
|----------|---------------|
| [[ai-development/agents-skills-prompts-instructions]] | Kiedy używać agents, skills, prompts i instructions |
| [[ai-development/build-custom-agents]] | Jak projektować i rozwijać własnych agentów |
| [[ai-development/build-agent-skills]] | Jak tworzyć umiejętności, które agent ładuje progresywnie |
| [[ai-development/build-custom-mcp]] | Jak budować własne serwery MCP i dobrze projektować narzędzia |
| [[ai-development/references]] | Oficjalne źródła, porównania i dalsza lektura |

## Zalecana kolejność

1. **[[ai-development/agents-skills-prompts-instructions]]**
2. **[[ai-development/build-custom-agents]]**
3. **[[ai-development/build-agent-skills]]**
4. **[[ai-development/build-custom-mcp]]**
5. **[[ai-development/references]]**

## Główna zasada

Zaczynaj od najprostszego mechanizmu, który rozwiązuje problem:

- **instructions** dla stałych reguł
- **prompt file** dla jednego workflow uruchamianego ręcznie
- **agent** dla persony z własnymi narzędziami i handoffami
- **skill** dla przenośnej capability z instrukcjami, przykładami i zasobami
- **MCP** gdy model musi działać na zewnętrznych systemach przez narzędzia, zasoby lub prompty

## Źródła i dalsza lektura

Jeśli chcesz samodzielnie zweryfikować założenia z tych notatek, zacznij od:

- [[ai-development/references]]
- [VS Code: Custom agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
- [VS Code: Prompt files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)
- [VS Code: Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- [VS Code: Custom instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
- [VS Code: MCP servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
