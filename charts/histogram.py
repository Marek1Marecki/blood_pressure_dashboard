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
import plotly.graph_objects as go
import numpy as np
from .utils import utworz_pusty_wykres, validate_dataframe

from config import PROGI_ESC, TEMPLATE_PLOTLY, KOLORY_PARAMETROW, KOLORY_ESC, KOLEJNOSC_ESC


def get_color_for_value(value, column_type):
    """
    Zwraca kolor HEX dla danej wartości SYS lub DIA zgodnie z poprawnymi, ciągłymi zakresami.
    Sprawdza warunki od najwyższej kategorii do najniższej.
    """
    if column_type == 'SYS':
        if value >= 180: return KOLORY_ESC['Nadciśnienie 3°']
        if value >= 160: return KOLORY_ESC['Nadciśnienie 2°']
        if value >= 140: return KOLORY_ESC['Nadciśnienie 1°']
        if value >= 130: return KOLORY_ESC['Podwyższone']
        if value >= 120: return KOLORY_ESC['Prawidłowe']
        return KOLORY_ESC['Optymalne']  # Wszystko poniżej 120

    elif column_type == 'DIA':
        if value >= 110: return KOLORY_ESC['Nadciśnienie 3°']
        if value >= 100: return KOLORY_ESC['Nadciśnienie 2°']
        if value >= 90: return KOLORY_ESC['Nadciśnienie 1°']
        if value >= 80: return KOLORY_ESC['Podwyższone']
        if value >= 70: return KOLORY_ESC['Prawidłowe']
        return KOLORY_ESC['Optymalne']  # Wszystko poniżej 70

    return KOLORY_PARAMETROW.get(column_type, 'grey')


def generate_histogram_chart(df, selected_column):
    """Generuje histogram rozkładu z kolorowaniem słupków wg kategorii."""
    valid, msg = validate_dataframe(df, [selected_column])
    if not valid:
        return utworz_pusty_wykres(msg)

    try:
        # Dla PUL używamy starego, prostego wykresu
        if selected_column == 'PUL':
            fig = px.histogram(
                df, x=selected_column, nbins=30,
                title=f"Rozkład wartości dla: {selected_column}",
                color_discrete_sequence=[KOLORY_PARAMETROW['PUL']]
            )
        else:
            # Dla SYS i DIA budujemy wykres ręcznie
            fig = go.Figure()

            # 1. Oblicz dane histogramu
            counts, bin_edges = np.histogram(df[selected_column], bins=30)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

            # 2. Określ kolor dla każdego słupka
            bar_colors = [get_color_for_value(center, selected_column) for center in bin_centers]

            # 3. Dodaj słupki do wykresu
            fig.add_trace(go.Bar(
                x=bin_centers,
                y=counts,
                marker_color=bar_colors,
                showlegend=False
            ))

            # 4. Stwórz ręczną legendę
            # Używamy "niewidzialnych" śladów, aby pokazać elementy w legendzie
            for kategoria in KOLEJNOSC_ESC:
                if kategoria in KOLORY_ESC:  # Upewnij się, że kategoria ma zdefiniowany kolor
                    fig.add_trace(go.Bar(
                        x=[None], y=[None], name=kategoria,
                        marker_color=KOLORY_ESC[kategoria]
                    ))

            fig.update_layout(
                title=f"Rozkład wartości dla: {selected_column}",
                legend_title="Kategorie ciśnienia"
            )

        # Linia średniej wartości (wspólna dla obu typów wykresów)
        mean_val = df[selected_column].mean()
        fig.add_vline(x=mean_val, line_dash="dash", line_color="black",
                      annotation_text=f"Średnia: {mean_val:.1f}",
                      annotation_position="top left")

        # Wspólne ustawienia layoutu
        fig.update_layout(
            template=TEMPLATE_PLOTLY,
            xaxis_title="Wartość",
            yaxis_title="Liczba pomiarów (częstotliwość)",
            bargap=0.02  # Niewielka przerwa między słupkami
        )
        return fig

    except Exception as e:
        return utworz_pusty_wykres(f"Błąd: {e}")