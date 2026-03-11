---
type: note
status: active
tags: [type/docs, area/ai-development, area/agents]
created: 2026-03-11
updated: 2026-03-11
---

# Build Custom Agents

Jak rozwijać własnych agentów tak, żeby byli przewidywalni, użyteczni i łatwi do utrzymania.

## Czym jest custom agent w VS Code

Custom agent to plik `.agent.md` w `.github/agents/` lub lokalizacji user-level. Agent definiuje:

- nazwę i opis
- personę
- dostępne narzędzia
- opcjonalny model
- dostępnych subagentów
- opcjonalne handoffy

Oficjalnie to jest właściwy mechanizm, gdy chcesz trwałą personę z określonym zakresem działania, a nie tylko jednorazowy prompt.

## Minimalny szkielet

```md
---
name: Research Lead
description: Analizuje problem, zbiera kontekst i proponuje plan.
tools: ['search', 'fetch']
agents: []
---

# Research Lead

## Mission
Zbieraj kontekst i proponuj plan. Nie implementuj zmian.

## Workflow
1. Zbierz kontekst.
2. Wypisz ryzyka i luki.
3. Zaproponuj kolejny krok.
```

## Jak projektować dobrego agenta

### 1. Zacznij od roli, nie od stylu

Najpierw odpowiedz sobie:

- Za co ten agent odpowiada?
- Jakiego typu zadania ma przyjmować?
- Jakich zadań ma odmawiać albo przekazywać dalej?

Jeśli nie potrafisz tego opisać jednym akapitem, agent jest jeszcze źle zdefiniowany.

### 2. Ogranicz narzędzia

VS Code oficjalnie wspiera definiowanie `tools` w frontmatter. To ważne z dwóch powodów:

- bezpieczeństwo
- przewidywalność zachowania

Zasada praktyczna:

- planowanie i research: tylko read-only tools
- implementacja: search + edit + terminal
- review/security: search + read + ewentualnie limited terminal

To jest zgodne z zasadą least privilege z dokumentacji custom agents.

### 3. Trzymaj workflow prosty

Anthropic rekomenduje prostotę zamiast nadmiernej agentyzacji. Agent powinien mieć prosty, czytelny workflow:

1. zrozum task
2. zbierz ground truth z otoczenia
3. wykonaj właściwe kroki
4. zatrzymaj się na blockerach
5. przekaż dalej lub zakończ

### 4. Oddziel rolę od procedury

- Rola, ton, granice, narzędzia: **agent**
- Wielokrotnie używane procedury: **skill**
- Jednorazowe skróty: **prompt file**

To najczęstszy błąd w custom agents: pakowanie do nich wszystkiego.

## Handoffs

Handoffs w VS Code pozwalają budować kontrolowane przejścia między agentami, np.:

- Planner → Tech Lead
- Tech Lead → Debug
- Tech Lead → Review

To dobry mechanizm, gdy chcesz zachować etapowość zamiast jednego autonomicznego super-agenta.

Przykład:

```yaml
handoffs:
  - label: Start Implementation
    agent: Tech Lead
    prompt: Implement the approved plan.
    send: false
```

## Jak agent "się zachowuje"

Na zachowanie wpływają cztery rzeczy najczęściej:

1. Jakość opisu roli
2. Jakość i ograniczenie toolsetu
3. Zgodność z instrukcjami repo
4. Jakość skilli, do których może sięgnąć

Jeśli agent jest chaotyczny, zwykle problemem nie jest sama persona, tylko jedna z tych warstw.

## Kiedy zrobić nowego agenta

Zrób nowego agenta, gdy:

- masz powtarzalny typ pracy z innym trybem myślenia
- chcesz inny zestaw narzędzi
- potrzebujesz innego poziomu autonomii
- chcesz wprowadzić handoff do kolejnego etapu

Nie rób nowego agenta, gdy wystarczy nowy prompt albo skill.

## Debugowanie custom agenta

- Sprawdź, czy plik jest w `.github/agents/`.
- Sprawdź frontmatter YAML.
- Otwórz Chat Diagnostics w VS Code i zobacz, czy agent jest ładowany.
- Sprawdź, czy problem nie leży w skillu albo instruction file.
- Upewnij się, że agent ma tylko potrzebne narzędzia.

## Rekomendowany proces w Jointhubs OS

1. Zdefiniuj rolę i granice.
2. Zbuduj prosty `.agent.md`.
3. Przetestuj na 3-5 realnych zadaniach.
4. Wyjmij powtarzalne procedury do skilla.
5. Dodaj handoffy dopiero gdy workflow jest stabilny.

## Źródła

- [VS Code: Custom agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
- [VS Code: Prompt files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)
- [VS Code: Custom instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

Najważniejsze rzeczy do samodzielnego sprawdzenia w źródłach:

- format frontmatter i obsługiwane pola agenta
- handoffs i ich semantyka
- zasada least privilege dla `tools`
- kiedy wystarczy prompt workflow zamiast nowego agenta

## Co dalej

- **[[ai-development/build-agent-skills]]**
- **[[ai-development/build-custom-mcp]]**
- **[[ai-development/references]]**
