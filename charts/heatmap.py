

"""
=== charts/heatmap.py ===
Heatmapa ciśnienia
"""

import plotly.express as px
from .utils import utworz_pusty_wykres
from config import TEMPLATE_PLOTLY


def generate_heatmap_chart(df):
    """Generuje heatmapę ciśnienia skurczowego."""
    if df.empty:
        return utworz_pusty_wykres()

    try:
        if df['Dzień'].nunique() > 1 and df['Hour'].nunique() > 1:
            pivot = df.pivot_table(index='Dzień', columns='Hour', values='SYS', aggfunc='mean')
            fig = px.imshow(
                pivot, color_continuous_scale='RdYlBu_r',
                title="Heatmapa ciśnienia skurczowego (SYS) - Dzień x Godzina",
                labels={'x': 'Godzina', 'y': 'Dzień', 'color': 'SYS [mmHg]'},
                text_auto='.0f'
            )
            fig.update_layout(template=TEMPLATE_PLOTLY)
            return fig
        else:
            return utworz_pusty_wykres("Zbyt mało danych do wygenerowania heatmapy")
    except Exception as e:
        return utworz_pusty_wykres(f"Błąd: {e}")
