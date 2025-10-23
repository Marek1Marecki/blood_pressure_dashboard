"""
Definicje wszystkich callbacków aplikacji
"""

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
    generate_summary_data
)


def register_callbacks(app, initial_df):
    """
    Rejestruje wszystkie callbacki aplikacji.

    Args:
        app: Instancja aplikacji Dash
        initial_df: Początkowy DataFrame (dla fallbacku)
    """

    # =========================================================================
    # CALLBACK: Odświeżanie danych z pliku
    # =========================================================================
    @callback(
        Output('data-store', 'data'),
        Output('status-output', 'children'),
        Input('refresh-button', 'n_clicks')
    )
    def refresh_data(n_clicks):
        """Odświeża dane z pliku Excel."""
        if n_clicks is None:
            return no_update, no_update

        df, status = wczytaj_i_przetworz_dane(NAZWA_PLIKU_EXCEL)
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
        Input('data-store', 'data')
    )
    def update_summary(stored_data):
        """Aktualizuje zakładkę podsumowania (KPI + wykres kołowy)."""
        if stored_data is None:
            return "B/D", "B/D", "B/D", "B/D", {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_summary_data(df)

    # =========================================================================
    # CALLBACK: Aktualizacja wykresu klasyfikacji ESC
    # =========================================================================
    @callback(
        Output('graph-esc-bar', 'figure'),
        Input('data-store', 'data')
    )
    def update_esc_bar(stored_data):
        """Aktualizuje wykres słupkowy klasyfikacji ESC."""
        if stored_data is None:
            return {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_esc_category_bar_chart(df)

    # =========================================================================
    # CALLBACK: Aktualizacja macierzy klasyfikacji
    # =========================================================================
    @callback(
        Output('graph-classification-matrix', 'figure'),
        Input('data-store', 'data')
    )
    def update_matrix(stored_data):
        """Aktualizuje macierz klasyfikacji."""
        if stored_data is None:
            return {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_classification_matrix_chart(df)

    # =========================================================================
    # CALLBACK: Aktualizacja wykresu trendu
    # =========================================================================
    @callback(
        Output('graph-trend', 'figure'),
        Input('data-store', 'data')
    )
    def update_trend(stored_data):
        """Aktualizuje wykres trendu w czasie."""
        if stored_data is None:
            return {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_trend_chart(df)

    # =========================================================================
    # CALLBACK: Aktualizacja wykresu rytmu dobowego
    # =========================================================================
    @callback(
        Output('graph-hour', 'figure'),
        Input('data-store', 'data')
    )
    def update_circadian(stored_data):
        """Aktualizuje wykres rytmu dobowego."""
        if stored_data is None:
            return {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_circadian_rhythm_chart(df)

    # =========================================================================
    # CALLBACK: Aktualizacja wykresu korelacji
    # =========================================================================
    @callback(
        Output('graph-scatter', 'figure'),
        Input('data-store', 'data')
    )
    def update_correlation(stored_data):
        """Aktualizuje wykres korelacji SYS-DIA-PUL."""
        if stored_data is None:
            return {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_correlation_chart(df)

    # =========================================================================
    # CALLBACK: Aktualizacja heatmapy
    # =========================================================================
    @callback(
        Output('graph-heatmap', 'figure'),
        Input('data-store', 'data')
    )
    def update_heatmap(stored_data):
        """Aktualizuje heatmapę ciśnienia."""
        if stored_data is None:
            return {}

        df = pd.read_json(StringIO(stored_data), orient='split')
        return generate_heatmap_chart(df)

    # =========================================================================
    # CALLBACK: Aktualizacja wykresu porównawczego
    # =========================================================================
    @callback(
        Output('graph-comparison', 'figure'),
        Input('boxplot-radio', 'value'),
        Input('comparison-chart-type-radio', 'value'),
        Input('data-store', 'data')
    )
    def update_comparison(category, chart_type, stored_data):
        """Aktualizuje wykres porównawczy (box/violin)."""
        if stored_data is None:
            df = initial_df
        else:
            df = pd.read_json(StringIO(stored_data), orient='split')

        return generate_comparison_chart(df, category, chart_type)

    # =========================================================================
    # CALLBACK: Aktualizacja histogramu
    # =========================================================================
    @callback(
        Output('graph-histogram', 'figure'),
        Input('histogram-radio', 'value'),
        Input('data-store', 'data')
    )
    def update_histogram(column, stored_data):
        """Aktualizuje histogram rozkładu parametru."""
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
        """Eksportuje wszystkie wykresy do pliku HTML."""
        if stored_data is None or n_clicks is None:
            return "❌ Brak danych do wyeksportowania"

        try:
            df = pd.read_json(StringIO(stored_data), orient='split')
            if df.empty:
                return "❌ Brak danych do wyeksportowania"

            # Generowanie wszystkich wykresów
            wykresy = {
                'Trend_w_czasie': generate_trend_chart(df),
                'Rytm_dobowy': generate_circadian_rhythm_chart(df),
                'Korelacja_SYS_DIA': generate_correlation_chart(df),
                'Heatmapa': generate_heatmap_chart(df),
                'Macierz_klasyfikacji': generate_classification_matrix_chart(df),
                'Klasyfikacja_ESC': generate_esc_category_bar_chart(df),
                'Histogram_SYS': generate_histogram_chart(df, 'SYS'),
                'Histogram_DIA': generate_histogram_chart(df, 'DIA'),
                'Porownanie_okresow': generate_comparison_chart(df, 'Godzina Pomiaru', 'box'),
            }

            # Tworzenie pliku HTML
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nazwa_pliku = f"Dashboard_Cisnienie_{timestamp}.html"

            with open(nazwa_pliku, 'w', encoding='utf-8') as f:
                f.write('<!DOCTYPE html>')
                f.write('<html><head>')
                f.write('<meta charset="utf-8">')
                f.write('<title>Dashboard Ciśnienia Krwi (ESC/ESH)</title>')
                f.write('<style>')
                f.write('body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }')
                f.write('h1 { text-align: center; color: #2c3e50; }')
                f.write('.chart-container { margin: 30px 0; background: white; padding: 20px; ')
                f.write('border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }')
                f.write('</style>')
                f.write('</head><body>')

                f.write('<h1>💓 Dashboard Pomiarów Ciśnienia Krwi (wg ESC/ESH)</h1>')
                f.write(
                    f'<p style="text-align:center; color:#666;">Wygenerowano: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>')

                for nazwa, wykres in wykresy.items():
                    f.write('<div class="chart-container">')
                    f.write(wykres.to_html(full_html=False, include_plotlyjs='cdn'))
                    f.write('</div>')

                f.write('</body></html>')

            return f"✅ Wykresy wyeksportowane: {nazwa_pliku}"

        except Exception as e:
            return f"❌ Błąd podczas eksportu: {e}"

    # =========================================================================
    # CALLBACK: Dynamiczne dodawanie stylów CSS (clientside)
    # =========================================================================
    app.clientside_callback(
        """
        function(n) {
            const style = document.createElement('style');
            style.innerHTML = `
                .kpi-card {
                    background-color: #f9f9f9;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 10px;
                    text-align: center;
                    min-width: 200px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                }
                .kpi-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                }
                .kpi-card h5 {
                    color: #666;
                    margin-bottom: 10px;
                    font-size: 0.9em;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                .kpi-card h3 {
                    color: #333;
                    margin: 0;
                    font-size: 2em;
                    font-weight: bold;
                }
            `;
            document.head.appendChild(style);
            return '';
        }
        """,
        Output('status-output', 'className'),
        Input('status-output', 'children')
    )