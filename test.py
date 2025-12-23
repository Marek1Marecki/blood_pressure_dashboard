import gspread
from gspread_dataframe import get_as_dataframe

# --- UZUPEŁNIJ TE DWIE ZMIENNE ---
TWOJ_URL = "https://docs.google.com/spreadsheets/d/1LXsCX071uHog7Ejpp5nCK5wZYJzkCQg0eo3bqBw98LE/edit"
NAZWA_ZAKLADKI = "Pomiary" # lub "Arkusz1" albo inna nazwa Twojej zakładki z danymi
# ------------------------------------

NAZWA_PLIKU_CREDENTIALS = "google_credentials.json"

print("--- Rozpoczynam test połączenia z Google Sheets ---")

try:
    print(f"1. Próba autoryzacji przy użyciu pliku: {NAZWA_PLIKU_CREDENTIALS}")
    gc = gspread.service_account(filename=NAZWA_PLIKU_CREDENTIALS)
    print("   ✅ Autoryzacja zakończona sukcesem!")

    print(f"\n2. Próba otwarcia arkusza po URL: {TWOJ_URL}")
    spreadsheet = gc.open_by_url(TWOJ_URL)
    print("   ✅ Arkusz otwarty pomyślnie!")

    print(f"\n3. Próba otwarcia zakładki o nazwie: '{NAZWA_ZAKLADKI}'")
    worksheet = spreadsheet.worksheet(NAZWA_ZAKLADKI)
    print("   ✅ Zakładka znaleziona!")

    print("\n4. Próba pobrania danych do ramki danych Pandas...")
    df = get_as_dataframe(worksheet)
    print("   ✅ Dane pobrane pomyślnie!")

    print("\n--- TEST ZAKOŃCZONY SUKCESEM ---")
    print(f"Pobrano {len(df)} wierszy. Oto 5 pierwszych:")
    print(df.head())

except FileNotFoundError:
    print(f"\n--- BŁĄD KRYTYCZNY ---")
    print(f"Nie znaleziono pliku '{NAZWA_PLIKU_CREDENTIALS}'. Upewnij się, że jest w tym samym folderze co skrypt.")

except gspread.exceptions.SpreadsheetNotFound:
    print(f"\n--- BŁĄD KRYTYCZNY ---")
    print("Nie udało się odnaleźć arkusza. Możliwe przyczyny:")
    print("1. URL arkusza jest niepoprawny.")
    print("2. Konto usługi (e-mail z pliku .json) NIE zostało udostępnione w arkuszu.")
    print("3. Arkusz nie ma ustawionego dostępu na 'Każdy, kto ma link'.")

except gspread.exceptions.WorksheetNotFound:
    print(f"\n--- BŁĄD KRYTYCZNY ---")
    print(f"W arkuszu nie znaleziono zakładki o nazwie '{NAZWA_ZAKLADKI}'. Sprawdź, czy nazwa jest poprawna.")

except Exception as e:
    print(f"\n--- WYSTĄPIŁ NIESPODZIEWANY BŁĄD ---")
    print(e)