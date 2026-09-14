---
name: junit-unit-tests
description: Deleguj pisanie i refaktoryzację testów jednostkowych Java/JUnit do subagenta OpenAI Luna, z obowiązkowymi fixtures, @DisplayName i scenariuszami domenowymi given/when/then. Używaj przy dodawaniu, poprawianiu i porządkowaniu testów jednostkowych. Nie zastępuj tym skillem testów integracyjnych ani implementacji kodu produkcyjnego.
---

# Czytelne testy jednostkowe JUnit

Traktuj test jako wykonywalny przykład zachowania. Stosuj zasady czytelności i utrzymywalności inspirowane Clean Code Uncle Boba, z pierwszeństwem zrozumienia przez człowieka przed mechaniczną eliminacją powtórzeń i mnożeniem abstrakcji.

## Wykonawca — wymagany subagent OpenAI Luna

- Główny agent rozpoznaje zakres i oczekiwane zachowania, następnie deleguje pisanie i modyfikowanie testów oraz fixtures do subagenta korzystającego z modelu OpenAI Luna. Sam odpowiada za review i końcową weryfikację.
- W środowisku udostępniającym `spawn_agent` i model `gpt-5.6-luna` wybierz jawnie `model: "gpt-5.6-luna"` oraz `fork_turns: "none"`; przekaż kompletny, samodzielny opis zadania. W innych środowiskach użyj dostępnego mechanizmu delegacji i sprawdź w konfiguracji, że wykonawca rzeczywiście korzysta z OpenAI Luna. Sama nazwa agenta „luna” nie potwierdza modelu; nie zgaduj identyfikatora dostawcy ani modelu.
- Przekaż Lunie ten skill, instrukcje projektu, zakres plików, wymagane scenariusze i reguły, istniejące fixtures oraz polecenie uruchomienia testów. Zleć implementację, uruchomienie odpowiednich testów i raport wyników. Podczas jej pracy główny agent może niezależnie sprawdzać wymagania i przypadki brzegowe, bez równoczesnego edytowania tych samych plików.
- Subagent Luna wykonuje zadanie bez dalszego delegowania. Ta sekcja nie wymaga, aby wykonawca uruchamiał kolejną Lunę.
- Główny agent sprawdza rzeczywisty diff, zgodność scenariuszy z regułami, fixtures, `@DisplayName`, given/when/then oraz wynik wykonania. Potrzebne poprawki kodu testów przekazuje Lunie i ponownie ocenia rezultat; nie uznaje samego raportu subagenta za dowód poprawności.
- Jeśli Luna lub delegacja są niedostępne, kontynuuj możliwą analizę i przygotowanie scenariuszy, a następnie wyjaśnij ograniczenie. Nie zastępuj Luny innym modelem ani samodzielnym pisaniem testów bez zgody użytkownika. Nie deklaruj użycia Luny bez potwierdzenia uruchomienia właściwego modelu.

## Rozpoznanie i zakres

1. Przeczytaj instrukcje projektu, konfigurację budowania, testowany kod, najbliższe testy i dostępne fixtures. Dopasuj kod do faktycznych wersji Java, JUnit i biblioteki asercji; nie aktualizuj zależności przy okazji.
2. Ustal oczekiwane zachowania na podstawie wymagań, dokumentacji i kontraktów. Nie utrwalaj widocznego błędu jako poprawnego wyniku tylko dlatego, że tak działa implementacja. Gdy sprzeczność zmienia oczekiwany wynik, wskaż ją i zapytaj o tę konkretną regułę; kontynuuj jednoznaczne scenariusze.
3. Obejmij istotny poprawny przebieg, błędy biznesowe i granice wynikające z reguł. Dobieraj testy do ryzyka, nie do każdej metody lub procentu pokrycia. Nie pisz testów banalnych getterów, kodu generowanego ani zachowania bibliotek.
4. Zmieniaj testy i ich pomocniczy kod w zakresie zadania. Jeżeli test ujawni błąd produkcyjny, zgłoś go; naprawiaj kod produkcyjny tylko w ramach udzielonego zakresu pracy. Nie osłabiaj asercji, aby ukryć błąd.

## Scenariusze i nazwy — wymagane

- Używaj JUnit Jupiter i obowiązkowego `@DisplayName` na każdej metodzie testowej, klasie testowej oraz klasie `@Nested`. Jeżeli repozytorium używa wyłącznie starszego JUnit, jawnie wskaż konflikt zamiast dodawać niedziałające adnotacje lub przeprowadzać niezamówioną migrację.
- Opisuj w `@DisplayName` warunek i rezultat językiem domeny, np. „Wysłane zamówienie nie może zostać anulowane”. Unikaj „test cancel”, „happy path”, nazw mocków i szczegółów wywołań technicznych.
- Zachowaj język opisów przyjęty w projekcie; przy braku konwencji pisz opisy po polsku, a identyfikatory Java po angielsku.
- Stosuj jedną czytelną strukturę `// given`, `// when`, `// then` i jedną główną badaną operację. Przy `assertThrows` połącz wykonanie z asercją wyjątku w sekcji `when`; pozostałe skutki sprawdź w `then`.
- Sprawdzaj jeden scenariusz na test. Kilka asercji jest właściwe, gdy razem opisują jego rezultat.
- Używaj `@Nested`, gdy rzeczywiście porządkuje reguły. Parametryzuj warianty tej samej reguły; dodawaj `@DisplayName` i czytelny wzorzec `@ParameterizedTest(name = ...)`, aby rozróżnić wykonania. Nie łącz różnych zachowań w test z warunkami.

## Fixtures — obowiązkowe

- Przygotowuj obiekty domenowe i złożone dane wejściowe przez fixtures: nazwane fabryki, Object Mother lub test data builders. Najpierw wykorzystaj lub rozszerz istniejące fixtures; jeśli ich nie ma, utwórz minimalne w źródłach testowych.
- Nie zastępuj fixtures wielokrotnie kopiowanymi konstruktorami, wieloma setterami ani obszernymi grafami obiektów w metodach testowych. Proste wartości istotne dla scenariusza, takie jak liczby i daty, pozostaw jawne w teście.
- Nadaj fixtures nazwy domenowe, np. `OrderFixtures.shippedOrder()` albo `OrderFixtures.anOrder().withTotal(...).build()`.
- Zapewnij poprawne, deterministyczne wartości domyślne. Jawnie nadpisuj w teście dane decydujące o zachowaniu; nie chowaj progów, uprawnień i istotnych kwot za ogólnym `defaultOrder()`.
- Twórz nowy obiekt i nowe zmienne kolekcje przy każdym wywołaniu lub `build()`. Nie współdziel zmiennych obiektów ani builderów między testami. Niemutowalne stałe mogą być wspólne.
- Buduj stan przez legalne API domenowe. Nie używaj refleksji ani obchodzenia walidacji. Dla błędnego wejścia przygotuj poprawne otoczenie fixture i podaj błędną wartość bezpośrednio do badanej operacji, aby wyjątek nie pochodził z przygotowania.
- Nie umieszczaj badanego zachowania, asercji ani obliczania oczekiwanego wyniku w fixture. Fixture dla wysłanego zamówienia może wykonać legalne przejścia przygotowawcze, ale test wysyłki powinien zacząć od fixture zamówienia gotowego do wysłania.
- Utrzymuj fixtures lokalnie przy danej domenie; wydziel wspólne dopiero przy realnym ponownym użyciu. Unikaj uniwersalnych fabryk opartych na flagach i wielkich klas bazowych. Małe powtórzenie jest lepsze niż nieczytelna abstrakcja.
- Ogranicz `@BeforeEach` do prostego, wspólnego przygotowania; warunki scenariusza pokazuj w metodzie testowej.

## Izolacja i zależności

- Uruchamiaj testy jednostkowe w pamięci, bez kontekstu Springa, bazy danych, kontenerów, plików zależnych od środowiska i sieci. Nie używaj `@SpringBootTest` ani testowych slice'ów Springa.
- Testuj prawdziwe obiekty domenowe i value objects. Jednostka zachowania może obejmować kilka współpracujących klas; nie mockuj każdej klasy automatycznie.
- Dla zewnętrznych portów wybierz najprostszy czytelny stub, fake lub mock. Preferuj małe fake'i, gdy ułatwiają sprawdzanie skutków. Mockito jest dopuszczalne, gdy upraszcza scenariusz; nie narzucaj zakazu ani obowiązku jego używania.
- Nie mockuj testowanego obiektu, jego metod prywatnych ani wewnętrznych kroków algorytmu. Unikaj deep stubs i spy maskujących nieczytelną konstrukcję.
- Weryfikuj interakcje tylko wtedy, gdy same są kontraktem, np. zlecenie wysłania powiadomienia. Nie wymagaj kolejności lub dokładnej liczby wywołań, jeśli reguła tego nie określa. Nie dodawaj automatycznie `verifyNoMoreInteractions`.
- Nie traktuj fake repozytorium jako dowodu działania SQL, transakcji ani mapowania. Te właściwości wymagają osobnych testów integracyjnych.
- Kontroluj czas przez `Clock` lub istniejący port czasu, losowość przez jawne dane lub kontrolowany generator. Nie używaj `Thread.sleep` ani aktualnego czasu do przewidywania wyniku. Testuj każdą istotną granicę czasową deterministycznie.
- Zapewnij niezależność od kolejności uruchamiania, strefy czasowej i zmiennego stanu statycznego. Resetuj stan fake'ów przez tworzenie świeżych instancji dla każdego testu.

## Asercje i utrzymywalność

- Sprawdzaj obserwowalne wyniki, stan i wymagane efekty biznesowe przez publiczny kontrakt. Nie uzależniaj testu od struktury klas, prywatnych pól czy wewnętrznej delegacji.
- Używaj biblioteki asercji dostępnej w projekcie; nie dodawaj nowej tylko dla stylistyki. Preferuj asercje podające oczekiwaną i faktyczną wartość zamiast ogólnego `assertTrue`.
- Wylicz oczekiwany rezultat niezależnie od implementacji; nie kopiuj algorytmu produkcyjnego do testu ani nie wywołuj go do ustalenia oczekiwania.
- Sprawdzaj właściwy typ wyjątku i istotne dane domenowe. Treść komunikatu sprawdzaj wyłącznie, jeśli stanowi kontrakt. Asercja wyjątku powinna obejmować tylko badaną operację.
- Dla odrzucenia operacji sprawdzaj także brak niedozwolonego skutku, jeśli jest częścią reguły, np. brak zmiany statusu lub brak powiadomienia.
- Nie twórz testów bez asercji, przypadkowych danych, wielkich snapshotów ani sprawdzania wszystkich pól bez związku ze scenariuszem.

## Przykład struktury

Przykład jest ilustracyjny; dostosuj typy i fixture do rzeczywistego API projektu.

```java
@DisplayName("Anulowanie zamówienia")
class OrderTest {

    @Test
    @DisplayName("Wysłane zamówienie nie może zostać anulowane")
    void shouldRejectCancellationOfShippedOrder() {
        // given
        var order = OrderFixtures.shippedOrder();

        // when
        var exception = assertThrows(
                OrderCannotBeCancelled.class,
                order::cancel
        );

        // then
        assertEquals(order.id(), exception.orderId());
        assertEquals(OrderStatus.SHIPPED, order.status());
    }
}
```

## Weryfikacja i wynik pracy

Uruchom zmienione testy właściwym poleceniem projektu. Rozszerz uruchomienie na bezpośrednich użytkowników zmienionych wspólnych fixtures. Sprawdź, czy asercje wykryłyby realne naruszenie reguły i czy przygotowanie nie wykonuje już badanej operacji. Nie uruchamiaj kosztownych dodatkowych narzędzi bez konkretnej potrzeby.

Zakończ krótką informacją o pokrytych zachowaniach, dodanych lub wykorzystanych fixtures oraz wyniku uruchomienia. Jeśli testów nie można uruchomić, podaj przyczynę; nie deklaruj sukcesu bez wykonania. Ujawnij istotne rozbieżności między wymaganiami a implementacją.
