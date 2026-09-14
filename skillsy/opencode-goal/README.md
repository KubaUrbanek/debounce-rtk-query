# OpenCode /goal

Luna implementuje, model bieżącej sesji analizuje i weryfikuje, a następnie
zleca poprawki. Pakiet to komenda i subagent, nie plugin runtime.

## Instalacja
1. Skopiuj zawartość katalogu `.opencode` z paczki do `.opencode` w projekcie.
   Zachowaj istniejące pliki. Jeśli masz już goal.md lub goal-coder.md,
   porównaj je przed zastąpieniem.
   Globalnie: commands/ i agents/ umieść pod ~/.config/opencode/.
2. Uruchom `opencode models` i znajdź dokładny identyfikator Luny w formacie
   provider/model-id. W `.opencode/agents/goal-coder.md` zastąp
   `REPLACE_PROVIDER/REPLACE_LUNA_MODEL_ID` tym identyfikatorem.
   Sama nazwa „Luna GPT” nie potwierdza identyfikatora ani dostępności
   u Twojego dostawcy. Jeśli model nie jest dostępny, wymaga najpierw
   skonfigurowania dostawcy; pakiet nie dokonuje cichej zamiany modelu.
3. Otwórz ponownie OpenCode. Wybierz agenta Build i model do sprawdzania.
   Komenda nie ustawia agent ani model; korzysta z bieżącej sesji.
4. Wpisz:
   /goal Zaimplementuj wymagania z docs/plan.md i sprawdź wynik

Bieżący agent musi mieć dostęp do Task i uprawnienie do goal-coder.
Jeśli ograniczasz task w konfiguracji, dodaj regułę goal-coder: allow
w permission.task właściwego agenta, po pasujących regułach deny.
Pakiet nie zmienia globalnych uprawnień ani ustawień obecnego agenta.

## Co oznacza pętla
Prompt nakazuje kontynuować implementację i przegląd do spełnienia kryteriów,
a realne blokady zgłaszać jako BLOCKED. Nie ustawia limitu rund.
Nie jest to mechanizm wymuszający wznowienie po zakończeniu odpowiedzi,
błędzie API, restarcie, limicie kroków lub przerwaniu sesji. Do takiego
trwałego loopa potrzebny jest dodatkowy plugin lub zewnętrzny runner.
Nie usuwa też istniejącego limitu steps Twojego agenta.

Równoległość tylko dla rozłącznych zakresów plików. Koordynator samodzielnie
sprawdza rezultat, a implementację i poprawki oddaje goal-coder.
Pisanie testów nie jest domyślnym zadaniem; istniejące kontrole są uruchamiane.

## Weryfikacja pakietu
Sprawdzono strukturę ZIP oraz frontmatter plików. OpenCode nie jest dostępny
w środowisku przygotowania, więc nie wykonano próby end-to-end. Konfiguracja
modelu wymaga uzupełnienia przed uruchomieniem.

Dokumentacja użyta do konfiguracji:
- https://opencode.ai/docs/commands/
- https://opencode.ai/docs/agents/
- https://opencode.ai/docs/cli/
