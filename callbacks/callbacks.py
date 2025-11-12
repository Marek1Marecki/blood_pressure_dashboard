"""Moduł odpowiedzialny za rejestrację i definicję wszystkich callbacków.

Ten plik centralizuje logikę interaktywności aplikacji Dash.
Callbacki to funkcje, które są automatycznie wywoływane przez Dash
w odpowiedzi na interakcje użytkownika, takie jak kliknięcie przycisku,
wybór opcji z menu, czy zmiana wartości na suwaku.

Główne zadania tego modułu to:
- Aktualizacja danych w aplikacji po kliknięciu przycisku "Odśwież".
- Dynamiczne odświeżanie wszystkich wykresów, gdy dane ulegną zmianie.
- Obsługa interaktywnych komponentów, np. przełączników w zakładkach.
- Realizacja eksportu danych i wykresów do pliku HTML.
"""

import os
import datetime
import pandas as pd
from io import StringIO
from dash import callback, Input, Output, State, no_update

from config import NAZWA_PLIKU_EXCEL
from data_processing import wczytaj_i_przetworz_dane
from charts import (
    generate_trend_chart,
    generate_circadian_rhythm_chart,
    generate_correlation_chart,
    generate_heatmap_chart,
    generate_histogram_chart,
    generate_classification_matrix_chart,
    generate_esc_category_bar_chart,
    generate_comparison_chart,
    generate_summary_data,
    generate_hemodynamics_chart
)


def register_callbacks(app, project_root_path):
    """Rejestruje wszystkie callbacki aplikacji Dash.

    Ta funkcja jest centralnym punktem, w którym wszystkie dynamiczne
    interakcje aplikacji są definiowane i przypisywane do layoutu.
    Zawiera ona zagnieżdżone definicje funkcji callbacków, co jest
    praktyką pozwalającą na hermetyzację logiki i zachowanie czystości
    globalnej przestrzeni nazw.

    Args:
        app (dash.Dash): Główna instancja aplikacji Dash, do której
            callbacki zostaną zarejestrowane.
        project_root_path (str): Ścieżka do głównego folderu projektu,
            konieczna do prawidłowego lokalizowania pliku z danymi
            podczas operacji odświeżania.
    """

    # =========================================================================
    # CALLBACK: Odświeżanie danych z pliku (JEDYNE MIEJSCE gdzie wczytujemy plik)
    # =========================================================================
    @callback(
        Output('data-store', 'data'),
        Output('status-output', 'children'),
        Input('refresh-button', 'n_clicks'),
        prevent_initial_call=True  # ← KLUCZOWE: Nie uruchamiaj przy starcie
    )
    def refresh_data(n_clicks):
        """Callback odświeżający dane po kliknięciu przycisku.

        Ta funkcja jest wywoływana po kliknięciu przycisku "Odśwież dane".
        Jej zadaniem jest ponowne wczytanie i przetworzenie danych
        z pliku Excel, a następnie zaktualizowanie centralnego magazynu
        danych (`dcc.Store`) oraz komunikatu o statusie.

        Args:
            n_clicks (int): Liczba kliknięć przycisku. Parametr ten jest
                potrzebny do wyzwolenia callbacku, ale jego wartość
                nie jest używana.

        Returns:
            tuple[str, str]: Krotka zawierająca:
                - zaktualizowane dane w formacie JSON,
                - nowy komunikat o statusie operacji.
        """
        df, status = wczytaj_i_przetworz_dane(project_root_path)
        return df.to_json(date_format='iso', orient='split'), status


    # =========================================================================
    # CALLBACK: Aktualizacja zakładki podsumowania
    # =========================================================================
    @callback(
        Output('kpi-avg-sys', 'children'),
        Output('kpi-avg-dia', 'children'),
        Output('kpi-max-reading', 'children'),
        Output('kpi-norm-percent', 'children'),
        Output('graph-classification-pie', 'figure'),
        Input('data-store', 'data'),
        prevent_initial_call=True  # ← Wykresy już są w initial_figures
    )
    def update_summary(stored_data):
        """Callback aktualizujący zakładkę podsumowania.

        Wywoływany, gdy dane w `dcc.Store` ulegną zmianie.
        Pobiera zaktualizowane dane, przelicza kluczowe wskaźniki (KPI)
        oraz generuje nowy wykres kołowy, a następnie odświeża
        odpowiednie komponenty w zakładce "Podsumowanie".

        Args:
            stored_data (str): Dane w formacie JSON pochodzące
                z `dcc.Store`.

        Returns:
            tuple: Krotka zawierająca zaktualizowane wartości dla KPI
                oraz nowy obiekt `go.Figure` dla wykresu kołowego.
        """
        if stored_data is None:
            return "B/D", "B/D", "B/D", "B/D", {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_summary_data(df)


    # =========================================================================
    # CALLBACK: Aktualizacja wykresu klasyfikacji ESC
    # =========================================================================
    @callback(
        Output('graph-esc-bar', 'figure'),
        Input('data-store', 'data'),
        prevent_initial_call=True  # ← Wykres już jest w initial_figures
    )
    def update_esc_bar(stored_data):
        """Callback aktualizujący wykres słupkowy klasyfikacji ESC.

        Wywoływany, gdy dane w `dcc.Store` ulegną zmianie.
        Generuje na nowo wykres słupkowy i aktualizuje komponent
        `dcc.Graph` w zakładce "Klasyfikacja".

        Args:
            stored_data (str): Dane w formacie JSON pochodzące
                z `dcc.Store`.

        Returns:
            go.Figure: Nowy obiekt wykresu Plotly.
        """
        if stored_data is None:
            return {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_esc_category_bar_chart(df)


    # =========================================================================
    # CALLBACK: Aktualizacja macierzy klasyfikacji
    # =========================================================================
    @callback(
        Output('graph-classification-matrix', 'figure'),
        Input('data-store', 'data'),
        prevent_initial_call=True  # ← Wykres już jest w initial_figures
    )
    def update_matrix(stored_data):
        """Callback aktualizujący macierz klasyfikacji.

        Wywoływany, gdy dane w `dcc.Store` ulegną zmianie.
        Generuje na nowo macierz klasyfikacji i aktualizuje komponent
        `dcc.Graph` w zakładce "Macierz".

        Args:
            stored_data (str): Dane w formacie JSON pochodzące
                z `dcc.Store`.

        Returns:
            go.Figure: Nowy obiekt wykresu Plotly.
        """
        if stored_data is None:
            return {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_classification_matrix_chart(df)


    # =========================================================================
    # CALLBACK: Aktualizacja wykresu trendu
    # =========================================================================
    @callback(
        Output('graph-trend', 'figure'),
        Input('data-store', 'data'),
        prevent_initial_call=True  # ← Wykres już jest w initial_figures
    )
    def update_trend(stored_data):
        """Callback aktualizujący wykres trendu w czasie.

        Wywoływany, gdy dane w `dcc.Store` ulegną zmianie.
        Generuje na nowo wykres trendu i aktualizuje komponent
        `dcc.Graph` w zakładce "Trend".

        Args:
            stored_data (str): Dane w formacie JSON pochodzące
                z `dcc.Store`.

        Returns:
            go.Figure: Nowy obiekt wykresu Plotly.
        """
        if stored_data is None:
            return {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_trend_chart(df)


    # =========================================================================
    # CALLBACK: Aktualizacja wykresu rytmu dobowego
    # =========================================================================
    @callback(
        Output('graph-hour', 'figure'),
        Input('data-store', 'data'),
        prevent_initial_call=True  # ← Wykres już jest w initial_figures
    )
    def update_circadian(stored_data):
        """Callback aktualizujący wykres rytmu dobowego.

        Wywoływany, gdy dane w `dcc.Store` ulegną zmianie.
        Generuje na nowo wykres rytmu dobowego i aktualizuje komponent
        `dcc.Graph` w zakładce "Rytm dobowy".

        Args:
            stored_data (str): Dane w formacie JSON pochodzące
                z `dcc.Store`.

        Returns:
            go.Figure: Nowy obiekt wykresu Plotly.
        """
        if stored_data is None:
            return {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_circadian_rhythm_chart(df)


    # =========================================================================
    # CALLBACK: Aktualizacja wykresu korelacji
    # =========================================================================
    @callback(
        Output('graph-scatter', 'figure'),
        Input('data-store', 'data'),
        prevent_initial_call=True  # ← Wykres już jest w initial_figures
    )
    def update_correlation(stored_data):
        """Callback aktualizujący wykres korelacji.

        Wywoływany, gdy dane w `dcc.Store` ulegną zmianie.
        Generuje na nowo wykres korelacji i aktualizuje komponent
        `dcc.Graph` w zakładce "Korelacje".

        Args:
            stored_data (str): Dane w formacie JSON pochodzące
                z `dcc.Store`.

        Returns:
            go.Figure: Nowy obiekt wykresu Plotly.
        """
        if stored_data is None:
            return {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_correlation_chart(df)


    # =========================================================================
    # CALLBACK: Aktualizacja heatmapy
    # =========================================================================
    @callback(
        Output('graph-heatmap', 'figure'),
        Input('data-store', 'data'),
        prevent_initial_call=True  # ← Wykres już jest w initial_figures
    )
    def update_heatmap(stored_data):
        """Callback aktualizujący heatmapę.

        Wywoływany, gdy dane w `dcc.Store` ulegną zmianie.
        Generuje na nowo heatmapę i aktualizuje komponent
        `dcc.Graph` w zakładce "Heatmapa".

        Args:
            stored_data (str): Dane w formacie JSON pochodzące
                z `dcc.Store`.

        Returns:
            go.Figure: Nowy obiekt wykresu Plotly.
        """
        if stored_data is None:
            return {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_heatmap_chart(df)


    # =========================================================================
    # CALLBACK: Aktualizacja wykresu hemodynamicznego
    # =========================================================================
    @callback(
        Output('graph-hemodynamics', 'figure'),
        Input('data-store', 'data'),
        prevent_initial_call=True  # ← Wykres już jest w initial_figures
    )
    def update_hemodynamics(stored_data):
        """Callback aktualizujący wykres analizy hemodynamicznej.

        Wywoływany, gdy dane w `dcc.Store` ulegną zmianie.
        Generuje na nowo wykres hemodynamiczny i aktualizuje komponent
        `dcc.Graph` w zakładce "Analiza Hemodynamiczna".

        Args:
            stored_data (str): Dane w formacie JSON pochodzące
                z `dcc.Store`.

        Returns:
            go.Figure: Nowy obiekt wykresu Plotly.
        """
        if stored_data is None:
            return {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_hemodynamics_chart(df)


    # =========================================================================
    # CALLBACK: Aktualizacja wykresu porównawczego
    # =========================================================================
    @callback(
        Output('graph-comparison', 'figure'),
        Input('boxplot-radio', 'value'),
        Input('data-store', 'data'),
        prevent_initial_call=True  # ← Wykres generowany w layouts/tabs.py
    )
    def update_comparison(category, stored_data):
        """Callback aktualizujący wykres porównawczy.

        Wywoływany, gdy zmianie ulegną dane w `dcc.Store` lub gdy
        użytkownik wybierze inną kategorię porównania za pomocą
        przycisków radiowych. Generuje na nowo wykres porównawczy
        (skrzypcowy) i aktualizuje odpowiedni komponent `dcc.Graph`.

        Args:
            category (str): Wybrana kategoria do porównania
                (np. 'Godzina Pomiaru' lub 'Typ Dnia').
            stored_data (str): Dane w formacie JSON z `dcc.Store`.

        Returns:
            go.Figure: Nowy obiekt wykresu Plotly.
        """
        if stored_data is None:
            return {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_comparison_chart(df, category, 'violin')


    # =========================================================================
    # CALLBACK: Aktualizacja histogramu
    # =========================================================================
    @callback(
        Output('graph-histogram', 'figure'),
        Input('histogram-radio', 'value'),
        Input('data-store', 'data'),
        prevent_initial_call=True  # ← Wykres już jest w initial_figures
    )
    def update_histogram(column, stored_data):
        """Callback aktualizujący histogram.

        Wywoływany, gdy zmianie ulegną dane w `dcc.Store` lub gdy
        użytkownik wybierze inny parametr do analizy za pomocą
        przycisków radiowych. Generuje na nowo histogram i aktualizuje
        odpowiedni komponent `dcc.Graph`.

        Args:
            column (str): Wybrany parametr do wizualizacji
                (np. 'SYS', 'DIA', 'PUL').
            stored_data (str): Dane w formacie JSON z `dcc.Store`.

        Returns:
            go.Figure: Nowy obiekt wykresu Plotly.
        """
        if stored_data is None:
            return {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_histogram_chart(df, column)


    # =========================================================================
    # CALLBACK: Eksport do HTML
    # =========================================================================
    @callback(
        Output('status-output', 'children', allow_duplicate=True),
        Input('export-button', 'n_clicks'),
        State('data-store', 'data'),
        prevent_initial_call=True
    )
    def export_html(n_clicks, stored_data):
        """Callback eksportujący wszystkie wykresy do pliku HTML.

        Wywoływany po kliknięciu przycisku "Eksport HTML".
        Funkcja ta generuje wszystkie zdefiniowane w konfiguracji wykresy,
        a następnie osadza je w jednym, samodzielnym pliku HTML.
        Plik ten zawiera również podstawowe informacje podsumowujące
        oraz tabelę z wytycznymi ciśnienia.

        Args:
            n_clicks (int): Liczba kliknięć przycisku. Parametr ten jest
                potrzebny do wyzwolenia callbacku, ale jego wartość
                nie jest używana.
            stored_data (str): Dane w formacie JSON z `dcc.Store`.

        Returns:
            str: Komunikat informujący o sukcesie lub błędzie operacji
                eksportu, który jest wyświetlany w komponencie statusu.
        """
        if stored_data is None or n_clicks is None:
            return "❌ Brak danych do wyeksportowania"

        try:
            df = pd.read_json(StringIO(stored_data), orient='split')
            if df.empty:
                return "❌ Brak danych do wyeksportowania"

            # =====================================================================
            # KONFIGURACJA EKSPORTU - łatwa edycja wykresów do eksportu
            # =====================================================================
            # Ustaw False dla wykresów, które NIE mają być eksportowane
            wykresy_config = {
                # Podstawowe wykresy
                'Podsumowanie_KPI': True,                    # Wykres kołowy klasyfikacji
                'Klasyfikacja_ESC': False,                    # Wykres słupkowy
                'Macierz_klasyfikacji': True,                # Macierz 2D
                'Trend_w_czasie': True,                      # Trend wszystkich parametrów
                'Rytm_dobowy': True,                         # Dobowy rytm ciśnienia
                'Analiza_hemodynamiczna': True,              # PP vs MAP
                'Korelacja_SYS_DIA': True,                   # Scatter SYS-DIA-PUL
                'Heatmapa': True,                            # Mapa cieplna

                # Porównania - tylko VIOLIN
                'Porownanie_godziny_violin': True,           # Violin plot - godziny
                'Porownanie_dzien_violin': True,             # Violin plot - dzień roboczy/weekend

                # Histogramy - WSZYSTKIE parametry
                'Histogram_SYS': True,                       # Rozkład SYS
                'Histogram_DIA': True,                       # Rozkład DIA
                'Histogram_PUL': True,                       # Rozkład pulsu
            }
            # =====================================================================

            # Generowanie wykresów (tylko te zaznaczone jako True)
            wykresy = {}

            # --- PODSTAWOWE WYKRESY ---
            if wykresy_config.get('Podsumowanie_KPI', False):
                _, _, _, _, fig_pie = generate_summary_data(df)
                wykresy['01_Podsumowanie_klasyfikacji'] = fig_pie

            if wykresy_config.get('Klasyfikacja_ESC', False):
                wykresy['02_Klasyfikacja_ESC_wykres'] = generate_esc_category_bar_chart(df)

            if wykresy_config.get('Macierz_klasyfikacji', False):
                wykresy['03_Macierz_klasyfikacji'] = generate_classification_matrix_chart(df)

            if wykresy_config.get('Trend_w_czasie', False):
                wykresy['04_Trend_w_czasie'] = generate_trend_chart(df)

            if wykresy_config.get('Rytm_dobowy', False):
                wykresy['05_Rytm_dobowy'] = generate_circadian_rhythm_chart(df)

            if wykresy_config.get('Analiza_hemodynamiczna', False):
                wykresy['06_Analiza_hemodynamiczna'] = generate_hemodynamics_chart(df)

            if wykresy_config.get('Korelacja_SYS_DIA', False):
                wykresy['07_Korelacja_SYS_DIA_PUL'] = generate_correlation_chart(df)

            if wykresy_config.get('Heatmapa', False):
                wykresy['08_Heatmapa_dzien_godzina'] = generate_heatmap_chart(df)

            # --- PORÓWNANIA - TYLKO VIOLIN ---
            if wykresy_config.get('Porownanie_godziny_violin', False):
                wykresy['09_Porownanie_godziny_VIOLIN'] = generate_comparison_chart(df, 'Godzina Pomiaru', 'violin')

            if wykresy_config.get('Porownanie_dzien_violin', False):
                wykresy['10_Porownanie_dzien_roboczy_VIOLIN'] = generate_comparison_chart(df, 'Typ Dnia', 'violin')

            # --- HISTOGRAMY - WSZYSTKIE PARAMETRY ---
            if wykresy_config.get('Histogram_SYS', False):
                wykresy['11_Histogram_SYS'] = generate_histogram_chart(df, 'SYS')

            if wykresy_config.get('Histogram_DIA', False):
                wykresy['12_Histogram_DIA'] = generate_histogram_chart(df, 'DIA')

            if wykresy_config.get('Histogram_PUL', False):
                wykresy['13_Histogram_Puls'] = generate_histogram_chart(df, 'PUL')

            if not wykresy:
                return "⚠️ Brak wykresów do eksportu - wszystkie są wyłączone w konfiguracji"

            # Tworzenie pliku HTML
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nazwa_pliku = f"Dashboard_Cisnienie_{timestamp}.html"

            with open(nazwa_pliku, 'w', encoding='utf-8') as f:
                f.write('<!DOCTYPE html>')
                f.write('<html><head>')
                f.write('<meta charset="utf-8">')
                f.write('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
                f.write('<title>Dashboard Ciśnienia Krwi (wg aktualnych wytycznych)</title>')
                f.write('<style>')
                f.write('body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }')
                f.write('h1 { text-align: center; color: #2c3e50; margin-bottom: 10px; }')
                f.write('.chart-container { margin: 30px auto; background: white; padding: 20px; ')
                f.write('border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 1200px; }')
                f.write('.info { text-align: center; color: #666; font-size: 14px; margin: 10px 0; }')
                f.write('.section-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); ')
                f.write('color: white; padding: 15px; margin: 40px auto 20px auto; border-radius: 10px; ')
                f.write('text-align: center; font-size: 1.3em; font-weight: bold; max-width: 1200px; ')
                f.write('box-shadow: 0 4px 6px rgba(0,0,0,0.1); }')
                f.write('.chart-title { color: #2c3e50; font-size: 0.9em; margin: 10px 0; ')
                f.write('text-align: center; font-weight: 600; }')
                f.write('.guidelines-table { width: 100%; max-width: 800px; margin: 30px auto; ')
                f.write('border-collapse: collapse; box-shadow: 0 2px 8px rgba(0,0,0,0.1); ')
                f.write('background: white; border-radius: 10px; overflow: hidden; }')
                f.write('.guidelines-table th { background: #f8f9fa; padding: 12px; ')
                f.write('border-bottom: 2px solid #ddd; font-weight: bold; text-align: left; }')
                f.write('.guidelines-table td { padding: 10px 12px; border-bottom: 1px solid #eee; }')
                f.write('.guidelines-table tr:last-child td { border-bottom: none; }')
                f.write('.guidelines-header { text-align: center; color: #2c3e50; ')
                f.write('margin: 40px 0 20px 0; font-size: 1.5em; font-weight: bold; }')
                f.write('.note-box { max-width: 800px; margin: 20px auto; padding: 15px; ')
                f.write('background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 5px; ')
                f.write('font-size: 13px; color: #666; font-style: italic; }')
                f.write('</style>')
                f.write('</head><body>')

                f.write('<h1>💓 Dashboard Pomiarów Ciśnienia Krwi</h1>')
                f.write(f'<p class="info">Wygenerowano: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>')
                f.write(f'<p class="info">Liczba pomiarów: <strong>{len(df)}</strong> | ')
                f.write(f'Zakres dat: <strong>{df["Datetime"].min().strftime("%Y-%m-%d")} - {df["Datetime"].max().strftime("%Y-%m-%d")}</strong></p>')

                # ===== TABELKA WYTYCZNYCH NA POCZĄTKU =====
                f.write('<h2 class="guidelines-header">📋 Aktualne Wytyczne Ciśnienia Tętniczego</h2>')
                f.write('<table class="guidelines-table">')
                f.write('<thead><tr>')
                f.write('<th>Kategoria</th>')
                f.write('<th>Ciśnienie skurczowe (SYS) [mmHg]</th>')
                f.write('<th>Ciśnienie rozkurczowe (DIA) [mmHg]</th>')
                f.write('</tr></thead>')
                f.write('<tbody>')

                # Import KOLORY_ESC z config
                from config import KOLORY_ESC

                kategorie_dane = [
                    ('Optymalne', '< 120', '< 70', KOLORY_ESC['Optymalne']),
                    ('Prawidłowe', '120-129', '70-79', KOLORY_ESC['Prawidłowe']),
                    ('Podwyższone', '130-139', '80-89', KOLORY_ESC['Podwyższone']),
                    ('Nadciśnienie 1°', '140-159', '90-99', KOLORY_ESC['Nadciśnienie 1°']),
                    ('Nadciśnienie 2°', '160-179', '100-109', KOLORY_ESC['Nadciśnienie 2°']),
                    ('Nadciśnienie 3°', '≥ 180', '≥ 110', KOLORY_ESC['Nadciśnienie 3°']),
                    ('Izolowane nadciśnienie skurczowe', '≥ 140', '< 90', KOLORY_ESC['Izolowane nadciśnienie skurczowe']),
                ]

                for kategoria, sys_val, dia_val, kolor in kategorie_dane:
                    f.write(f'<tr>')
                    f.write(f'<td style="font-weight: bold; color: {kolor};">{kategoria}</td>')
                    f.write(f'<td>{sys_val}</td>')
                    f.write(f'<td>{dia_val}</td>')
                    f.write(f'</tr>')

                f.write('</tbody></table>')

                # Notatka kliniczna
                f.write('<div class="note-box">')
                f.write('⚕️ <strong>Zasada klasyfikacji:</strong> Przy niejednoznacznych parach ')
                f.write('(np. SYS w jednej kategorii, DIA w innej) klasyfikacja następuje do wyższej kategorii.')
                f.write('</div>')

                # Grupowanie wykresów według sekcji
                sekcje = {
                    'Podstawowe Analizy': [
                        '01_Podsumowanie_klasyfikacji',
                        '02_Klasyfikacja_ESC_wykres',
                        '03_Macierz_klasyfikacji',
                        '04_Trend_w_czasie',
                        '05_Rytm_dobowy'
                    ],
                    'Analizy Zaawansowane': [
                        '06_Analiza_hemodynamiczna',
                        '07_Korelacja_SYS_DIA_PUL',
                        '08_Heatmapa_dzien_godzina'
                    ],
                    'Porównania Okresów (Violin Plots)': [
                        '09_Porownanie_godziny_VIOLIN',
                        '10_Porownanie_dzien_roboczy_VIOLIN'
                    ],
                    'Rozkłady Parametrów': [
                        '11_Histogram_SYS',
                        '12_Histogram_DIA',
                        '13_Histogram_Puls'
                    ]
                }

                for sekcja_nazwa, sekcja_wykresy in sekcje.items():
                    # Sprawdź czy są jakieś wykresy w tej sekcji
                    wykresy_w_sekcji = [w for w in sekcja_wykresy if w in wykresy]
                    if wykresy_w_sekcji:
                        f.write(f'<div class="section-header">📊 {sekcja_nazwa}</div>')

                        for wykres_key in wykresy_w_sekcji:
                            wykres = wykresy[wykres_key]
                            # Czytelna nazwa wykresu
                            wykres_nazwa = wykres_key.split('_', 1)[1].replace('_', ' ').title()

                            f.write('<div class="chart-container">')
                            f.write(f'<div class="chart-title">{wykres_nazwa}</div>')
                            f.write(wykres.to_html(
                                full_html=False,
                                include_plotlyjs='cdn',
                                config={'responsive': True, 'displayModeBar': True}
                            ))
                            f.write('</div>')

                f.write('<hr style="margin: 40px auto; max-width: 1200px; border: none; border-top: 2px solid #ddd;">')
                f.write('<p class="info">📋 Dashboard zgodny z aktualnymi wytycznymi ESC/ESH</p>')
                f.write('<p class="info" style="font-size: 12px; color: #999;">Wygenerowano przez Blood Pressure Dashboard v2.0</p>')
                f.write('</body></html>')

            liczba_wykresow = len(wykresy)
            return f"✅ Wyeksportowano {liczba_wykresow} wykresów do pliku: {nazwa_pliku}"

        except Exception as e:
            return f"❌ Błąd podczas eksportu: {e}"

    # =========================================================================
    # CALLBACK: Aktualizacja statycznego wykresu rytmu dobowego (gdy dane się zmieniają)
    # =========================================================================
    @callback(
        Output('graph-hour-static', 'figure'),
        Input('data-store', 'data'),
        prevent_initial_call=True  # ← Wykres już jest w initial_figures
    )
    def update_static_circadian_chart(stored_data):
        """Callback aktualizujący statyczny wykres rytmu dobowego.

        Wywoływany, gdy dane w `dcc.Store` ulegną zmianie.
        Zapewnia, że statyczna wersja wykresu rytmu dobowego jest
        zawsze aktualna w tle, nawet gdy użytkownik ma włączony
        widok animowany.

        Args:
            stored_data (str): Dane w formacie JSON z `dcc.Store`.

        Returns:
            go.Figure: Nowy obiekt wykresu Plotly.
        """
        if stored_data is None:
            return {}
        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_circadian_rhythm_chart(df)  # Wywołanie bez dat generuje widok statyczny

    # =========================================================================
    # CALLBACKI: Logika zakładki Rytm Dobowy (przełączanie i animacja)
    # =========================================================================

    @callback(
        Output('static-circadian-container', 'style'),
        Output('animated-circadian-container', 'style'),
        Input('circadian-mode-radio', 'value')
    )
    def toggle_circadian_view(mode):
        """Callback przełączający widok między statycznym a animowanym.

        Zmienia styl `display` kontenerów w zakładce "Rytm dobowy",
        aby pokazać wybrany przez użytkownika tryb (statyczny lub
        animowany) i ukryć drugi.

        Args:
            mode (str): Wartość wybrana w `dcc.RadioItems`
                ('static' lub 'animated').

        Returns:
            tuple[dict, dict]: Dwa słowniki stylów CSS, jeden dla
                kontenera statycznego, drugi dla animowanego.
        """
        if mode == 'animated':
            return {'display': 'none'}, {'display': 'block'}
        else:
            return {'display': 'block'}, {'display': 'none'}

    @callback(
        Output('day-slider', 'max'),
        Output('day-slider', 'marks'),
        Input('data-store', 'data'),
        prevent_initial_call=True  # ← Dane już są w initial_df_json
    )
    def update_day_slider_options(stored_data):
        """Callback aktualizujący opcje suwaka animacji.

        Wywoływany, gdy dane w `dcc.Store` ulegną zmianie.
        Oblicza dostępny zakres dat dla animacji (wymagane jest
        minimum 7 dni danych) i konfiguruje maksymalną wartość
        oraz etykiety suwaka.

        Args:
            stored_data (str): Dane w formacie JSON z `dcc.Store`.

        Returns:
            tuple[int, dict]: Krotka zawierająca:
                - maksymalną wartość dla suwaka,
                - słownik etykiet dla suwaka.
        """
        if stored_data is None:
            return 0, {0: 'Brak danych'}

        df = pd.read_json(StringIO(stored_data), orient='split')
        unique_days = sorted(df['Datetime'].dt.date.unique())

        # Animacja jest możliwa tylko jeśli mamy co najmniej 7 dni
        if len(unique_days) < 7:
            return 0, {0: 'Potrzeba min. 7 dni'}

        # Suwak będzie iterował po możliwych datach końcowych okna
        possible_end_dates = unique_days[6:]
        max_val = len(possible_end_dates) - 1

        # Tworzenie etykiet - pokazujemy co piątą dla czytelności
        marks = {i: date.strftime('%d.%m') for i, date in enumerate(possible_end_dates) if i % 5 == 0 or i == max_val}

        return max_val, marks

    @callback(
        Output('graph-hour-animated', 'figure'),
        Input('day-slider', 'value'),
        State('data-store', 'data')
    )
    def update_animated_chart_on_slide(slider_value, stored_data):
        """Callback aktualizujący animowany wykres rytmu dobowego.

        Wywoływany, gdy wartość suwaka animacji ulegnie zmianie.
        Określa 7-dniowe okno danych na podstawie aktualnej pozycji
        suwaka i generuje dla niego wykres rytmu dobowego.

        Args:
            slider_value (int): Aktualna wartość suwaka.
            stored_data (str): Dane w formacie JSON z `dcc.Store`.

        Returns:
            go.Figure: Nowy obiekt wykresu Plotly dla wybranego okna
                czasowego.
        """
        if stored_data is None:
            return {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        unique_days = sorted(df['Datetime'].dt.date.unique())

        if len(unique_days) < 7:
            from charts.utils import utworz_pusty_wykres
            return utworz_pusty_wykres("Potrzeba min. 7 dni do animacji")

        possible_end_dates = unique_days[6:]

        # Upewnij się, że wartość suwaka jest w zakresie
        if slider_value >= len(possible_end_dates):
            slider_value = len(possible_end_dates) - 1

        end_date = possible_end_dates[slider_value]
        start_date = unique_days[slider_value]  # Indeks startowy okna

        return generate_circadian_rhythm_chart(df, start_date=start_date, end_date=end_date)

    @callback(
        Output('animation-interval', 'disabled'),
        Input('play-button', 'n_clicks'),
        Input('pause-button', 'n_clicks'),
    )
    def toggle_animation_interval(play_clicks, pause_clicks):
        """Callback włączający/wyłączający interwał animacji.

        Zarządza stanem komponentu `dcc.Interval` na podstawie
        interakcji z przyciskami "Play" i "Pause".

        Args:
            play_clicks (int): Liczba kliknięć przycisku "Play".
            pause_clicks (int): Liczba kliknięć przycisku "Pause".

        Returns:
            bool: `True`, aby wyłączyć interwał (pauza),
                  `False`, aby go włączyć (odtwarzanie).
        """
        from dash import ctx
        if not ctx.triggered_id: return True
        return ctx.triggered_id == 'pause-button'

    @callback(
        Output('day-slider', 'value'),
        Input('animation-interval', 'n_intervals'),
        State('day-slider', 'value'),
        State('day-slider', 'max'),
    )
    def advance_slider(n_intervals, current_value, max_value):
        """Callback automatycznie przesuwający suwak animacji.

        Wywoływany cyklicznie przez aktywny `dcc.Interval`.
        Inkrementuje wartość suwaka, a po dojściu do końca
        resetuje go do początku, tworząc pętlę animacji.

        Args:
            n_intervals (int): Liczba wywołań interwału.
            current_value (int): Aktualna pozycja suwaka.
            max_value (int): Maksymalna wartość suwaka.

        Returns:
            int: Nowa wartość suwaka.
        """
        if n_intervals == 0 or current_value is None: return no_update
        new_value = current_value + 1
        return 0 if new_value > max_value else new_value


    # =========================================================================
    # CALLBACK: Dynamiczne dodawanie stylów CSS (clientside)
    # =========================================================================
    # Dodanie stylów CSS dla KPI i tabelki
    app.clientside_callback(
        """
        function(n) {
            if (document.getElementById('dynamic-styles')) { return ''; }
            const style = document.createElement('style');
            style.id = 'dynamic-styles';
            style.innerHTML = `
                /* Style dla kafelków KPI */
                .kpi-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; border-radius: 15px; padding: 20px; margin: 10px; text-align: center; min-width: 220px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); transition: transform 0.3s, box-shadow 0.3s; color: white; }
                .kpi-card:hover { transform: translateY(-5px); box-shadow: 0 15px 30px rgba(0,0,0,0.2); }
                .kpi-card h5 { color: rgba(255, 255, 255, 0.9); margin-bottom: 10px; font-size: 1em; text-transform: uppercase; letter-spacing: 1px; }
                .kpi-card h3 { color: white; margin: 0; font-size: 2.5em; font-weight: bold; }

                /* Kolory kafelków */
                .kpi-card:nth-child(1) { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); } /* Średnie SYS */
                .kpi-card:nth-child(2) { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); } /* Średnie DIA */
                .kpi-card:nth-child(3) { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); } /* Najwyższy pomiar */
                .kpi-card:nth-child(4) { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); } /* % w normie */

                /* Style dla tabelki z wytycznymi */
                .guidelines-table { width: 100%; border-collapse: collapse; margin-top: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .guidelines-table th { padding: 10px; border-bottom: 2px solid #ddd; font-weight: bold; font-size: 0.9em; background-color: #f8f9fa; text-align: left;}
                .guidelines-table td { padding: 8px 10px; border-bottom: 1px solid #eee; font-size: 0.85em; }
                .note-box { font-size: 11px; color: #666; font-style: italic; margin-top: 10px; padding: 10px; background-color: #fff3cd; border-left: 3px solid #ffc107; border-radius: 5px; }
            `;
            document.head.appendChild(style);
            return '';
        }
        """,
        Output('status-output', 'className'),
        Input('status-output', 'children')
    )