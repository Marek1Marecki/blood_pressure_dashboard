"""Moduł zawierający funkcje pomocnicze dla modułów wykresów.

Ten plik gromadzi wspólne narzędzia i funkcje, które są wykorzystywane
przez różne moduły generujące wykresy w aplikacji. Celem jest unikanie
powielania kodu i centralizacja standardowych operacji.
"""

import plotly.graph_objects as go
from config import TEMPLATE_PLOTLY


def utworz_pusty_wykres(tytul="Brak danych do wyświetlenia"):
    """Tworzy pusty obiekt wykresu Plotly z wyśrodkowanym komunikatem.

    Ta funkcja jest używana w całej aplikacji do generowania standardowego,
    pustego wykresu w sytuacjach, gdy brakuje danych do wizualizacji lub
    wystąpił błąd. Zapobiega to awariom aplikacji i informuje użytkownika
    o problemie w spójny sposób.

    Args:
        tytul (str, optional): Tekst, który ma zostać wyświetlony na
            środku pustego wykresu. Domyślnie "Brak danych do wyświetlenia".

    Returns:
        go.Figure: Pusty obiekt `plotly.graph_objects.Figure` z ukrytymi
            osiami i widocznym tytułem.
    """
    return go.Figure().update_layout(
        title=tytul,
        xaxis={'visible': False},
        yaxis={'visible': False},
        template=TEMPLATE_PLOTLY
    )