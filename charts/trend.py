"""
Wykres trendu ciśnienia i pulsu w czasie
"""

import plotly.graph_objects as go
from .utils import utworz_pusty_wykres
from config import KOLORY_PARAMETROW, PROGI_ESC, TEMPLATE_PLOTLY


def generate_trend_chart(df):
    """
    Generuje wykres trendu ciśnienia i pulsu w czasie.

    Args:
        df: DataFrame z pomiarami

    Returns:
        go.Figure: Wykres Plotly
    """
    if df.empty:
        return utworz_pusty_wykres()

    try:
        fig = go.Figure()

        # Dodawanie śladów dla każdego parametru
        parametry = [
            ('SYS', 'SYS (Skurczowe)', 'lines+markers'),
            ('DIA', 'DIA (Rozkurczowe)', 'lines+markers'),
            ('PUL', 'Puls', 'lines+markers'),
            ('MAP', 'MAP (Śr. ciśnienie tętnicze)', 'lines'),
            ('PP', 'PP (Ciśnienie tętna)', 'lines')
        ]

        for param, nazwa, mode in parametry:
            dash_style = 'dot' if param == 'MAP' else ('dash' if param == 'PP' else 'solid')
            fig.add_trace(go.Scatter(
                x=df['Datetime'],
                y=df[param],
                mode=mode,
                name=nazwa,
                line=dict(color=KOLORY_PARAMETROW[param], dash=dash_style)
            ))

        # Linie progowe wg aktualnych wytycznych
        fig.add_hline(
            y=PROGI_ESC['optymalne']['sys'],
            line_dash="dot",
            line_color="green",
            annotation_text="Optymalne SYS (120)",
            annotation_position="right"
        )
        fig.add_hline(
            y=PROGI_ESC['podwyzszone']['sys'],
            line_dash="dot",
            line_color="orange",
            annotation_text="Podwyższone SYS (140)",
            annotation_position="right"
        )

        fig.update_layout(
            title="Trend ciśnienia i pulsu w czasie",
            xaxis_title="Data i godzina",
            yaxis_title="Wartość",
            legend_title="Parametr",
            template=TEMPLATE_PLOTLY,
            hovermode='x unified'
        )

        return fig

    except Exception as e:
        return utworz_pusty_wykres(f"Błąd: {e}")