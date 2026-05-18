---
title: "Sentrux — jak uruchamiać na repo"
type: doc
status: active
tags: [tools/sentrux, tools/static-analysis, tools/mcp]
created: 2026-05-04
updated: 2026-05-04
---

# Sentrux — analiza architektury kodu

Sentrux to statyczny analizator jakości architektury kodu. Działa jako GUI, CLI i serwer MCP dla agentów AI.

- Wersja: 0.5.7
- Binarka: `sentrux` w `PATH` użytkownika
- Źródło: https://github.com/sentrux/sentrux

---

## Szybki start

### 1. Scan GUI — wizualizacja repo

Otwiera interaktywny widok struktury katalogów i zależności:

```powershell
sentrux scan C:\path\to\repo
# lub z bieżącego katalogu:
sentrux scan .
```

### 2. Check — weryfikacja reguł architektonicznych

Sprawdza repo względem reguł zdefiniowanych w `.sentrux/rules.toml`:

```powershell
cd C:\path\to\repo
sentrux check
# lub podając ścieżkę:
sentrux check C:\path\to\repo
```

> Reguły musisz najpierw zdefiniować — patrz sekcja [[#Konfiguracja rules.toml]].

### 3. Gate — regresja strukturalna (CI/CD)

Porównuje bieżące metryki z zapisanym baselineiem:

```powershell
# Pierwsze uruchomienie — zapisz baseline:
sentrux gate --save

# Potem przy każdym PR/commicie:
sentrux gate
```

Zwraca exit code 1 jeśli metryki się pogorszyły → łatwe do użycia w pipeline CI.

### 4. MCP — integracja z agentami AI

Uruchamia lokalny serwer MCP, który Copilot / Claude może odpytywać:

```powershell
sentrux mcp
# Domyślnie słucha na stdin/stdout (stdio transport)
```

Konfiguracja w VS Code (`settings.json`) lub `mcp.json`:

```json
{
  "mcpServers": {
    "sentrux": {
      "command": "sentrux",
      "args": ["mcp"]
    }
  }
}
```

---

## Konfiguracja rules.toml

Utwórz plik `.sentrux/rules.toml` w katalogu głównym repo:

```toml
# Przykład — zakaz importów między warstwami
[[rules]]
name = "no-infra-to-domain"
deny = { from = "infra/**", to = "domain/**" }

[[rules]]
name = "max-coupling"
max_incoming = 10
```

Dokumentacja reguł: https://sentrux.dev/docs/rules

---

## PATH — żeby działało w każdej sesji

Po instalacji dodaj do stałego PATH użytkownika (jednorazowo):

```powershell
[Environment]::SetEnvironmentVariable(
  "PATH",
  [Environment]::GetEnvironmentVariable("PATH", "User") + ";$env:USERPROFILE\bin",
  "User"
)
```

Potem zresetuj terminal — `sentrux --version` powinno działać.

---

## Telemetria

Sentrux wysyła anonimowe dane (tier, nowy użytkownik, liczba skanów). Aby wyłączyć:

```powershell
sentrux analytics disable
```

Plik: `~/.sentrux/telemetry_pending.json`

---

## Notatki z instalacji (2026-05-04)

- Wymaga toolchain Rust **GNU** (nie MSVC) na Windows, bo MSVC `link.exe` nie był dostępny
- Zależność: `mingw-w64-x86_64-gcc` z MSYS2
- Build z źródeł: `cargo build --release` w sklonowanym repo (~1m 20s)
- Binarka: 30 MB, gramatyki języków (~30 MB, pobrane jednorazowo przy pierwszym uruchomieniu)
- Pro dylib: opcjonalny komponent proprietary, jeśli używasz wersji Pro

---

## Zobacz też

- [[build-custom-mcp]] — jak skonfigurować własny serwer MCP
- [[2026-05-02_agent-monitoring-nowych-spolek_plan]] — plan monitoringu agentów
