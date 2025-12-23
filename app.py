"""Główny plik aplikacji do analizy pomiarów ciśnienia krwi.

Ten plik pełni rolę punktu startowego aplikacji. Jego główne zadania to:
- Inicjalizacja aplikacji Dash.
- Wczytanie i przetworzenie danych przy użyciu modułu `data_processing`.
- Wygenerowanie początkowych wersji wykresów za pomocą modułu `charts`.
- Zbudowanie kompletnego layoutu aplikacji z modułu `layouts`.
- Zarejestrowanie wszystkich interaktywnych callbacków z modułu `callbacks`.
- Uruchomienie serwera deweloperskiego Dash.

Aplikacja została zaprojektowana w architekturze modularnej, co oznacza,
że główna logika została podzielona na wyspecjalizowane moduły (dane,
wykresy, layout, callbacki). Dzięki temu `app.py` pozostaje zwięzły
i czytelny, a rozwijanie i utrzymanie aplikacji jest znacznie łatwiejsze.

Aby uruchomić aplikację, należy wykonać polecenie w terminalu:
    python app.py
"""

import os
import sys
import logging
from io import TextIOWrapper
from logging.handlers import RotatingFileHandler
from dash import Dash


def _ensure_utf8_stream(stream):
    """Return a text stream that can handle UTF-8 output on Windows consoles."""
    if stream is None:
        return None

    # Python 3.7+ exposes reconfigure on TextIOWrapper for safe runtime changes.
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
            return stream
        except (AttributeError, ValueError, OSError):
            pass

    if hasattr(stream, "buffer"):
        return TextIOWrapper(stream.buffer, encoding="utf-8", errors="replace")

    return stream


# Konfiguracja loggingu aplikacji
utf8_stdout = _ensure_utf8_stream(getattr(sys, "stdout", None))
utf8_stderr = _ensure_utf8_stream(getattr(sys, "stderr", None))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('app.log', maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'),
        logging.StreamHandler(stream=utf8_stderr or sys.stderr)
    ]
)

# Import modułów projektu
from data_processing import wczytaj_i_przetworz_dane
from charts import (
    generate_trend_chart,
    generate_circadian_rhythm_chart,
    generate_correlation_chart,
    generate_heatmap_chart,
    generate_histogram_chart,
    generate_classification_matrix_chart,
    generate_esc_category_bar_chart,
    generate_summary_data,
    generate_hemodynamics_chart
    # generate_comparison_chart - używany w layouts/tabs.py
)
from layouts import create_app_layout
from callbacks import register_callbacks


# =============================================================================
# INICJALIZACJA DANYCH I WYKRESÓW POCZĄTKOWYCH
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("🔄 Wczytywanie danych...")
initial_df, initial_status = wczytaj_i_przetworz_dane(BASE_DIR)

print("📊 Generowanie wykresów początkowych...")
# Wykresy
initial_figures = {
    'trend': generate_trend_chart(initial_df),
    'hour': generate_circadian_rhythm_chart(initial_df),
    'scatter': generate_correlation_chart(initial_df),
    'heatmap': generate_heatmap_chart(initial_df),
    'histogram': generate_histogram_chart(initial_df, 'SYS'),
    'matrix': generate_classification_matrix_chart(initial_df),
    'esc_bar': generate_esc_category_bar_chart(initial_df),
    'hemodynamics': generate_hemodynamics_chart(initial_df)
    # comparison - generowany bezpośrednio w layouts/tabs.py
}

# KPI
initial_kpis = generate_summary_data(initial_df)

# JSON danych
initial_df_json = initial_df.to_json(date_format='iso', orient='split')


# =============================================================================
# TWORZENIE APLIKACJI
# =============================================================================
print("🚀 Inicjalizacja aplikacji Dash...")
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Analizator Ciśnienia Krwi"

# Layout
app.layout = create_app_layout(
    initial_df_json=initial_df_json,
    initial_status=initial_status,
    initial_kpis=initial_kpis,
    initial_figures=initial_figures,
    initial_df=initial_df  # Dodajemy DataFrame dla zakładki porównawczej
)

# Callbacki
register_callbacks(app, BASE_DIR)


# =============================================================================
# URUCHOMIENIE APLIKACJI
# =============================================================================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8050,
        debug=False
    )