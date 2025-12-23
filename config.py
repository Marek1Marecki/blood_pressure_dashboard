# /config.py

import os
from dotenv import load_dotenv

load_dotenv()

"""Moduł konfiguracyjny aplikacji.

Ten plik centralizuje wszystkie stałe, progi, palety kolorów i inne
parametry konfiguracyjne używane w różnych częściach aplikacji.
Dzięki temu, zmiana np. progu dla danej kategorii ciśnienia czy koloru
wykresu wymaga modyfikacji tylko w jednym miejscu.

Zawiera konfiguracje dla:
-   Nazw plików wejściowych i cache.
-   Standardowych godzin pomiarów.
-   Progów klasyfikacji ciśnienia zgodnie z wytycznymi ESC/ESH.
-   Palet kolorów dla kategorii ciśnienia i parametrów medycznych.
-   Domyślnych ustawień wizualnych dla wykresów Plotly.
"""

# =============================================================================
# PODSTAWOWA KONFIGURACJA
# =============================================================================
NAZWA_PLIKU_FEATHER = "pomiary_cache.feather"
DATA_CACHE_FILE = "pomiary_cache.pkl"
DATA_CACHE_TTL_MINUTES = 5  # Ile minut cache może być uznany za świeży
STANDARDOWE_GODZINY = [10, 13, 16, 19, 22]

# =============================================================================
# KONFIGURACJA EKSPORTU WYKRESÓW (HTML)
# =============================================================================
# Każdy wpis określa kolejność, sekcję i generator wykresu używany w eksporcie.
# Pole `builder` to klucz mapowany w callbacks/export_html na konkretną funkcję.
EXPORT_CHART_DEFINITIONS = [
    {
        "id": "01_Podsumowanie_klasyfikacji",
        "section": "Podstawowe Analizy",
        "builder": "summary_pie",
        "enabled": True,
    },
    {
        "id": "02_Klasyfikacja_ESC_wykres",
        "section": "Podstawowe Analizy",
        "builder": "esc_bar",
        "enabled": False,
    },
    {
        "id": "03_Macierz_klasyfikacji",
        "section": "Podstawowe Analizy",
        "builder": "classification_matrix",
        "enabled": True,
    },
    {
        "id": "04_Trend_w_czasie",
        "section": "Podstawowe Analizy",
        "builder": "trend",
        "enabled": True,
    },
    {
        "id": "05_Rytm_dobowy",
        "section": "Podstawowe Analizy",
        "builder": "circadian",
        "enabled": True,
    },
    {
        "id": "06_Analiza_hemodynamiczna",
        "section": "Analizy Zaawansowane",
        "builder": "hemodynamics",
        "enabled": True,
    },
    {
        "id": "07_Korelacja_SYS_DIA_PUL",
        "section": "Analizy Zaawansowane",
        "builder": "correlation",
        "enabled": True,
    },
    {
        "id": "08_Heatmapa_dzien_godzina",
        "section": "Analizy Zaawansowane",
        "builder": "heatmap",
        "enabled": True,
    },
    {
        "id": "09_Porownanie_godziny_VIOLIN",
        "section": "Porównania Okresów (Violin Plots)",
        "builder": "comparison_hour",
        "enabled": True,
    },
    {
        "id": "10_Porownanie_dzien_roboczy_VIOLIN",
        "section": "Porównania Okresów (Violin Plots)",
        "builder": "comparison_day",
        "enabled": True,
    },
    {
        "id": "11_Histogram_SYS",
        "section": "Rozkłady Parametrów",
        "builder": "histogram_sys",
        "enabled": True,
    },
    {
        "id": "12_Histogram_DIA",
        "section": "Rozkłady Parametrów",
        "builder": "histogram_dia",
        "enabled": True,
    },
    {
        "id": "13_Histogram_Puls",
        "section": "Rozkłady Parametrów",
        "builder": "histogram_pul",
        "enabled": True,
    },
]

# =============================================================================
# KONFIGURACJA GOOGLE SHEETS
# =============================================================================
GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")
WORKSHEET_NAME = os.getenv("GOOGLE_WORKSHEET_NAME", "Pomiary")
GOOGLE_CREDENTIALS_FILE = os.getenv(
    "GOOGLE_CREDENTIALS_FILE", "google_credentials.json"
)

if not GOOGLE_SHEET_URL:
    raise RuntimeError(
        "Brak GOOGLE_SHEET_URL. Ustaw zmienną w pliku .env"
    )


# =============================================================================
# PROGI KLASYFIKACJI CIŚNIENIA (wg aktualnych wytycznych ESC/ESH)
# =============================================================================
# ⚠️ UWAGA: Te wartości oznaczają DOLNE GRANICE każdej kategorii
#
# INTERPRETACJA PROGÓW:
# ====================
# 'prawidlowe': {'sys': 120, 'dia': 70}
#   → Prawidłowe: SYS ≥ 120 LUB DIA ≥ 70
#   → Górna granica to dolna granica następnej kategorii
#
# ZASADY KLASYFIKACJI:
# ===================
# 1. Przy niejednoznacznych parach (SYS w jednej kategorii, DIA w innej)
#    klasyfikacja następuje do WYŻSZEJ kategorii (operator LUB)
#    WYJĄTEK: Izolowane nadciśnienie skurczowe (ISH)
#
# 2. ISH = SYS ≥ 140 AND DIA < 90
#    ISH ma PRIORYTET nad zasadą "wyższej kategorii"
#
# 3. Kolejność sprawdzania: ISH, potem N3, N2, N1, Podwyższone, Prawidłowe, Optymalne
#
# KATEGORIE I ZAKRESY:
# ===================
# Optymalne:              SYS < 120   AND DIA < 70
# Prawidłowe:             SYS 120-129 OR  DIA 70-79
# Podwyższone:            SYS 130-139 OR  DIA 80-89
# Nadciśnienie 1°:        SYS 140-159 OR  DIA 90-99
# Nadciśnienie 2°:        SYS 160-179 OR  DIA 100-109
# Nadciśnienie 3°:        SYS ≥ 180   OR  DIA ≥ 110
# Izolowane nadciśnienie: SYS ≥ 140   AND DIA < 90
#
# PRZYKŁADY:
# ==========
# 112/68 → Optymalne (SYS < 120 AND DIA < 70)
# 127/78 → Prawidłowe (SYS ≥ 120)
# 142/72 → ISH (SYS ≥ 140 AND DIA < 90)
# 154/80 → ISH (SYS ≥ 140 AND DIA < 90)
# 154/95 → Nadciśnienie 1° (DIA ≥ 90, wyższa kategoria)
# 185/85 → ISH (SYS ≥ 140 AND DIA < 90, nie N3!)
# 185/95 → Nadciśnienie 3° (SYS ≥ 180)

PROGI_ESC = {
    # Optymalne: domyślna kategoria (gdy nic nie pasuje)
    'optymalne': {
        'sys': 120,  # Dolna granica Prawidłowego
        'dia': 70
    },

    # Prawidłowe: SYS 120-129 LUB DIA 70-79
    'prawidlowe': {
        'sys': 120,  # ← DOLNA granica Prawidłowego
        'dia': 70
    },

    # Podwyższone: SYS 130-139 LUB DIA 80-89
    'podwyzszone': {
        'sys': 130,  # ← DOLNA granica Podwyższonego
        'dia': 80
    },

    # Nadciśnienie 1°: SYS 140-159 LUB DIA 90-99
    'nadcisnienie_1': {
        'sys': 140,  # ← DOLNA granica Nadciśnienia 1°
        'dia': 90
    },

    # Nadciśnienie 2°: SYS 160-179 LUB DIA 100-109
    'nadcisnienie_2': {
        'sys': 160,  # ← DOLNA granica Nadciśnienia 2°
        'dia': 100
    },

    # Nadciśnienie 3°: SYS ≥180 LUB DIA ≥110
    'nadcisnienie_3': {
        'sys': 180,  # ← DOLNA granica Nadciśnienia 3°
        'dia': 110
    }
}

# =============================================================================
# KOLORY DLA KATEGORII (wg zaktualizowanej klasyfikacji)
# =============================================================================
KOLORY_ESC = {
    'Optymalne': '#2ca02c',                          # Zielony
    'Prawidłowe': '#90EE90',                         # Jasnozielony
    'Podwyższone': '#FFD700',                        # Złoty
    'Nadciśnienie 1°': '#FFA500',                    # Pomarańczowy
    'Nadciśnienie 2°': '#FF6347',                    # Pomidorowy
    'Nadciśnienie 3°': '#8B0000',                    # Ciemnoczerwony
    'Izolowane nadciśnienie skurczowe': '#9370DB'    # Fioletowy
}

# Kolejność kategorii (dla wykresów i sortowania)
KOLEJNOSC_ESC = [
    'Optymalne',
    'Prawidłowe',
    'Podwyższone',
    'Nadciśnienie 1°',
    'Nadciśnienie 2°',
    'Nadciśnienie 3°',
    'Izolowane nadciśnienie skurczowe'
]

# =============================================================================
# KOLORY DLA PARAMETRÓW MEDYCZNYCH
# =============================================================================
KOLORY_PARAMETROW = {
    'SYS': 'red',
    'DIA': 'blue',
    'PUL': 'green',
    'MAP': 'orange',
    'PP': 'purple'
}

# =============================================================================
# USTAWIENIA WYKRESÓW
# =============================================================================
TEMPLATE_PLOTLY = "plotly_white"
WYSOKOSC_WYKRESU_STANDARD = 600
WYSOKOSC_WYKRESU_DUZY = 700
WYSOKOSC_WYKRESU_MALY = 500

# Granice dla osi wykresów (nowa sekcja)
MIN_DIA = 40
MAX_DIA = 120
MIN_SYS = 60
MAX_SYS = 200