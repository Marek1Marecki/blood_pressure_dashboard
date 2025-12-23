

"""Moduł odpowiedzialny za generowanie heatmapy ciśnienia.

Ten moduł dostarcza funkcję do tworzenia heatmapy (mapy cieplnej),
która wizualizuje średnie wartości ciśnienia skurczowego (SYS)
w zależności od dnia i godziny pomiaru.

Heatmapa pozwala na szybką identyfikację wzorców i trendów,
np. dni tygodnia lub pór dnia, w których ciśnienie jest systematycznie
wyższe lub niższe.
"""

import plotly.express as px
from .utils import utworz_pusty_wykres, validate_dataframe
from config import TEMPLATE_PLOTLY


def generate_heatmap_chart(df):
    """Generuje heatmapę średniego ciśnienia skurczowego (SYS).

    Funkcja tworzy tabelę przestawną, gdzie wiersze odpowiadają dniom,
    a kolumny godzinom pomiarów. Wartości w komórkach tabeli to średnie
    ciśnienie skurczowe (SYS) dla danego dnia i godziny.

    Następnie, na podstawie tej tabeli, generowana jest heatmapa,
    gdzie kolor każdej komórki odpowiada wartości średniego ciśnienia,
    co pozwala na łatwą wizualną analizę.

    Args:
        df (pd.DataFrame): Ramka danych zawierająca przetworzone pomiary,
            w tym kolumny 'Dzień', 'Hour' i 'SYS'.

    Returns:
        go.Figure: Obiekt wykresu Plotly. W przypadku niewystarczającej
            ilości danych do stworzenia tabeli przestawnej lub błędu,
            zwraca pusty wykres z komunikatem.
    """
    valid, msg = validate_dataframe(df, ['Dzień', 'Hour', 'SYS'])
    if not valid:
        return utworz_pusty_wykres(msg)

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
