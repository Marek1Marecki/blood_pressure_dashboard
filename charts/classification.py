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
    Wersja ostateczna - definiuje każdy prostokąt siatki osobno, bez nakładania.
    """
    if df.empty:
        return utworz_pusty_wykres()

    try:
        fig = go.Figure()

        min_dia, max_dia = 40, 120
        min_sys, max_sys = 60, 220

        p = PROGI_ESC # Skrót dla czytelności

        strefy = [
            # --- SEKCJA 1: Strefy "normalne" (DIA < 90, SYS < 140) ---
            # 1. Optymalne
            {'x0': min_dia, 'y0': min_sys, 'x1': p['optymalne']['dia'], 'y1': p['optymalne']['sys'], 'color': KOLORY_ESC['Optymalne'], 'nazwa': 'Optymalne'},
            # 2. Prawidłowe (2 prostokąty tworzące "L")
            {'x0': p['optymalne']['dia'], 'y0': min_sys, 'x1': p['prawidlowe']['dia'], 'y1': p['optymalne']['sys'], 'color': KOLORY_ESC['Prawidłowe'], 'nazwa': 'Prawidłowe'},
            {'x0': min_dia, 'y0': p['optymalne']['sys'], 'x1': p['prawidlowe']['dia'], 'y1': p['prawidlowe']['sys'], 'color': KOLORY_ESC['Prawidłowe'], 'nazwa': 'Prawidłowe'},
            # 3. Podwyższone (2 prostokąty tworzące "L")
            {'x0': p['prawidlowe']['dia'], 'y0': min_sys, 'x1': p['podwyzszone']['dia'], 'y1': p['prawidlowe']['sys'], 'color': KOLORY_ESC['Podwyższone'], 'nazwa': 'Podwyższone'},
            {'x0': min_dia, 'y0': p['prawidlowe']['sys'], 'x1': p['podwyzszone']['dia'], 'y1': p['podwyzszone']['sys'], 'color': KOLORY_ESC['Podwyższone'], 'nazwa': 'Podwyższone'},

            # --- SEKCJA 2: Izolowane Nadciśnienie Skurczowe (ISH) ---
            # 4. ISH (jeden duży prostokąt)
            {'x0': min_dia, 'y0': p['podwyzszone']['sys'], 'x1': p['podwyzszone']['dia'], 'y1': max_sys, 'color': KOLORY_ESC['Izolowane nadciśnienie skurczowe'], 'nazwa': 'Izolowane nadciśnienie skurczowe'},

            # --- SEKCJA 3: Siatka nadciśnienia (DIA >= 90) ---
            # Kolumna DIA [90, 100)
            # 5. Nadciśnienie 1 (bo DIA jest w N1)
            {'x0': p['podwyzszone']['dia'], 'y0': min_sys, 'x1': p['nadcisnienie_1']['dia'], 'y1': p['podwyzszone']['sys'], 'color': KOLORY_ESC['Nadciśnienie 1°'], 'nazwa': 'Nadciśnienie 1°'},
            # 6. Nadciśnienie 1 (max(N1_DIA, N1_SYS))
            {'x0': p['podwyzszone']['dia'], 'y0': p['podwyzszone']['sys'], 'x1': p['nadcisnienie_1']['dia'], 'y1': p['nadcisnienie_1']['sys'], 'color': KOLORY_ESC['Nadciśnienie 1°'], 'nazwa': 'Nadciśnienie 1°'},
            # 7. Nadciśnienie 2 (max(N1_DIA, N2_SYS))
            {'x0': p['podwyzszone']['dia'], 'y0': p['nadcisnienie_1']['sys'], 'x1': p['nadcisnienie_1']['dia'], 'y1': p['nadcisnienie_2']['sys'], 'color': KOLORY_ESC['Nadciśnienie 2°'], 'nazwa': 'Nadciśnienie 2°'},
            # 8. Nadciśnienie 3 (max(N1_DIA, N3_SYS))
            {'x0': p['podwyzszone']['dia'], 'y0': p['nadcisnienie_2']['sys'], 'x1': p['nadcisnienie_1']['dia'], 'y1': max_sys, 'color': KOLORY_ESC['Nadciśnienie 3°'], 'nazwa': 'Nadciśnienie 3°'},

            # Kolumna DIA [100, 110)
            # 9. Nadciśnienie 2 (bo DIA jest w N2)
            {'x0': p['nadcisnienie_1']['dia'], 'y0': min_sys, 'x1': p['nadcisnienie_2']['dia'], 'y1': p['nadcisnienie_1']['sys'], 'color': KOLORY_ESC['Nadciśnienie 2°'], 'nazwa': 'Nadciśnienie 2°'},
            # 10. Nadciśnienie 2 (max(N2_DIA, N2_SYS))
            {'x0': p['nadcisnienie_1']['dia'], 'y0': p['nadcisnienie_1']['sys'], 'x1': p['nadcisnienie_2']['dia'], 'y1': p['nadcisnienie_2']['sys'], 'color': KOLORY_ESC['Nadciśnienie 2°'], 'nazwa': 'Nadciśnienie 2°'},
            # 11. Nadciśnienie 3 (max(N2_DIA, N3_SYS))
            {'x0': p['nadcisnienie_1']['dia'], 'y0': p['nadcisnienie_2']['sys'], 'x1': p['nadcisnienie_2']['dia'], 'y1': max_sys, 'color': KOLORY_ESC['Nadciśnienie 3°'], 'nazwa': 'Nadciśnienie 3°'},

            # Kolumna DIA >= 110
            # 12. Nadciśnienie 3 (bo DIA jest w N3)
            {'x0': p['nadcisnienie_2']['dia'], 'y0': min_sys, 'x1': max_dia, 'y1': max_sys, 'color': KOLORY_ESC['Nadciśnienie 3°'], 'nazwa': 'Nadciśnienie 3°'},
        ]

        shapes = [
            dict(
                type="rect", xref="x", yref="y",
                x0=s['x0'], y0=s['y0'], x1=s['x1'], y1=s['y1'],
                fillcolor=s['color'],
                opacity=0.3,
                layer="below",
                line_width=0
            ) for s in strefy
        ]

        # Dodanie niewidocznych śladów dla legendy (w kolejności KOLEJNOSC_ESC)
        for kategoria in KOLEJNOSC_ESC:
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(size=10, color=KOLORY_ESC[kategoria]),
                name=kategoria,
                showlegend=True
            ))

        # Dodanie punktów pomiarowych
        fig.add_trace(go.Scatter(
            x=df['DIA'], y=df['SYS'], mode='markers',
            marker=dict(color='darkblue', size=8, opacity=0.8, line=dict(width=1, color='white')),
            hovertext=df.apply(lambda r: f"{r['Datetime'].strftime('%Y-%m-%d %H:%M')}<br>Kategoria: {r['Kategoria']}", axis=1),
            hovertemplate='<b>%{hovertext}</b><br>SYS: %{y}<br>DIA: %{x}<extra></extra>',
            name='Pomiary',
            showlegend=True
        ))

        # Konfiguracja layoutu
        fig.update_layout(
            title="Macierz Klasyfikacji Pomiarów Ciśnienia (wg aktualnych wytycznych)",
            xaxis_title="Ciśnienie Rozkurczowe (DIA) [mmHg]",
            yaxis_title="Ciśnienie Skurczowe (SYS) [mmHg]",
            xaxis=dict(range=[min(min_dia, df['DIA'].min() - 5), max(max_dia, df['DIA'].max() + 5)], gridcolor='rgba(200,200,200,0.5)'),
            yaxis=dict(range=[min(min_sys, df['SYS'].min() - 5), max(max_sys, df['SYS'].max() + 5)], gridcolor='rgba(200,200,200,0.5)'),
            shapes=shapes,
            template='plotly_white',
            height=WYSOKOSC_WYKRESU_DUZY,
            hovermode='closest',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
        return fig

    except Exception as e:
        return utworz_pusty_wykres(f"Błąd podczas generowania macierzy: {e}")

def generate_esc_category_bar_chart(df):
    """
    Generuje wykres słupkowy liczebności kategorii wg aktualnych wytycznych.
    """
    if df.empty:
        return utworz_pusty_wykres()
    try:
        counts = df['Kategoria'].value_counts().reset_index()
        counts.columns = ['Kategoria', 'Liczba']
        total = counts['Liczba'].sum()
        counts['Procent'] = (counts['Liczba'] / total * 100).round(1)
        counts['Kategoria'] = pd.Categorical(counts['Kategoria'], categories=KOLEJNOSC_ESC, ordered=True)
        counts = counts.sort_values('Kategoria')
        fig = px.bar(
            counts, x='Kategoria', y='Liczba', color='Kategoria',
            title="🧮 Klasyfikacja Pomiarów Ciśnienia (wg aktualnych wytycznych)",
            template=TEMPLATE_PLOTLY, color_discrete_map=KOLORY_ESC,
            text=counts.apply(lambda r: f"{int(r['Liczba'])}<br>({r['Procent']:.1f}%)", axis=1)
        )
        fig.update_traces(textposition='outside', textfont_size=12)
        fig.update_layout(
            xaxis_title="Kategoria ciśnienia", yaxis_title="Liczba pomiarów", showlegend=False,
            height=WYSOKOSC_WYKRESU_MALY,
            xaxis={'categoryorder': 'array', 'categoryarray': KOLEJNOSC_ESC},
            yaxis={'gridcolor': 'lightgray'}, margin=dict(t=80)
        )
        return fig
    except Exception as e:
        return utworz_pusty_wykres(f"Błąd podczas generowania wykresu słupkowego: {e}")