# 💓 Dashboard do Analizy Ciśnienia Krwi

Interaktywny dashboard do wizualizacji i analizy pomiarów ciśnienia krwi, zbudowany w oparciu o biblioteki Dash i Plotly. Aplikacja jest w pełni zgodna z najnowszymi wytycznymi Europejskiego Towarzystwa Kardiologicznego (ESC/ESH).

![przykład](https://i.imgur.com/example.png)

## 🌟 Główne Funkcje

- **Pełna Modularyzacja**: Kod został podzielony na logiczne moduły (dane, wykresy, layout, callbacki), co sprawia, że jest niezwykle czytelny, łatwy w utrzymaniu i rozbudowie.
- **Interaktywne Wykresy**: 9 różnych zakładek analitycznych, które pozwalają na dogłębną analizę danych pod różnymi kątami.
- **Automatyczne Odświeżanie**: Pobieranie świeżych danych z Google Sheets jednym kliknięciem (z lokalnym cache dla szybkości).
- **Eksport do HTML**: Jednym kliknięciem można wygenerować samodzielny plik HTML zawierający wszystkie kluczowe wykresy i podsumowania.
- **Inteligentny Cache**: Aplikacja wykorzystuje cache w formacie Feather, dzięki czemu ponowne uruchomienia są błyskawiczne.
- **Zgodność z Wytycznymi**: Logika klasyfikacji ciśnienia jest w pełni zgodna z aktualnymi standardami ESC/ESH.

## 🚀 Uruchomienie

1.  **Zainstaluj wymagane biblioteki:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Skonfiguruj źródło Google Sheets:**
    - Utwórz arkusz z kolumnami **`Data`, `Godzina`, `SYS`, `DIA`, `PUL`**.
    - W Google Cloud Console utwórz **Service Account**, pobierz klucz JSON i zapisz go jako `google_credentials.json` w głównym folderze projektu.
    - Udostępnij arkusz adresowi e-mail konta serwisowego (tryb „Editor”).
    - Skopiuj URL arkusza i ustaw `GOOGLE_SHEET_URL` oraz `WORKSHEET_NAME` w `config.py`.

3.  **Uruchom aplikację:**
    ```bash
    python app.py
    ```

4.  **Otwórz przeglądarkę:**
    Przejdź pod adres [http://127.0.0.1:8050](http://127.0.0.1:8050).

## 📁 Struktura i Przeznaczenie Plików

Projekt jest podzielony na logiczne moduły, co ułatwia nawigację i rozwój.

-   **`app.py`**: Główny plik startowy. Jego jedynym zadaniem jest inicjalizacja wszystkich modułów i uruchomienie aplikacji. Nie zawiera logiki biznesowej.
-   **`config.py`**: Centralny plik konfiguracyjny. Tutaj zdefiniowane są wszystkie stałe, takie jak nazwy plików, progi ciśnienia, kolory wykresów itp.
-   **`data_processing.py`**: Moduł odpowiedzialny za wczytywanie, czyszczenie i przetwarzanie danych. To tutaj odbywa się klasyfikacja ciśnienia i obliczanie dodatkowych wskaźników.
-   **`requirements.txt`**: Lista wszystkich zależności projektu.

## 🔐 Przepływ Google Sheets (krok po kroku)

1. **Autoryzacja** – plik `google_credentials.json` (klucz konta serwisowego) jest wczytywany przez `gspread.service_account`. Nie commituj tego pliku do repozytorium! 
2. **Dostęp do arkusza** – adres e-mail konta serwisowego musi mieć uprawnienia „Editor” do dokumentu wskazanego w `GOOGLE_SHEET_URL`/`WORKSHEET_NAME`.
3. **Pobranie danych** – `get_as_dataframe` z `gspread_dataframe` pobiera dane wraz z formułami (ustaw `evaluate_formulas=True`).
4. **Cache** – wynik zapisywany jest lokalnie w `DATA_CACHE_FILE` na czas `DATA_CACHE_TTL_MINUTES`, dzięki czemu UI reaguje szybciej przy częstych odświeżeniach.
5. **Limit API** – Google Sheets dopuszcza ok. 60 żądań/min na projekt; cache i przycisk „⏭️ Odśwież bez cache” pomagają kontrolować ruch.

## ⚠️ Typowe błędy i jak je diagnozować

| Komunikat | Co oznacza? | Jak naprawić |
| --- | --- | --- |
| `❌ Błąd: Nie znaleziono arkusza Google` | URL w `config.py` jest błędny albo konto nie ma dostępu | Zweryfikuj `GOOGLE_SHEET_URL`, udostępnij arkusz kontu serwisowemu |
| `❌ Brakujące kolumny: ...` | Arkusz nie posiada wymaganych nagłówków | Dodaj kolumny `Data`, `Godzina`, `SYS`, `DIA`, `PUL` |
| `⚠️ ... Pokazuję dane z cache sprzed ...` | API zwróciło błąd, ale istnieje ostatni cache | Napraw przyczynę (np. quota), możesz wymusić odświeżenie przyciskiem „⏭️” |
| `json.decoder.JSONDecodeError` w konsoli | Plik `google_credentials.json` ma zły format | Pobierz klucz ponownie i upewnij się, że zapis jest kompletny |

### Moduły Aplikacji

-   **`charts/`**: Ten folder zawiera wszystkie funkcje generujące wykresy. Każdy plik `.py` odpowiada za jeden typ wykresu (np. `trend.py`, `heatmap.py`).
-   **`layouts/`**: Odpowiada za strukturę wizualną aplikacji. `tabs.py` definiuje wygląd poszczególnych zakładek i składa je w jedną całość.
-   **`callbacks/`**: Serce interaktywności aplikacji. `callbacks.py` zawiera wszystkie funkcje, które reagują na działania użytkownika (np. kliknięcia przycisków, zmiany w menu).

## 📊 Dostępne Analizy (Zakładki)

1.  **Podsumowanie**: Kluczowe wskaźniki (KPI), takie jak średnie wartości, najwyższy pomiar i procent pomiarów w normie, a także wykres kołowy z procentowym udziałem poszczególnych kategorii ciśnienia.
2.  **Klasyfikacja**: Wykres słupkowy pokazujący, ile pomiarów wpada do każdej z oficjalnych kategorii ciśnienia wg ESC/ESH.
3.  **Macierz**: Wizualizacja pomiarów na tle siatki kategorii ciśnienia, co pozwala na szybką ocenę każdego punktu.
4.  **Trend**: Wykres liniowy przedstawiający zmiany ciśnienia (SYS, DIA) i pulsu (PUL) w czasie.
5.  **Rytm dobowy**: Średnie wartości ciśnienia w poszczególnych godzinach doby, z możliwością animacji 7-dniowego okna kroczącego.
6.  **Analiza Hemodynamiczna**: Wykres trendu dla Ciśnienia Tętna (PP) i Średniego Ciśnienia Tętniczego (MAP).
7.  **Korelacje**: Wykres punktowy zależności między ciśnieniem skurczowym a rozkurczowym, gdzie kolor punktów reprezentuje puls.
8.  **Heatmapa**: Mapa cieplna średnich wartości ciśnienia skurczowego w zależności od dnia tygodnia i godziny.
9.  **Porównanie**: Wykresy skrzypcowe (violin plots) pozwalające na porównanie rozkładów ciśnienia w różnych grupach (np. w dni robocze vs. weekendy).
10. **Rozkład**: Histogramy pokazujące rozkład wartości dla SYS, DIA i PUL.

## 🛠️ Rozwój i Personalizacja

Dzięki modularnej architekturze, dodawanie nowych funkcji jest proste i szybkie.

### Jak dodać nową zakładkę?

1.  **Stwórz nowy wykres**: Dodaj plik np. `charts/nowy_wykres.py` z funkcją `generate_nowy_wykres(df)`.
2.  **Zarejestruj wykres**: Zaimportuj nową funkcję w `charts/__init__.py`.
3.  **Dodaj wykres do layoutu**: W `layouts/tabs.py` stwórz funkcję `create_nowa_zakladka()` i dodaj ją do listy zakładek.
4.  **Dodaj callback**: W `callbacks/callbacks.py` dodaj callback, który będzie aktualizował Twój nowy wykres, gdy dane się zmienią.
5.  **Zainicjalizuj w `app.py`**: Dodaj wywołanie nowej funkcji generującej wykres w `app.py`, aby pojawił się on przy starcie.

## 📄 Licencja

Projekt jest dostępny na licencji MIT.
