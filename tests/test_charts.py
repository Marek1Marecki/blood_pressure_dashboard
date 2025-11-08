import unittest
import pandas as pd
import plotly.graph_objects as go

# Import wszystkich funkcji generujących wykresy
from charts.trend import generate_trend_chart
from charts.circadian import generate_circadian_rhythm_chart
from charts.correlation import generate_correlation_chart
from charts.heatmap import generate_heatmap_chart
from charts.histogram import generate_histogram_chart
from charts.classification import generate_classification_matrix_chart, generate_esc_category_bar_chart
from charts.comparison import generate_comparison_chart
from charts.summary import generate_summary_data

class TestCharts(unittest.TestCase):

    def setUp(self):
        """Przygotowuje przykładową ramkę danych do testów."""
        data = {
            'Datetime': pd.to_datetime(['2023-01-01 10:00', '2023-01-02 14:00', '2023-01-03 18:00']),
            'Hour': [10, 14, 18],
            'SYS': [120, 130, 140],
            'DIA': [80, 85, 90],
            'PUL': [60, 65, 70],
            'Kategoria': ['Prawidłowe', 'Podwyższone', 'Nadciśnienie 1°'],
            'Dzień': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']).date,
            'Typ Dnia': ['Weekend', 'Dzień roboczy', 'Dzień roboczy']
        }
        self.df = pd.DataFrame(data)
        self.empty_df = pd.DataFrame()

    def test_generowanie_wykresow_z_danymi(self):
        """Testuje, czy każda funkcja generująca wykres zwraca obiekt Figure, gdy ma dane."""

        # Lista funkcji do przetestowania wraz z ich argumentami
        funkcje_do_testowania = [
            (generate_trend_chart, (self.df,)),
            (generate_circadian_rhythm_chart, (self.df,)),
            (generate_correlation_chart, (self.df,)),
            (generate_heatmap_chart, (self.df,)),
            (generate_histogram_chart, (self.df, 'SYS')),
            (generate_classification_matrix_chart, (self.df,)),
            (generate_esc_category_bar_chart, (self.df,)),
            (generate_comparison_chart, (self.df, 'Typ Dnia', 'box')),
        ]

        for funkcja, args in funkcje_do_testowania:
            with self.subTest(funkcja=funkcja.__name__):
                wynik = funkcja(*args)
                self.assertIsInstance(wynik, go.Figure)

        # Osobny test dla generate_summary_data, ponieważ zwraca krotkę
        with self.subTest(funkcja='generate_summary_data'):
            wynik_summary = generate_summary_data(self.df)
            self.assertIsInstance(wynik_summary, tuple)
            self.assertEqual(len(wynik_summary), 5)
            self.assertIsInstance(wynik_summary[4], go.Figure)


    def test_generowanie_wykresow_z_pustymi_danymi(self):
        """Testuje, czy każda funkcja zwraca pusty wykres (Figure), gdy nie ma danych."""

        funkcje_do_testowania = [
            (generate_trend_chart, (self.empty_df,)),
            (generate_circadian_rhythm_chart, (self.empty_df,)),
            (generate_correlation_chart, (self.empty_df,)),
            (generate_heatmap_chart, (self.empty_df,)),
            (generate_histogram_chart, (self.empty_df, 'SYS')),
            (generate_classification_matrix_chart, (self.empty_df,)),
            (generate_esc_category_bar_chart, (self.empty_df,)),
            (generate_comparison_chart, (self.empty_df, 'Typ Dnia', 'box')),
        ]

        for funkcja, args in funkcje_do_testowania:
            with self.subTest(funkcja=funkcja.__name__):
                wynik = funkcja(*args)
                self.assertIsInstance(wynik, go.Figure)

if __name__ == '__main__':
    unittest.main()
