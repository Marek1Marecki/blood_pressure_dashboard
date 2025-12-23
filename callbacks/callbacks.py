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
import logging
from collections import OrderedDict
import pandas as pd
from functools import lru_cache
from io import StringIO
from dash import callback, Input, Output, State, no_update

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
from config import EXPORT_CHART_DEFINITIONS, KOLORY_ESC

logger = logging.getLogger(__name__)


@lru_cache(maxsize=16)
def _parse_store_cached(raw_json: str) -> pd.DataFrame:
    """Cache-aware parser for data stored in dcc.Store."""
    df = pd.read_json(StringIO(raw_json), orient='split')

    # Konwertuj kolumnę Datetime z powrotem na datetime, jeśli istnieje
    if 'Datetime' in df.columns:
        df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')

    # Konwertuj kolumnę Data z powrotem na datetime, jeśli istnieje
    if 'Data' in df.columns:
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

    return df

def parse_store(stored_data):
    """Safely parse JSON payload shared between callbacks and reuse cache."""
    if not stored_data:
        return None
    try:
        # Return shallow copy so downstream code can't mutate cached frame
        return _parse_store_cached(stored_data).copy()
    except ValueError:
        return None

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
    # CALLBACK: Odświeżanie danych (centralne miejsce pobierania danych)
    # =========================================================================
    @callback(
        Output('data-store', 'data'),
        Output('status-output', 'children'),
        Input('refresh-button', 'n_clicks'),
        Input('refresh-bypass-button', 'n_clicks'),
        prevent_initial_call=True  # ← KLUCZOWE: Nie uruchamiaj przy starcie
    )
    def refresh_data(n_clicks_regular, n_clicks_bypass):
        """Callback odświeżający dane po kliknięciu przycisku.

        Ta funkcja jest wywoływana po kliknięciu przycisku "Odśwież dane"
        lub "Odśwież bez cache". Jej zadaniem jest ponowne wczytanie i
        przetworzenie danych z Google Sheets, a następnie zaktualizowanie
        centralnego magazynu danych (`dcc.Store`) oraz komunikatu o statusie.

        Args:
            n_clicks_regular (int): Liczba kliknięć przycisku standardowego.
            n_clicks_bypass (int): Liczba kliknięć wymuszających pominięcie cache.

        Returns:
            tuple[str, str]: Krotka zawierająca:
                - zaktualizowane dane w formacie JSON,
                - nowy komunikat o statusie operacji.
        """
        try:
            force_refresh = bool(n_clicks_bypass)
            df, status = wczytaj_i_przetworz_dane(project_root_path, force_refresh=force_refresh)
            return df.to_json(date_format='iso', orient='split'), status
        except Exception as exc:  # noqa: BLE001 - logujemy i sygnalizujemy błąd w UI
            logger.exception("Błąd odświeżania danych")
            return no_update, f"❌ Błąd: {exc}"


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

        df = parse_store(stored_data)
        if df is None:
            return "B/D", "B/D", "B/D", "B/D", {}
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

        df = parse_store(stored_data)
        if df is None:
            return {}
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

        df = parse_store(stored_data)
        if df is None:
            return {}
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

        df = parse_store(stored_data)
        if df is None:
            return {}
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

        df = parse_store(stored_data)
        if df is None:
            return {}
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

        df = parse_store(stored_data)
        if df is None:
            return {}
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

        df = parse_store(stored_data)
        if df is None:
            return {}
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

        df = parse_store(stored_data)
        if df is None:
            return {}
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

        df = parse_store(stored_data)
        if df is None:
            return {}
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

        df = parse_store(stored_data)
        if df is None:
            return {}
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
            df = parse_store(stored_data)
            if df is None or df.empty:
                return "❌ Brak danych do wyeksportowania"

            chart_definitions = [
                ("01_Podsumowanie_klasyfikacji", "Podstawowe Analizy", True,
                 lambda frame: generate_summary_data(frame)[4]),
                ("02_Klasyfikacja_ESC_wykres", "Podstawowe Analizy", False,
                 lambda frame: generate_esc_category_bar_chart(frame)),
                ("03_Macierz_klasyfikacji", "Podstawowe Analizy", True,
                 lambda frame: generate_classification_matrix_chart(frame)),
                ("04_Trend_w_czasie", "Podstawowe Analizy", True,
                 lambda frame: generate_trend_chart(frame)),
                ("05_Rytm_dobowy", "Podstawowe Analizy", True,
                 lambda frame: generate_circadian_rhythm_chart(frame)),
                ("06_Analiza_hemodynamiczna", "Analizy Zaawansowane", True,
                 lambda frame: generate_hemodynamics_chart(frame)),
                ("07_Korelacja_SYS_DIA_PUL", "Analizy Zaawansowane", True,
                 lambda frame: generate_correlation_chart(frame)),
                ("08_Heatmapa_dzien_godzina", "Analizy Zaawansowane", True,
                 lambda frame: generate_heatmap_chart(frame)),
                ("09_Porownanie_godziny_VIOLIN", "Porównania Okresów (Violin Plots)", True,
                 lambda frame: generate_comparison_chart(frame, 'Godzina Pomiaru', 'violin')),
                ("10_Porownanie_dzien_roboczy_VIOLIN", "Porównania Okresów (Violin Plots)", True,
                 lambda frame: generate_comparison_chart(frame, 'Typ Dnia', 'violin')),
                ("11_Histogram_SYS", "Rozkłady Parametrów", True,
                 lambda frame: generate_histogram_chart(frame, 'SYS')),
                ("12_Histogram_DIA", "Rozkłady Parametrów", True,
                 lambda frame: generate_histogram_chart(frame, 'DIA')),
                ("13_Histogram_Puls", "Rozkłady Parametrów", True,
                 lambda frame: generate_histogram_chart(frame, 'PUL')),
            ]

            wykresy = {}
            sekcje = OrderedDict()

            for chart_id, section, enabled, builder in chart_definitions:
                if not enabled:
                    continue
                figure = builder(df)
                if figure is None:
                    continue
                wykresy[chart_id] = figure
                if section not in sekcje:
                    sekcje[section] = []
                sekcje[section].append(chart_id)

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
                f.write('body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; color: #333; }')
                f.write('@page { size: A4; margin: 1.5cm; }')
                f.write('.page { page-break-after: always; padding: 20px; box-sizing: border-box; }')
                f.write('.page:last-child { page-break-after: auto; }')
                f.write('h1 { text-align: center; color: #2c3e50; margin-bottom: 10px; }')
                f.write('.chart-container { margin: 20px 0; background: white; padding: 20px; ')
                f.write('border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); page-break-inside: avoid; }')
                f.write('.info { text-align: center; color: #666; font-size: 14px; margin: 10px 0; }')
                f.write('.section-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); ')
                f.write('color: white; padding: 15px; margin: 20px 0; border-radius: 10px; ')
                f.write('text-align: center; font-size: 1.3em; font-weight: bold; page-break-after: avoid; }')
                f.write('.chart-title { color: #2c3e50; font-size: 1.1em; margin: 15px 0; ')
                f.write('text-align: center; font-weight: 600; }')
                f.write('.guidelines-table { width: 100%; border-collapse: collapse; margin: 20px 0; ')
                f.write('box-shadow: 0 2px 8px rgba(0,0,0,0.1); background: white; page-break-inside: avoid; }')
                f.write('.guidelines-table th { background: #f8f9fa; padding: 12px; ')
                f.write('border-bottom: 2px solid #ddd; font-weight: bold; text-align: left; }')
                f.write('.guidelines-table td { padding: 10px 12px; border-bottom: 1px solid #eee; }')
                f.write('.guidelines-table tr:last-child td { border-bottom: none; }')
                f.write('.guidelines-header { text-align: center; color: #2c3e50; ')
                f.write('margin: 20px 0; font-size: 1.5em; font-weight: bold; }')
                f.write('.note-box { margin: 20px 0; padding: 15px; background: #fff3cd; ')
                f.write('border-left: 4px solid #ffc107; border-radius: 5px; page-break-inside: avoid; }')
                
                # Style dla druku
                f.write('@media print {')
                f.write('  body { background: white; -webkit-print-color-adjust: exact; print-color-adjust: exact; }')
                f.write('  .chart-container { box-shadow: none; border: 1px solid #eee; }')
                f.write('  .page { margin: 0; padding: 0; }')
                f.write('  .section-header { -webkit-print-color-adjust: exact; print-color-adjust: exact; }')
                f.write('  .note-box { -webkit-print-color-adjust: exact; print-color-adjust: exact; }')
                f.write('  .no-print { display: none !important; }')
                f.write('  @page { margin: 1.5cm; }')
                f.write('}')
                f.write('</style>')
                f.write('</head><body>')

                # Strona tytułowa
                f.write('<div class="page">')
                f.write('<h1>💓 Dashboard Pomiarów Ciśnienia Krwi</h1>')
                f.write(f'<p class="info">Wygenerowano: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>')
                f.write(f'<p class="info">Liczba pomiarów: <strong>{len(df)}</strong> | ')
                f.write(f'Zakres dat: <strong>{df["Data"].min().strftime("%Y-%m-%d")} - {df["Data"].max().strftime("%Y-%m-%d")}</strong></p>')
                f.write('</div>')

                # Strona z wytycznymi
                f.write('<div class="page">')
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
                f.write('</div>')

                # Grupowanie wykresów według sekcji
                for sekcja_nazwa, sekcja_wykresy in sekcje.items():
                    f.write(f'<div class="page">')  # Nowa strona dla każdej sekcji
                    f.write(f'<div class="section-header">📊 {sekcja_nazwa}</div>')

                    for wykres_key in sekcja_wykresy:
                        wykres = wykresy[wykres_key]
                        wykres_nazwa = wykres_key.split('_', 1)[1].replace('_', ' ').title()

                        f.write('<div class="chart-container">')
                        f.write(f'<div class="chart-title">{wykres_nazwa}</div>')
                        f.write(wykres.to_html(
                            full_html=False,
                            include_plotlyjs='cdn',
                            config={'responsive': True, 'displayModeBar': False}  # Wyłączony pasek w druku
                        ))
                        f.write('</div>')
                    
                    f.write('</div>')

                # Stopka na osobnej stronie
                f.write('<div class="page" style="text-align: center; padding-top: 2cm;">')
                f.write('<hr style="margin: 20px auto; max-width: 80%; border: none; border-top: 1px solid #ddd;">')
                f.write('<p class="info">📋 Dashboard zgodny z aktualnymi wytycznymi ESC/ESH</p>')
                f.write('<p class="info" style="font-size: 12px; color: #999;">Wygenerowano przez Blood Pressure Dashboard v2.0</p>')
                f.write('</div>')
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

        df = parse_store(stored_data)
        if df is None:
            return {}
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

        df = parse_store(stored_data)
        if df is None:
            return 0, {0: 'Brak danych'}
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

        df = parse_store(stored_data)
        if df is None:
            return {}
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