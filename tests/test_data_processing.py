import unittest
import pandas as pd
from data_processing import klasyfikuj_cisnienie_esc, wczytaj_i_przetworz_dane

class TestDataProcessing(unittest.TestCase):

    def test_klasyfikuj_cisnienie_esc(self):
        """Testuje wszystkie kategorie klasyfikacji ciśnienia wg ESC."""
        scenariusze = {
            "Optymalne": {'SYS': 115, 'DIA': 65},
            "Prawidłowe": {'SYS': 125, 'DIA': 75},
            "Podwyższone": {'SYS': 135, 'DIA': 85},
            "Nadciśnienie 1°": {'SYS': 145, 'DIA': 95},
            "Nadciśnienie 2°": {'SYS': 165, 'DIA': 105},
            "Nadciśnienie 3°": {'SYS': 185, 'DIA': 115},
            "Izolowane nadciśnienie skurczowe": {'SYS': 145, 'DIA': 85},
        }

        for kategoria, pomiar in scenariusze.items():
            with self.subTest(kategoria=kategoria):
                self.assertEqual(klasyfikuj_cisnienie_esc(pomiar), kategoria)

    def test_wczytaj_i_przetworz_dane_poprawny_plik(self):
        """Testuje wczytywanie i przetwarzanie danych z poprawnego pliku Excel."""
        # Używamy istniejącego pliku Pomiary_SYS_DIA.xlsx
        df, komunikat = wczytaj_i_przetworz_dane("Pomiary_SYS_DIA.xlsx")

        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.assertIn("Pomyślnie wczytano", komunikat)
        self.assertIn('Kategoria', df.columns)

    def test_wczytaj_i_przetworz_dane_brak_pliku(self):
        """Testuje obsługę błędu, gdy plik nie istnieje."""
        df, komunikat = wczytaj_i_przetworz_dane("nieistniejacy_plik.xlsx")

        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)
        self.assertIn("Błąd podczas wczytywania pliku", komunikat)

if __name__ == '__main__':
    unittest.main()
