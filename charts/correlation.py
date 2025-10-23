"""
=== charts/correlation.py ===
Wykres korelacji SYS-DIA
"""

import plotly.express as px
from .utils import utworz_pusty_wykres
from config import TEMPLATE_PLOTLY


def generate_correlation_chart(df):
    """Generuje wykres korelacji SYS-DIA z uwzględnieniem pulsu."""
    if df.empty:
        return utworz_pusty_wykres()

    try:
        fig = px.scatter(
            df, x='DIA', y='SYS', color='PUL', size='PUL',
            title="Zależność SYS–DIA (kolor i rozmiar = puls)",
            labels={'SYS': 'Ciśnienie Skurczowe', 'DIA': 'Ciśnienie Rozkurczowe', 'PUL': 'Puls'},
            color_continuous_scale='Viridis'
        )
        fig.update_layout(template=TEMPLATE_PLOTLY)
        return fig
    except Exception as e:
        return utworz_pusty_wykres(f"Błąd: {e}")

