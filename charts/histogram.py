"""
=== charts/histogram.py ===
Histogram rozkładu parametrów
"""

import plotly.express as px
from .utils import utworz_pusty_wykres
from config import PROGI_ESC, TEMPLATE_PLOTLY


def generate_histogram_chart(df, selected_column):
    """Generuje histogram rozkładu wybranego parametru."""
    if df.empty:
        return utworz_pusty_wykres()

    try:
        fig = px.histogram(df, x=selected_column, nbins=20,
                          title=f"Rozkład wartości dla: {selected_column}")

        mean_val = df[selected_column].mean()
        fig.add_vline(x=mean_val, line_dash="dash", line_color="red",
                     annotation_text=f"Średnia: {mean_val:.1f}")

        # Dodanie linii progowych wg aktualnych wytycznych
        if selected_column == 'SYS':
            progi = [
                (PROGI_ESC['optymalne']['sys'], 'green', 'Optymalne (120)'),
                (PROGI_ESC['prawidlowe']['sys'], 'lightgreen', 'Prawidłowe (130)'),
                (PROGI_ESC['podwyzszone']['sys'], 'orange', 'Podwyższone (140)'),
                (PROGI_ESC['nadcisnienie_1']['sys'], 'orangered', 'Nadciśnienie 1° (160)'),
                (PROGI_ESC['nadcisnienie_2']['sys'], 'red', 'Nadciśnienie 2° (180)')
            ]
        elif selected_column == 'DIA':
            progi = [
                (PROGI_ESC['optymalne']['dia'], 'green', 'Optymalne (70)'),
                (PROGI_ESC['prawidlowe']['dia'], 'lightgreen', 'Prawidłowe (80)'),
                (PROGI_ESC['podwyzszone']['dia'], 'orange', 'Podwyższone (90)'),
                (PROGI_ESC['nadcisnienie_1']['dia'], 'orangered', 'Nadciśnienie 1° (100)'),
                (PROGI_ESC['nadcisnienie_2']['dia'], 'red', 'Nadciśnienie 2° (110)')
            ]
        else:
            progi = []

        for wartosc, kolor, etykieta in progi:
            fig.add_vline(x=wartosc, line_dash="dot", line_color=kolor,
                         annotation_text=etykieta, annotation_position="top")

        fig.update_layout(template=TEMPLATE_PLOTLY, xaxis_title="Wartość",
                         yaxis_title="Liczba pomiarów (częstotliwość)")
        return fig
    except Exception as e:
        return utworz_pusty_wykres(f"Błąd: {e}")