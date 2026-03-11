---
type: note
status: active
tags: [type/docs, area/setup, area/mcp]
created: 2026-03-11
updated: 2026-03-11
---

# Setup: MCP + Google Workspace

Jak podłączyć Google Workspace (Gmail, Calendar, Drive, Tasks) do agentów VS Code Copilot przez MCP.

---

## Jak to działa

```
VS Code Copilot  ──stdio──►  workspace-mcp  ──OAuth──►  Google APIs
    (agent)                   (lokalny serwer)            (Gmail, Calendar, Drive...)
```

1. **VS Code** czyta `.vscode/mcp.json` i uruchamia serwer MCP jako proces lokalny
2. **workspace-mcp** (pakiet Python, uruchamiany przez `uvx`) startuje i czeka na komendy
3. Agent Copilot wysyła zapytania do serwera MCP (np. "pokaż dzisiejsze wydarzenia")
4. Serwer MCP robi OAuth do Google API z Twoimi credentials i zwraca dane agentowi

**Wszystko działa lokalnie** — żaden serwer zewnętrzny nie przetwarza Twoich danych. OAuth pozwala MCP działać w Twoim imieniu na Twoim koncie Google.

---

## Co potrzebujesz

- Konto Google (Gmail)
- Dostęp do Google Cloud Console
- Zainstalowany `uv` (menedżer pakietów Python) — https://docs.astral.sh/uv/

### Instalacja `uv` (jeśli nie masz)

```powershell
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Po instalacji sprawdź:
```powershell
uv --version
uvx --version
```

---

## Krok 1: Utwórz projekt w Google Cloud Console

1. Wejdź na https://console.cloud.google.com/
2. Zaloguj się kontem Google, którego chcesz używać
3. Na górze strony kliknij **selektor projektu** (obok logo Google Cloud)
4. Kliknij **"New Project"**
5. Wpisz nazwę, np. `jointhubs-mcp`
6. Kliknij **"Create"**
7. Poczekaj aż projekt się utworzy i upewnij się, że jest wybrany na górze

---

## Krok 2: Włącz potrzebne API

1. W menu bocznym: **APIs & Services** → **Library**
2. Wyszukaj i włącz (**Enable**) każde z tych API:
   - **Gmail API**
   - **Google Calendar API**
   - **Google Drive API**
   - **Google Tasks API**
   - **Google Docs API**
   - **Google Sheets API**
   - **Google Slides API**
   - **Google People API** (kontakty)

> Włączaj te, które Ci potrzebne. Minimum to Gmail + Calendar + Tasks.

Dla każdego API:
1. Kliknij na nazwę API w wynikach wyszukiwania
2. Kliknij **"Enable"**
3. Wróć do Library i powtórz dla kolejnego

---

## Krok 3: Skonfiguruj OAuth Consent Screen

1. **APIs & Services** → **OAuth consent screen**
2. Kliknij **"Configure Consent Screen"** (lub "Edit App Registration")
3. Wybierz **"External"** (chyba że masz Google Workspace org — wtedy "Internal")
4. Kliknij **"Create"**

### Wypełnij formularz:
| Pole | Wartość |
|------|---------|
| App name | `Jointhubs MCP` (dowolna nazwa) |
| User support email | Twój email |
| Developer contact email | Twój email |

5. Kliknij **"Save and Continue"**

### Scopes (opcjonalnie):
1. Kliknij **"Add or Remove Scopes"**
2. Dodaj scopes potrzebne przez API (lub pomiń — MCP sam poprosi o uprawnienia)
3. **"Save and Continue"**

### Test Users:
1. Kliknij **"Add Users"**
2. Dodaj **swój adres email** (ten, do którego chcesz dać dostęp)
3. **"Save and Continue"**

> **Ważne**: Dopóki app jest w trybie "Testing", tylko dodani test users mogą się logować. To dobra opcja dla osobistego użytku.

4. Kliknij **"Back to Dashboard"**

---

## Krok 4: Utwórz OAuth Client ID

1. **APIs & Services** → **Credentials**
2. Kliknij **"+ Create Credentials"** → **"OAuth client ID"**
3. **Application type**: wybierz **"Desktop app"** (lub "Web application" jeśli dokumentacja `workspace-mcp` wskazuje inaczej)
4. **Name**: `jointhubs-local` (dowolna nazwa, dla Twojej orientacji)
5. Kliknij **"Create"**

### Skopiuj credentials:
Po utworzeniu zobaczysz popup z:
- **Client ID** — długi string kończący się na `.apps.googleusercontent.com`
- **Client Secret** — string zaczynający się od `GOCSPX-`

> **Skopiuj oba teraz!** Możesz też kliknąć "Download JSON" dla bezpieczeństwa.

---

## Krok 5: Skonfiguruj `.vscode/mcp.json`

1. W folderze projektu skopiuj template:

```powershell
cp .vscode/mcp.json.example .vscode/mcp.json
```

2. Otwórz `.vscode/mcp.json` w edytorze i wklej swoje credentials:

```json
{
  "servers": {
    "googleWorkspace": {
      "type": "stdio",
      "command": "uvx",
      "args": ["workspace-mcp", "--tool-tier", "core"],
      "env": {
        "GOOGLE_OAUTH_CLIENT_ID": "WKLEJ-SWOJ-CLIENT-ID.apps.googleusercontent.com",
        "GOOGLE_OAUTH_CLIENT_SECRET": "GOCSPX-WKLEJ-SWOJ-SECRET",
        "OAUTHLIB_INSECURE_TRANSPORT": "1"
      }
    }
  }
}
```

3. Zamień:
   - `WKLEJ-SWOJ-CLIENT-ID...` → Twój Client ID z kroku 4
   - `GOCSPX-WKLEJ-SWOJ-SECRET` → Twój Client Secret z kroku 4

> **`OAUTHLIB_INSECURE_TRANSPORT=1`** — pozwala OAuth działać przez HTTP na localhost (normalnie wymaga HTTPS). Bezpieczne dla lokalnego użytku.

---

## Krok 6: Pierwsze uruchomienie i autoryzacja

1. Otwórz VS Code z projektem `jointhubs-os`
2. Otwórz Copilot Chat → wybierz dowolnego agenta
3. Poproś o coś z Google, np.:
   ```
   Pokaż moje dzisiejsze wydarzenia z kalendarza
   ```
4. **Przy pierwszym użyciu** — przeglądarka otworzy stronę logowania Google:
   - Zaloguj się kontem, które dodałeś jako test user
   - Zobaczysz ostrzeżenie "This app isn't verified" → kliknij **"Advanced"** → **"Go to Jointhubs MCP (unsafe)"**
   - Zaakceptuj uprawnienia
5. Token zostanie zapisany lokalnie — kolejne użycia nie będą wymagały logowania

---

## Krok 7: Sprawdź, czy MCP działa

Wpisz w Copilot Chat:
```
Ile mam nieprzeczytanych maili?
```
lub
```
Co mam dzisiaj w kalendarzu?
```

Jeśli agent odpowiada z danymi z Twojego konta — **MCP działa poprawnie**.

---

## Bezpieczeństwo

| Co | Status |
|----|--------|
| `.vscode/mcp.json` | **Ignorowany przez git** — nigdy nie trafi do repo |
| `.vscode/mcp.json.example` | Bezpieczny template w repo (bez sekretów) |
| Token OAuth | Przechowywany lokalnie przez `workspace-mcp` |
| Dane z Google | Przetwarzane tylko lokalnie przez agenta |

### Gdyby credentials wyciekły:
1. Wejdź na https://console.cloud.google.com/ → **APIs & Services** → **Credentials**
2. Kliknij na swój OAuth Client
3. Kliknij **"Reset Secret"**
4. Skopiuj nowy secret do `.vscode/mcp.json`

---

## Parametr `--tool-tier`

`workspace-mcp` ma kilka poziomów narzędzi:

| Tier | Narzędzia | Kiedy używać |
|------|-----------|-------------|
| `core` | Gmail, Calendar, Tasks, Drive (podstawowe) | Codzienne użycie |
| `full` | Wszystkie API + zaawansowane operacje | Gdy potrzebujesz więcej |

Zmiana w `.vscode/mcp.json`:
```json
"args": ["workspace-mcp", "--tool-tier", "full"]
```

---

## Rozwiązywanie problemów

| Problem | Rozwiązanie |
|---------|-------------|
| `uvx: command not found` | Zainstaluj `uv`: https://docs.astral.sh/uv/ |
| "This app isn't verified" | Normalne — kliknij Advanced → Go to app. To Twoja własna app |
| "Access blocked: app not verified" | Dodaj siebie jako test user w OAuth consent screen |
| MCP nie startuje | Sprawdź czy `uvx workspace-mcp --help` działa w terminalu |
| Token wygasł | Usuń zapisany token i zautoryzuj ponownie |
| Agent nie widzi MCP | Zrestartuj VS Code po zmianie `mcp.json` |

---

## Następne kroki

- [[repo-init/setup-agents]] — jak używać agentów z MCP
- [[repo-init/customize-vault]] — personalizacja vault
- [[ai-development/build-custom-mcp]] — jak budować własne serwery MCP
