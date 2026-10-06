# Prompt do uruchomienia w repozytorium

Przygotuj projektową część dołączonego setupu OpenCode. Pracuj na mocniejszym modelu w trybie umożliwiającym edycję. Wykonaj pracę, nie kończ na samym planie. Nie zmieniaj kodu aplikacji.

## Punkt startowy
Przeczytaj .opencode/config.template.json, .opencode/prompts/*.md, README-AI-SETUP.md i istniejące instrukcje projektu. Role, ogólny workflow i szablon planu są już przygotowane — zachowaj je, nie twórz kolejnych agentów ani frameworka orkiestracji.

Sprawdź lokalną wersję OpenCode, dostępną składnię i modele. Setup jest przeznaczony dla 1.x, z modelem Luna („ai-luna6”) dla build/explore i Sol („OpenAI Sol 6”) dla plan/reviewer. Nazwy użytkownika nie muszą być identyfikatorami API. Nie wymyślaj identyfikatorów, korzystaj z lokalnej listy modeli. Przy niejednoznaczności zapytaj o mapowanie, wykonując wcześniej pozostałe niezablokowane prace. Nie aktualizuj OpenCode.

Jeżeli istnieje opencode.ai-setup.candidate.json, scal go z aktywną konfiguracją bez usuwania providerów, MCP, instrukcji i innych agentów. W razie konfliktu istniejących ról zachowaj ograniczenia uprawnień i wskaż konflikt. Sprawdź także lokalne definicje Markdown agentów i wpływ konfiguracji globalnej, jeśli jest dostępna. Nie edytuj konfiguracji globalnej. Nie rozszerzaj ograniczeń organizacji. Jeśli brak aktywnej konfiguracji, skonfiguruj szablon przez .opencode/configure.py z rozpoznanymi modelami.

## Rozpoznanie projektu
Sprawdź strukturę modułów, manifesty, build, CI, architekturę, testy i dokumentację. Przeczytaj reprezentatywne implementacje oraz testy. Ustal realne komendy i miejsca rozszerzania funkcjonalności. Nie zakładaj Java/Spring ani żadnego innego stosu bez dowodów. Nie próbuj analizować wszystkich przepływów biznesowych.

## AGENTS.md
Utwórz lub uzupełnij zwięzły główny AGENTS.md. Zachowaj istniejące zasady. Uwzględnij:
- przeznaczenie projektu i mapę modułów;
- komendy build, właściwych testów, lintowania i formatowania;
- potwierdzone granice architektoniczne i konkretne konwencje;
- zasady pracy na istniejących zmianach oraz weryfikacji zachowania;
- wybór między małą zmianą realizowaną przez build a planowaniem większej zmiany;
- informację, że build wywołuje reviewer po zmianach zachowania, danych, integracji, uprawnień i zmianach przekrojowych;
- listę projektowych skilli, warunki ich użycia i ścieżki.

Nie powielaj pełnych promptów agentów ani skilli w AGENTS.md. Nie wymyślaj standardów projektu. Niezweryfikowane informacje oznacz jawnie. Zagnieżdżone AGENTS.md dodawaj tylko tam, gdzie moduły rzeczywiście wymagają odmiennych reguł.

## Projektowe skille
Utwórz około 3–5 przydatnych skilli w .opencode/skills/<nazwa>/SKILL.md. Najpierw oceń istniejące i uzupełnij je zamiast tworzyć duplikaty. Użyj poprawnego frontmatter name i description oraz formatu obsługiwanego przez lokalną wersję.

Dobierz zakres na podstawie projektu: implementacja zgodna z architekturą, testy, diagnozowanie błędów, review charakterystycznych ryzyk projektu, aktualizacja dokumentacji zachowania. Nie twórz pustych skilli tylko dla osiągnięcia określonej liczby.

Każdy skill: kiedy używać, krótki workflow, realne ścieżki i przykłady, odpowiednie komendy, oczekiwany wynik i warunek zakończenia. Opis review ma zawierać ryzyka specyficzne dla repozytorium, nie kopię ogólnego promptu reviewer. Skille są ładowane na żądanie. Nie dodawaj ich wszystkich do globalnego kontekstu.

## Integracja i weryfikacja
Zachowaj: build/explore na słabszym modelu, plan/reviewer na mocniejszym; plan i reviewer tylko odczyt; build może wywoływać explore/reviewer, plan tylko explore. Reviewer nie uruchamia shella — otrzymuje diff i wyniki testów od build. Plan jest przekazywany w rozmowie, a zapisuje go build. Nie udawaj automatycznego przełączania głównych agentów.

Sprawdź dostępność modeli, składnię konfiguracji, odkrywanie skilli, role i efektywne uprawnienia. Gdy możesz, wykonaj krótki test wywołania explore i reviewer, a wynik odróżnij od samej statycznej walidacji. Jeśli wymaga to nowej sesji OpenCode, podaj konkretne kroki użytkownikowi. Nie uruchamiaj całego zestawu testów aplikacji tylko z powodu zmian setupu.

Uzupełnij README-AI-SETUP.md o projektowe komendy i skille. Jeśli trzeba, dopisz do istniejącego .gitignore wyłącznie katalog tymczasowych diffów .opencode/reviews/; nie ignoruj całego .opencode. Nie usuwaj istniejących wpisów.

Na końcu podaj zmienione pliki, tabelę agent/model/uprawnienia, listę skilli, wykonane sprawdzenia oraz nieweryfikowane elementy. Nie wykonuj commita, pusha ani wdrożenia.
