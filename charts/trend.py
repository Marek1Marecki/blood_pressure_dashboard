"""Moduł odpowiedzialny za generowanie wykresu trendu w czasie.

Ten moduł dostarcza funkcję do tworzenia wykresu liniowego, który
wizualizuje zmiany wartości ciśnienia skurczowego (SYS), rozkurczowego
(DIA) oraz pulsu (PUL) w funkcji czasu.

Wykres ten jest kluczowym narzędziem do obserwacji długoterminowych
trendów, sezonowych wahań oraz wpływu zmian w stylu życia czy leczeniu
na wartości ciśnienia. Na wykresie umieszczone są również linie progowe
dla ciśnienia skurczowego, co ułatwia szybką ocenę pomiarów.
"""

import plotly.graph_objects as go
from .utils import utworz_pusty_wykres, validate_dataframe
from config import KOLORY_PARAMETROW, PROGI_ESC, TEMPLATE_PLOTLY


def generate_trend_chart(df):
    """Generuje wykres liniowy trendu ciśnienia i pulsu w czasie.

    Funkcja tworzy wykres liniowy, na którym oś X reprezentuje czas,
    a oś Y wartości pomiarów. Na wykresie przedstawione są trzy serie
    danych: ciśnienie skurczowe (SYS), ciśnienie rozkurczowe (DIA)
    oraz puls (PUL).

    Dodatkowo, na wykresie umieszczone są poziome linie referencyjne
    oznaczające kluczowe progi dla ciśnienia skurczowego (120 mmHg
    dla ciśnienia optymalnego i 140 mmHg dla podwyższonego), co ułatwia
    interpretację wizualną.

    Args:
        df (pd.DataFrame): Ramka danych zawierająca przetworzone pomiary,
            w tym kolumny 'Datetime', 'SYS', 'DIA' i 'PUL'.

    Returns:
        go.Figure: Obiekt wykresu Plotly. W przypadku braku danych lub
            błędu, zwraca pusty wykres z komunikatem.
    """
    valid, msg = validate_dataframe(df, ['Datetime', 'SYS', 'DIA', 'PUL'])
    if not valid:
        return utworz_pusty_wykres(msg)

    if df.empty:
        return utworz_pusty_wykres()

    try:
        fig = go.Figure()

        # Dodawanie śladów dla każdego parametru (bez MAP i PP)
        parametry = [
            ('SYS', 'SYS (Skurczowe)', 'lines+markers'),
            ('DIA', 'DIA (Rozkurczowe)', 'lines+markers'),
            ('PUL', 'Puls', 'lines+markers'),
        ]

        for param, nazwa, mode in parametry:
            fig.add_trace(go.Scatter(
                x=df['Datetime'],
                y=df[param],
                mode=mode,
                name=nazwa,
                line=dict(color=KOLORY_PARAMETROW[param])
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
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            margin=dict(b=100),  # Zwiększony dolny margines
            template=TEMPLATE_PLOTLY,
            hovermode='x unified'
        )

        return fig

    except Exception as e:
        return utworz_pusty_wykres(f"Błąd: {e}")