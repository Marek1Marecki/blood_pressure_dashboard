"""Moduł odpowiedzialny za generowanie wykresów klasyfikacyjnych.

Ten moduł dostarcza funkcje do tworzenia dwóch kluczowych wizualizacji
związanych z klasyfikacją pomiarów ciśnienia krwi:

1.  **Macierz Klasyfikacji**: Wykres punktowy (scatter plot), gdzie każdy
    pomiar jest umieszczony na tle siatki kategorii ciśnienia (np.
    optymalne, prawidłowe, nadciśnienie), co pozwala na wizualną ocenę,
    do której kategorii wpada dany pomiar.
2.  **Wykres Słupkowy Kategorii**: Wykres pokazujący liczbę i procentowy
    udział pomiarów w każdej zdefiniowanej kategorii ciśnienia.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .utils import utworz_pusty_wykres
from config import (
    PROGI_ESC, KOLORY_ESC, KOLEJNOSC_ESC,
    TEMPLATE_PLOTLY, WYSOKOSC_WYKRESU_DUZY
)

def generate_classification_matrix_chart(df):
    """Generuje macierz klasyfikacji, wizualizując pomiary na tle kategorii.

    Tworzy wykres punktowy, gdzie oś X reprezentuje ciśnienie rozkurczowe
    (DIA), a oś Y ciśnienie skurczowe (SYS). Każdy punkt na wykresie
    odpowiada jednemu pomiarowi. Tło wykresu jest pokolorowane zgodnie
    z siatką kategorii ciśnienia (np. "Optymalne", "Nadciśnienie 1°"),
    co pozwala na natychmiastową wizualną identyfikację, do której
    kategorii należy dany pomiar.

    Args:
        df (pd.DataFrame): Ramka danych zawierająca przetworzone pomiary,
            w tym kolumny 'SYS' i 'DIA'.

    Returns:
        go.Figure: Obiekt wykresu Plotly. W przypadku braku danych lub
            błędu, zwraca pusty wykres z komunikatem.
    """
    if df.empty:
        return utworz_pusty_wykres()

    try:
        fig = go.Figure()

        min_dia, max_dia = 40, 120
        min_sys, max_sys = 60, 200

        p = PROGI_ESC # Skrót dla czytelności

        strefy = [
            # 1. Optymalne
            {'x0': min_dia, 'y0': min_sys, 'x1': p['optymalne']['dia'], 'y1': p['optymalne']['sys'], 'color': KOLORY_ESC['Optymalne'], 'nazwa': 'Optymalne'},

            # 2. Prawidłowe (2 prostokąty tworzące "L")
            {'x0': min_dia, 'y0': p['prawidlowe']['sys'], 'x1': p['prawidlowe']['dia'], 'y1': p['podwyzszone']['sys'], 'color': KOLORY_ESC['Prawidłowe'], 'nazwa': 'Prawidłowe'},
            {'x0': p['prawidlowe']['dia'], 'y0': min_sys, 'x1': p['podwyzszone']['dia'], 'y1': p['podwyzszone']['sys'], 'color': KOLORY_ESC['Prawidłowe'], 'nazwa': 'Prawidłowe'},

            # 3. Podwyższone (2 prostokąty tworzące "L")
            {'x0': min_dia, 'y0': p['podwyzszone']['sys'], 'x1': p['podwyzszone']['dia'], 'y1': p['nadcisnienie_1']['sys'], 'color': KOLORY_ESC['Podwyższone'], 'nazwa': 'Podwyższone'},
            {'x0': p['podwyzszone']['dia'], 'y0': min_sys, 'x1': p['nadcisnienie_1']['dia'], 'y1': p['nadcisnienie_1']['sys'], 'color': KOLORY_ESC['Podwyższone'], 'nazwa': 'Podwyższone'},

            # 4. ISH (jeden duży prostokąt) OK
            {'x0': min_dia, 'y0': p['nadcisnienie_1']['sys'], 'x1': p['nadcisnienie_1']['dia'], 'y1': max_sys, 'color': KOLORY_ESC['Izolowane nadciśnienie skurczowe'], 'nazwa': 'Izolowane nadciśnienie skurczowe'},

            # 5. Nadciśnienie 1
            {'x0': p['nadcisnienie_1']['dia'], 'y0': min_sys, 'x1': p['nadcisnienie_2']['dia'], 'y1': p['nadcisnienie_2']['sys'], 'color': KOLORY_ESC['Nadciśnienie 1°'], 'nazwa': 'Nadciśnienie 1°'},

            # 9. Nadciśnienie 2
            {'x0': p['nadcisnienie_1']['dia'], 'y0': p['nadcisnienie_2']['sys'], 'x1': p['nadcisnienie_2']['dia'], 'y1': p['nadcisnienie_3']['sys'], 'color': KOLORY_ESC['Nadciśnienie 2°'], 'nazwa': 'Nadciśnienie 2°'},
            {'x0': p['nadcisnienie_2']['dia'], 'y0': min_sys, 'x1': p['nadcisnienie_3']['dia'], 'y1': p['nadcisnienie_3']['sys'], 'color': KOLORY_ESC['Nadciśnienie 2°'], 'nazwa': 'Nadciśnienie 2°'},

            {'x0': p['nadcisnienie_1']['dia'], 'y0': p['nadcisnienie_3']['sys'], 'x1': p['nadcisnienie_3']['dia'], 'y1': max_sys, 'color': KOLORY_ESC['Nadciśnienie 3°'], 'nazwa': 'Nadciśnienie 3°'},
            {'x0': p['nadcisnienie_3']['dia'], 'y0': min_sys, 'x1': max_dia, 'y1': max_sys, 'color': KOLORY_ESC['Nadciśnienie 3°'], 'nazwa': 'Nadciśnienie 3°'},
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
    """Generuje wykres słupkowy pokazujący rozkład pomiarów w kategoriach.

    Funkcja zlicza, ile pomiarów wpada do każdej z predefiniowanych
    kategorii ciśnienia (zgodnie z kolumną 'Kategoria' w ramce danych).
    Następnie tworzy wykres słupkowy, gdzie każdy słupek odpowiada jednej
    kategorii, a jego wysokość reprezentuje liczbę pomiarów. Dodatkowo,
    na słupkach wyświetlane są etykiety z dokładną liczbą i udziałem
    procentowym.

    Args:
        df (pd.DataFrame): Ramka danych zawierająca przetworzone pomiary,
            w tym kolumnę 'Kategoria'.

    Returns:
        go.Figure: Obiekt wykresu Plotly. W przypadku braku danych lub
            błędu, zwraca pusty wykres z komunikatem.
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
            height=WYSOKOSC_WYKRESU_DUZY,
            xaxis={'categoryorder': 'array', 'categoryarray': KOLEJNOSC_ESC},
            yaxis={'gridcolor': 'lightgray'}, margin=dict(t=80)
        )
        return fig
    except Exception as e:
        return utworz_pusty_wykres(f"Błąd podczas generowania wykresu słupkowego: {e}")