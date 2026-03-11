---
type: note
status: active
tags: [type/docs, area/ai-development, area/copilot]
created: 2026-03-11
updated: 2026-03-11
---

# Agents, Skills, Prompts, Instructions

Najważniejsze rozróżnienie w praktyce Jointhubs OS.

## Krótka odpowiedź

- **Instructions** mówią agentowi, jakie reguły ma zawsze lub warunkowo respektować.
- **Prompt files** uruchamiają konkretny workflow na żądanie.
- **Agents** definiują personę, narzędzia, model i handoffy.
- **Skills** pakują wyspecjalizowaną umiejętność z instrukcjami, przykładami i dodatkowymi zasobami.
- **MCP** dostarcza zewnętrzne narzędzia, zasoby, prompty i aplikacje.

## Tabela decyzyjna

| Mechanizm | Użyj gdy | Czego nie robi |
|-----------|----------|----------------|
| **`.github/copilot-instructions.md`** | Chcesz ustawić globalne zasady dla repo | Nie daje persony ani własnych narzędzi |
| **`*.instructions.md`** | Chcesz reguły zależne od folderu, typu pliku albo zadania | Nie jest dobrym miejscem na wieloetapowe procedury |
| **`.prompt.md`** | Chcesz gotowy slash command do jednego zadania | Nie buduje trwałej persony |
| **`.agent.md`** | Chcesz wyspecjalizowanego agenta z tool restrictions i handoffami | Nie zastępuje skilli jako magazynu wiedzy proceduralnej |
| **`SKILL.md`** | Chcesz capability, którą model ładuje on-demand i może rozszerzyć o pliki/skrypty | Nie powinno służyć do globalnych reguł repo |
| **`mcp.json` + serwer MCP** | Model musi działać na zewnętrznych systemach | Nie zastępuje instrukcji ani prompt engineeringu |

## Jak to mapować mentalnie

- **Agent = kto pracuje**
- **Skill = jak pracuje w konkretnej klasie zadań**
- **Instruction = jakie reguły musi respektować**
- **Prompt = jaki workflow chcesz uruchomić teraz**
- **MCP = jakie ma ręce i oczy poza samym modelem**

To jest też zgodne z oficjalnym kierunkiem VS Code i Anthropic:

- VS Code opisuje **agents** jako trwałe persony z narzędziami, modelem i handoffami.
- VS Code opisuje **skills** jako przenośne capability z progressive loading.
- VS Code opisuje **prompt files** jako lekkie, ręcznie uruchamiane workflow.
- VS Code opisuje **instructions** jako reguły always-on albo conditional.
- Anthropic rekomenduje budowanie możliwie prostych, kompozycyjnych systemów i zwiększanie złożoności dopiero wtedy, gdy proste prompty nie wystarczają.

## Jak działa zachowanie agenta

Na finalne zachowanie wpływają jednocześnie:

1. Model bazowy
2. Always-on instructions
3. Warunkowe `.instructions.md`
4. Wybrany agent i jego body/frontmatter
5. Prompt file, jeśli został uruchomiony
6. Skills załadowane automatycznie lub ręcznie
7. Dostępne narzędzia, w tym MCP
8. Aktualny task i stan rozmowy

To znaczy, że agent nie jest "magią". To zestaw kontrolowanych warstw kontekstu i narzędzi.

## Dobre praktyki

- Zacznij od instrukcji, jeśli problem dotyczy reguły.
- Użyj prompt file, jeśli problem dotyczy powtarzalnego zadania.
- Użyj custom agenta, jeśli potrzebujesz persony, ograniczeń narzędzi albo handoffu.
- Użyj skilla, jeśli chcesz przenośnej wiedzy proceduralnej z przykładami i plikami pomocniczymi.
- Użyj MCP tylko wtedy, gdy agent musi realnie coś zrobić poza workspace.

## Czego unikać

- Nie wkładaj całej wiedzy proceduralnej do `copilot-instructions.md`.
- Nie rób z prompt files substytutu dla skilli.
- Nie rób z agenta wielkiego worka instrukcji bez jasnej roli.
- Nie buduj MCP tylko po to, żeby przekazać modelowi statyczny tekst.
- Nie dawaj agentowi więcej narzędzi niż potrzebuje.

## Źródła i uwagi

- Oficjalna dokumentacja VS Code i Anthropic jest źródłem nadrzędnym.
- [VS Code: Custom agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
- [VS Code: Prompt files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)
- [VS Code: Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- [VS Code: Custom instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
- [Anthropic: Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- Wątek Reddit jest użyteczny jako intuicja społeczności, ale nie jako specyfikacja: [difference between skills, instructions, prompts](https://www.reddit.com/r/GithubCopilot/comments/1r8pwqx/difference_between_skills_instructions_prompts/)
- Najlepszy skrót z Reddita, który warto zachować: **agent = what, skill = how**. To dobra metafora, ale nie pełna definicja.

## Co dalej

- **[[ai-development/build-custom-agents]]**
- **[[ai-development/build-agent-skills]]**
- **[[ai-development/build-custom-mcp]]**
- **[[ai-development/references]]**
