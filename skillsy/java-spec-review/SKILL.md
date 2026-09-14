---
name: java-spec-review
description: Wykonuj review kodu Java/Spring pod kątem zgodności ze specyfikacją, rzeczywistych błędów, czytelności i łatwości utrzymania. Preferuj Lomboka, niemutowalne obiekty i bogatą domenę bez dogmatycznego clean code. Używaj przy przeglądzie kodu, PR/MR, commitów i lokalnych zmian; nie zastępuj tym skillem zwykłej implementacji.
---

# Java Spec Review

Oceniaj kod z perspektywy człowieka, który musi zrozumieć jego zachowanie i bezpiecznie go zmienić. Najpierw sprawdzaj poprawność i wymagania, następnie czytelność i utrzymanie. Preferencje architektoniczne nie są automatycznie wymaganiami biznesowymi ani dowodem błędu.

## Ustal specyfikację i zakres

- Przeczytaj instrukcje projektu i zakres wskazany przez użytkownika. Poszukaj specyfikacji w podanych materiałach, kryteriach akceptacji, zadaniu, dokumentacji biznesowej i odpowiednich plikach projektu. Użyj `rg` do zawężenia poszukiwań. Nie wykonuj nieograniczonego skanowania wszystkich materiałów.
- Nie traktuj obecnej implementacji jako specyfikacji. Testy i komentarze są dowodami pomocniczymi, które również mogą być błędne. Oddziel jawne wymagania od założeń i zachowania zastanego.
- **Jeżeli specyfikacja nie istnieje albo nie jest dostępna, a użytkownik nie wybrał już zakresu review, zatrzymaj się przed review i zapytaj, co sprawdzić.** Zaproponuj w pytaniu konkretne możliwości: wskazane commity lub zakres commitów, różnicę względem brancha, staged files, unstaged files albo konkretne pliki/katalogi. Przykład: „Nie znalazłem specyfikacji. Co mam reviewować: konkretne commity, zmiany względem brancha, pliki staged, unstaged czy wskazane pliki?”. Nie wybieraj sam zakresu zastępczego.
- Jeżeli użytkownik już podał ten zakres, nie pytaj ponownie. Jeżeli odpowie wyborem zmian bez specyfikacji, wykonaj review błędów i jakości; oznacz zgodność ze specyfikacją jako nieocenioną. Nie żądaj stworzenia specyfikacji i nie twórz jej samodzielnie.
- Jeżeli specyfikacja istnieje, ustal jej związek z kodem. Przy jednoznacznym wskazaniu funkcjonalności przejrzyj jej implementację. Jeśli istnieje kilka możliwych celów porównania, zapytaj o zakres zamiast zgadywać branch bazowy lub commity.
- Dla lokalnych zmian rozróżniaj staged (`git diff --cached`), unstaged w śledzonych plikach (`git diff`) i untracked (`git ls-files --others --exclude-standard`). Nie dodawaj untracked do zakresu „unstaged” bez zaznaczenia tej różnicy i wyboru użytkownika. „Wszystkie lokalne zmiany” obejmuje te trzy kategorie.
- Dla pojedynczego commita porównaj go z właściwym rodzicem; przy merge commicie wyjaśnij niejednoznaczność rodzica. Dla brancha ustal bazę porównania i użyj właściwego merge-base. Dla zestawu commitów nie włączaj po cichu zmian spoza wyboru.
- Czytaj także wywołujących, wywoływane metody, konfigurację i mapowania konieczne do oceny skutków. To kontekst review, a nie zgoda na ocenę całego repozytorium.

## Sprawdź wymagania i błędy

Dla istotnych wymagań ustal: źródło, oczekiwane zachowanie, ścieżkę implementacji i wynik — spełnione, częściowo spełnione, niespełnione albo niezweryfikowane. Nie uznawaj braku dowodu za dowód naruszenia. Przy sprzecznych materiałach nazwij konflikt, a nie wybieraj po cichu wygodniejszej wersji.

Prześledź wykonanie od wejścia przez domenę po zapis i skutki zewnętrzne. Zależnie od zmienionego kodu sprawdź:

- Warunki brzegowe, null/puste dane, zakresy, obliczenia, porównania, czas i strefy czasowe.
- Walidację, uprawnienia, izolację danych, dozwolone przejścia statusów i niezmienniki domeny.
- Utracone aktualizacje, współbieżność, idempotencję, duplikaty, retry i kolejność zdarzeń.
- Granice transakcji, rollback, częściowy sukces i rozbieżność między skutkiem zewnętrznym a zapisanym stanem.
- Mapowania, serializację, zapytania, stronicowanie, zgodność kontraktów oraz zachowanie dotychczasowych wywołań.
- Obsługę wyjątków, zwalnianie zasobów i propagację błędów pracy asynchronicznej; wydajność tylko przy wiarygodnym scenariuszu wpływu.

Sprawdzaj zachowanie Springa i bibliotek dla wersji rzeczywiście użytych w projekcie. Nie zgłaszaj błędu na podstawie samej nazwy adnotacji bez sprawdzenia ścieżki wywołania, konfiguracji i obsługi przez framework.

Każdy bug uzasadnij osiągalnym scenariuszem, warunkami wystąpienia, oczekiwanym i rzeczywistym skutkiem oraz miejscem w kodzie. Sprawdź, czy inna warstwa nie zapewnia już ochrony. Oddziel potwierdzone problemy od podejrzeń wymagających danych. Przy review zmian odróżnij błędy wprowadzone lub ujawnione zmianą od problemów wcześniejszych; wcześniejsze zgłaszaj oddzielnie tylko, gdy wpływają na oceniane zachowanie.

Możesz uruchomić istniejące, adekwatne testy lub kompilację, jeśli środowisko na to pozwala. W trybie review nie pisz ani nie modyfikuj testów; opisz potrzebny scenariusz weryfikacji. Nie traktuj zielonych testów jako dowodu pełnej poprawności. Jawnie podaj, czego nie uruchomiono lub nie udało się sprawdzić.

## Oceń czytelność i utrzymanie

Stosuj następującą kolejność: poprawność i kontrakty, zrozumiałość dla człowieka, łatwość bezpiecznej zmiany, a dopiero potem zgodność z preferowanym stylem.

- Preferuj nazwy wyrażające intencję biznesową, jawny przepływ, spójny poziom abstrakcji i mało zagnieżdżeń. Oceń, ile plików i pośredników trzeba przeczytać, aby zrozumieć jeden przypadek użycia.
- Preferuj prostą pętlę nad skomplikowanym streamem, gdy ułatwia zrozumienie. Nie wymagaj krótszych metod, dodatkowych interfejsów, wzorców ani usuwania każdej duplikacji bez konkretnej korzyści. Nie zamieniaj lokalnej czytelności w nadmiar drobnych metod i klas.
- **Lombok:** preferuj usuwanie mechanicznego boilerplate przez adekwatne adnotacje, np. `@RequiredArgsConstructor`, `@Getter`, `@Value`. Nie zgłaszaj ręcznie napisanego konstruktora jako buga. Oceniaj wygenerowane zachowanie: `equals/hashCode`, `toString`, konstrukcję i dostęp do stanu. Nie rekomenduj automatycznie `@Data`, setterów, builderów ani `@With`, jeżeli osłabiają niezmienniki lub ujawniają dane. Szanuj ograniczenia projektu i istniejące czytelne rekordy; nie wymuszaj Lomboka kosztem poprawności.
- **Niemutowalność:** preferuj niemutowalne wartości i obiekty, gdy upraszczają rozumienie stanu. Sprawdź defensywne kopiowanie kolekcji oraz mutowalne elementy; `final`, rekord i `@Value` same nie zapewniają głębokiej niemutowalności. Oceń, czy builder lub kopiowanie pozwalają stworzyć niedozwolony stan. Zaakceptuj kontrolowaną mutację agregatu lub wymagania mechanizmu persystencji, jeżeli rozwiązanie jest czytelniejsze i chroni reguły.
- **Bogata domena:** preferuj umieszczanie reguł, obliczeń i przejść stanu w obiekcie lub agregacie, który posiada dane i odpowiada za niezmiennik. Zwracaj uwagę na serwisy manipulujące cudzym stanem przez gettery i settery. Preferuj operację domenową wyrażającą intencję zamiast rozproszonej modyfikacji pól.
- Pozostaw orkiestrację, transakcje i integracje w warstwie aplikacyjnej/infrastrukturze. Dopuść serwis domenowy dla reguły, która nie ma naturalnego właściciela. Nie przenoś I/O do encji dla samego „bogactwa” domeny; DTO nie musi mieć logiki biznesowej.
- **Clean code:** traktuj zasady jako narzędzia. Zgłaszając sugestię, wyjaśnij, co konkretnie stanie się łatwiejsze do zrozumienia lub zmiany i jaki jest koszt. Nie blokuj poprawnego kodu wyłącznie z powodu gustu ani nie proponuj przebudowy architektury dla lokalnego uproszczenia.

## Raport review

Zacznij od najważniejszych ustaleń, w kolejności wpływu. Rozdziel błędy/niezgodności, sugestie utrzymaniowe i pytania otwarte. Nie wymuszaj minimalnej liczby uwag.

Dla każdego problemu podaj:

- Priorytet i krótki tytuł: P0 — krytyczny i bezwarunkowy problem; P1 — poważny, do pilnej poprawy; P2 — istotny w określonym scenariuszu; P3 — drobny. Sugestie stylu oznacz jako sugestie, bez udawania bugów.
- Lokalizację: plik i możliwie wąski zakres linii.
- Dowód: scenariusz, skutek i powiązane wymaganie, jeżeli istnieje. Zaznacz warunki i niepewność.
- Najmniejszą sensowną poprawkę oraz sposób zweryfikowania zachowania; unikaj pełnego przepisywania kodu w raporcie.

Na końcu krótko podaj zakres, użyte źródła specyfikacji, pokrycie istotnych wymagań i ograniczenia weryfikacji. Gdy brak specyfikacji, napisz wprost, że oceniono błędy i jakość, bez potwierdzenia zgodności biznesowej. Gdy nie znaleziono problemów, napisz „Nie znalazłem problemów w sprawdzonym zakresie”, bez gwarantowania braku błędów.

Domyślnie przedstaw review bez modyfikacji plików projektu. Naprawiaj dopiero, gdy użytkownik tego zażąda; osobne polecenie naprawy określa zakres zmian.
