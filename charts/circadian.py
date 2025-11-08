"""
Wykres dobowego rytmu ciśnienia (statyczny i z oknem kroczącym)
"""

import pandas as pd
import plotly.graph_objects as go
from .utils import utworz_pusty_wykres
from config import KOLORY_PARAMETROW, TEMPLATE_PLOTLY

def generate_circadian_rhythm_chart(df, start_date=None, end_date=None):
    """
    Generuje wykres dobowego rytmu ciśnienia.
    Jeśli podane są daty, filtruje dane do podanego okresu.

    Args:
        df (pd.DataFrame): DataFrame z pomiarami.
        start_date (str, optional): Data początkowa okna.
        end_date (str, optional): Data końcowa okna.

    Returns:
        go.Figure: Wykres Plotly.
    """
    if df.empty:
        return utworz_pusty_wykres()

    try:
        plot_df = df.copy()

        # Ustawienie tytułu i filtrowanie danych
        if start_date and end_date:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            plot_df = plot_df[(plot_df['Datetime'] >= start) & (plot_df['Datetime'] <= end)]
            title = f"Dobowy Rytm Ciśnienia (Okno 7-dniowe: {start.strftime('%d.%m')} - {end.strftime('%d.%m.%Y')})"
        else:
            title = "Dobowy Rytm Ciśnienia (Średnia z całego okresu)"

        if plot_df.empty:
            return utworz_pusty_wykres(f"Brak danych dla wybranego okresu")

        # Statystyki dla każdej godziny
        hourly_stats = plot_df.groupby('Hour').agg(
            SYS_mean=('SYS', 'mean'), SYS_std=('SYS', 'std'),
            DIA_mean=('DIA', 'mean'), DIA_std=('DIA', 'std')
        ).reset_index().fillna(0).sort_values(by='Hour')

        if len(hourly_stats) < 2:
            return utworz_pusty_wykres(f"Zbyt mało danych dla wybranego okresu")

        hourly_stats['Godzina_Str'] = hourly_stats['Hour'].apply(lambda h: f"{h:02d}:00")
        fig = go.Figure()

        # Generowanie śladów (traces)
        for param in ['DIA', 'SYS']:
            mean_col, std_col = f'{param}_mean', f'{param}_std'
            color = KOLORY_PARAMETROW[param]
            rgba_color = f'rgba({255 if param=="SYS" else 0}, 0, {255 if param=="DIA" else 0}, 0.2)'

            x_coords = hourly_stats['Godzina_Str']
            y_upper = hourly_stats[mean_col] + hourly_stats[std_col]
            y_lower = hourly_stats[mean_col] - hourly_stats[std_col]

            # Wypełnienie dla odchylenia standardowego
            fig.add_trace(go.Scatter(
                x=list(x_coords) + list(x_coords[::-1]),
                y=list(y_upper) + list(y_lower[::-1]),
                fill='toself', fillcolor=rgba_color, line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip", showlegend=False
            ))
            # Linia średniej Z PRZYWRÓCONYMI ETYKIETAMI
            fig.add_trace(go.Scatter(
                x=x_coords,
                y=hourly_stats[mean_col],
                mode='lines+markers+text',  # <--- POPRAWKA
                name=f'Średnia {param}',
                line=dict(color=color),
                text=hourly_stats[mean_col].round(0).astype(int), # <--- POPRAWKA
                textposition='top center',                        # <--- POPRAWKA
                textfont=dict(size=10, color=color)               # <--- POPRAWKA
            ))

        # Dodanie "fałszywego" śladu dla legendy odchylenia standardowego
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode='lines', name='Zakres ± 1 Odch. Std.',
            line=dict(width=10, color='rgba(128, 128, 128, 0.4)'), showlegend=True
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Godzina pomiaru",
            yaxis_title="Wartość Ciśnienia [mmHg]",
            yaxis_range=[df['DIA'].min() - 10, df['SYS'].max() + 10],
            template=TEMPLATE_PLOTLY,
            legend={'traceorder': 'reversed'}
        )
        fig.update_xaxes(type='category')

        return fig
    except Exception as e:
        return utworz_pusty_wykres(f"Błąd: {e}")
