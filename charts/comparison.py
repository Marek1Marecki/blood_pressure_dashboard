"""
=== charts/comparison.py ===
Wykresy porównawcze (boxplot, violin)
"""

import plotly.express as px
from .utils import utworz_pusty_wykres
from config import KOLORY_PARAMETROW, TEMPLATE_PLOTLY, WYSOKOSC_WYKRESU_STANDARD


def generate_comparison_chart(df, category_column, chart_type='box'):
    """Generuje wykres porównawczy (boxplot lub violin)."""
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
