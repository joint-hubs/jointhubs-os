---
type: note
status: active
tags: [type/docs, area/ai-development, area/skills]
created: 2026-03-11
updated: 2026-03-11
---

# Build Agent Skills

Jak tworzyć skills, które naprawdę poprawiają jakość pracy agenta.

## Po co w ogóle skill

Skill służy do zapakowania wyspecjalizowanej capability w sposób:

- przenośny
- ładowany on-demand
- rozszerzalny o przykłady, skrypty i pliki referencyjne

To jest lepsze niż kopiowanie długich instrukcji do promptów lub agentów.

## Jak skill ładuje się w praktyce

Zgodnie z VS Code i Anthropic, skill działa progresywnie:

1. **Metadata** z YAML frontmatter jest znane od początku
2. **Body `SKILL.md`** ładuje się dopiero, gdy skill jest trafny dla zadania
3. **Dodatkowe pliki i skrypty** są czytane lub wykonywane tylko wtedy, gdy są potrzebne

To oznacza, że możesz mieć bogaty skill bez ciągłego zużywania kontekstu.

## Minimalna struktura

```text
.github/skills/
  my-skill/
    SKILL.md
    examples/
    scripts/
    references/
```

W VS Code nazwa folderu powinna odpowiadać polu `name` w frontmatter.

## Minimalny SKILL.md

```md
---
name: api-design
description: Projektowanie API HTTP. Use when working on endpoint design, payload shape, validation, or status codes.
---

# API Design

## When to use
Użyj przy projektowaniu nowych endpointów lub refaktorze kontraktu API.

## Workflow
1. Zidentyfikuj consumerów i przypadki użycia.
2. Zaprojektuj resource shape.
3. Zdefiniuj validation i error model.
4. Sprawdź backward compatibility.

## Examples
Patrz [examples/create-user.md](examples/create-user.md).
```

## Co powinno być w dobrym skillu

- jasne **when to use**
- procedura krok po kroku
- przykłady input/output
- linki do lokalnych zasobów
- opcjonalne skrypty dla deterministycznych operacji

## Kiedy skill, a kiedy prompt

Użyj **skilla**, gdy:

- procedura wraca wielokrotnie
- potrzebujesz plików pomocniczych
- capability ma być przenośna między surface'ami i agentami

Użyj **prompt file**, gdy:

- chcesz jeden gotowy slash command
- zadanie jest lekkie i jednorazowe
- nie potrzebujesz dużej bazy pomocniczej

## Kiedy skill, a kiedy instruction

Użyj **instruction**, gdy to reguła.
Użyj **skill**, gdy to procedura lub capability.

Przykład:

- "Używaj 4 spaces" → instruction
- "Jak prowadzić weekly review z syntezą i ekstrakcją patternów" → skill

## Co wynika z Anthropic

Najważniejsze praktyki z dokumentacji Anthropic:

- opisuj dokładnie **co skill robi i kiedy go używać**
- wykorzystuj filesystem jako magazyn zasobów
- umieszczaj kod tam, gdzie chcesz deterministycznego działania
- traktuj każdy skill jak instalację oprogramowania i audytuj go pod kątem bezpieczeństwa

## Najczęstsze błędy

- zbyt ogólny opis `description`
- brak examples
- pakowanie do skilla zasad repo zamiast capability
- zbyt długi `SKILL.md` bez odsyłaczy do plików pomocniczych
- brak jawnego rozróżnienia, kiedy skill ma się załadować

## Wzorzec Jointhubs OS

W Jointhubs OS skill powinien zwykle zawierać:

- `SKILL.md` jako główną procedurę
- `template.md` jeśli generuje notatki lub dokumenty
- `references/` dla zasad i przykładów
- `scripts/` dla prostych, deterministycznych operacji

## Debugowanie skilli w VS Code

- sprawdź nazwę folderu i `name` w frontmatter
- sprawdź, czy `description` jasno opisuje use case
- użyj Chat Diagnostics, żeby zobaczyć czy skill został załadowany
- przetestuj zarówno auto-load, jak i manualne wywołanie przez `/`

## Źródła

- [VS Code: Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- [Anthropic: Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Agent Skills standard](https://agentskills.io/)
- [Reference skills repository](https://github.com/anthropics/skills)

To jest obszar, gdzie dobrze czytać równolegle VS Code i Anthropic, bo VS Code opisuje surface i format integracji, a Anthropic lepiej tłumaczy logikę progressive loading i bundlingu zasobów.

## Co dalej

- **[[ai-development/build-custom-agents]]**
- **[[ai-development/build-custom-mcp]]**
- **[[ai-development/references]]**
