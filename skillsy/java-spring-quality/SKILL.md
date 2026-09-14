---
name: java-spring-quality
description: Implementuj i refaktoryzuj produkcyjny kod Java oraz Spring/Spring Boot z priorytetem czytelności dla człowieka i łatwości utrzymania, preferując Lomboka, niemutowalne obiekty i bogatą domenę. Nie obejmuje pisania ani modyfikowania testów. Używaj przy dodawaniu funkcjonalności, naprawianiu błędów i przeglądzie jakości kodu backendowego w tych technologiach.
---

# Java i Spring — dobry kod

Dostarczaj kompletne rozwiązanie, które człowiek łatwo przeczyta, zrozumie i utrzyma. Poprawność zachowania i spójność danych są warunkiem koniecznym. Wśród poprawnych rozwiązań priorytetyzuj czytelność i łatwość utrzymania przed zwięzłością, sprytnymi konstrukcjami, wzorcami i hipotetyczną wydajnością. Zachowuj zakres zadania i istniejące kontrakty.

Stosuj Clean Code, SOLID i DRY tylko wtedy, gdy pomagają zrozumieć kod i bezpiecznie go zmieniać. Nie egzekwuj mechanicznych limitów długości metod ani liczby parametrów. Nie rozbijaj prostego przepływu na wiele drobnych metod lub klas, jeśli wymusza to skakanie po plikach. Dopuść lokalną duplikację zamiast nieczytelnej abstrakcji.

## Zakres: kod produkcyjny bez pisania testów

Nie twórz ani nie modyfikuj testów, fixture'ów, snapshotów ani infrastruktury testowej w ramach tego skilla. Pisanie testów należy do osobnego skilla; nie uruchamiaj go ani nie deleguj mu pracy automatycznie. Możesz czytać i uruchamiać istniejące testy w celu zrozumienia kontraktu i weryfikacji zmiany. Jeśli wymagają aktualizacji, wskaż to krótko, bez ich edycji i bez osłabiania asercji lub wyłączania testów.

## Rozpoznaj projekt

- Przeczytaj obowiązujące instrukcje repozytorium, konfigurację Maven/Gradle, właściwy moduł, jego wywołujących i pobliskie testy. Obejrzyj podobną implementację przed dodaniem nowej konwencji.
- Ustal rzeczywiste wersje Javy, Spring Boot i bibliotek, model MVC/WebFlux oraz używany sposób persystencji. Nie zakładaj najnowszych API, Hibernate ani automatycznego dirty checking.
- Ustal wejścia, wynik, reguły biznesowe, skutki uboczne i zachowanie przy błędzie. Przy refaktoryzacji zachowaj obserwowalne zachowanie, chyba że użytkownik zlecił jego zmianę.
- Gdy brak repozytorium, pracuj na przekazanym fragmencie i jawnie oznacz istotne założenia. Pytaj tylko o brak, który zmienia kontrakt lub poprawność; rutynowe wybory rozstrzygaj sam.
- Sprawdź dokumentację producenta dla używanej wersji, jeśli rozwiązanie zależy od niepewnej semantyki API. Nie aktualizuj zależności ani wersji języka przy okazji zadania.

## Projektuj odpowiedzialności

- Domyślnie projektuj bogate obiekty domenowe: stan wraz z zachowaniem, regułami i ochroną niezmienników. Preferuj `case.submit(actor)` zamiast pobierania danych do serwisu, podejmowania tam decyzji i ustawiania pól przez settery. DTO i projekcje odczytowe mogą pozostać nośnikami danych.
- Logikę umieszczaj w obiekcie, do którego pojęciowo należy. Serwis aplikacyjny pobiera dane, wywołuje zachowanie domeny i zapisuje wynik; nie przejmuje reguł obiektów. Serwis domenowy stosuj dla reguł, które nie należą naturalnie do jednego obiektu. Nie wtłaczaj całej logiki do jednego agregatu ani nie dodawaj sztucznych zachowań do prostego CRUD.
- Oddziel reguły domeny od I/O: obiekt domenowy nie powinien pobierać beanów Springa, wykonywać HTTP ani wyszukiwać własnych danych w repozytorium. Przekazuj mu potrzebne wartości lub wyniki odczytów.
- Oddziel orkiestrację przypadku użycia od transportu i szczegółów zapisu zgodnie z architekturą projektu. Kontroler nie powinien stawać się miejscem reguł biznesowych; nie narzucaj jednak DDD, CQRS ani architektury heksagonalnej istniejącej aplikacji.
- Przy `a.getB().getC().getD()` rozstrzygnij, czy kod jedynie odczytuje DTO, czy podejmuje decyzję na cudzym stanie. Przy decyzji domenowej rozważ metodę zachowania lub zapytanie domenowe. Nie twórz delegujących getterów wyłącznie dla skrócenia łańcucha.
- Dodawaj interfejs, strategię, fabrykę lub generyczny mechanizm, gdy reprezentuje rzeczywistą granicę albo potrzebną zmienność. Nie twórz ich automatycznie dla każdej klasy.
- Usuwaj duplikację wiedzy biznesowej. Nie łącz podobnych fragmentów, jeśli mają różne powody do zmiany. Preferuj kompozycję; nie buduj klas bazowych dla oszczędzenia kilku linii.

## Pisz czytelną Javę

- Nazywaj operacje i zmienne językiem domeny. Zachowuj jeden poziom abstrakcji w metodzie, stosuj guard clauses tam, gdzie upraszczają przepływ. Wydzielaj spójne operacje, nie przypadkowe fragmenty dla limitu linii.
- Wybieraj pętlę lub stream według czytelności. Unikaj skutków ubocznych w pipeline, zagnieżdżonych collectorów i `parallelStream()` bez analizy współbieżności oraz zasobów.
- Domyślnie preferuj niemutowalne obiekty: pola `final`, brak setterów, poprawny stan już po utworzeniu i defensywne kopie mutowalnych danych na wejściu i wyjściu. Samo `final`, record lub Lombok `@Value` nie zapewnia głębokiej niemutowalności.
- Łącz niemutowalność z zachowaniem: operacja domenowa waliduje reguły i zwraca nowy poprawny obiekt, np. `var submittedCase = currentCase.submit(actor)`. Wywołujący musi użyć i zapisać zwrócony wynik. Nie zastępuj zachowania publicznym `withStatus(...)`, jeśli pozwala to ominąć przejście domenowe.
- Gdy persystencja lub istniejący model wymagają mutowalności, ogranicz ją do jawnych metod domenowych chroniących niezmienniki. Nie przebudowuj całej architektury wyłącznie dla niemutowalności.
- Rozróżniaj brak wartości, pusty wynik i błąd. Stosuj `Optional` przede wszystkim jako wynik potencjalnie nieudanego wyszukania, zgodnie z konwencjami projektu. Nie zastępuj naruszenia obowiązkowego invariantu cichym `null`, pustą listą lub wartością domyślną.
- Dobieraj typy do semantyki: `BigDecimal` wraz z walutą i regułą zaokrąglania dla pieniędzy, `Instant` dla punktu w czasie, `LocalDate` dla daty kalendarzowej. Przy logice zależnej od czasu rozważ wstrzyknięty `Clock`.
- Preferuj Lomboka do usuwania boilerplate'u: `@RequiredArgsConstructor` przy zależnościach `final`, `@Value` dla odpowiednich niemutowalnych klas i selektywne `@Getter`, gdy potrzebny jest odczyt. Zachowuj jawną walidację konstrukcji i świadomą semantykę równości. Respektuj ograniczenia narzędzi i wyraźne konwencje projektu; records pozostają dobrą opcją dla prostych nośników danych.
- Unikaj `@Data` i publicznych setterów w domenie. Dobieraj generowane `equals`, `hashCode` i `toString` do tożsamości obiektu i wrażliwości danych. `@Builder` stosuj, gdy poprawia czytelność tworzenia; builder i `@With` nie mogą omijać reguł poprawnego stanu lub dozwolonych przejść.
- Używaj MapStruct zgodnie z projektem. Przy mapowaniu aktualizacji rozróżniaj brak pola od żądania wyzerowania wartości; mapper nie powinien omijać zachowań domenowych.
- Komentarzem wyjaśniaj przyczynę, invariant lub ograniczenie; nazwy i kod powinny opisywać samo działanie.

## Stosuj Spring świadomie

- Preferuj wstrzykiwanie przez konstruktor. Nie przechowuj stanu pojedynczego żądania w polach singletonowego beana. Nie ukrywaj cyklu zależności przez `@Lazy`; sprawdź podział odpowiedzialności.
- Waliduj format wejścia na granicy aplikacji, a reguły biznesowe tam, gdzie nie da się ich ominąć inną ścieżką wywołania. Zachowuj istniejący kontrakt DTO i odpowiedzi błędów.
- Utrzymuj spójne mapowanie wyjątków na odpowiedzi HTTP. Nie zwracaj sukcesu po błędzie, nie połykaj wyjątków i nie twórz nowej hierarchii wyjątków bez potrzeby. Zachowuj przyczynę i loguj awarię na właściwej granicy, unikając wielokrotnego logowania tego samego stosu.
- Umieszczaj transakcję wokół wymaganej jednostki atomowej. Zweryfikuj właściwy transaction manager, propagation i reguły rollbacku dla wyjątków faktycznie występujących w tej ścieżce.
- Sprawdź, czy wywołanie przechodzi przez proxy: w standardowym trybie proxy self-invocation nie uruchamia nowej semantyki `@Transactional`. Analogicznie sprawdzaj ścieżkę dla `@Async`, cache i zabezpieczeń opartych o proxy. Nie zakładaj przeniesienia transakcji do nowego wątku.
- Unikaj długiego zewnętrznego I/O w transakcji bazy. Gdy zapis i publikacja muszą przetrwać awarię, ustal wymagane gwarancje i rozważ istniejący mechanizm outbox. Sam callback po commicie nie zapewnia trwałego dostarczenia.
- Dla grup ustawień preferuj typowaną konfigurację zgodną z projektem. Nie zaszywaj sekretów ani nie loguj tokenów, pełnych danych osobowych i wrażliwych payloadów.

## Sprawdzaj dane i współbieżność, gdy zadanie ich dotyczy

- Obejrzyj wygenerowane lub ręczne zapytania i liczbę wywołań. Unikaj nieograniczonych odczytów i wzorca zapytanie na każdy element; stosuj właściwe filtrowanie, projekcję, batch lub paginację.
- Nie traktuj `exists` poprzedzającego `insert` jako ochrony przed wyścigiem. Rozważ constraint, warunkowy zapis lub kontrolę wersji zgodnie z bazą i wymaganiem. Zachowuj reguły agregatu przy częściowych aktualizacjach.
- Rozróżniaj semantykę JPA, Spring Data JDBC, MyBatis i innych magazynów. Przy ich łączeniu sprawdź faktyczne uczestnictwo w tej samej transakcji.
- Retry dodawaj dla odpowiednio sklasyfikowanych błędów, z limitem i odstępami. Najpierw rozstrzygnij idempotencję i przypadek, w którym operacja zdalna się udała, ale odpowiedź zaginęła.
- Przy asynchroniczności określ właściciela zadania, obsługę błędów, anulowanie, shutdown i limit pracy w toku. Nie używaj fire-and-forget dla pracy, której nie wolno utracić.
- Nie blokuj wątku event loop. Virtual threads nie znoszą limitów połączeń ani usług zewnętrznych. Poprawnie propaguj przerwanie lub przywróć flagę, jeśli nie możesz go przekazać wyżej.

## Zweryfikuj zmianę bez pisania testów

- Korzystaj z istniejącego wrappera i narzędzi projektu. Uruchom kompilację i adekwatne istniejące testy lub kontrole, proporcjonalnie do zmiany. Nie dodawaj nowych testów ani nie poprawiaj istniejących w tym skillu.
- Przejrzyj diff pod kątem czytelności dla człowieka: czy intencja jest oczywista, przepływ można śledzić bez zbędnego skakania, a reguły mają jedno naturalne miejsce? Uprość abstrakcje, które utrudniają odpowiedź.
- Sprawdź kontrakty, niezmienniki, transakcje, użycie wyników niemutowalnych operacji i skutki błędów. Nie rozszerzaj pracy o niezwiązane porządki.

## Zakończ konkretnym wynikiem

Przy implementacji dostarcz zmianę, a nie sam plan. Krótko podaj efekt, istotną decyzję oraz rzeczywiście uruchomioną weryfikację. Jawnie wskaż, czego nie udało się sprawdzić. Przy prośbie o review przedstaw ustalenia z miejscem w kodzie i scenariuszem problemu; nie edytuj automatycznie kodu tylko dlatego, że wykonujesz przegląd.

Źródło semantyki transakcji: [Using @Transactional](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html) oraz [Rolling Back a Declarative Transaction](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/rolling-back.html). Przy pracy dobierz dokumentację do wersji projektu.
