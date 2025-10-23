"""
Narzędzia wspólne dla wszystkich wykresów
"""

import plotly.graph_objects as go
from config import TEMPLATE_PLOTLY


def utworz_pusty_wykres(tytul="Brak danych do wyświetlenia"):
    """
    Tworzy pusty wykres z komunikatem.

    Args:
        tytul: Komunikat do wyświetlenia

    Returns:
        go.Figure: Pusty wykres Plotly
    """
    return go.Figure().update_layout(
        title=tytul,
        xaxis={'visible': False},
        yaxis={'visible': False},
        template=TEMPLATE_PLOTLY
    )