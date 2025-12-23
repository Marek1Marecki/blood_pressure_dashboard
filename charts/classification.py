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
from .utils import utworz_pusty_wykres, validate_dataframe

from config import (
    PROGI_ESC, KOLORY_ESC, KOLEJNOSC_ESC,
    TEMPLATE_PLOTLY, WYSOKOSC_WYKRESU_DUZY,
    MIN_DIA, MAX_DIA, MIN_SYS, MAX_SYS,
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
    valid, msg = validate_dataframe(df, ['SYS', 'DIA', 'Datetime', 'Kategoria'])
    if not valid:
        return utworz_pusty_wykres(msg)

    try:
        fig = go.Figure()

        p = PROGI_ESC # Skrót dla czytelności

        strefy = [
            # === OPTYMALNE (lewy dolny róg): SYS < 120 i DIA < 70 ===
            {'x0': MIN_DIA, 'y0': MIN_SYS, 'x1': p['optymalne']['dia'], 'y1': p['optymalne']['sys'], 'color': KOLORY_ESC['Optymalne'], 'nazwa': 'Optymalne'},

            # === PRAWIDŁOWE (kształt litery "L") ===
            # pionowy słupek – DIA < 70, SYS 120-130
            {'x0': MIN_DIA, 'y0': p['prawidlowe']['sys'], 'x1': p['prawidlowe']['dia'], 'y1': p['podwyzszone']['sys'], 'color': KOLORY_ESC['Prawidłowe'], 'nazwa': 'Prawidłowe'},
            # poziomy pasek – DIA 70-80, SYS < 130
            {'x0': p['prawidlowe']['dia'], 'y0': MIN_SYS, 'x1': p['podwyzszone']['dia'], 'y1': p['podwyzszone']['sys'], 'color': KOLORY_ESC['Prawidłowe'], 'nazwa': 'Prawidłowe'},

            # === PODWYŻSZONE (również kształt "L") ===
            # pion – SYS 130-140 przy DIA < 80
            {'x0': MIN_DIA, 'y0': p['podwyzszone']['sys'], 'x1': p['podwyzszone']['dia'], 'y1': p['nadcisnienie_1']['sys'], 'color': KOLORY_ESC['Podwyższone'], 'nazwa': 'Podwyższone'},
            # poziom – DIA 80-90 przy SYS < 140
            {'x0': p['podwyzszone']['dia'], 'y0': MIN_SYS, 'x1': p['nadcisnienie_1']['dia'], 'y1': p['nadcisnienie_1']['sys'], 'color': KOLORY_ESC['Podwyższone'], 'nazwa': 'Podwyższone'},

            # === IZOLOWANE NADCIŚNIENIE SKURCZOWE (wysokie SYS, niskie DIA) ===
            {'x0': MIN_DIA, 'y0': p['nadcisnienie_1']['sys'], 'x1': p['nadcisnienie_1']['dia'], 'y1': MAX_SYS, 'color': KOLORY_ESC['Izolowane nadciśnienie skurczowe'], 'nazwa': 'Izolowane nadciśnienie skurczowe'},

            # === NADCIŚNIENIE 1° (prostokąt dla DIA 90-100 oraz SYS 140-160) ===
            {'x0': p['nadcisnienie_1']['dia'], 'y0': MIN_SYS, 'x1': p['nadcisnienie_2']['dia'], 'y1': p['nadcisnienie_2']['sys'], 'color': KOLORY_ESC['Nadciśnienie 1°'], 'nazwa': 'Nadciśnienie 1°'},

            # === NADCIŚNIENIE 2° (dwuczęściowe: pion + poziom) ===
            {'x0': p['nadcisnienie_1']['dia'], 'y0': p['nadcisnienie_2']['sys'], 'x1': p['nadcisnienie_2']['dia'], 'y1': p['nadcisnienie_3']['sys'], 'color': KOLORY_ESC['Nadciśnienie 2°'], 'nazwa': 'Nadciśnienie 2°'},
            {'x0': p['nadcisnienie_2']['dia'], 'y0': MIN_SYS, 'x1': p['nadcisnienie_3']['dia'], 'y1': p['nadcisnienie_3']['sys'], 'color': KOLORY_ESC['Nadciśnienie 2°'], 'nazwa': 'Nadciśnienie 2°'},

            # === NADCIŚNIENIE 3° (skrajne wartości SYS/DIA) ===
            {'x0': p['nadcisnienie_1']['dia'], 'y0': p['nadcisnienie_3']['sys'], 'x1': p['nadcisnienie_3']['dia'], 'y1': MAX_SYS, 'color': KOLORY_ESC['Nadciśnienie 3°'], 'nazwa': 'Nadciśnienie 3°'},
            {'x0': p['nadcisnienie_3']['dia'], 'y0': MIN_SYS, 'x1': MAX_DIA, 'y1': MAX_SYS, 'color': KOLORY_ESC['Nadciśnienie 3°'], 'nazwa': 'Nadciśnienie 3°'},
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
            xaxis=dict(range=[min(MIN_DIA, df['DIA'].min() - 5), max(MAX_DIA, df['DIA'].max() + 5)], gridcolor='rgba(200,200,200,0.5)'),
            yaxis=dict(range=[min(MIN_SYS, df['SYS'].min() - 5), max(MAX_SYS, df['SYS'].max() + 5)], gridcolor='rgba(200,200,200,0.5)'),
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
    valid, msg = validate_dataframe(df, ['Kategoria'])
    if not valid:
        return utworz_pusty_wykres(msg)

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