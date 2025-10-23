
"""
=== charts/summary.py ===
Dane podsumowujące (KPI + wykres kołowy)
"""

import pandas as pd
import plotly.express as px
from .utils import utworz_pusty_wykres
from config import KOLORY_ESC, KOLEJNOSC_ESC, TEMPLATE_PLOTLY


def generate_summary_data(df):
    """Generuje dane podsumowujące (KPI + wykres kołowy)."""
    if df.empty:
        return "B/D", "B/D", "B/D", "B/D", utworz_pusty_wykres()

    try:
        # KPI
        avg_sys = f"{df['SYS'].mean():.0f}"
        avg_dia = f"{df['DIA'].mean():.0f}"

        max_sys_row = df.loc[df['SYS'].idxmax()]
        max_reading_text = f"{max_sys_row['SYS']:.0f} / {max_sys_row['DIA']:.0f}"

        # Pomiary w normie (Optymalne + Prawidłowe + Podwyższone)
        # Zgodnie z aktualnymi wytycznymi: ciśnienie poniżej 140/90 uważa się za niepowikłane
        in_norm = df['Kategoria'].isin(['Optymalne', 'Prawidłowe', 'Podwyższone'])
        in_norm_count = in_norm.sum()
        norm_percent_text = f"{(in_norm_count / len(df) * 100):.1f}%"

        # Wykres kołowy klasyfikacji
        category_counts = df['Kategoria'].value_counts().reset_index()
        category_counts.columns = ['Kategoria', 'Liczba']

        # Sortowanie według zdefiniowanej kolejności
        category_counts['Kategoria'] = pd.Categorical(
            category_counts['Kategoria'],
            categories=KOLEJNOSC_ESC,
            ordered=True
        )
        category_counts = category_counts.sort_values('Kategoria')

        fig_pie = px.pie(
            category_counts,
            names='Kategoria',
            values='Liczba',
            title='Klasyfikacja Pomiarów (wg aktualnych wytycznych)',
            color='Kategoria',
            color_discrete_map=KOLORY_ESC,
            category_orders={'Kategoria': KOLEJNOSC_ESC}
        )
        fig_pie.update_layout(template=TEMPLATE_PLOTLY)

        return avg_sys, avg_dia, max_reading_text, norm_percent_text, fig_pie

    except Exception as e:
        return "Błąd", "Błąd", "Błąd", "Błąd", utworz_pusty_wykres(f"Błąd: {e}")