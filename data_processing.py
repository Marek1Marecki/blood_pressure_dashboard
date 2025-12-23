"""Moduł odpowiedzialny za wczytywanie i przetwarzanie danych pomiarowych.

Zawiera funkcje do:
- Wczytywania danych z Arkusza Google wraz z prostym mechanizmem cache.
- Klasyfikacji pomiarów ciśnienia krwi zgodnie z najnowszymi wytycznymi ESC/ESH.
- Wzbogacania danych o dodatkowe kolumny, takie jak MAP (średnie ciśnienie tętnicze)
  i PP (ciśnienie tętna).
"""
import os
import logging
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import gspread
from gspread_dataframe import get_as_dataframe
from config import (
    PROGI_ESC,
    STANDARDOWE_GODZINY,
    GOOGLE_SHEET_URL,
    WORKSHEET_NAME,
    GOOGLE_CREDENTIALS_FILE,
    DATA_CACHE_FILE,
    DATA_CACHE_TTL_MINUTES,
)

logger = logging.getLogger(__name__)

def klasyfikuj_cisnienie_esc_wektorowo(df):
    """Klasyfikuje pomiary ciśnienia krwi do odpowiednich kategorii.

    Wykorzystuje zoptymalizowaną metodę wektorową `np.select` do szybkiej
    klasyfikacji. Implementuje logikę zgodną z najnowszymi wytycznymi
    Europejskiego Towarzystwa Kardiologicznego (ESC/ESH), uwzględniając
    zasadę priorytetu dla Izolowanego Nadciśnienia Skurczowego (ISH).

    Args:
        df (pd.DataFrame): Ramka danych zawierająca kolumny 'SYS' (ciśnienie
            skurczowe) i 'DIA' (ciśnienie rozkurczowe).

    Returns:
        pd.DataFrame: Oryginalna ramka danych wzbogacona o nową kolumnę
        'Kategoria', która zawiera tekstową nazwę kategorii ciśnienia
        dla każdego pomiaru.
    """

    p = PROGI_ESC

    # KLUCZOWA KOLEJNOŚĆ: ISH JAKO PIERWSZE!
    conditions = [
        # 1. IZOLOWANE NADCIŚNIENIE SKURCZOWE - ABSOLUTNY PRIORYTET!
        # POPRAWKA: Używamy p['nadcisnienie_1']['dia'] (90), NIE p['podwyzszone']['dia'] (80)!
        (df['SYS'] >= p['nadcisnienie_1']['sys']) & (df['DIA'] < p['nadcisnienie_1']['dia']),

        # 2. NADCIŚNIENIE 3°
        (df['SYS'] >= p['nadcisnienie_3']['sys']) | (df['DIA'] >= p['nadcisnienie_3']['dia']),

        # 3. NADCIŚNIENIE 2°
        (df['SYS'] >= p['nadcisnienie_2']['sys']) | (df['DIA'] >= p['nadcisnienie_2']['dia']),

        # 4. NADCIŚNIENIE 1°
        (df['SYS'] >= p['nadcisnienie_1']['sys']) | (df['DIA'] >= p['nadcisnienie_1']['dia']),

        # 5. PODWYŻSZONE
        (df['SYS'] >= p['podwyzszone']['sys']) | (df['DIA'] >= p['podwyzszone']['dia']),

        # 6. PRAWIDŁOWE
        (df['SYS'] >= p['optymalne']['sys']) | (df['DIA'] >= p['optymalne']['dia']),
    ]

    choices = [
        "Izolowane nadciśnienie skurczowe",
        "Nadciśnienie 3°",
        "Nadciśnienie 2°",
        "Nadciśnienie 1°",
        "Podwyższone",
        "Prawidłowe",
    ]

    df['Kategoria'] = np.select(conditions, choices, default="Optymalne")

    # DIAGNOSTYKA
    ish_pomiary = df[df['Kategoria'] == 'Izolowane nadciśnienie skurczowe']
    if not ish_pomiary.empty:
        logger.debug("Znaleziono %d pomiarów ISH", len(ish_pomiary))
        for _, row in ish_pomiary.head(10).iterrows():
            logger.debug("ISH przykład: SYS=%s, DIA=%s", row['SYS'], row['DIA'])

    return df


def wczytaj_i_przetworz_dane(sciezka_folderu_projektu, force_refresh=False):
    """Wczytuje i przetwarza dane z Arkusza Google z prostym cache.

    Args:
        sciezka_folderu_projektu (str): Ścieżka bazowa projektu.
        force_refresh (bool): Gdy True, pomija cache TTL i wymusza pobranie.
    """

    cache_path = os.path.join(sciezka_folderu_projektu, DATA_CACHE_FILE)
    cache_ttl = timedelta(minutes=DATA_CACHE_TTL_MINUTES)
    now = datetime.now()

    def _read_cache():
        if not os.path.exists(cache_path):
            return None, None
        try:
            payload = pd.read_pickle(cache_path)
            if isinstance(payload, dict) and 'df' in payload:
                return payload['df'], payload.get('status')
            return payload, None
        except Exception as err:
            logger.warning("Nie udało się odczytać cache: %s", err)
            return None, None

    cached_df, cached_status = _read_cache()
    cache_age = None
    if cached_df is not None and os.path.exists(cache_path):
        cache_age = now - datetime.fromtimestamp(os.path.getmtime(cache_path))

    if (
        not force_refresh
        and cached_df is not None
        and cache_age is not None
        and cache_age <= cache_ttl
    ):
        status = cached_status or (
            f"⚡ Wczytano {len(cached_df)} pomiarów z cache (<= {DATA_CACHE_TTL_MINUTES} min)."
        )
        return cached_df.copy(), status

    if force_refresh:
        logger.info("⏭️ Pomijam cache - wymuszam pobranie z Google Sheets...")
    else:
        logger.info("🌍 Łączenie z Google Sheets...")
    try:
        credentials_path = os.path.join(sciezka_folderu_projektu, GOOGLE_CREDENTIALS_FILE)

        gc = gspread.service_account(filename=credentials_path)
        spreadsheet = gc.open_by_url(GOOGLE_SHEET_URL)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)

        # Pobierz dane. Ignoruj pierwszy wiersz (nagłówki) i użyj własnych nazw, jeśli trzeba.
        df = get_as_dataframe(worksheet, evaluate_formulas=True)
        # Usuń puste wiersze, które gspread czasem dołącza
        df.dropna(how='all', inplace=True)

        required_columns = ['Data', 'Godzina', 'SYS', 'DIA', 'PUL']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            pretty_missing = ', '.join(missing_columns)
            return pd.DataFrame(), f"❌ Brakujące kolumny: {pretty_missing}"

        logger.info("Pomyślnie pobrano %d wierszy z Google Sheets.", len(df))

        for col in ['SYS', 'DIA', 'PUL']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        datetime_series = pd.to_datetime(
            df['Data'].astype(str) + ' ' + df['Godzina'].astype(str), errors='coerce'
        )
        if datetime_series.dt.tz is not None:
            datetime_series = datetime_series.dt.tz_localize(None)
        df['Datetime'] = datetime_series

        df.dropna(subset=['Datetime', 'SYS', 'DIA', 'PUL'], inplace=True)
        df = df.sort_values('Datetime').reset_index(drop=True)

        liczba_przed = len(df)
        liczba_po = len(df)  # Pozostaje dla kompatybilności z wcześniejszą diagnozą

        df['MAP'] = round((df['SYS'] + 2 * df['DIA']) / 3, 1)
        df['PP'] = df['SYS'] - df['DIA']
        df['Hour'] = df['Datetime'].dt.hour
        df['Dzień'] = df['Datetime'].dt.date
        df['Godzina Pomiaru'] = df['Hour'].apply(
            lambda h: f"{h:02d}:00" if h in STANDARDOWE_GODZINY else None
        )
        df['Typ Dnia'] = df['Datetime'].dt.dayofweek.apply(
            lambda x: 'Weekend' if x >= 5 else 'Dzień roboczy'
        )

        df = klasyfikuj_cisnienie_esc_wektorowo(df)

        komunikat = f"✅ Pomyślnie wczytano {len(df)} pomiarów z Google Sheets."
        if liczba_przed > liczba_po:
            komunikat += f" Usunięto {liczba_przed - liczba_po} niekompletnych wierszy."

        try:
            pd.to_pickle(
                {
                    'df': df,
                    'status': komunikat,
                    'fetched_at': datetime.now().isoformat()
                },
                cache_path
            )
        except Exception as cache_err:
            logger.warning("Nie udało się zapisać cache: %s", cache_err)

        return df, komunikat

    except gspread.exceptions.SpreadsheetNotFound as exc:
        error_msg = f"❌ Błąd: Nie znaleziono arkusza Google. Sprawdź URL lub uprawnienia."
    except gspread.exceptions.WorksheetNotFound as exc:
        error_msg = f"❌ Błąd: Nie znaleziono zakładki '{WORKSHEET_NAME}' w arkuszu."
    except Exception as exc:
        error_msg = f"❌ Błąd podczas łączenia z Google Sheets: {exc}"

    return pd.DataFrame(), error_msg