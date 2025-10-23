"""
Wykres dobowego rytmu ciśnienia
"""

import pandas as pd
import plotly.graph_objects as go
from .utils import utworz_pusty_wykres
from config import KOLORY_PARAMETROW, TEMPLATE_PLOTLY


def generate_circadian_rhythm_chart(df):
    """
    Generuje wykres dobowego rytmu ciśnienia.

    Args:
        df: DataFrame z pomiarami

    Returns:
        go.Figure: Wykres Plotly
    """
    if df.empty:
        return utworz_pusty_wykres()

    try:
        # Statystyki dla każdej godziny
        hourly_stats = df.groupby('Hour').agg(
            SYS_mean=('SYS', 'mean'),
            SYS_std=('SYS', 'std'),
            DIA_mean=('DIA', 'mean'),
            DIA_std=('DIA', 'std')
        ).reset_index().fillna(0).sort_values(by='Hour')

        hourly_stats['Godzina_Str'] = hourly_stats['Hour'].apply(lambda h: f"{h:02d}:00")

        fig = go.Figure()

        # Legenda dla zakresu odchylenia standardowego
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='lines',
            name='Zakres ± 1 Odch. Std.',
            line=dict(width=10, color='rgba(128, 128, 128, 0.4)'),
            showlegend=True
        ))

        # Dla DIA i SYS: zakres odchylenia + linia średniej
        for param in ['DIA', 'SYS']:
            mean_col = f'{param}_mean'
            std_col = f'{param}_std'
            color = KOLORY_PARAMETROW[param]

            # Zakres odchylenia standardowego
            x_coords = hourly_stats['Godzina_Str']
            y_upper = hourly_stats[mean_col] + hourly_stats[std_col]
            y_lower = hourly_stats[mean_col] - hourly_stats[std_col]

            # Połączenie górnej i dolnej granicy (dla wypełnienia)
            x_combined = pd.concat([x_coords, x_coords.iloc[::-1]])
            y_combined = pd.concat([y_upper, y_lower.iloc[::-1]])

            fig.add_trace(go.Scatter(
                x=x_combined,
                y=y_combined,
                fill='toself',
                fillcolor=f'rgba({255 if param=="SYS" else 0}, 0, {255 if param=="DIA" else 0}, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=False
            ))

            # Linia średniej
            fig.add_trace(go.Scatter(
                x=x_coords,
                y=hourly_stats[mean_col],
                mode='lines+markers',
                name=f'Średnia {param}',
                line=dict(color=color)
            ))

        fig.update_layout(
            title="Dobowy Rytm Ciśnienia (Średnia ± Odchylenie Standardowe)",
            xaxis_title="Godzina pomiaru",
            yaxis_title="Wartość Ciśnienia [mmHg]",
            template=TEMPLATE_PLOTLY,
            legend={'traceorder': 'reversed'}
        )
        fig.update_xaxes(type='category')

        return fig

    except Exception as e:
        return utworz_pusty_wykres(f"Błąd: {e}")