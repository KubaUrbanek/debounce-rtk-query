---
name: grill-me-to-plan
description: Rozszerz rozmowę w stylu grill-me o dwa końcowe pliki Markdown — plan implementacji z ustaleniami oraz osobne scenariusze biznesowe do przetestowania. Używaj, gdy użytkownik chce przepracować pomysł lub projekt przez dociekliwe pytania i otrzymać specyfikację oraz wykonalny plan dla siebie lub kolejnego agenta, albo zapisać plan po trwającej sesji grill-me. Nie uruchamiaj dla samej implementacji ani ogólnych pytań bez intencji planowania.
---

# Grill Me → Plan

Doprowadź do wspólnego zrozumienia zmiany, a następnie zapisz dwa powiązane dokumenty: plan implementacji oraz scenariusze biznesowe do przetestowania. Dokumenty mają pozwolić kolejnemu agentowi pracować bez znajomości rozmowy. Pisz w języku użytkownika, chyba że projekt wymaga innego języka dokumentacji.

## Połączenie z grill-me

- Sprawdź dostępne skille i ich lokalne instrukcje. Jeśli `grill-me` jest dostępny, przeczytaj go i zastosuj jego sposób prowadzenia wywiadu. Jeśli odsyła do `grilling`, przeczytaj również tę zależność; samo wymienienie nazwy nie oznacza jej załadowania.
- Ten skill dodaje zakończenie w postaci dwóch dokumentów. Regułę oryginału o braku zapisu plików zastąp zapisem planu i scenariuszy wymaganym przez użytkownika. Pozostałe instrukcje stosuj w granicach bieżącego zadania i uprawnień.
- Nie edytuj ani nie nadpisuj oryginalnego skilla. Nie zakładaj, że środowisko automatycznie uruchomi ten dodatek po każdym wywołaniu samego `grill-me`.
- Jeśli oryginału lub zależności nie ma, krótko poinformuj, że zastosujesz samodzielny wywiad opisany poniżej. Nie instaluj zależności automatycznie i nie twierdź, że oryginał został uruchomiony.
- Jeżeli rozmowa już zawiera wywiad, przejmij jego ustalenia. Nie zaczynaj pytań od nowa.

## Przygotowanie

Przeczytaj instrukcje projektu, istniejącą dokumentację oraz kod związany ze zmianą, jeśli są dostępne. Ustal cel, obecne zachowanie i ograniczenia. O informacje możliwe do odczytania z projektu nie pytaj użytkownika. W razie sprzeczności dokumentacji z kodem pokaż rozbieżność; nie rozstrzygaj samodzielnie, jakie zachowanie biznesowe jest zamierzone.

Bez dostępu do projektu nadal opracuj plan, ale oznacz niezweryfikowane założenia techniczne. Nie wymyślaj istniejących klas, ścieżek, API ani konfiguracji. Rozróżniaj elementy znalezione w projekcie od proponowanych nowych elementów.

## Wywiad

Jeśli nie jest dostępny oryginalny wywiad, prowadź go w ten sposób:

- Zadawaj konkretne pytania podważające niejasne założenia. Najpierw ustal cel i zakres, potem zachowanie oraz kompromisy, na końcu szczegóły implementacyjne.
- Zadawaj jedno pytanie lub niewielką grupę pytań niezależnych od siebie. Poczekaj na odpowiedź przed rozstrzyganiem kwestii, które od niej zależą.
- Przy wyborze przedstaw rekomendację, jej uzasadnienie i istotny kompromis. Rekomendacji nie zapisuj jako decyzji użytkownika.
- Sprawdzaj odpowiednio do zmiany: użytkowników i role, główny scenariusz, wyjątki, walidacje, statusy i przejścia, uprawnienia, dane, integracje oraz skutki błędów. Pytaj o ponowienia, duplikaty, współbieżność, migrację i zgodność tylko wtedy, gdy mają znaczenie.
- Nie pytaj ponownie o podjęte decyzje, chyba że pojawiła się sprzeczność. Nie rozszerzaj zakresu o opcjonalne usprawnienia.

Przez całą rozmowę rozróżniaj: ustalone wymagania, fakty potwierdzone w projekcie, rekomendacje, założenia robocze i otwarte pytania. Gdy użytkownik zmieni decyzję, zastąp nieaktualne ustalenie również w zależnych częściach planu.

## Kiedy zakończyć

Zakończ wywiad, gdy cel, zakres, oczekiwane zachowanie i istotne decyzje pozwalają ułożyć wykonalny plan albo gdy użytkownik prosi o podsumowanie, zapis lub zakończenie. Nie ustalaj sztywnego limitu pytań i nie wymagaj osobnej zgody na zapis dokumentu, o który już poproszono.

Jeśli użytkownik kończy wcześniej, zapisz wersję roboczą z otwartymi pytaniami. Każdemu blokerowi przypisz kroki, których nie można bez niego wykonać. Nie oznaczaj takiego planu jako gotowego. Jeśli użytkownik jednoznacznie anuluje całe zadanie lub zakazuje zapisu, zastosuj jego polecenie.

## Dwa końcowe pliki Markdown

Zawsze utwórz dwa osobne pliki, także przy małej zmianie lub wcześniejszym zakończeniu wywiadu:

1. `<krotka-nazwa-zmiany>-plan.md` — ustalenia, reguły biznesowe, kryteria akceptacji i plan implementacji.
2. `<krotka-nazwa-zmiany>-tests.md` — scenariusze biznesowe Given/When/Then, dane testowe, oczekiwane wyniki i tabela pokrycia. To specyfikacja testów, a nie kod testów.

Użyj wskazanej lokalizacji lub istniejącej konwencji projektu. W repozytorium bez konwencji zapisz oba pliki w `docs/plans/`. Bez projektu utwórz oba pliki do pobrania za pomocą dostępnego mechanizmu plików. Dodaj wzajemne odnośniki względne i wspólną nazwę zmiany. Przy kontynuacji aktualizuj tę samą parę plików, zachowując niezwiązane treści. Jeśli istnieje wcześniejszy pojedynczy plan, zachowaj jego ścieżkę, przenieś szczegółowe scenariusze do osobnego pliku `-tests.md` i zastąp je w planie odnośnikiem.

Nie powielaj pełnej treści reguł, kryteriów i scenariuszy między plikami: plan jest źródłem ustaleń, a plik testów odwołuje się do ich identyfikatorów. Zmianę decyzji uwzględnij w obu dokumentach. Jeśli brakuje ustaleń, zapisz oba jako robocze i wskaż odpowiednie blokery. Nie poprzestawaj na blokach Markdown w odpowiedzi, jeśli możesz zapisać pliki. Przy nieudanym zapisie podaj, którego pliku brakuje, oraz jego kompletną treść; nie twierdź, że oba pliki istnieją.

## Zawartość planu implementacji

Dobierz długość do zmiany. Zawrzyj poniższe informacje, łącząc sekcje przy małym zakresie i pomijając elementy rzeczywiście nieistotne:

1. **Tytuł i status** — data, „Roboczy — wymaga rozstrzygnięć” albo „Gotowy do implementacji”. Gotowość oznacza kompletność planu, nie zgodę na rozpoczęcie pracy ani ukończenie funkcjonalności.
2. **Cel i kontekst** — problem, oczekiwany rezultat, obecne zachowanie i pojęcia domenowe potrzebne do zrozumienia zmiany.
3. **Zakres i wyłączenia** — co ma powstać, co świadomie pozostaje poza zadaniem.
4. **Docelowe zachowanie** — scenariusze użytkownika, reguły biznesowe, walidacje, role, przejścia stanów i obsługa błędów odpowiednie do zmiany. Opisz obserwowalne skutki, nie tylko nazwy metod.
5. **Decyzje i uzasadnienia** — wybrane rozwiązania oraz powody istotnych kompromisów. Odrzucone alternatywy uwzględnij tylko tam, gdzie zapobiegną ponownemu otwieraniu tego samego sporu.
6. **Podejście techniczne** — odpowiedzialności komponentów, przepływ danych, kontrakty i zmiany danych potrzebne do realizacji zachowania. Podaj zweryfikowane ścieżki jako odnośniki; nowe miejsca wyraźnie oznacz jako proponowane.
7. **Plan implementacji** — kroki w kolejności zależności, z identyfikatorami `P1`, `P2` itd. Dla każdego podaj cel, konkretną zmianę, obszar lub pliki, zależności i warunek ukończenia. Dziel według spójnych rezultatów. Unikaj pustych zadań typu „zaimplementuj backend”.
8. **Kryteria akceptacji** — nadaj kryteriom identyfikatory `AC1`, `AC2` itd., opisz sprawdzalne warunki i powiąż je z krokami planu. Dodaj odnośnik do osobnego pliku ze scenariuszami; szczegółowe Given/When/Then zapisz wyłącznie tam. Samo planowanie nie obejmuje pisania ani uruchamiania testów.
9. **Ryzyka, założenia i otwarte pytania** — wpływ na realizację, proponowany sposób rozstrzygnięcia oraz blokowane kroki. Dla migracji i wdrożenia opisz kolejność i odzyskanie poprawnego stanu, jeśli zmiana tego wymaga.
10. **Wskazówki dla następnego agenta** — od czego zacząć, które dokumenty i pliki przeczytać, jakie ograniczenia zachować. Wskaż miejsca dokumentacji biznesowej do aktualizacji po implementacji; plan nie jest dowodem, że zachowanie już istnieje.

Nie umieszczaj transkrypcji rozmowy, sekretów ani wymyślonych wyników weryfikacji. Nie twórz rozbudowanej dokumentacji całego projektu dla małej zmiany. Plan ma samodzielnie wyjaśniać zadanie, lecz odsyłać do istniejących źródeł zamiast je kopiować.

## Scenariusze biznesowe do przetestowania

Zapisz scenariusze w osobnym pliku `<krotka-nazwa-zmiany>-tests.md`, tak aby tester, programista lub kolejny agent mógł wykonać je ręcznie albo przełożyć na testy automatyczne bez znajomości rozmowy. Na początku pliku podaj nazwę zmiany, datę, status, odnośnik do planu i krótki kontekst potrzebny do wykonania scenariuszy. Generuj je na podstawie ustalonych reguł i kryteriów akceptacji; nie poprzestawaj na liście kategorii testów.

- Każdemu scenariuszowi nadaj stabilny identyfikator `SC1`, `SC2` itd., tytuł opisujący zachowanie domenowe oraz priorytet wynikający ze skutków biznesowych. Zachowuj identyfikatory podczas aktualizacji planu.
- Wskaż powiązane reguły (np. `BR1`), kryteria `AC` i kroki `P`. Nadaj regułom identyfikatory w sekcji docelowego zachowania, aby odwołania były jednoznaczne.
- **Given / Mając:** opisz rolę, stan początkowy, wymagane dane lub fixtures i warunki wstępne. Używaj konkretnych, syntetycznych wartości, szczególnie przy granicach walidacji; przykładowe dane nie mogą ustanawiać nowych reguł.
- **When / Gdy:** podaj jedną akcję biznesową lub zdarzenie wyzwalające. Dla procesu wieloetapowego opisz niezbędną kolejność działań.
- **Then / Wtedy:** określ jednoznaczny, obserwowalny wynik, np. status, widoczność danych, zapis, obliczoną wartość lub powiadomienie. Uwzględnij skutki uboczne oraz to, co nie może się zmienić, jeśli jest to istotne. Unikaj wyników typu „działa poprawnie” i asercji dotyczących prywatnych metod.

Dobierz pokrycie do zakresu zmiany: główny przebieg, istotne alternatywy, odrzucenia i błędne dane, wartości graniczne, uprawnienia oraz dozwolone i niedozwolone przejścia stanów. Dodaj błędy integracji, ponowienia, duplikaty, współbieżność, częściowe powodzenie lub regresję istniejących zachowań tylko wtedy, gdy wynikają z planowanej zmiany. Nie twórz sztucznej liczby scenariuszy ani wszystkich kombinacji bez uzasadnienia; warianty różniące się tylko danymi możesz zapisać w tabeli.

Jeśli wynik oczekiwany zależy od nierozstrzygniętej decyzji, oznacz scenariusz jako **zablokowany**, odwołaj się do otwartego pytania i wskaż brakującą regułę. Nie wymyślaj wyniku. W trwającym wywiadzie wykorzystaj taki brak do zadania konkretnego pytania; jeśli użytkownik kończy rozmowę, zachowaj go w wersji roboczej.

Dodaj krótką tabelę pokrycia: **reguła / kryterium → scenariusze → kroki planu**. Każda istotna reguła i każde kryterium powinny mieć scenariusz lub jawnie opisaną lukę. Oznacz scenariusze jako planowane i niewykonane; nie przedstawiaj ich jako zaliczonych. Nie generuj kodu testów bez zlecenia implementacji.

## Kontrola i przekazanie

Przeczytaj oba zapisane dokumenty i sprawdź wzajemne odnośniki. Sprawdź zgodność z ostatnimi decyzjami, spójność reguł i kroków, zależności oraz pokrycie wymagań kryteriami akceptacji i scenariuszami biznesowymi. Sprawdź odwołania BR/AC/SC/P, konkretność danych i wyników oraz zgodność scenariuszy z ostatnimi decyzjami. Usuń szablonowe instrukcje i nieaktualne warianty; zachowaj rzeczywiste otwarte pytania. Nie udawaj weryfikacji ścieżek, do których nie masz dostępu.

Na końcu podaj odnośniki lub ścieżki obu plików, ich statusy i ewentualne blokery. Nie zaczynaj implementacji tylko dlatego, że plan jest gotowy. Jeśli użytkownik już zlecił również implementację, kontynuuj zgodnie z tym zleceniem bez ponownego pytania o zgodę.
