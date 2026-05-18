---
type: note
status: active
tags: [type/note, project/thoughtmap, topic/copilot, topic/mcp, topic/context-grounding]
created: 2026-04-22
updated: 2026-04-22
---

# ThoughtMap as Copilot Context Layer

Plan wdrożenia, utrzymania i doprowadzenia ThoughtMap do stanu, w którym jest pełnoprawną warstwą kontekstową dla Copilot Agenta.

> [!success] Status
> Faza 1 została wdrożona 2026-04-22.
> Faza 2 została wdrożona 2026-04-22.
> Faza 3 została wdrożona 2026-04-22.
> Decyzja: nie dodajemy nowej instrukcji ani nowego skillu tylko po to, żeby „mieć jeszcze jedną warstwę”. Obecny układ instruction + skill + prompt integration jest wystarczający; następny sensowny krok to dopiero faza 4.

## Checklist wdrożenia

- [x] Faza 1 — ujednolicić politykę między `assistant.instructions.md`, `thoughtmap-out.instructions.md` i `.github/skills/thoughtmap/SKILL.md`
- [x] Faza 2 — wprowadzić jawny `context pack` jako wspólny artefakt promptów i dodać reguły jakości
- [x] Faza 3 — zintegrować `context pack` z promptami `deep-work` i `daily-review`
- [ ] Faza 4 — przenieść standard do agenta `jointhubs-os` lub wspólnego wrappera groundingowego
- [ ] Faza 5 — domknąć kryteria produkcyjne, utrzymanie i testy jakości

## Teza

Największy zysk nie wynika z „większej ilości ThoughtMap”, tylko z lepszego podziału ról:

- `thoughtmap-out` powinien być **tanim routerem** i warstwą szybkiego rozeznania.
- ThoughtMap MCP powinien być **obowiązkową warstwą semantycznego uziemienia** przed pracą nad każdym nietrywialnym zadaniem.
- Źródłowe notatki i pliki projektu powinny pozostać **warstwą weryfikacji i finalnego oparcia decyzji**.

To rozwiązuje obecną niespójność między globalną instrukcją „czytaj najpierw statyczny indeks” a promptami/skillami, które czasem traktują MCP tylko jako fallback.

## Problem dzisiaj

Obecny system działa w dwóch niespójnych trybach:

1. `assistant.instructions.md` promuje model: statyczny indeks najpierw, MCP dopiero gdy indeks jest za słaby.
2. `.github/skills/thoughtmap/SKILL.md` promuje model: zacznij od MCP, bo to najszybsze semantyczne wejście.
3. `.github/prompts/deep-work.prompt.md` używa MCP tylko wtedy, gdy notatki statyczne są cienkie.
4. `.github/prompts/daily-review-prompt.md` używa ThoughtMap-out jako kompasu, ale nie wymusza małego pakietu zapytań MCP do zbudowania zwartego kontekstu roboczego.

Efekt:

- czasem agent działa jak indeksator plików,
- czasem jak retriever semantyczny,
- ale nie ma jednego stabilnego protokołu przejścia od pytania użytkownika do kontekstu roboczego.

## Docelowy model operacyjny

### Warstwy

| Warstwa | Rola | Koszt | Funkcja |
|---|---|---|---|
| `thoughtmap-out` | Router | niski | mówi, gdzie patrzeć |
| ThoughtMap MCP | Grounding | średni | mówi, co jest teraz naprawdę istotne |
| Source files | Verification | wyższy | potwierdza szczegóły i daje materiał do działania |

### Zasada główna

Dla każdego **nietrywialnego zadania** agent przechodzi przez trzy kroki:

1. **Wyłuskanie anchorów**
2. **Tani routing przez `thoughtmap-out`**
3. **Mały pakiet zapytań MCP zakończony `context packiem`**

MCP nie jest fallbackiem. Jest obowiązkową warstwą interpretacyjną po tanim routingu.

## Anchory

Agent powinien wyłuskać z prośby użytkownika od 1 do 4 anchorów z tych klas:

- **Project** — np. Fenix, ThoughtMap, office_ai
- **Person** — np. klient, współpracownik, kandydat
- **Topic** — np. NER, pricing, hiring, embeddings
- **Decision** — np. wybór architektury, priorytet, kierunek działania

To są jednostki, wokół których budowany jest retrieval pack.

## Routing przez thoughtmap-out

Po zidentyfikowaniu anchorów agent czyta najtańszy możliwy kontekst:

1. `REPORT.md` — gdy potrzeba szerokiego przeglądu lub statusu dnia/tygodnia
2. `entities/_entity-index.md` i odpowiedni entity note — gdy anchor jest osobą, projektem, organizacją lub narzędziem
3. `topics/<slug>.md` — gdy anchor jest tematem lub problemem
4. `Second Brain/Projects/<project>/CONTEXT.md` — gdy anchor dotyczy konkretnego projektu

Cel tego kroku nie polega na pełnym zrozumieniu sprawy, tylko na szybkim ustaleniu:

- jaki jest właściwy obszar wiedzy,
- które źródła są najbardziej obiecujące,
- czy statyczny indeks jest świeży i wiarygodny.

## MCP grounding bundle

Po routingu agent musi wykonać **2-3 krótkie zapytania MCP na anchor**.

Minimalny bundle:

1. zapytanie w dokładnym języku użytkownika,
2. `"<anchor> current status"`,
3. `"<anchor> open questions"` albo `"<anchor> next step"`.

Jeżeli zadanie jest bardziej strategiczne lub relacyjne, bundle rozszerza się o:

- `cluster_distances(cluster_id)` — żeby zobaczyć sąsiedztwo tematu,
- `text_distance(text_a, text_b)` — żeby sprawdzić, czy nowy wątek należy do danego kontekstu,
- `get_cluster(cluster_id)` — gdy wynik wymaga reprezentatywnych fragmentów, a nie tylko hitów.

## Context Pack

Agent nie powinien pracować na surowych hitach z `search_thoughts`. Powinien przekształcać wyniki w krótki, jednolity `context pack`.

### Format

`context pack` powinien mieć pięć pól:

1. **Prior decisions** — wcześniejsze decyzje, ustalenia, ramy
2. **Open threads** — co jest nadal otwarte, niedomknięte, blokujące
3. **Reusable assets** — gotowe notatki, pliki, prompty, szkice, analizy
4. **Freshest relevant source** — najświeższe źródło z najwyższym sygnałem
5. **Gaps / conflicts** — czego brakuje albo co jest sprzeczne między źródłami

### Zasada użycia

Od momentu zbudowania `context packa` agent ma kontynuować pracę na nim, a nie na całym strumieniu wyników MCP.

To ogranicza koszt poznawczy, zmniejsza szum i stabilizuje jakość decyzji.

## Rekomendowany protokół

Poniższy blok powinien zostać użyty jako wspólny standard w promptach i instrukcjach:

```text
ThoughtMap grounding protocol:
1. Extract 1-4 anchors from the user request: people, projects, topics, decisions.
2. Read the cheapest static context first: REPORT.md, entity note, topic note, CONTEXT.md.
3. Run 2-3 MCP queries:
   - the user's exact phrasing
   - "<anchor> current status"
   - "<anchor> open questions" or "<anchor> next step"
4. Keep only results with strong relevance (for example distance < 0.40).
5. Read the top 1-2 source files behind the best hits.
6. Produce a compact context pack:
   - Prior decisions
   - Open threads
   - Reusable assets
   - Freshest relevant source
   - Gaps / conflicts
7. Continue the task using that pack, not raw search output.
```

## Rekomendowana implementacja

### Faza 1 — Ujednolicenie polityki

Cel: wyeliminować sprzeczne zasady między instrukcjami i promptami.

Status: Completed 2026-04-22.

Zmiany:

1. W `.github/instructions/assistant.instructions.md` dodać twardą regułę:
   - dla pytań o strategię,
   - relacje między tematami,
   - status projektu,
   - „co już o tym wiemy”,
   - „jak to się łączy”,
   agent wykonuje krótki `retrieval pack` przez MCP po tanim routingu statycznym.
2. W `.github/skills/thoughtmap/SKILL.md` doprecyzować, że MCP jest warstwą groundingową po routingu, a nie uniwersalnym punktem startowym dla wszystkiego.
3. W `.github/instructions/thoughtmap-out.instructions.md` dopisać explicite, że `thoughtmap-out` służy do wyboru ścieżki, a nie do końcowego rozumienia sprawy.

Rezultat: jedna spójna filozofia użycia.

Wdrożone w:

- `.github/instructions/assistant.instructions.md`
- `.github/skills/thoughtmap/SKILL.md`
- `.github/instructions/thoughtmap-out.instructions.md`

### Faza 2 — Wspólny artefakt: context pack

Cel: ustandaryzować kształt kontekstu przekazywanego dalej.

Status: Completed 2026-04-22.

Zmiany:

1. Wprowadzić do promptów jawny artefakt `context pack`.
2. Zdefiniować maksymalną długość każdego pola, żeby nie powodować rozlewania się tokenów.
3. Dodać prostą regułę jakości:
   - każde pole musi odnosić się do konkretnego źródła,
   - co najmniej jedno pole musi wskazywać świeże źródło,
   - jeśli brak silnych hitów, agent zapisuje to w `Gaps / conflicts`, zamiast zgadywać.

Rezultat: agent operuje na stabilnym, małym formacie, a nie na przypadkowej mieszance wyników.

Wdrożone w:

- `.github/prompts/deep-work.prompt.md` — jawny `Context Pack`, obowiązkowy MCP grounding bundle, reguły jakości i praca na packu zamiast raw hits
- `.github/prompts/daily-review-prompt.md` — wczesny warm set, `ThoughtMap Context Pack`, użycie packa jako working memory dla kolejnych kroków review

### Faza 3 — Integracja z promptami

Status: Completed 2026-04-22.

Decyzja wdrożeniowa:

- nie dodajemy nowego promptu ani nowego skillu tylko po to, żeby nazwać integrację osobno,
- obecny zestaw jest już spójny: polityka w instrukcjach, interpretacja w skillu, wykonanie w promptach,
- kolejna warstwa w tym miejscu zwiększyłaby raczej duplikację niż jakość.

#### `deep-work.prompt.md`

Zmiana zalecana:

- po statycznym lookupie zawsze wykonać `MCP query bundle`, nawet jeśli entity/topic notes są mocne,
- wygenerować briefing oparty na `context packu`, a nie na samych notatkach statycznych,
- pozwolić MCP doprecyzować, co jest „najbliższym używalnym kontekstem”.

Nowa logika:

1. Anchory
2. Tani routing
3. MCP bundle
4. Context pack
5. Briefing dla użytkownika
6. Propozycja 2-3 frame'ów pracy

Status wdrożenia:

- completed w `.github/prompts/deep-work.prompt.md`

#### `daily-review-prompt.md`

Zmiana zalecana:

- rozdzielić semantykę na dwa momenty:
  - **warm set** zaraz po Step 1,
  - **historyczna synteza** w późniejszym etapie.

Warm set powinien:

- ustawić aktywne osoby,
- aktywne projekty,
- bieżące wątki,
- świeże źródła o wysokim sygnale.

Późniejsza synteza powinna:

- wykrywać powracające tematy,
- sprawdzać, co wraca mimo braku domknięcia,
- porównywać dzień do starszego rozkładu tematów.

Status wdrożenia:

- completed w `.github/prompts/daily-review-prompt.md`

#### `assistant.instructions.md`

Zmiana zalecana:

- dopisać jedną twardą regułę uruchamiającą retrieval pack dla zadań strategicznych i relacyjnych,
- dopisać, że przy niskim koszcie statyczny routing jest obowiązkowy, ale niewystarczający bez krótkiego MCP bundle.

Status wdrożenia:

- completed w `.github/instructions/assistant.instructions.md` w ramach fazy 1

### Faza 4 — Integracja z agentem

Cel: zmniejszyć zależność od jakości pojedynczych promptów.

Zmiany:

1. Dodać do agenta `jointhubs-os` standard użycia `context packa` jako części startowego briefu.
2. Jeżeli to możliwe, dodać osobny prompt lub skill typu `ground-with-thoughtmap`, który będzie reusable wrapperem dla innych promptów.
3. Z czasem przejść z „prompt discipline” na pół-strukturalne wywołanie procedury groundingowej.

Rezultat: mniej zależności od ręcznie napisanych promptów, większa powtarzalność zachowania.

### Faza 5 — Produkcyjna integracja

Cel: ThoughtMap ma być pełnoprawną warstwą kontekstową Copilota, a nie tylko ciekawym dodatkiem.

Docelowo system powinien mieć:

1. **Stały protokół retrievalu** dla zadań nietrywialnych
2. **Jednolity format context packa**
3. **Reguły jakości i selekcji wyników**
4. **Jawne kryteria staleness** dla `REPORT.md` i `thoughtmap-out`
5. **Mechanizm relacyjny**, nie tylko wyszukiwawczy
6. **Źródłowe potwierdzenie** dla ważnych decyzji

## Utrzymanie

System wymaga regularnego utrzymania na trzech poziomach.

### 1. Retrieval quality

Co sprawdzać:

- czy `distance < 0.40` nadal daje dobre trafienia,
- czy query bundle nie produkuje za dużo szumu,
- czy anchors są dobrze wyciągane z próśb użytkownika,
- czy `context pack` pozostaje krótki i używalny.

Rytm:

- szybki przegląd co 1-2 tygodnie,
- głębszy tuning po większych zmianach w promptach albo pipeline.

### 2. Freshness and drift

Co sprawdzać:

- wiek `REPORT.md`,
- zgodność `thoughtmap-out` z najnowszymi notatkami,
- przypadki, w których MCP i statyczny indeks wskazują różne obrazy sytuacji.

Rytm:

- automatyczne ostrzeżenie przy staleness > 7 dni,
- traktowanie indeksu jako advisory przy staleness > 14 dni.

### 3. Prompt and instruction governance

Co sprawdzać:

- czy wszystkie prompty używają tej samej logiki groundingowej,
- czy nie pojawił się nowy prompt, który obchodzi context pack,
- czy agent nie wraca do modelu „tylko pliki” albo „tylko search hits”.

Rytm:

- przegląd po każdej większej zmianie promptów lub instrukcji.

## Kryteria jakości

Integrację można uznać za zdrową, jeśli:

1. w zadaniach strategicznych agent regularnie buduje `context pack`,
2. użytkownik widzi mniej odpowiedzi oderwanych od wcześniejszych decyzji,
3. agent częściej wskazuje świeże, naprawdę relewantne źródła,
4. maleje liczba odpowiedzi opartych tylko na statycznym indeksie,
5. maleje liczba odpowiedzi opartych tylko na surowych hitach `search_thoughts`.

## Kryteria produkcyjne

ThoughtMap jest produkcyjnie zintegrowany z Copilotem dopiero wtedy, gdy spełnione są wszystkie poniższe warunki:

1. **Policy alignment**
   - instrukcje, prompty i skille nie są ze sobą sprzeczne.
2. **Deterministic grounding behavior**
   - dla tej samej klasy zadań agent wykonuje podobny proces groundingowy.
3. **Compact context handoff**
   - każdy ważniejszy task przechodzi przez `context pack`.
4. **Source-backed answers**
   - ważne odpowiedzi są osadzone w źródłach, nie tylko w retrievalu.
5. **Staleness awareness**
   - agent umie rozpoznać, że indeks jest przeterminowany.
6. **Operational maintenance loop**
   - istnieje prosty rytm przeglądu jakości i korekt.

## Ryzyka

### Ryzyko 1 — za dużo retrievalu

Jeśli bundle będzie zbyt szeroki, koszt tokenowy zabije korzyść. Dlatego query bundle musi pozostać mały.

### Ryzyko 2 — zbyt duże zaufanie do MCP

MCP daje semantyczny skrót, ale nie zastępuje źródeł. Dlatego `Freshest relevant source` i późniejszy odczyt 1-2 plików są obowiązkowe.

### Ryzyko 3 — dryf promptów

Jeżeli każdy prompt zacznie własnoręcznie implementować grounding, po kilku tygodniach system znów się rozjedzie. Dlatego potrzebny jest wspólny protokół i najlepiej wspólny wrapper.

### Ryzyko 4 — martwy context pack

Jeśli `context pack` będzie tylko formalnością, a agent i tak wróci do raw hits, zysk zniknie. Trzeba egzekwować zasadę pracy na packu, nie na surowych wynikach.

## Kolejne ulepszenia

### Krótki horyzont

1. Dodać wspólny blok `ThoughtMap grounding protocol` do promptów i instrukcji.
2. Wprowadzić format `context pack` do `deep-work.prompt.md` i `daily-review-prompt.md`.
3. Ujednolicić język wokół `routing -> MCP grounding -> verification`.

### Średni horyzont

1. Zbudować reusable skill lub agent-side wrapper dla grounding bundle.
2. Dodać prosty scoring jakości retrievalu na podstawie przykładowych zadań.
3. Użyć `cluster_distances` i `text_distance` częściej przy zadaniach strategicznych.

### Długi horyzont

1. Zbudować pół-strukturalny generator `context packa` jako osobny krok lub helper.
2. Dodać caching retrievalu w obrębie jednej sesji.
3. Opracować zestaw testowych pytań kontrolnych dla promptów i agenta.

## Rekomendacja końcowa

Najlepszy model nie brzmi: „więcej ThoughtMap”.

Najlepszy model brzmi:

- `thoughtmap-out` wybiera ścieżkę,
- MCP ustala realny stan kontekstu,
- `context pack` stabilizuje przekaz do agenta,
- źródła domykają prawdę operacyjną.

To jest najkrótsza droga do stanu, w którym ThoughtMap staje się pełnoprawnym systemem kontekstowym Copilota, a nie tylko dodatkową warstwą eksploracji wiedzy.

## Powiązania

- [[CONTEXT|ThoughtMap Context]]
- [[PRD|ThoughtMap PRD]]
- [[extraction-pipeline|Extraction Pipeline Architecture]]