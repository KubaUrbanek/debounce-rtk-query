# OpenCode: Luna implementuje, Sol planuje i robi review

Przenośny setup projektowy dla OpenCode 1.x. Konfiguracja używa granularnego `permission` opisanego w dokumentacji dla 1.1.1 i nowszych; wcześniejsze 1.x mogą wymagać dostosowania. Nie jest to konfiguracja v2.

## Co dostajesz

| Rola | Model | Praca | Dostęp |
| --- | --- | --- | --- |
| build | Luna | Implementacja i testy; wywołuje explore/reviewer | Edycja; shell wymaga akceptacji |
| plan | Sol | Decyzje i plan; wywołuje explore | Odczyt, bez shella |
| explore | Luna | Szukanie kodu i zależności | Odczyt, bez shella i delegacji |
| reviewer | Sol | Review zadania i diffu | Odczyt, bez shella i delegacji |

Gotowe są prompty agentów, konfiguracja, skrypt ustawiający modele i szablon planu. `PROJECT-SETUP-PROMPT.md` tworzy dopiero elementy wymagające znajomości repozytorium: AGENTS.md, skille i projektowe komendy. Nie dostarczamy fikcyjnych zasad projektu ani pustych skilli.

## 1. Skopiuj pliki

Rozpakuj ZIP. Skopiuj zawartość katalogu `opencode-ai-setup` do głównego katalogu projektu, włącznie z ukrytym folderem `.opencode`. README ma osobną nazwę, aby nie zastępować README projektu. Jeśli masz już pliki pod tymi samymi ścieżkami, porównaj i scal je zamiast nadpisywać.

Definicje agentów są w `.opencode/config.template.json`, a ich instrukcje w `.opencode/prompts/`. Nie ma dodatkowych definicji Markdown w `.opencode/agents`, aby nie definiować tych samych ról dwukrotnie. Sam plik szablonu nie jest aktywną konfiguracją.

## 2. Ustaw rzeczywiste identyfikatory modeli

W terminalu, w katalogu projektu:

```bash
opencode --version
opencode models
```

Znajdź dokładne `provider/model-id` dla Twojej Luny i Sola. Nie zakładaj, że nazwy wyświetlane „ai-luna6” i „OpenAI Sol 6” są tymi identyfikatorami. Podstaw je do komendy:

```bash
python3 .opencode/configure.py --weak 'PROVIDER/LUNA_ID' --strong 'PROVIDER/SOL_ID'
```

Skrypt wymaga tylko Pythona 3. Tworzy `opencode.json` z jawnym przypisaniem modelu każdej roli. Nie kontaktuje się z providerem ani nie potwierdza dostępności modeli.

Jeśli wykryje istniejący opencode.json/jsonc, konfigurację w .opencode lub katalog agentów, zapisze `opencode.ai-setup.candidate.json`. Kandydat nie jest automatycznie ładowany: jego scalenie wykonuje prompt z następnego kroku. Skrypt nigdy nie nadpisuje istniejącego pliku docelowego. Globalnych ustawień nie analizuje — prompt każe sprawdzić ich wpływ.

## 3. Jednorazowo dostosuj do projektu

Uruchom OpenCode. Wybierz agenta z prawem edycji (`build`) i tymczasowo ustaw mu mocniejszy model Sol przez selektor modeli. Przy istniejących restrykcjach użyj dotychczasowego, uprawnionego trybu edycji. Nie uruchamiaj tego kroku w naszym read-only `plan`.

Wklej pełną treść `PROJECT-SETUP-PROMPT.md`. Agent zbada projekt, utworzy AGENTS.md i projektowe skille, scali konfigurację, sprawdzi zgodność z lokalną wersją i uzupełni ten README. Nie ma potrzeby ponownego generowania ogólnych promptów agentów.

Po zakończeniu uruchom nową sesję i sprawdź wybrane modele: build = Luna, plan = Sol. Ręczny wybór modelu w sesji może zmienić bieżący model — nie zakładaj, że samo przełączenie roli zawsze usuwa ręczny override. Jeśli lokalna wersja nie przyjmuje konfiguracji, przywróć poprzednią i zleć dopasowanie do jej schematu; nie aktualizuj narzędzia automatycznie.

## 4. Codzienna praca

### Mała poprawka

W `build` napisz: „Napraw [problem]. Sprawdź odpowiednie testy i wykonaj review, jeśli zmieniasz zachowanie”. Agent sam wykonuje lokalne, jednoznaczne zadania.

### Większa funkcjonalność

Przełącz głównego agenta na `plan` (standardowo Tab). Napisz: „Zaplanuj [funkcjonalność]. Ustal kryteria akceptacji i przygotuj etapy dla build”. Przejrzyj plan, następnie w tej samej rozmowie przełącz na `build`: „Zrealizuj powyższy plan etapami, zweryfikuj i zleć reviewerowi review”. Przy nowej rozmowie przekaż pełny plan lub ścieżkę do zapisanego przez build planu.

### Skąd build wie, że ma użyć reviewer?

Ma jawną instrukcję w `.opencode/prompts/build.md`, a konfiguracja zezwala mu na `task` do `reviewer`. Opis reviewera wyjaśnia jego zastosowanie. Build przygotowuje zakres, kryteria, wyniki sprawdzeń oraz tekstowy diff (także staged i nowe pliki), ponieważ reviewer nie ma shella. Reviewer może czytać aktualny kod. Build poprawia potwierdzone problemy i powtarza potrzebne sprawdzenia.

To instrukcja dla modelu, nie deterministyczny hook ani bramka CI. Jeśli model pominie review, napisz: „Wywołaj teraz reviewer zgodnie z instrukcją build”. Możesz też użyć `@reviewer` z zadaniem, kryteriami i ścieżką do diffu. Wymuszenie review przed merge wymaga osobnego mechanizmu CI, którego ta paczka nie instaluje.

### Gdy Luna utknie

Po dwóch nieskutecznych próbach build ma przedstawić dowody i pytanie. Przełącz na `plan`, uzyskaj korektę rozwiązania, potem wróć do `build`. Nie ma automatycznego wywołania planisty jako subagenta.

## Uprawnienia i ograniczenia

Plan, explore i reviewer mają deny jako domyślną politykę oraz jawne zezwolenia na czytanie/wyszukiwanie i skille. Edycje, shell, zewnętrzne katalogi i nieprzewidziane narzędzia są zablokowane. Plan może delegować tylko do explore; reviewer i explore nie delegują. To role do analizy, nie do uruchamiania testów.

Build może edytować pliki. Shell ma `ask`, więc pierwsze komendy mogą wymagać akceptacji; projektowy prompt może udokumentować wymagane komendy, ale nie ma automatycznie znosić istniejących ograniczeń. Testy uruchamia build. Brak sekretów w konfiguracji — wykorzystujesz własne uwierzytelnienie providera. Uprawnienia narzędzi nie zastępują izolacji systemowej; sprawdź ich efektywną postać po scaleniu z istniejącym setupem.

## Zawartość i weryfikacja paczki

- `.opencode/config.template.json`: role, modele do podstawienia, uprawnienia.
- `.opencode/configure.py`: bezpieczne wygenerowanie konfiguracji lub kandydata.
- `.opencode/prompts/`: cztery gotowe instrukcje.
- `.opencode/templates/implementation-plan.md`: format przekazania planu.
- `PROJECT-SETUP-PROMPT.md`: jednorazowe dostosowanie do projektu.
- `README-AI-SETUP.md`: ten przewodnik.

Sprawdzono statycznie JSON, odwołania do promptów, przypisania modeli, podstawowe ograniczenia ról i działanie skryptu (w tym brak nadpisania oraz ścieżkę kandydata). W środowisku przygotowania paczki nie było OpenCode ani dostępu do Twoich providerów. Nie wykonano testu działania agentów; końcowa walidacja lokalnej wersji i modeli odbywa się w kroku 3.

Dokumentacja referencyjna (sprawdzona 2026-10-05):
- https://opencode.ai/docs/agents/
- https://opencode.ai/docs/permissions/
- https://opencode.ai/docs/skills/
- https://opencode.ai/docs/cli/
