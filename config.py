"""
Konfiguracja aplikacji Dashboard Ciśnienia Krwi
Zawiera wszystkie stałe, progi i kolory używane w aplikacji
"""

# =============================================================================
# PODSTAWOWA KONFIGURACJA
# =============================================================================
NAZWA_PLIKU_EXCEL = "Pomiary_SYS_DIA.xlsx"
STANDARDOWE_GODZINY = [10, 13, 16, 19, 22]

# =============================================================================
# PROGI KLASYFIKACJI CIŚNIENIA (wg aktualnych wytycznych klinicznych)
# =============================================================================
# UWAGA: Zaktualizowane według najnowszych wytycznych
#
# Zasady klasyfikacji:
# 1. Przy niejednoznacznych parach (SYS w jednej kategorii, DIA w innej)
#    klasyfikacja następuje do WYŻSZEJ kategorii (operator LUB, nie I)
# 2. Izolowane nadciśnienie skurczowe: SYS ≥140 I DIA <90
# 3. Kolejność sprawdzania: od najwyższej do najniższej kategorii
#
# Progi definiują DOLNE granice każdej kategorii
# Górne granice są automatycznie dolnymi granicami następnej kategorii

PROGI_ESC = {
    # Optymalne: SYS <120 I DIA <70
    'optymalne': {'sys': 120, 'dia': 70},

    # Prawidłowe: SYS 120-129 LUB DIA 70-79
    'prawidlowe': {'sys': 130, 'dia': 80},

    # Podwyższone: SYS 130-139 LUB DIA 80-89
    'podwyzszone': {'sys': 140, 'dia': 90},

    # Nadciśnienie 1°: SYS 140-159 LUB DIA 90-99
    'nadcisnienie_1': {'sys': 160, 'dia': 100},

    # Nadciśnienie 2°: SYS 160-179 LUB DIA 100-109
    'nadcisnienie_2': {'sys': 180, 'dia': 110},

    # Nadciśnienie 3°: SYS ≥180 LUB DIA ≥110
    # (próg ten sam co nadcisnienie_2, bo sprawdzamy >= 180)
    'nadcisnienie_3': {'sys': 180, 'dia': 110}
}

# =============================================================================
# KOLORY DLA KATEGORII (wg zaktualizowanej klasyfikacji)
# =============================================================================
# Kolory są spójne z kluczami kategorii używanymi w aplikacji
KOLORY_ESC = {
    'Optymalne': '#2ca02c',                      # Zielony
    'Prawidłowe': '#90EE90',                     # Jasnozielony
    'Podwyższone': '#FFD700',                    # Złoty
    'Nadciśnienie 1°': '#FFA500',                # Pomarańczowy
    'Nadciśnienie 2°': '#FF6347',                # Pomidorowy
    'Nadciśnienie 3°': '#8B0000',                # Ciemnoczerwony
    'Izolowane nadciśnienie skurczowe': '#9370DB'  # Fioletowy
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