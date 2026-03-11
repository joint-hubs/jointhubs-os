---
type: note
status: active
tags: [type/docs, area/setup, area/vault]
created: 2026-03-11
updated: 2026-03-11
---

# Personalizacja Vault

Jak dostosować Jointhubs OS do siebie po forku.

---

## Co personalizujesz

Po forku masz kopię vault z przykładową strukturą. Żeby system działał dla Ciebie, musisz:

1. **Uzupełnić swoje dane** w instrukcjach globalnych
2. **Wyczyścić przykładowe notatki** i zacząć swoje
3. **Dostosować tagi i projekty**
4. **Opcjonalnie**: zmienić strukturę folderów

---

## Krok 1: Uzupełnij globalne instrukcje

### `copilot-instructions.md`

Plik `.github/copilot-instructions.md` — to główny przewodnik dla agentów. Znajdź sekcję na górze:

```markdown
**User**: [Your Name]
**Work style**: [How you work best]
**Active projects**: [Your projects]
```

Zamień na swoje dane, np.:
```markdown
**User**: Anna Kowalska
**Work style**: deep focus mornings, meetings afternoons, ADHD-friendly structure
**Active projects**: #thesis, #side-project, #freelance
```

### `assistant.instructions.md`

Plik `.github/instructions/assistant.instructions.md` — analogicznie, znajdź sekcję User Context i uzupełnij.

---

## Krok 2: Wyczyść przykładowe notatki

### Notatki dzienne
Folder `Second Brain/Operations/Periodic Notes/Daily/` zawiera przykładowe notatki. Masz dwie opcje:

**Opcja A: Zacznij od zera**
```powershell
# Usuń wszystkie przykładowe notatki dzienne (zachowaj README)
cd "Second Brain/Operations/Periodic Notes/Daily"
Get-ChildItem -Filter "*.md" -Exclude "README.md" | Remove-Item
```

**Opcja B: Zostaw jako przykłady**
Nie musisz usuwać — nowe notatki będą powstawać obok nich. Możesz wyczyścić później.

### Projekty
Folder `Second Brain/Projects/` ma przykładowe projekty. Przejrzyj je:
- Zostaw te, które Ci się przydadzą jako wzorce
- Usuń lub zarchiwizuj te, które nie pasują
- Każdy projekt, który zachowasz, powinien mieć aktualny `CONTEXT.md`

---

## Krok 3: Utwórz pierwszą notatkę dzienną

1. Utwórz plik: `Second Brain/Operations/Periodic Notes/Daily/YYYY-MM-DD.md` (dzisiejsza data)
2. Użyj szablonu:

```markdown
---
type: daily
status: active
tags: [type/daily]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Daily Log: YYYY-MM-DD

## Focus
Konfiguracja Jointhubs OS

## Logs
HH:MM — Vault skonfigurowany, first entry

## End of Day
- **Done**: Setup środowiska
- **Carried**: →
- **Tomorrow**:
```

Lub poproś agenta Planner:
```
Stwórz mi dzisiejszy daily log
```

---

## Krok 4: Dostosuj tagi

### Gdzie definiujesz tagi
- `.github/skills/obsidian-vault/references/tags.md` — pełna lista konwencji tagów
- `.github/instructions/assistant.instructions.md` — sekcja Tags

### Konwencja tagów

| Prefix | Przykłady | Kiedy |
|--------|-----------|-------|
| `type/` | `type/daily`, `type/meeting`, `type/note` | Kategoria notatki |
| `status/` | `status/active`, `status/done`, `status/paused` | Stan notatki |
| `project/` | `project/thesis`, `project/app` | Projekt |
| proste | `#thesis`, `#health`, `#ideas` | Szybkie tagowanie |

Dodaj swoje tagi projektów w odpowiednich plikach instrukcji.

---

## Krok 5: Utwórz swój pierwszy projekt

1. Utwórz folder: `Second Brain/Projects/moj-projekt/`
2. Dodaj `README.md`:

```markdown
---
type: project
status: active
tags: [project/moj-projekt]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Mój Projekt

Krótki opis — co to jest i po co.
```

3. Dodaj `CONTEXT.md`:

```markdown
---
type: context
status: active
tags: [project/moj-projekt]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# CONTEXT: Mój Projekt

## Past
Jak tu dotarliśmy. Geneza, wcześniejsze decyzje.

## Current
- **Status**: Początek
- **Aktywne zadania**: [co teraz]
- **Blokery**: [co blokuje]

## Future
- **Następny milestone**: [co dalej]
- **Cel końcowy**: [dokąd zmierzamy]
- **Otwarte pytania**: [co trzeba rozstrzygnąć]
```

Lub użyj prompta:
```
/new-project
```

---

## Krok 6: Zmodyfikuj instrukcje kontekstowe (opcjonalnie)

Jeśli zmieniłeś strukturę folderów, zaktualizuj pliki `.github/instructions/*.instructions.md`:

| Plik | Dotyczy |
|------|---------|
| `projects.instructions.md` | `Second Brain/Projects/**` |
| `operations.instructions.md` | `Second Brain/Operations/**` |
| `health.instructions.md` | `Second Brain/Personal/Health/**` |
| `stocks.instructions.md` | `Second Brain/Personal/Finances/stocks/**` |

Każdy plik ma w frontmatter `applyTo` — to ścieżka glob, gdzie instrukcje się stosują.

---

## Krok 7: Stwórz własnego agenta (opcjonalnie)

Jeśli masz domenę, która nie pasuje do istniejących agentów:

1. Skopiuj `.github/agents/_TEMPLATE.agent.md`
2. Nazwij plik np. `thesis-advisor.agent.md`
3. Wypełnij osobowość i odpowiedzialności
4. Przetestuj w Copilot Chat

Szczegóły: [[repo-init/setup-agents]]

---

## Kontrakt personalizacji

Gdy zmieniasz vault, pamiętaj o aktualizacji agentów:

| Zmieniłeś | Zaktualizuj |
|------------|-------------|
| Ścieżki folderów | `.github/skills/obsidian-vault/SKILL.md` |
| Format daily log | `.github/skills/daily-log/SKILL.md` |
| Strukturę projektów | `.github/skills/project-context/SKILL.md` |
| Nowe konwencje | `.github/instructions/*.instructions.md` |

To jest kluczowe — agenci nawigują po vault na podstawie tych instrukcji. Jeśli zmienisz strukturę bez aktualizacji, agenci się zgubią.

---

## Rozwiązywanie problemów

| Problem | Rozwiązanie |
|---------|-------------|
| Agent nie widzi moich notatek | Sprawdź, czy ścieżki w instrukcjach pasują do Twojej struktury |
| Wiki linki nie działają w Obsidian | Upewnij się, że Obsidian otwiera cały folder `jointhubs-os` jako vault |
| Tagi się nie wyświetlają | Sprawdź format: `tags: [tag1, tag2]` w frontmatter (YAML array) |
| Agent tworzy notatki w złym formacie | Zaktualizuj template w `.github/skills/daily-log/template.md` |
