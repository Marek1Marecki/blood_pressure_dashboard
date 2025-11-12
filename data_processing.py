"""
Moduł przetwarzania danych
Zawiera funkcje wczytywania i przetwarzania pomiarów ciśnienia
z wykorzystaniem wektoryzacji i inteligentnego cache'u w folderze tymczasowym.
"""
import os
import pandas as pd
import numpy as np
import tempfile
from config import PROGI_ESC, STANDARDOWE_GODZINY, NAZWA_PLIKU_EXCEL

# --- Logika Cache'u ---
CACHE_DIR = os.path.join(tempfile.gettempdir(), "blood_pressure_dashboard_cache")
NAZWA_PLIKU_FEATHER = "pomiary_cache_v3.feather"  # ← ZMIENIONA NAZWA (wymuś przebudowę)
os.makedirs(CACHE_DIR, exist_ok=True)
# --- Koniec Logiki Cache'u ---


def klasyfikuj_cisnienie_esc_wektorowo(df):
    """
    Klasyfikuje pomiar ciśnienia wektorowo za pomocą np.select.

    KLUCZOWA ZASADA KLINICZNA:
    ==========================
    ISH (Izolowane Nadciśnienie Skurczowe) = SYS ≥ 140 AND DIA < 90

    ISH ma NAJWYŻSZY PRIORYTET i jest sprawdzane JAKO PIERWSZE!

    PRZYKŁADY:
    ==========
    SYS=142, DIA=72  → ISH ✓ (140 ≤ SYS, DIA < 90)
    SYS=154, DIA=84  → ISH ✓ (140 ≤ SYS, DIA < 90)
    SYS=185, DIA=85  → ISH ✓ (140 ≤ SYS, DIA < 90, mimo że SYS ≥ 180!)
    SYS=154, DIA=95  → N1 ✓  (DIA ≥ 90, więc nie ISH)
    SYS=185, DIA=95  → N3 ✓  (DIA ≥ 90, więc nie ISH)
    """

    p = PROGI_ESC

    # KLUCZOWA KOLEJNOŚĆ: ISH JAKO PIERWSZE!
    conditions = [
        # 1. IZOLOWANE NADCIŚNIENIE SKURCZOWE - ABSOLUTNY PRIORYTET!
        # ⚠️ POPRAWKA: Używamy p['nadcisnienie_1']['dia'] (90), NIE p['podwyzszone']['dia'] (80)!
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
        print(f"\n🔍 Znaleziono {len(ish_pomiary)} pomiarów ISH:")
        for _, row in ish_pomiary.head(10).iterrows():
            print(f"   SYS={row['SYS']}, DIA={row['DIA']}")

    return df
    """
    Klasyfikuje pomiar ciśnienia wektorowo za pomocą np.select.
    
    STRUKTURA PROGÓW W CONFIG.PY:
    ==============================
    Wartości w PROGI_ESC oznaczają GÓRNE granice (włącznie) każdej kategorii.
    
    ZASADA KLINICZNA - KLUCZOWE!
    =============================
    Przy niejednoznacznych parach klasyfikacja do WYŻSZEJ kategorii,
    ALE z WYJĄTKIEM dla Izolowanego Nadciśnienia Skurczowego (ISH):
    
    ISH = SYS ≥ 140 AND DIA < 90
    
    To oznacza, że ISH ma PRIORYTET nad logiką "wyższej kategorii":
    - 154/80: SYS → N1, DIA → Podwyższone → WYNIK: ISH (nie N1!)
    - 142/72: SYS → N1, DIA → Prawidłowe → WYNIK: ISH (nie N1!)
    - 185/85: SYS → N3, DIA → Podwyższone → WYNIK: ISH (nie N3!)
    
    WYJĄTEK: Jeśli DIA ≥ 90, wtedy normalna logika wyższej kategorii:
    - 154/95: SYS → N1, DIA → N1 → WYNIK: N1 ✓
    - 185/95: SYS → N3, DIA → N1 → WYNIK: N3 ✓
    
    PRZYKŁADY KLASYFIKACJI:
    =======================
    SYS=112, DIA=68  → Optymalne ✓
    SYS=127, DIA=78  → Prawidłowe ✓
    SYS=142, DIA=72  → ISH ✓ (SYS≥140, DIA<90)
    SYS=154, DIA=80  → ISH ✓ (SYS≥140, DIA<90)
    SYS=154, DIA=95  → Nadciśnienie 1° ✓ (DIA≥90)
    SYS=185, DIA=85  → ISH ✓ (SYS≥140, DIA<90)
    SYS=185, DIA=95  → Nadciśnienie 3° ✓ (SYS≥180)
    """

    p = PROGI_ESC

    # KRYTYCZNA KOLEJNOŚĆ: ISH PRZED wszystkimi kategoriami nadciśnienia!
    conditions = [
        # 1. IZOLOWANE NADCIŚNIENIE SKURCZOWE - NAJWYŻSZY PRIORYTET!
        # SYS ≥ 140 ALE DIA < 90
        # Ten warunek MUSI być PIERWSZY, żeby:
        # - 154/80 → ISH (nie N1)
        # - 142/72 → ISH (nie N1)
        # - 185/85 → ISH (nie N3)
        (df['SYS'] >= p['nadcisnienie_1']['sys']) & (df['DIA'] < p['podwyzszone']['dia']),

        # 2. NADCIŚNIENIE 3°
        # SYS ≥ 180 LUB DIA ≥ 110
        # Sprawdzane DOPIERO PO ISH, więc:
        # - 185/85 → ISH (złapane wcześniej)
        # - 185/95 → N3 (bo DIA >= 90, nie pasuje do ISH)
        (df['SYS'] >= p['nadcisnienie_3']['sys']) | (df['DIA'] >= p['nadcisnienie_3']['dia']),

        # 3. NADCIŚNIENIE 2°
        # SYS ≥ 160 LUB DIA ≥ 100
        (df['SYS'] >= p['nadcisnienie_2']['sys']) | (df['DIA'] >= p['nadcisnienie_2']['dia']),

        # 4. NADCIŚNIENIE 1°
        # SYS ≥ 140 LUB DIA ≥ 90
        # Sprawdzane DOPIERO PO ISH, więc:
        # - 154/80 → ISH (złapane wcześniej)
        # - 154/95 → N1 (bo DIA >= 90, nie pasuje do ISH)
        (df['SYS'] >= p['nadcisnienie_1']['sys']) | (df['DIA'] >= p['nadcisnienie_1']['dia']),

        # 5. PODWYŻSZONE
        # SYS ≥ 130 LUB DIA ≥ 80
        (df['SYS'] >= p['podwyzszone']['sys']) | (df['DIA'] >= p['podwyzszone']['dia']),

        # 6. PRAWIDŁOWE
        # SYS ≥ 120 LUB DIA ≥ 70
        (df['SYS'] >= p['optymalne']['sys']) | (df['DIA'] >= p['optymalne']['dia']),
    ]

    choices = [
        "Izolowane nadciśnienie skurczowe",  # Teraz PIERWSZE!
        "Nadciśnienie 3°",
        "Nadciśnienie 2°",
        "Nadciśnienie 1°",
        "Podwyższone",
        "Prawidłowe",
    ]

    # Default (gdy żaden warunek nie pasuje) = Optymalne
    # Czyli: SYS < 120 AND DIA < 70
    df['Kategoria'] = np.select(conditions, choices, default="Optymalne")

    return df


def wczytaj_i_przetworz_dane(sciezka_folderu_projektu):
    """
    Wczytuje i przetwarza dane, wykorzystując inteligentny cache w folderze tymczasowym.
    1. Sprawdza, czy istnieje plik cache (.feather).
    2. Porównuje daty modyfikacji .xlsx i .feather.
    3. Jeśli .xlsx jest nowszy, wczytuje go, tworzy nowy cache i zwraca dane.
    4. W przeciwnym razie, błyskawicznie wczytuje dane z cache.
    """
    sciezka_excel = os.path.join(sciezka_folderu_projektu, NAZWA_PLIKU_EXCEL)
    sciezka_feather = os.path.join(CACHE_DIR, NAZWA_PLIKU_FEATHER)

    print(f"[DIAGNOSTYKA] Program szuka pliku Excel pod ścieżką: {sciezka_excel}")
    print(f"[DIAGNOSTYKA] Program używa pliku cache pod ścieżką: {sciezka_feather}")

    df = None
    cache_jest_aktualny = False

    try:
        # Sprawdź, czy plik Excel w ogóle istnieje
        if not os.path.exists(sciezka_excel):
            raise FileNotFoundError

        # Sprawdź, czy cache jest aktualny
        if os.path.exists(sciezka_feather):
            czas_modyfikacji_excel = os.path.getmtime(sciezka_excel)
            czas_modyfikacji_feather = os.path.getmtime(sciezka_feather)
            if czas_modyfikacji_feather >= czas_modyfikacji_excel:
                cache_jest_aktualny = True

        # Wczytaj dane
        if cache_jest_aktualny:
            print("⚡️ Wczytywanie danych z szybkiego cache'u (Feather)...")
            df = pd.read_feather(sciezka_feather)
            zrodlo_danych = "cache"
        else:
            print("🐌 Wczytywanie danych z pliku Excel (aktualizacja cache'u)...")
            df = pd.read_excel(sciezka_excel)
            zrodlo_danych = "Excel"

        # --- Dalsze przetwarzanie danych (wspólne dla obu ścieżek) ---

        # Konwersja kolumn daty i godziny, jeśli istnieją w surowych danych
        if 'Data' in df.columns and 'Godzina' in df.columns:
            df['Datetime'] = pd.to_datetime(
                df['Data'].astype(str) + ' ' + df['Godzina'].astype(str), errors='coerce'
            )
        # Jeśli kolumna Datetime już istnieje (z cache'u), upewnij się, że jest w dobrym formacie
        elif 'Datetime' in df.columns:
             df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')

        df.dropna(subset=['Datetime'], inplace=True)
        df = df.sort_values('Datetime').reset_index(drop=True)

        liczba_przed = len(df)
        df.dropna(subset=['SYS', 'DIA', 'PUL'], inplace=True)
        liczba_po = len(df)

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

        # Zastosowanie nowej, wektorowej klasyfikacji
        df = klasyfikuj_cisnienie_esc_wektorowo(df)

        # *** KLUCZOWA POPRAWKA: Zapisz cache DOPIERO TERAZ ***
        # Po wszystkich przekształceniach i z czytelnym try-except
        if not cache_jest_aktualny:
            try:
                # Resetujemy index przed zapisem (wymóg Feather)
                df_do_zapisu = df.copy()
                df_do_zapisu.reset_index(drop=True, inplace=True)

                # Konwertuj kolumnę 'Dzień' na string (object -> datetime.date powoduje błędy w Feather)
                if 'Dzień' in df_do_zapisu.columns:
                    df_do_zapisu['Dzień'] = df_do_zapisu['Dzień'].astype(str)

                df_do_zapisu.to_feather(sciezka_feather)
                print(f"✅ Cache zapisany pomyślnie: {sciezka_feather}")
            except Exception as e_cache:
                print(f"⚠️ Błąd zapisu cache (nie krytyczny): {e_cache}")
                print(f"   Aplikacja działa normalnie, ale przy następnym uruchomieniu dane zostaną ponownie wczytane z Excel.")

        komunikat = f"✅ Pomyślnie wczytano {len(df)} pomiarów z pliku {zrodlo_danych}. "
        if liczba_przed > liczba_po:
            komunikat += f"Usunięto {liczba_przed - liczba_po} niekompletnych wierszy."

        return df, komunikat

    except FileNotFoundError:
        return pd.DataFrame(), f"❌ Błąd: Nie znaleziono pliku {NAZWA_PLIKU_EXCEL} w folderze projektu."
    except Exception as e:
        return pd.DataFrame(), f"❌ Błąd podczas wczytywania lub przetwarzania danych: {e}"