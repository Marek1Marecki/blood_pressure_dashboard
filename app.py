"""
Dashboard Pomiarów Ciśnienia Krwi - Aplikacja główna (PEŁNA MODULARYZACJA)
===========================================================================

STRUKTURA PROJEKTU:
-------------------
blood_pressure_dashboard/
├── app.py                      # <- TEN PLIK (tylko inicjalizacja i uruchomienie)
├── config.py                   # Konfiguracja i stałe
├── data_processing.py          # Wczytywanie i przetwarzanie danych
├── charts/                     # Moduł wykresów
│   ├── __init__.py
│   ├── utils.py
│   ├── trend.py
│   ├── circadian.py
│   ├── correlation.py
│   ├── heatmap.py
│   ├── histogram.py
│   ├── classification.py
│   ├── comparison.py
│   └── summary.py
├── layouts/                    # Moduł layoutów
│   ├── __init__.py
│   └── tabs.py                # Definicje wszystkich zakładek
└── callbacks/                  # Moduł callbacków
    ├── __init__.py
    └── callbacks.py           # Wszystkie callbacki

JAK DODAĆ NOWĄ ZAKŁADKĘ:
------------------------
1. Utwórz plik wykresu w charts/ (np. charts/nowy_wykres.py)
2. Dodaj import w charts/__init__.py
3. Wygeneruj wykres początkowy w sekcji INICJALIZACJA (poniżej)
4. Dodaj zakładkę w layouts/tabs.py (funkcja create_nowy_tab())
5. Dodaj callback w callbacks/callbacks.py
6. Opcjonalnie: Dodaj do eksportu HTML w callbacks/callbacks.py

URUCHOMIENIE:
-------------
python app.py
"""

from dash import Dash

# Import modułów projektu
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
    generate_summary_data,
    generate_hemodynamics_chart
    # generate_comparison_chart - używany w layouts/tabs.py
)
from layouts import create_app_layout
from callbacks import register_callbacks


# =============================================================================
# INICJALIZACJA DANYCH I WYKRESÓW POCZĄTKOWYCH
# =============================================================================
print("🔄 Wczytywanie danych...")
initial_df, initial_status = wczytaj_i_przetworz_dane(NAZWA_PLIKU_EXCEL)

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
register_callbacks(app)


# =============================================================================
# URUCHOMIENIE APLIKACJI
# =============================================================================
if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   💓 Dashboard Pomiarów Ciśnienia Krwi                        ║
    ║   📋 Zgodny z wytycznymi ESC/ESH                              ║
    ║                                                                ║
    ║   ✅ Aplikacja uruchomiona pomyślnie!                         ║
    ║   🌐 Otwórz przeglądarkę: http://127.0.0.1:8050               ║
    ║                                                                ║
    ║   📂 Struktura modularna - łatwe dodawanie zakładek!          ║
    ║   📊 9 zakładek z analizami                                   ║
    ║   🔄 Automatyczne odświeżanie danych                          ║
    ║   📥 Eksport do HTML                                          ║
    ║                                                                ║
    ║   📚 Dokumentacja: README.md                                  ║
    ║   ⚡ Szybki start: QUICK_START.md                             ║
    ║   🎓 Przykład: EXAMPLE_NEW_TAB.md                             ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    app.run(debug=True)