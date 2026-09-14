---
name: junit-domain-integration-tests
description: Pisz i refaktoryzuj domenowe testy integracyjne Java/JUnit w stylu BDD, z @DisplayName, fixtures i bez Mockito. Używaj przy testowaniu współpracy komponentów, persystencji i przepływów biznesowych, także w Spring. Nie zastępuj tym skillem pisania testów jednostkowych ani implementacji funkcjonalności produkcyjnej.
---

# Domenowe testy integracyjne JUnit

Twórz testy będące czytelną, wykonywalną specyfikacją zachowania biznesowego. Priorytetyzuj zrozumienie scenariusza przez człowieka i łatwość utrzymania. Stosuj inspiracje Clean Code Roberta C. Martina pragmatycznie; BDD, fixtures i zakaz Mockito są wymaganiami tego skilla, nie przypisuj ich wszystkich autorowi Clean Code.

## Ustal zachowanie i granicę integracji

- Przeczytaj instrukcje projektu, specyfikację biznesową, kod objęty zadaniem oraz istniejącą konfigurację testów. Dostosuj się do wersji Javy, JUnit Jupiter i Spring używanych w projekcie; nie aktualizuj zależności przy okazji.
- Wyprowadź scenariusze z reguł i obserwowalnych skutków biznesowych. Uwzględnij odpowiednie ścieżki pozytywne, odmowy, granice i błędy. Nie produkuj testu dla każdej metody ani kombinacji bez uzasadnienia.
- Gdy zakres jest znany, nie pytaj ponownie. Jeśli go nie podano i nie da się ustalić z kontekstu, zapytaj o funkcjonalność, klasy lub zmiany do przetestowania. Brak formalnej specyfikacji nie blokuje pracy, lecz nie traktuj obecnego kodu jako dowodu poprawności niejasnej reguły. Wyjaśnij istotną niejasność z użytkownikiem.
- Określ, jakie rzeczywiste komponenty mają współpracować. Jeśli test sprawdza zapis do bazy, użyj prawdziwego repozytorium, mapowania i testowej bazy. Nie podmieniaj elementów integracji, którą deklarujesz sprawdzać.

## Obowiązkowe BDD i nazwy

- Każdy scenariusz zapisuj jako Given–When–Then, z widocznymi sekcjami `// Given`, `// When`, `// Then`. Given ustawia warunki domenowe, When wykonuje jedną badaną akcję, Then sprawdza jej rezultat. Nie przeplataj wielu niezależnych akcji i asercji w jednym teście.
- Dodawaj jawne `@DisplayName` do klasy testowej i każdej metody `@Test` lub `@ParameterizedTest`; także do `@Nested`, jeśli ich używasz. Nie zastępuj ich samym generatorem nazw.
- Opisuj regułę językiem domeny: „Odrzucona płatność pozostawia zamówienie nieopłacone”, zamiast „execute zwraca wyjątek” czy „test serwisu”. Uwzględniaj warunek i oczekiwany wynik.
- Zachowaj język projektu; bez istniejącej konwencji używaj polskich DisplayName i angielskich nazw metod, np. `shouldKeepOrderUnpaidWhenPaymentIsDeclined`.
- W parametryzacji nadaj przypadkom czytelne nazwy zawierające znaczenie wariantu. Parametryzuj tę samą regułę z różnymi danymi, nie odmienne procesy biznesowe.
- BDD nie wymaga Cucumber ani plików Gherkin. Nie dodawaj ich bez potrzeby wynikającej z projektu lub prośby użytkownika.

## Fixtures

- Przygotowuj dane przez nazwane fixtures lub test data builders: `unpaidOrder()`, `submittedCase()`. Preferuj istniejące narzędzia projektu i domenowe fabryki.
- Fixture dostarcza minimalny poprawny obiekt i rozsądne domyślne wartości. W teście jawnie podaj dane decydujące o wyniku: status, kwotę, rolę czy termin. Nie chowaj tych warunków w setupie.
- Każde wywołanie zwraca świeże dane lub świeży builder; nie współdziel mutowalnych obiektów. Preferuj immutable wartości; wykorzystuj Lomboka, jeśli jest już używany i upraszcza kod. Nie dodawaj setterów ani builderów produkcyjnych wyłącznie dla wygody testu.
- Rozdziel tworzenie danych od persystencji: `orders.save(unpaidOrder().build())`. Jeśli pomocnik zapisuje dane, ujawnij to nazwą, np. `persistUnpaidOrder()`.
- Wybieraj stabilne wartości zamiast przypadkowych danych. Unikalne identyfikatory mogą izolować testy, ale losowość nie powinna decydować o sprawdzanej regule.

## Bez Mockito; fake na właściwej granicy

- Nie używaj Mockito, BDDMockito, `@Mock`, `@Spy`, `@MockBean`, `@MockitoBean`, `@MockitoSpyBean`, mockowania statycznego ani odpowiedników w innych bibliotekach jako obejścia zakazu.
- Używaj rzeczywistych komponentów wewnątrz sprawdzanej granicy. Fake może zastąpić zewnętrzny port, którego adapter nie jest przedmiotem tego testu, np. dostawcę płatności lub wysyłkę poczty.
- Fake implementuje prawdziwy kontrakt, zachowuje się deterministycznie i ma proste metody domenowe konfiguracji lub obserwacji. Brak wymaganej konfiguracji powinien dawać czytelny błąd, a nie przypadkowy sukces. Nie kopiuj złożonej logiki produkcyjnej do fake'a.
- Obserwuj biznesowy efekt fake'a, np. treść wysłanej wiadomości. Nie sprawdzaj kolejności wewnętrznych wywołań. Liczbę efektów sprawdzaj wtedy, gdy realizuje wymaganie, np. brak podwójnego obciążenia.
- Gdy testujesz adapter HTTP, pozostaw go prawdziwym i użyj lokalnego serwera testowego, np. WireMock/MockWebServer, zamiast fake'a portu. Taki serwer nie jest mockowaniem obiektów przez Mockito. Analogicznie dobierz broker lub emulator do badanej integracji.
- W Spring zapewnij jednoznaczne wstrzykiwanie fake'a i wyłącz produkcyjny adapter, jeśli jego tworzenie lub uruchamianie ma skutki uboczne. Samo `@Primary` nie zapobiega utworzeniu pozostałych beanów.
- Uczciwie określ granicę: fake płatności nie dowodzi zgodności z protokołem dostawcy.

## Asercje i niezawodność

- Sprawdzaj wynik, zmianę stanu i istotne skutki biznesowe. Preferuj czytelne asercje AssertJ, jeśli dostępne, albo standardowe JUnit. Jeden scenariusz może wymagać wielu asercji; nie wymuszaj jednej asercji na test.
- Sprawdzaj konkretne oczekiwane wartości, nie tylko `notNull`, liczbę rekordów czy brak wyjątku. Dla odmowy sprawdzaj również wymagany brak zmiany stanu lub efektów ubocznych.
- Przy persystencji odczytaj zapisany rezultat. Przy ORM uwzględnij flush/clear lub odrębną transakcję, jeśli inaczej test może czytać wyłącznie cache. Testowy rollback nie potwierdza zachowania po commit; nie dodawaj `@Transactional` automatycznie do testów procesów transakcyjnych.
- Preferuj bazę zgodną z produkcyjną oraz istniejącą infrastrukturę testową; Testcontainers stosuj, gdy pasuje i jest dostępny. Nie zastępuj specyficznej semantyki bazy przez H2 bez ujawnienia ograniczenia.
- Izoluj dane, stan fake'ów, zegar i zasoby. Nie opieraj testów na kolejności. Czyszczenie całych tabel dopuszczaj wyłącznie w dedykowanej bazie testowej bez konkurujących testów. Współdzielony kontekst Spring oznacza też współdzielone singletony.
- Używaj kontrolowanego `Clock`, gdy scenariusz zależy od czasu. Dla asynchroniczności czekaj na konkretny rezultat z limitem czasu, np. Awaitility; nie używaj arbitralnego `Thread.sleep()` ani retry ukrywającego niestabilność.
- Stosuj FIRST: możliwie szybkie, niezależne, powtarzalne, samodzielnie rozstrzygające wynik i tworzone wraz ze zmianą. Nie poświęcaj realnej integracji tylko dla szybkości. Uruchamiaj najmniejszy kontekst wystarczający do scenariusza; nie narzucaj `@SpringBootTest` każdemu testowi.

## Czytelność ponad abstrakcje

- Układaj klasy wokół przypadku użycia lub reguły domenowej. `@Nested` stosuj tylko, gdy ułatwia grupowanie scenariuszy.
- Ukrywaj techniczny szum w małych pomocnikach, ale pozostaw widoczny przebieg biznesowy. Unikaj rozbudowanych klas bazowych, flag sterujących scenariuszem, refleksji i uniwersalnych DSL-i.
- Dopuść niewielką duplikację, jeśli abstrakcja utrudniłaby przeczytanie testu od początku do końca. Nie przenoś całego Given do `@BeforeEach`; umieszczaj tam tylko wspólną konfigurację techniczną.
- Nie zmieniaj kodu produkcyjnego ani innych rodzajów testów poza zakresem zadania. Jeśli wykryjesz błąd, nie dopasowuj oczekiwań do błędnego zachowania; zgłoś go z reprodukcją.

## Wzorzec pojedynczego scenariusza

Przykład ilustruje styl; dostosuj symbole i konfigurację do projektu, nie traktuj go jako gotowej aplikacji. Zakłada prawdziwy przypadek użycia i repozytorium oraz fake zewnętrznej bramki płatności.

```java
@DisplayName("Opłacanie zamówienia")
class PayOrderIntegrationTest {
    // Wstrzykiwanie i izolacja zasobów zgodnie z konfiguracją projektu.

    @Test
    @DisplayName("Odrzucona płatność pozostawia zamówienie nieopłacone")
    void shouldKeepOrderUnpaidWhenPaymentIsDeclined() {
        // Given
        var order = orders.save(OrderFixtures.unpaidOrder().build());
        payments.declinePaymentFor(order.getId());

        // When
        var failure = catchThrowable(() -> payOrder.execute(order.getId()));

        // Then
        assertThat(failure).isInstanceOf(PaymentDeclinedException.class);
        var savedOrder = orders.findById(order.getId()).orElseThrow();
        assertThat(savedOrder.getStatus()).isEqualTo(OrderStatus.UNPAID);
    }
}
```

## Zakończenie pracy

Uruchom zmienione testy oraz niezbędny zakres testów powiązanych przy użyciu istniejącego mechanizmu projektu. Sprawdź, czy runner rzeczywiście wykonał testy integracyjne. Nie deklaruj sukcesu na podstawie samej kompilacji. Jeśli infrastruktura blokuje uruchomienie, podaj to wprost. W odpowiedzi krótko wskaż pokryte reguły, realne integracje, użyte fake'i oraz wynik uruchomienia. Nie podawaj niezmierzonego pokrycia procentowego.
