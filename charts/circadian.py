"""Moduł odpowiedzialny za generowanie wykresu rytmu dobowego ciśnienia.

Ten moduł dostarcza funkcję do tworzenia wizualizacji, która przedstawia
średnie wartości ciśnienia skurczowego (SYS) i rozkurczowego (DIA)
w poszczególnych godzinach doby. Umożliwia to analizę wahań ciśnienia
w cyklu 24-godzinnym. Wykres może być generowany w dwóch trybach:
statycznym (średnia z całego okresu) oraz animowanym (kroczące okno 7-dniowe).
"""

import pandas as pd
import plotly.graph_objects as go
from .utils import utworz_pusty_wykres, validate_dataframe
from config import KOLORY_PARAMETROW, TEMPLATE_PLOTLY

def generate_circadian_rhythm_chart(df, start_date=None, end_date=None):
    """Generuje wykres rytmu dobowego, pokazujący wahania ciśnienia w ciągu doby.

    Funkcja może działać w dwóch trybach:
    1.  **Tryb statyczny**: Jeśli `start_date` i `end_date` nie są podane,
        wykres pokazuje średnie wartości ciśnienia dla każdej godziny,
        obliczone na podstawie całego dostępnego zakresu danych.
    2.  **Tryb okna kroczącego**: Jeśli `start_date` i `end_date` są podane,
        wykres pokazuje średnie wartości tylko dla danych z tego okresu,
        co jest używane do tworzenia animacji.

    Wizualizacja obejmuje średnie wartości SYS i DIA oraz zakresy odchylenia
    standardowego, co pozwala ocenić zarówno tendencję centralną, jak
    i zmienność pomiarów o różnych porach dnia.

    Args:
        df (pd.DataFrame): Ramka danych zawierająca przetworzone pomiary,
            w tym kolumny 'Datetime', 'Hour', 'SYS' i 'DIA'.
        start_date (str lub datetime, optional): Data początkowa dla okna
            kroczącego. Domyślnie None.
        end_date (str lub datetime, optional): Data końcowa dla okna
            kroczącego. Domyślnie None.

    Returns:
        go.Figure: Obiekt wykresu Plotly, gotowy do wyświetlenia w aplikacji
            Dash. W przypadku braku danych lub błędu, zwraca pusty wykres
            z odpowiednim komunikatem.
    """
    valid, msg = validate_dataframe(df, ['Datetime', 'Hour', 'SYS', 'DIA'])
    if not valid:
        return utworz_pusty_wykres(msg)

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
