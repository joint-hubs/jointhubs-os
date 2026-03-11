---
type: note
status: active
tags: [type/docs, area/setup]
created: 2026-03-11
updated: 2026-03-11
---

# Setup: Środowisko

Klik po kliku — od zera do działającego workspace Jointhubs OS.

---

## Wymagania

| Narzędzie | Do czego | Link |
|-----------|----------|------|
| **Git** | Wersjonowanie, clone, push | https://git-scm.com/downloads |
| **VS Code** | Edytor + Copilot + agenty | https://code.visualstudio.com/ |
| **Obsidian** | Otwieranie vault z notatkami | https://obsidian.md/ |
| **GitHub account** | Fork repo, Copilot subscription | https://github.com/ |
| **GitHub Copilot** | Subskrypcja (Free / Pro / Business) | https://github.com/features/copilot |

---

## Krok 1: Zainstaluj Git

### Windows
1. Pobierz instalator z https://git-scm.com/downloads
2. Uruchom instalator — domyślne opcje są OK
3. Upewnij się, że zaznaczono **"Git from the command line and also from 3rd-party software"**
4. Sprawdź:
   ```powershell
   git --version
   ```

### macOS
```bash
brew install git
# lub: xcode-select --install
git --version
```

### Linux
```bash
sudo apt install git   # Ubuntu/Debian
sudo dnf install git   # Fedora
git --version
```

### Konfiguracja Git (jednorazowo)
```bash
git config --global user.name "Twoje Imię"
git config --global user.email "twoj@email.com"
```

---

## Krok 2: Zainstaluj VS Code

1. Pobierz z https://code.visualstudio.com/
2. Zainstaluj — domyślne opcje
3. Opcjonalnie zaznacz **"Add to PATH"** (Windows) — pozwoli otworzyć VS Code z terminala komendą `code`

---

## Krok 3: Zainstaluj rozszerzenia VS Code

Po uruchomieniu VS Code:

1. Otwórz panel rozszerzeń: `Ctrl+Shift+X` (Windows/Linux) / `Cmd+Shift+X` (macOS)
2. Zainstaluj:
   - **GitHub Copilot** (`GitHub.copilot`)
   - **GitHub Copilot Chat** (`GitHub.copilot-chat`)
3. Zaloguj się do GitHub gdy pojawi się monit

> Repo ma plik `.vscode/extensions.json` z rekomendacjami — VS Code zasugeruje instalację automatycznie po otworzeniu projektu.

---

## Krok 4: Zainstaluj Obsidian

1. Pobierz z https://obsidian.md/
2. Zainstaluj — domyślne opcje
3. **Nie otwieraj jeszcze vault** — najpierw potrzebujemy repo

---

## Krok 5: Fork i Clone repo

### Fork na GitHub
1. Wejdź na https://github.com/jointhubs/jointhubs-os (lub link udostępniony przez prowadzącego)
2. Kliknij **Fork** (prawy górny róg)
3. Zostaw domyślne ustawienia → **Create fork**
4. Masz teraz kopię repo na swoim koncie: `github.com/TWOJ-LOGIN/jointhubs-os`

### Clone na komputer
```powershell
# Wejdź do folderu gdzie trzymasz projekty
cd ~/Documents/GitHub

# Clone — użyj swojego forka
git clone https://github.com/TWOJ-LOGIN/jointhubs-os.git

# Wejdź do folderu
cd jointhubs-os
```

> Zamień `TWOJ-LOGIN` na swój login GitHub.

---

## Krok 6: Otwórz w VS Code

```powershell
code .
```

Lub:
1. Otwórz VS Code
2. `File` → `Open Folder` → wybierz folder `jointhubs-os`

VS Code zaproponuje instalację rekomendowanych rozszerzeń — zaakceptuj.

---

## Krok 7: Otwórz jako Vault w Obsidian

1. Otwórz Obsidian
2. Kliknij **"Open folder as vault"**
3. Wybierz folder `jointhubs-os` (ten sam co w VS Code)
4. Obsidian otworzy vault i załaduje pluginy z `.obsidian/`

> **VS Code i Obsidian mogą być otwarte jednocześnie** — oba edytują te same pliki. Obsidian daje lepszą nawigację po Wiki linkach, VS Code daje agentów AI.

---

## Krok 8: Sprawdź, czy działa

### W VS Code:
1. Otwórz Copilot Chat: `Ctrl+Shift+I` (Windows/Linux) / `Cmd+Shift+I` (macOS)
2. W polu chatu kliknij ikonę agenta (lub wpisz `@`) → powinny pojawić się agenty: Tech Lead, Planner, Journal, itd.
3. Napisz coś do wybranego agenta — jeśli odpowiada, setup działa

### W Obsidian:
1. Otwórz `Second Brain/Operations/Periodic Notes/Daily/` → powinieneś widzieć przykładowe notatki dzienne
2. Sprawdź, czy Wiki linki działają — kliknij `[[jakikolwiek link]]` w notatce

---

## Rozwiązywanie problemów

| Problem | Rozwiązanie |
|---------|-------------|
| `git` nie działa w terminalu | Zamknij i otwórz terminal po instalacji Git |
| Copilot nie odpowiada | Sprawdź, czy jesteś zalogowany do GitHub i masz aktywną subskrypcję |
| Agenty nie pojawiają się | Upewnij się, że folder `.github/agents/` istnieje w repo |
| Obsidian nie widzi notatek | Sprawdź, czy otwarto właściwy folder (`jointhubs-os`, nie subfolder) |
| VS Code sugeruje rozszerzenia ale nie instaluje | Zainstaluj ręcznie z panelu Extensions (`Ctrl+Shift+X`) |

---

## Następne kroki

- [[repo-init/setup-mcp-google]] — podłącz Google Workspace do agentów (opcjonalne)
- [[repo-init/setup-agents]] — poznaj jak działają agenty
- [[repo-init/customize-vault]] — dostosuj vault do siebie
- [[ai-development/README]] — jeśli chcesz rozwijać własne customizacje AI
