"""Moduł odpowiedzialny za generowanie wykresu analizy hemodynamicznej.

Ten moduł dostarcza funkcję do tworzenia wykresu liniowego, który
przedstawia trend dwóch kluczowych wskaźników hemodynamicznych w czasie:
-   **PP (Pulse Pressure - Ciśnienie Tętna)**: Różnica między ciśnieniem
    skurczowym a rozkurczowym (SYS - DIA).
-   **MAP (Mean Arterial Pressure - Średnie Ciśnienie Tętnicze)**:
    Średnie ciśnienie w tętnicach podczas jednego cyklu pracy serca.

Wykres zawiera również linie referencyjne dla ciśnienia tętna,
co ułatwia interpretację kliniczną wyników.
"""

import plotly.graph_objects as go
from .utils import utworz_pusty_wykres, validate_dataframe
from config import TEMPLATE_PLOTLY, WYSOKOSC_WYKRESU_STANDARD, KOLORY_PARAMETROW


def generate_hemodynamics_chart(df):
    """Generuje wykres trendu wskaźników hemodynamicznych (PP i MAP).

    Tworzy wykres liniowy z dwiema seriami danych:
    1.  Ciśnienie Tętna (PP), obliczone jako `SYS - DIA`.
    2.  Średnie Ciśnienie Tętnicze (MAP), obliczone jako `(SYS + 2*DIA) / 3`.

    Na wykresie umieszczone są poziome linie referencyjne dla PP (40 mmHg
    jako wartość normalna i 60 mmHg jako wartość podwyższona), co ułatwia
    ocenę ryzyka sercowo-naczyniowego.

    Args:
        df (pd.DataFrame): Ramka danych zawierająca przetworzone pomiary,
            w tym kolumny 'Datetime', 'SYS' i 'DIA', na podstawie których
            obliczone są 'PP' i 'MAP'.

    Returns:
        go.Figure: Obiekt wykresu Plotly. W przypadku braku danych lub
            błędu, zwraca pusty wykres z komunikatem.
    """
    required_columns = ['Datetime', 'MAP', 'PP']
    valid, msg = validate_dataframe(df, required_columns)
    if not valid:
        return utworz_pusty_wykres(msg)

    if df.empty:
        return utworz_pusty_wykres()

    try:
        fig = go.Figure()

        # Dodawanie śladów dla MAP i PP
        fig.add_trace(go.Scatter(
            x=df['Datetime'],
            y=df['MAP'],
            mode='lines+markers',
            name='MAP (Średnie ciśnienie tętnicze)',
            line=dict(color=KOLORY_PARAMETROW['MAP'])
        ))

        fig.add_trace(go.Scatter(
            x=df['Datetime'],
            y=df['PP'],
            mode='lines+markers',
            name='PP (Ciśnienie tętna)',
            line=dict(color=KOLORY_PARAMETROW['PP'])
        ))

        # Linie referencyjne dla Ciśnienia Tętna (PP)
        fig.add_hline(
            y=40,
            line_dash="dot",
            line_color="green",
            annotation_text="Normalne PP (≈40 mmHg)",
            annotation_position="bottom right"
        )
        fig.add_hline(
            y=60,
            line_dash="dot",
            line_color="orange",
            annotation_text="Podwyższone PP (≥60 mmHg)",
            annotation_position="top right"
        )

        fig.update_layout(
            title={
                'text': "🔬 Analiza Hemodynamiczna: Trend MAP i PP w Czasie<br>" +
                        "<sub>PP (Pulse Pressure) = SYS - DIA  |  MAP (Mean Arterial Pressure) = (SYS + 2×DIA) / 3</sub>",
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title="Data pomiaru",
            yaxis_title="Wartość [mmHg]",
            template=TEMPLATE_PLOTLY,
            height=WYSOKOSC_WYKRESU_STANDARD,
            legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
            margin=dict(b=100),
            hovermode='x unified'
        )

        return fig

    except Exception as e:
        return utworz_pusty_wykres(f"Błąd: {e}")