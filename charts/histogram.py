"""Moduł odpowiedzialny za generowanie histogramów rozkładu danych.

Ten moduł dostarcza funkcję do tworzenia histogramów, które wizualizują
rozkład (częstotliwość występowania) wartości dla wybranych parametrów
pomiarowych, takich jak ciśnienie skurczowe (SYS), rozkurczowe (DIA)
czy puls (PUL).

Histogramy są użytecznym narzędziem do zrozumienia, jakie wartości
występują najczęściej, czy rozkład jest symetryczny, oraz do identyfikacji
potencjalnych wartości odstających. Wykresy zawierają również linie
progowe i linię średniej, co ułatwia interpretację.
"""

import plotly.express as px
from .utils import utworz_pusty_wykres
from config import PROGI_ESC, TEMPLATE_PLOTLY, KOLORY_PARAMETROW


def generate_histogram_chart(df, selected_column):
    """Generuje histogram rozkładu wartości dla wybranej kolumny.

    Tworzy wykres histogramu, który pokazuje, jak często różne wartości
    pojawiają się w wybranej kolumnie danych (np. 'SYS', 'DIA', 'PUL').
    Liczba słupków (bins) jest ustawiona na 20, aby zapewnić odpowiednią
    szczegółowość rozkładu.

    Na wykresie zaznaczone są dodatkowo:
    -   Pionowa linia przerywana wskazująca średnią wartość.
    -   Pionowe linie kropkowane wskazujące progi kliniczne dla ciśnienia
        (jeśli `selected_column` to 'SYS' lub 'DIA').

    Args:
        df (pd.DataFrame): Ramka danych zawierająca przetworzone pomiary.
        selected_column (str): Nazwa kolumny, dla której ma być
            wygenerowany histogram (np. 'SYS', 'DIA', 'PUL').

    Returns:
        go.Figure: Obiekt wykresu Plotly. W przypadku braku danych lub
            błędu, zwraca pusty wykres z komunikatem.
    """
    if df.empty:
        return utworz_pusty_wykres()

    try:
        # Kolory dla histogramu zgodne z wykresem trendu
        color_map = {
            'SYS': KOLORY_PARAMETROW['SYS'],
            'DIA': KOLORY_PARAMETROW['DIA'],
            'PUL': KOLORY_PARAMETROW['PUL']
        }

        fig = px.histogram(
            df,
            x=selected_column,
            nbins=20,
            title=f"Rozkład wartości dla: {selected_column}",
            color_discrete_sequence=[color_map.get(selected_column, 'blue')]
        )

        mean_val = df[selected_column].mean()
        fig.add_vline(x=mean_val, line_dash="dash", line_color="black",
                     annotation_text=f"Średnia: {mean_val:.1f}",
                     annotation_position="top right")

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