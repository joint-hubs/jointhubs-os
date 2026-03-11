---
type: note
status: active
tags: [type/docs, area/ai-development, area/mcp]
created: 2026-03-11
updated: 2026-03-11
---

# Build Custom MCP

Jak budować własne MCP tak, żeby agent miał dobre narzędzia zamiast złych abstrakcji.

## Kiedy budować MCP

Buduj MCP, gdy model musi:

- wykonać akcję poza workspace
- czytać dane z zewnętrznego systemu
- udostępnić zestaw operacji jako narzędzia
- dostarczać resources albo prompts związane z usługą

Nie buduj MCP, jeśli wystarczy lokalny skill, prompt albo zwykła dokumentacja.

## Co MCP może dać agentowi

W VS Code serwer MCP może dostarczyć:

- **tools**
- **resources**
- **prompts**
- **apps**

To ważne: MCP to nie tylko funkcje do wywołania. To pełna warstwa integracyjna.

## Architektura minimalna

```text
Agent in VS Code
  -> mcp.json
  -> MCP server
  -> external system/API/database/service
```

W workspace konfigurujesz serwer w `.vscode/mcp.json` albo globalnie w user profile. VS Code potrafi zarządzać zaufaniem, logami i restartem serwera.

## Najważniejsza zasada projektowa

Z dokumentacji Anthropic wynika bardzo mocno jedna rzecz: **projekt narzędzi jest równie ważny jak prompt**.

Źle zaprojektowane narzędzie powoduje:

- błędne argumenty
- mylenie podobnych operacji
- słabe planowanie przez model
- wyższy koszt i więcej iteracji

## Jak projektować dobre narzędzia MCP

### 1. Dawaj jasne nazwy

Nazwa i opis powinny mówić junior developerowi dokładnie, po co jest dane narzędzie.

Źle:

- `update`
- `modifyThing`

Dobrze:

- `create_calendar_event`
- `list_drive_files`
- `send_gmail_message`

### 2. Ogranicz niejednoznaczność argumentów

Anthropic poleca projektować ACI tak, by trudno było popełnić błąd.

Przykład praktyczny:

- wymagaj pełnych ścieżek, jeśli relative paths prowadzą do pomyłek
- rozbij skomplikowane argumenty na prostsze pola
- dawaj enumy tam, gdzie liczba opcji jest skończona

### 3. Opisz granice narzędzia

W opisie narzędzia zaznacz:

- kiedy go użyć
- kiedy go nie użyć
- jakie są edge cases
- jaki jest expected input format

### 4. Preferuj prosty interfejs nad "generyczny"

Nie próbuj budować jednego mega-tool do wszystkiego. Kilka dobrze nazwanych narzędzi zwykle działa lepiej niż jedno uniwersalne.

### 5. Projektuj pod obserwowalność

Dobre MCP musi być łatwe do debugowania:

- czytelne logi
- jednoznaczne błędy
- możliwie małe side effecty
- sensowne komunikaty dla auth failures, rate limits i timeouts

## Konfiguracja w VS Code

VS Code wspiera dwa miejsca konfiguracji:

- workspace: `.vscode/mcp.json`
- user profile: user-level `mcp.json`

Uwaga praktyczna:

- konfiguracje workspace łatwo współdzielić
- sekrety nie powinny być hardcodowane
- oficjalna dokumentacja VS Code rekomenduje input variables lub env files zamiast twardego wpisywania sekretów

## Trust i bezpieczeństwo

VS Code traktuje lokalne MCP jako kod wykonywany na Twojej maszynie. To słuszne.

Zasady:

- uruchamiaj tylko zaufane serwery
- audytuj komendę `command`, `args` i env
- nie współdziel sekretów w repo
- nie dawaj agentowi niepotrzebnych narzędzi

Na Windows sandboxing dla lokalnych stdio MCP nie jest obecnie dostępny, więc ostrożność jest jeszcze ważniejsza.

## Krok po kroku: pierwszy własny MCP

1. Wybierz konkretny system do integracji.
2. Spisz 3-7 najważniejszych operacji, które agent ma wykonywać.
3. Zdefiniuj każde narzędzie osobno i jasno.
4. Dodaj sensowne walidacje argumentów.
5. Zadbaj o auth i bezpieczne przechowywanie sekretów.
6. Podłącz serwer przez `.vscode/mcp.json`.
7. Przetestuj go na realnych promptach użytkownika.
8. Iteruj głównie na opisach i ergonomii narzędzi, nie tylko na kodzie serwera.

## Kiedy zrobić resource albo prompt zamiast toola

- **Resource**: gdy chcesz dać agentowi dane read-only jako kontekst
- **Prompt**: gdy chcesz wystawić gotowy workflow powiązany z serwerem
- **Tool**: gdy agent ma wykonać akcję lub pobrać dane dynamicznie

## Debugowanie MCP w VS Code

- użyj `MCP: List Servers`
- sprawdź `Show Output` dla serwera
- zweryfikuj trust prompt
- sprawdź `mcp.json` i zgodność ze schemą
- upewnij się, że serwer startuje poza VS Code

## Wzorzec dla Jointhubs OS

W Jointhubs OS własny MCP ma sens tam, gdzie agent ma pracować na:

- wewnętrznych danych biznesowych
- CRM lub pipeline sprzedaży
- notatkach lub zasobach nieobsługiwanych dobrze przez gotowe integracje
- wewnętrznych automatyzacjach operacyjnych

Najpierw jednak sprawdź, czy nie wystarczy gotowy serwer MCP albo skill z lokalnym skryptem.

## Źródła

- [VS Code: MCP servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

W praktyce najlepiej czytać to w tej kolejności:

1. VS Code dla konfiguracji `mcp.json`, trust model i operacji w edytorze.
2. MCP spec dla modelu pojęciowego: tools, resources, prompts, apps.
3. Anthropic dla jakości projektowania narzędzi i ACI.

## Co dalej

- **[[ai-development/references]]**
