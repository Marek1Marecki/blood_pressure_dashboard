"""
Moduł przetwarzania danych
Zawiera funkcje wczytywania i przetwarzania pomiarów ciśnienia
"""

import pandas as pd
from config import PROGI_ESC, STANDARDOWE_GODZINY


def klasyfikuj_cisnienie_esc(row):
    """
    Klasyfikuje pomiar ciśnienia według aktualnych wytycznych klinicznych.

    Zasada: Przy niejednoznacznych parach (SYS w jednej kategorii, DIA w innej)
    klasyfikacja następuje do WYŻSZEJ kategorii.

    Args:
        row: Wiersz DataFrame z kolumnami 'SYS' i 'DIA'

    Returns:
        str: Kategoria ciśnienia
    """
    sys, dia = row['SYS'], row['DIA']

    # Izolowane nadciśnienie skurczowe (SYS ≥140 i DIA <90)
    if sys >= PROGI_ESC['podwyzszone']['sys'] and dia < PROGI_ESC['podwyzszone']['dia']:
        return "Izolowane nadciśnienie skurczowe"

    # Nadciśnienie 3° (SYS ≥180 LUB DIA ≥110)
    if sys >= PROGI_ESC['nadcisnienie_3']['sys'] or dia >= PROGI_ESC['nadcisnienie_3']['dia']:
        return "Nadciśnienie 3°"

    # Nadciśnienie 2° (SYS 160-179 LUB DIA 100-109)
    if sys >= PROGI_ESC['nadcisnienie_1']['sys'] or dia >= PROGI_ESC['nadcisnienie_1']['dia']:
        return "Nadciśnienie 2°"

    # Nadciśnienie 1° (SYS 140-159 LUB DIA 90-99)
    if sys >= PROGI_ESC['podwyzszone']['sys'] or dia >= PROGI_ESC['podwyzszone']['dia']:
        return "Nadciśnienie 1°"

    # Podwyższone (SYS 130-139 LUB DIA 80-89)
    if sys >= PROGI_ESC['prawidlowe']['sys'] or dia >= PROGI_ESC['prawidlowe']['dia']:
        return "Podwyższone"

    # Prawidłowe (SYS 120-129 LUB DIA 70-79)
    if sys >= PROGI_ESC['optymalne']['sys'] or dia >= PROGI_ESC['optymalne']['dia']:
        return "Prawidłowe"

    # Optymalne (SYS <120 I DIA <70)
    return "Optymalne"


def wczytaj_i_przetworz_dane(sciezka_pliku):
    """
    Wczytuje dane z pliku Excel i przetwarza je do analizy.

    Args:
        sciezka_pliku: Ścieżka do pliku Excel z pomiarami

    Returns:
        tuple: (DataFrame z przetworzonymi danymi, komunikat tekstowy)
    """
    try:
        df = pd.read_excel(sciezka_pliku)

        # Tworzenie kolumny datetime
        df['Datetime'] = pd.to_datetime(
            df['Data'].astype(str) + ' ' + df['Godzina'].astype(str)
        )
        df = df.sort_values('Datetime').reset_index(drop=True)

        # Usuwanie niekompletnych pomiarów
        liczba_przed = len(df)
        df.dropna(subset=['SYS', 'DIA', 'PUL'], inplace=True)
        liczba_po = len(df)

        # Obliczanie dodatkowych parametrów
        df['MAP'] = round((df['SYS'] + 2 * df['DIA']) / 3, 1)  # Średnie ciśnienie tętnicze
        df['PP'] = df['SYS'] - df['DIA']  # Ciśnienie tętna

        # Ekstrakcja cech czasowych
        df['Hour'] = df['Datetime'].dt.hour
        df['Dzień'] = df['Datetime'].dt.date
        df['Godzina Pomiaru'] = df['Hour'].apply(
            lambda h: f"{h:02d}:00" if h in STANDARDOWE_GODZINY else None
        )
        df['Typ Dnia'] = df['Datetime'].dt.dayofweek.apply(
            lambda x: 'Weekend' if x >= 5 else 'Dzień roboczy'
        )

        # Klasyfikacja pomiarów wg ESC
        df['Kategoria'] = df.apply(klasyfikuj_cisnienie_esc, axis=1)

        # Komunikat
        komunikat = f"✅ Pomyślnie wczytano {len(df)} pomiarów. "
        if liczba_przed > liczba_po:
            komunikat += f"Usunięto {liczba_przed - liczba_po} niekompletnych wierszy."

        return df, komunikat

    except Exception as e:
        return pd.DataFrame(), f"❌ Błąd podczas wczytywania pliku: {e}"