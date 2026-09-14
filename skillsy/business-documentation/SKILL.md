---
name: business-documentation
description: Twórz i utrzymuj dokumentację biznesową projektu jako źródło wiedzy dla ludzi i kolejnych agentów. Używaj przy implementacji, zmianie lub usunięciu funkcjonalności biznesowej, naprawie błędu wpływającego na zachowanie, zmianie reguł, walidacji, uprawnień, statusów, obliczeń lub biznesowych skutków integracji, także bez osobnej prośby o dokumentację. Używaj również na bezpośrednią prośbę o dokumentację biznesową. Gdy dokumentacji brakuje, utwórz ją od podstaw. Pomijaj czysto techniczne refaktoryzacje bez zmiany zachowania biznesowego.
---

# Dokumentacja biznesowa

Utrzymuj w projekcie aktualny opis tego, po co system istnieje, kto go używa i jak działa biznesowo. Pisz tak, aby kolejny agent bez historii rozmowy mógł odnaleźć funkcjonalność, zrozumieć jej reguły i bezpiecznie ocenić konsekwencje kolejnej zmiany. Dokumentacja ma opisywać bieżący stan, nie być dziennikiem wykonanych zadań ani katalogiem klas.

## Rozpoznaj kontekst i wpływ zmiany

1. Przeczytaj obowiązujące instrukcje projektu i odnajdź dokumentację: README, docs, dokumenty domenowe, wymagania, decyzje oraz odnośniki do zewnętrznych źródeł. Użyj `rg --files` i wyszukiwania po nazwach pojęć; pomijaj zależności i pliki generowane. Uszanuj istniejącą lokalizację, język i strukturę.
2. Ustal zakres bieżącego zadania i rzeczywistych zmian. Gdy dostępny jest Git, obejrzyj odpowiedni diff, nowe pliki oraz kontekst zmienionych fragmentów. Nie uznawaj wszystkich zastanych zmian za część zadania i nie zakładaj, że cała zmiana mieści się w ostatnim commicie. Bez diffu porównaj dostępny stan z wymaganiami i dokumentacją; nie wymyślaj stanu poprzedniego.
3. Nazwij biznesowy skutek: kto może zrobić co, pod jakim warunkiem, z jakim rezultatem. Uwzględnij skutki pośrednie dla innych procesów. Zmiana konfiguracji, migracji, kolejki lub API również może zmieniać zachowanie biznesowe. Jeśli zmiana jest wyłącznie techniczna i dokumentacja pozostaje prawdziwa, zakończ bez jej modyfikowania.
4. Przed implementacją odczytaj związane reguły. Po implementacji zweryfikuj opis wobec końcowego stanu. W zadaniu planistycznym lub tylko do odczytu przedstaw proponowaną aktualizację; nie zapisuj planowanego zachowania jako już wdrożonego.

## Oprzyj opis na dowodach

Czytaj ścieżkę działania, a nie tylko nazwy metod: wejście użytkownika lub zdarzenie, warunki, logikę domenową, zapis i skutki zewnętrzne. Wykorzystuj istniejące testy jako dodatkowe dowody, bez pisania lub zmieniania testów w ramach tego skilla.

Rozdzielaj wymagania biznesowe od zachowania zaobserwowanego w kodzie. Błąd implementacji nie staje się regułą tylko dlatego, że istnieje w kodzie. Gdy wymaganie, dokumentacja, test i implementacja są sprzeczne, opisz rozbieżność oraz jej źródła. Wprowadź potwierdzoną część opisu, a o rozstrzygnięcie zapytaj tylko wtedy, gdy blokuje istotną decyzję. Nie zmieniaj kodu po to, aby dopasować go do dokumentacji poza zakresem zadania.

Przy istotnych regułach podawaj zwięzłe źródło: względną ścieżkę i symbol implementacji lub testu, albo dostępne wymaganie. Nie polegaj na numerach linii. Wnioski oznacz jako „Wniosek z implementacji”, a nieznane kwestie jako „Do potwierdzenia” wraz z konkretnym pytaniem. Nie zgaduj celu biznesowego, terminów, ról ani gwarancji. Nie opisuj zachowania jako produkcyjnego bez dowodu wdrożenia; zaznacz flagi funkcjonalne i warianty konfiguracji, jeśli wpływają na dostępność.

## Zaktualizuj istniejącą dokumentację

Edytuj kanoniczny opis funkcjonalności zamiast dopisywać konkurencyjny dokument o tej samej treści. Zachowaj istniejące identyfikatory reguł i terminologię. Aktualizuj powiązane definicje, tabele stanów, uprawnień, scenariusze i linki, jeśli zmiana je unieważnia. Usuwaj nieaktualne twierdzenia w objętym zakresie; uzasadnienia i historię zachowuj tam, gdzie projekt już je prowadzi.

Jeżeli dokumentacja istnieje, ale brakuje opisu zmienianej funkcjonalności, dodaj go w istniejącej strukturze. Nie przebudowuj całej dokumentacji przy małej zmianie. Jeśli dokumentacja jest wskazana w niedostępnym systemie zewnętrznym, nie utożsamiaj braku dostępu z brakiem dokumentacji: przygotuj lokalny projekt aktualizacji z oznaczeniem, że wymaga scalenia, zamiast ogłaszać nowe źródło prawdy. Nie publikuj zewnętrznie bez odpowiedniego upoważnienia.

## Gdy dokumentacji nie ma

Utwórz od podstaw użyteczną bazę wiedzy w Markdown. Przy braku konwencji użyj `docs/business/README.md` jako punktu wejścia i `docs/business/features/<nazwa-funkcjonalnosci>.md` dla szczegółów.

Najpierw zbuduj krótki obraz całego projektu z dostępnych źródeł: cel, główne role, pojęcia, obszary funkcjonalne oraz granice odpowiedzialności systemu. Następnie dokładnie opisz zmienianą funkcjonalność i zależności potrzebne do jej zrozumienia. Dla pozostałych obszarów podaj potwierdzony skrót i jawnie zaznacz brak szczegółowego rozpoznania. Nie udawaj kompletnej analizy całego systemu po przeczytaniu jednego modułu.

W punkcie wejścia umieść:

- krótki opis projektu i zakres dostępnej wiedzy;
- słownik najważniejszych pojęć, z odróżnieniem podobnych terminów;
- mapę funkcjonalności z linkami do istniejących opisów;
- wskazówkę dla następnego agenta: przeczytaj ten indeks, potem dokument funkcjonalności i wskazane reguły zależne, a przed zmianą zweryfikuj źródła w kodzie;
- istotne nierozstrzygnięte kwestie, jeśli występują.

Dla niewielkiego projektu połącz treści w jednym pliku zamiast tworzyć puste katalogi i dokumenty. Dodaj link do punktu wejścia w istniejącym README, jeśli projekt na to pozwala. Nie nadpisuj instrukcji AGENTS.md ani konfiguracji agenta, żeby wymusić aktywację skilla.

## Opis funkcjonalności

Dopasuj długość do złożoności. Uwzględnij tylko mające zastosowanie elementy, bez pustych sekcji:

- **Cel i zakres:** problem biznesowy, rezultat oraz granice funkcjonalności.
- **Aktorzy i uprawnienia:** kto inicjuje, widzi, edytuje lub zatwierdza; oddziel widoczność od prawa wykonania akcji.
- **Przebieg:** wyzwalacz, warunki wejściowe, główny scenariusz, alternatywy i wynik widoczny dla użytkownika lub innego systemu.
- **Reguły i niezmienniki:** konkretne warunki, limity, obliczenia i wyjątki. Przy kilku regułach nadaj stabilne identyfikatory, np. BR-ORD-001. Nie zmieniaj numeracji istniejących reguł.
- **Stany i przejścia:** stan początkowy, akcja, warunek, stan końcowy i skutek uboczny. Rozróżnij stan procesu od statusu technicznego.
- **Dane:** znaczenie biznesowe, wymagalność, wartości domyślne, walidacja i źródło prawdy, o ile mają znaczenie dla procesu.
- **Błędy i integracje:** skutki odmowy, częściowego niepowodzenia, ponowienia, duplikatu lub opóźnienia. Nie deklaruj atomowości ani dostarczenia dokładnie raz bez potwierdzenia.
- **Przykłady:** krótki scenariusz poprawny i istotny wyjątek lub przypadek graniczny, z oczekiwanym rezultatem. To przykłady biznesowe, nie nowe testy wykonywalne.
- **Powiązania i źródła:** zależne funkcjonalności, reguły, najważniejsze ścieżki i symbole w kodzie oraz otwarte pytania.

Pisz pełnymi, prostymi zdaniami. Używaj języka domeny; szczegóły techniczne dodawaj tylko dla śledzenia źródła albo wyjaśnienia obserwowalnego zachowania. Złożone reguły porównuj w tabelach. Diagram Mermaid dodaj, gdy rozgałęzienia procesu lub przejścia stanów są łatwiejsze do zrozumienia wizualnie. Nie kopiuj kodu, sekretów ani danych osobowych; używaj przykładów fikcyjnych.

## Sprawdź i zakończ

Porównaj dokumentację z końcową zmianą: czy opis obejmuje jej skutki biznesowe, czy warunki, role, statusy i przykłady są spójne, czy źródła oraz linki istnieją i czy nie pozostały sprzeczne twierdzenia w powiązanych opisach. Nie uruchamiaj pełnego zestawu testów tylko z powodu edycji Markdown; skorzystaj z istniejącej walidacji dokumentacji, jeśli jest wymagana przez projekt.

W odpowiedzi krótko wskaż utworzone lub zmienione dokumenty, opisane skutki biznesowe i ewentualne luki. Gdy aktualizacja jest zbędna, powiedz dlaczego. Nie ogłaszaj pełnego pokrycia dokumentacją bez przeanalizowania całego deklarowanego zakresu.
