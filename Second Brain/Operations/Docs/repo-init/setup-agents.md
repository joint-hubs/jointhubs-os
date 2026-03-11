---
type: note
status: active
tags: [type/docs, area/setup, area/agents]
created: 2026-03-11
updated: 2026-03-11
---

# Setup: Agenty AI

Jak używać, wybierać i tworzyć agentów w VS Code Copilot.

---

## Czym są agenci?

Agenci to **wyspecjalizowane osobowości AI** zdefiniowane w plikach `.github/agents/*.agent.md`. Każdy agent ma:

- **Osobowość** — ton, sposób myślenia, styl komunikacji
- **Odpowiedzialności** — co robi, a czego nie
- **Narzędzia** — z czego korzysta (np. MCP, terminal, pliki)
- **Handoffy** — kiedy przekazuje pracę innemu agentowi

Agenci czują się jak **różni specjaliści w zespole**, nie jak tryby jednego narzędzia.

---

## Dostępni agenci

### Agenci podstawowi

| Agent | Do czego | Kiedy wybrać |
|-------|----------|-------------|
| **Tech Lead** | Kod, architektura, debugging | Budujesz, naprawiasz, projektujesz system |
| **Planner** | Planowanie, priorytetyzacja, focus | Planujesz dzień/tydzień, potrzebujesz struktury |
| **Journal** | Refleksja, wzorce, synteza | Przetwarzasz co się wydarzyło, szukasz wzorców |
| **Debug** | Systematyczne debugowanie | Szukasz buga, analiza przyczyn |
| **Designer** | UX, design, user empathy | Oceniasz interfejs, decyzje designowe |

### Agenci specjalizowani

Możesz mieć dowolnych agentów domenowych, np.:
- **Scraper** — scraping danych, budowa aktorów Apify
- **Business Lead** — decyzje biznesowe, pricing, sales
- **Investor** — research inwestycyjny, analiza akcji
- **Travel Planner** — planowanie podróży

---

## Jak wybrać agenta

### Metoda 1: Przez interfejs
1. Otwórz Copilot Chat: `Ctrl+Shift+I`
2. Na dole pola wpisywania kliknij **selektor agenta** (ikona osoby lub nazwa aktualnego agenta)
3. Wybierz agenta z listy

### Metoda 2: Przez @ mention
1. W polu chatu wpisz `@`
2. Pojawi się lista agentów
3. Wybierz agenta → wpisz swoje pytanie

### Metoda 3: Bezpośrednio
1. Po prostu pisz w chacie — domyślny agent (bez specjalizacji) odpowie
2. Jeśli potrzebujesz innego, zmień selektor

---

## Jak agenci się zachowują

Każdy agent ma zdefiniowane:

### Ton i styl
- **Tech Lead**: bezpośredni, techniczny, myśli systemowo
- **Planner**: wspierający, organizujący, daje strukturę
- **Journal**: refleksyjny, szuka wzorców, pomaga przetwarzać
- **Debug**: metodyczny, systematyczny, krok po kroku

### Wiedza (Skills)
Agenci ładują `.github/skills/*/SKILL.md` gdy potrzebują wiedzy domenowej:
- Planner → `daily-log`, `weekly-review`, `session-rituals`
- Tech Lead → cała baza kodu + dokumentacja techniczna
- Journal → `weekly-review`, `obsidian-vault`

### Instrukcje kontekstowe
Pliki `.github/instructions/*.instructions.md` stosują się automatycznie gdy agent pracuje w danym folderze. Np.:
- Praca w `Second Brain/Projects/` → ładuje `projects.instructions.md`
- Praca w `Second Brain/Operations/` → ładuje `operations.instructions.md`

---

## Tworzenie własnego agenta

### Krok 1: Skopiuj szablon

```powershell
cp .github/agents/_TEMPLATE.agent.md .github/agents/moj-agent.agent.md
```

### Krok 2: Wypełnij sekcje

Otwórz plik i wypełnij:

```markdown
---
name: Nazwa Agenta
description: Jedno zdanie — co robi ten agent.
---

# Nazwa Agenta

## Soul
[Kim jest? Jaki ma charakter? Co go wyróżnia?]

## Responsibilities
- Co robi
- Czego NIE robi

## Tools
[Jakie narzędzia używa — MCP, terminal, pliki?]

## Workflow
[Jak podchodzi do zadań — krok po kroku]

## Handoffs
[Kiedy przekazuje pracę innemu agentowi]
```

### Krok 3: Przetestuj

1. Otwórz Copilot Chat
2. Wybierz nowego agenta z listy
3. Daj mu zadanie z jego domeny
4. Sprawdź, czy zachowuje się zgodnie z opisem

---

## Najlepsze praktyki

### Wybór agenta
- **Jeden agent na zadanie** — nie przeskakuj między agentami w ramach jednego problemu
- **Dopasuj do zadania** — planowanie → Planner, bug → Debug, refleksja → Journal
- **Domyślny jest OK** — jeśli nie wiesz kogo wybrać, domyślny Copilot też działa

### Komunikacja z agentem
- **Bądź konkretny** — "Zaplanuj mi jutrzejszy dzień" jest lepsze niż "pomóż mi"
- **Dawaj kontekst** — "Pracuję nad projektem X, mam problem z Y"
- **Używaj poleceń** — `/daily-kickoff`, `/session-end`, `/context-update`

### Utrzymanie agentów
- **Aktualizuj opisy** gdy agent nie zachowuje się jak powinien
- **Dodawaj examples** żeby agent lepiej rozumiał swoje zadania
- **Feedback loop** — jeśli agent robi coś źle, popraw instrukcje, nie powtarzaj korekty za każdym razem

---

## Prompty (szybkie workflow)

Jointhubs OS ma gotowe prompty w `.github/prompts/`:

| Prompt | Co robi |
|--------|---------|
| `/daily-kickoff` | Rozpocznij dzień z kontekstem |
| `/session-end` | Zamknij sesję czysto |
| `/new-project` | Utwórz nowy projekt |
| `/context-update` | Zaktualizuj CONTEXT.md projektu |
| `/weekly-review` | Piątkowa synteza tygodnia |
| `/beast-mode` | Autonomiczne rozwiązywanie problemów |
| `/remember` | Zapisz lekcję do pamięci |

Użyj ich wpisując `/` w polu chatu Copilot.

---

## Rozwiązywanie problemów

| Problem | Rozwiązanie |
|---------|-------------|
| Agent nie pojawia się na liście | Sprawdź, czy plik `.agent.md` jest w `.github/agents/` |
| Agent ignoruje instrukcje | Sprawdź, czy frontmatter YAML jest poprawny |
| Agent nie ładuje skills | Upewnij się, że skill jest w `copilot-instructions.md` |
| Agent nie widzi MCP | Sprawdź [[repo-init/setup-mcp-google]] |
| Agent zmienia osobowość w trakcie rozmowy | Normalne przy długich konwersacjach — zacznij nowy chat |

---

## Następne kroki

- [[repo-init/customize-vault]] — dostosuj vault do swoich potrzeb
- [[repo-init/setup-mcp-google]] — podłącz Google Workspace (jeśli jeszcze nie)
- [[ai-development/README]] — jeśli chcesz budować własnych agentów i skille
