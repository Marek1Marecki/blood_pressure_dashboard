"""Moduł odpowiedzialny za generowanie wykresów porównawczych.

Ten moduł dostarcza funkcję do tworzenia wizualizacji porównujących
rozkłady ciśnienia skurczowego (SYS) i rozkurczowego (DIA) w różnych
grupach kategorycznych. Obsługiwane typy wykresów to:

-   **Box Plot (wykres pudełkowy)**: Pokazuje kluczowe statystyki, takie
    jak mediana, kwartyle, zakresy i wartości odstające.
-   **Violin Plot (wykres skrzypcowy)**: Łączy w sobie cechy wykresu
    pudełkowego z wykresem gęstości, co pozwala na dokładniejszą analizę
    rozkładu danych.

Porównania mogą być dokonywane np. względem pory dnia lub typu dnia
(roboczy/weekend).
"""

import plotly.express as px
from .utils import utworz_pusty_wykres
from config import KOLORY_PARAMETROW, TEMPLATE_PLOTLY, WYSOKOSC_WYKRESU_STANDARD


def generate_comparison_chart(df, category_column, chart_type='box'):
    """Generuje wykres porównawczy typu box plot lub violin plot.

    Funkcja tworzy wizualizację, która pozwala na porównanie rozkładów
    wartości ciśnienia skurczowego (SYS) i rozkurczowego (DIA) pomiędzy
    różnymi kategoriami zdefiniowanymi w `category_column`.

    Args:
        df (pd.DataFrame): Ramka danych zawierająca przetworzone pomiary.
        category_column (str): Nazwa kolumny, która ma być użyta do
            grupowania danych (np. 'Godzina Pomiaru' lub 'Typ Dnia').
        chart_type (str, optional): Typ wykresu do wygenerowania.
            Dostępne opcje: 'box' (domyślnie) lub 'violin'.

    Returns:
        go.Figure: Obiekt wykresu Plotly. W przypadku braku danych lub
            błędu, zwraca pusty wykres z komunikatem.
    """
    if df.empty:
        return utworz_pusty_wykres()

    try:
        plot_df = df.dropna(subset=[category_column])
        melted_df = plot_df.melt(
            id_vars=[category_column],
            value_vars=['SYS', 'DIA'],
            var_name='Parametr',
            value_name='Wartość'
        )
        melted_df = melted_df.sort_values(by=category_column)

        if chart_type == 'violin':
            fig = px.violin(
                melted_df, x=category_column, y='Wartość', color='Parametr',
                box=True, points=False,
                title=f"Rozkład gęstości ciśnienia wg: {category_column.replace('_', ' ')}",
                labels={"Wartość": "Wartość pomiaru", category_column: "Kategoria"},
                color_discrete_map=KOLORY_PARAMETROW,
                category_orders={"Parametr": ["SYS", "DIA"]}
            )
        else:  # boxplot
            fig = px.box(
                melted_df, x=category_column, y='Wartość', color='Parametr',
                points="all",
                title=f"Rozkład ciśnienia wg: {category_column.replace('_', ' ')}",
                labels={"Wartość": "Wartość pomiaru", category_column: "Kategoria"},
                color_discrete_map=KOLORY_PARAMETROW,
                category_orders={"Parametr": ["SYS", "DIA"]}
            )

        fig.update_layout(template=TEMPLATE_PLOTLY, height=WYSOKOSC_WYKRESU_STANDARD)
        return fig

    except Exception as e:
        return utworz_pusty_wykres(f"Błąd: {e}")
