# 💓 Dashboard do Analizy Ciśnienia Krwi

Interaktywny dashboard do wizualizacji i analizy pomiarów ciśnienia krwi, zbudowany w oparciu o biblioteki Dash i Plotly. Aplikacja jest w pełni zgodna z najnowszymi wytycznymi Europejskiego Towarzystwa Kardiologicznego (ESC/ESH).

![przykład](https://i.imgur.com/example.png)

## 🌟 Główne Funkcje

- **Pełna Modularyzacja**: Kod został podzielony na logiczne moduły (dane, wykresy, layout, callbacki), co sprawia, że jest niezwykle czytelny, łatwy w utrzymaniu i rozbudowie.
- **Interaktywne Wykresy**: 9 różnych zakładek analitycznych, które pozwalają na dogłębną analizę danych pod różnymi kątami.
- **Automatyczne Odświeżanie**: Możliwość ponownego wczytania danych z pliku Excel bez restartowania aplikacji.
- **Eksport do HTML**: Jednym kliknięciem można wygenerować samodzielny plik HTML zawierający wszystkie kluczowe wykresy i podsumowania.
- **Inteligentny Cache**: Aplikacja wykorzystuje cache w formacie Feather, dzięki czemu ponowne uruchomienia są błyskawiczne.
- **Zgodność z Wytycznymi**: Logika klasyfikacji ciśnienia jest w pełni zgodna z aktualnymi standardami ESC/ESH.

## 🚀 Uruchomienie

1.  **Zainstaluj wymagane biblioteki:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Przygotuj plik z danymi:**
    - Upewnij się, że w głównym folderze projektu znajduje się plik `Pomiary_SYS_DIA.xlsx`.
    - Plik musi zawierać kolumny: `Data`, `Godzina`, `SYS`, `DIA`, `PUL`.

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
