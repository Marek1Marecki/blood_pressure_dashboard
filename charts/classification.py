"""
Wykresy klasyfikacji ciśnienia wg aktualnych wytycznych klinicznych
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .utils import utworz_pusty_wykres
from config import (
    PROGI_ESC, KOLORY_ESC, KOLEJNOSC_ESC,
    TEMPLATE_PLOTLY, WYSOKOSC_WYKRESU_DUZY, WYSOKOSC_WYKRESU_MALY
)


def generate_classification_matrix_chart(df):
    """
    Generuje macierz klasyfikacji pomiarów ciśnienia wg aktualnych wytycznych.

    Macierz pokazuje 7 stref klasyfikacji:
    - Optymalne (SYS <120, DIA <70)
    - Prawidłowe (SYS 120-129 lub DIA 70-79)
    - Podwyższone (SYS 130-139 lub DIA 80-89)
    - Izolowane nadciśnienie skurczowe (SYS ≥140, DIA <90)
    - Nadciśnienie 1° (SYS 140-159 lub DIA 90-99)
    - Nadciśnienie 2° (SYS 160-179 lub DIA 100-109)
    - Nadciśnienie 3° (SYS ≥180 lub DIA ≥110)

    Args:
        df: DataFrame z pomiarami

    Returns:
        go.Figure: Wykres Plotly z macierzą klasyfikacji
    """
    if df.empty:
        return utworz_pusty_wykres()

    try:
        fig = go.Figure()

        # Definicja stref klasyfikacji (według aktualnych wytycznych)
        # Strefy są rysowane od tyłu (najniższe priorytety) do przodu (najwyższe)

        strefy = [
            # Optymalne (SYS <120 i DIA <70)
            {
                'x0': 40, 'y0': 60,
                'x1': PROGI_ESC['optymalne']['dia'],
                'y1': PROGI_ESC['optymalne']['sys'],
                'color': KOLORY_ESC['Optymalne'],
                'nazwa': 'Optymalne'
            },

            # Prawidłowe - część dolna (DIA 70-79, SYS <120)
            {
                'x0': PROGI_ESC['optymalne']['dia'],
                'y0': 60,
                'x1': PROGI_ESC['prawidlowe']['dia'],
                'y1': PROGI_ESC['optymalne']['sys'],
                'color': KOLORY_ESC['Prawidłowe'],
                'nazwa': 'Prawidłowe'
            },

            # Prawidłowe - część górna (SYS 120-129, DIA <80)
            {
                'x0': 40,
                'y0': PROGI_ESC['optymalne']['sys'],
                'x1': PROGI_ESC['prawidlowe']['dia'],
                'y1': PROGI_ESC['prawidlowe']['sys'],
                'color': KOLORY_ESC['Prawidłowe'],
                'nazwa': 'Prawidłowe'
            },

            # Podwyższone - część dolna (DIA 80-89, SYS <130)
            {
                'x0': PROGI_ESC['prawidlowe']['dia'],
                'y0': 60,
                'x1': PROGI_ESC['podwyzszone']['dia'],
                'y1': PROGI_ESC['prawidlowe']['sys'],
                'color': KOLORY_ESC['Podwyższone'],
                'nazwa': 'Podwyższone'
            },

            # Podwyższone - część górna (SYS 130-139, DIA <90)
            {
                'x0': 40,
                'y0': PROGI_ESC['prawidlowe']['sys'],
                'x1': PROGI_ESC['podwyzszone']['dia'],
                'y1': PROGI_ESC['podwyzszone']['sys'],
                'color': KOLORY_ESC['Podwyższone'],
                'nazwa': 'Podwyższone'
            },

            # Izolowane nadciśnienie skurczowe (SYS ≥140, DIA <90)
            {
                'x0': 40,
                'y0': PROGI_ESC['podwyzszone']['sys'],
                'x1': PROGI_ESC['podwyzszone']['dia'],
                'y1': 220,
                'color': KOLORY_ESC['Izolowane nadciśnienie skurczowe'],
                'nazwa': 'Izolowane nadciśnienie skurczowe'
            },

            # Nadciśnienie 1° - część dolna (DIA 90-99, SYS <160)
            {
                'x0': PROGI_ESC['podwyzszone']['dia'],
                'y0': 60,
                'x1': PROGI_ESC['nadcisnienie_1']['dia'],
                'y1': PROGI_ESC['nadcisnienie_1']['sys'],
                'color': KOLORY_ESC['Nadciśnienie 1°'],
                'nazwa': 'Nadciśnienie 1°'
            },

            # Nadciśnienie 1° - część środkowa (SYS 140-159, DIA 90-99)
            {
                'x0': PROGI_ESC['podwyzszone']['dia'],
                'y0': PROGI_ESC['podwyzszone']['sys'],
                'x1': PROGI_ESC['nadcisnienie_1']['dia'],
                'y1': PROGI_ESC['nadcisnienie_1']['sys'],
                'color': KOLORY_ESC['Nadciśnienie 1°'],
                'nazwa': 'Nadciśnienie 1°'
            },

            # Nadciśnienie 2° - część dolna (DIA 100-109, SYS <180)
            {
                'x0': PROGI_ESC['nadcisnienie_1']['dia'],
                'y0': 60,
                'x1': PROGI_ESC['nadcisnienie_2']['dia'],
                'y1': PROGI_ESC['nadcisnienie_2']['sys'],
                'color': KOLORY_ESC['Nadciśnienie 2°'],
                'nazwa': 'Nadciśnienie 2°'
            },

            # Nadciśnienie 2° - część środkowa (SYS 160-179, DIA 90-109)
            {
                'x0': PROGI_ESC['podwyzszone']['dia'],
                'y0': PROGI_ESC['nadcisnienie_1']['sys'],
                'x1': PROGI_ESC['nadcisnienie_2']['dia'],
                'y1': PROGI_ESC['nadcisnienie_2']['sys'],
                'color': KOLORY_ESC['Nadciśnienie 2°'],
                'nazwa': 'Nadciśnienie 2°'
            },

            # Nadciśnienie 3° - część dolna (DIA ≥110, wszystkie SYS)
            {
                'x0': PROGI_ESC['nadcisnienie_2']['dia'],
                'y0': 60,
                'x1': 120,
                'y1': 220,
                'color': KOLORY_ESC['Nadciśnienie 3°'],
                'nazwa': 'Nadciśnienie 3°'
            },

            # Nadciśnienie 3° - część górna (SYS ≥180, DIA <110)
            {
                'x0': PROGI_ESC['podwyzszone']['dia'],
                'y0': PROGI_ESC['nadcisnienie_2']['sys'],
                'x1': PROGI_ESC['nadcisnienie_2']['dia'],
                'y1': 220,
                'color': KOLORY_ESC['Nadciśnienie 3°'],
                'nazwa': 'Nadciśnienie 3°'
            },
        ]

        # Konwersja stref na shapes dla Plotly
        shapes = [
            dict(
                type="rect",
                xref="x",
                yref="y",
                x0=s['x0'],
                y0=s['y0'],
                x1=s['x1'],
                y1=s['y1'],
                fillcolor=s['color'],
                opacity=0.3,
                layer="below",
                line_width=0
            ) for s in strefy
        ]

        # Dodanie punktów pomiarowych
        fig.add_trace(go.Scatter(
            x=df['DIA'],
            y=df['SYS'],
            mode='markers',
            marker=dict(
                color='darkblue',
                size=8,
                opacity=0.6,
                line=dict(width=1, color='white')
            ),
            hovertext=df.apply(
                lambda row: f"{row['Datetime'].strftime('%Y-%m-%d %H:%M')}<br>Kategoria: {row['Kategoria']}",
                axis=1
            ),
            hovertemplate='<b>%{hovertext}</b><br>SYS: %{y}<br>DIA: %{x}<extra></extra>',
            showlegend=False
        ))

        # Konfiguracja layoutu
        fig.update_layout(
            title="Macierz Klasyfikacji Pomiarów Ciśnienia (wg aktualnych wytycznych)",
            xaxis_title="Ciśnienie Rozkurczowe (DIA) [mmHg]",
            yaxis_title="Ciśnienie Skurczowe (SYS) [mmHg]",
            xaxis=dict(
                range=[min(40, df['DIA'].min() - 5), max(120, df['DIA'].max() + 5)],
                gridcolor='lightgray'
            ),
            yaxis=dict(
                range=[min(60, df['SYS'].min() - 5), max(220, df['SYS'].max() + 5)],
                gridcolor='lightgray'
            ),
            shapes=shapes,
            template=TEMPLATE_PLOTLY,
            height=WYSOKOSC_WYKRESU_DUZY,
            hovermode='closest'
        )

        return fig

    except Exception as e:
        return utworz_pusty_wykres(f"Błąd podczas generowania macierzy: {e}")


def generate_esc_category_bar_chart(df):
    """
    Generuje wykres słupkowy liczebności kategorii wg aktualnych wytycznych.

    Args:
        df: DataFrame z pomiarami

    Returns:
        go.Figure: Wykres słupkowy Plotly
    """
    if df.empty:
        return utworz_pusty_wykres()

    try:
        # Zliczanie pomiarów w każdej kategorii
        counts = df['Kategoria'].value_counts().reset_index()
        counts.columns = ['Kategoria', 'Liczba']

        # Dodanie procentów
        total = counts['Liczba'].sum()
        counts['Procent'] = (counts['Liczba'] / total * 100).round(1)

        # Sortowanie według zdefiniowanej kolejności
        counts['Kategoria'] = pd.Categorical(
            counts['Kategoria'],
            categories=KOLEJNOSC_ESC,
            ordered=True
        )
        counts = counts.sort_values('Kategoria')

        # Tworzenie wykresu słupkowego
        fig = px.bar(
            counts,
            x='Kategoria',
            y='Liczba',
            color='Kategoria',
            title="🧮 Klasyfikacja Pomiarów Ciśnienia (wg aktualnych wytycznych)",
            template=TEMPLATE_PLOTLY,
            color_discrete_map=KOLORY_ESC,
            text=counts.apply(
                lambda row: f"{int(row['Liczba'])}<br>({row['Procent']:.1f}%)",
                axis=1
            )
        )

        fig.update_traces(
            textposition='outside',
            textfont_size=12
        )

        fig.update_layout(
            xaxis_title="Kategoria ciśnienia",
            yaxis_title="Liczba pomiarów",
            showlegend=False,
            height=WYSOKOSC_WYKRESU_MALY,
            xaxis={
                'categoryorder': 'array',
                'categoryarray': KOLEJNOSC_ESC
            },
            yaxis={'gridcolor': 'lightgray'}
        )

        return fig

    except Exception as e:
        return utworz_pusty_wykres(f"Błąd podczas generowania wykresu słupkowego: {e}")