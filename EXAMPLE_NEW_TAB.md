# 🎓 Przykład: Dodanie Zakładki "Statystyki Miesięczne"

Ten plik zawiera **kompletny przykład** dodania nowej zakładki krok po kroku.

---

## 📝 Co będziemy tworzyć?

Zakładkę wyświetlającą statystyki miesięczne:
- Średnie SYS/DIA dla każdego miesiąca
- Wykres słupkowy grupowany
- Liczba pomiarów w każdym miesiącu

---

## 🔨 Krok 1: Utwórz `charts/monthly_stats.py`

```python
"""
Wykres statystyk miesięcznych
"""

import pandas as pd
import plotly.graph_objects as go
from charts.utils import utworz_pusty_wykres
from config import KOLORY_PARAMETROW, TEMPLATE_PLOTLY, WYSOKOSC_WYKRESU_STANDARD


def generate_monthly_stats_chart(df):
    """
    Generuje wykres statystyk miesięcznych.
    
    Args:
        df: DataFrame z pomiarami
    
    Returns:
        go.Figure: Wykres Plotly
    """
    if df.empty:
        return utworz_pusty_wykres()
    
    try:
        # Dodanie kolumny z miesiącem i rokiem
        df['Rok-Miesiąc'] = df['Datetime'].dt.to_period('M').astype(str)
        
        # Grupowanie po miesiącach
        monthly = df.groupby('Rok-Miesiąc').agg({
            'SYS': ['mean', 'std', 'count'],
            'DIA': ['mean', 'std']
        }).reset_index()
        
        # Płaskie nazwy kolumn
        monthly.columns = ['Miesiąc', 'SYS_mean', 'SYS_std', 'Liczba', 'DIA_mean', 'DIA_std']
        
        # Tworzenie wykresu
        fig = go.Figure()
        
        # Słupki dla SYS
        fig.add_trace(go.Bar(
            x=monthly['Miesiąc'],
            y=monthly['SYS_mean'],
            name='Średnie SYS',
            marker_color=KOLORY_PARAMETROW['SYS'],
            error_y=dict(
                type='data',
                array=monthly['SYS_std'],
                visible=True
            ),
            text=monthly['SYS_mean'].round(0),
            textposition='outside'
        ))
        
        # Słupki dla DIA
        fig.add_trace(go.Bar(
            x=monthly['Miesiąc'],
            y=monthly['DIA_mean'],
            name='Średnie DIA',
            marker_color=KOLORY_PARAMETROW['DIA'],
            error_y=dict(
                type='data',
                array=monthly['DIA_std'],
                visible=True
            ),
            text=monthly['DIA_mean'].round(0),
            textposition='outside'
        ))
        
        # Linia z liczbą pomiarów (na drugim osi Y)
        fig.add_trace(go.Scatter(
            x=monthly['Miesiąc'],
            y=monthly['Liczba'],
            name='Liczba pomiarów',
            mode='lines+markers',
            line=dict(color='green', width=2),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="📅 Statystyki Miesięczne Ciśnienia",
            xaxis_title="Miesiąc",
            yaxis_title="Średnie Ciśnienie [mmHg]",
            yaxis2=dict(
                title="Liczba pomiarów",
                overlaying='y',
                side='right',
                showgrid=False
            ),
            template=TEMPLATE_PLOTLY,
            barmode='group',
            height=WYSOKOSC_WYKRESU_STANDARD,
            hovermode='x unified'
        )
        
        return fig
    
    except Exception as e:
        return utworz_pusty_wykres(f"Błąd: {e}")


def generate_monthly_summary_table(df):
    """
    Generuje tabelę podsumowania miesięcznego.
    
    Args:
        df: DataFrame z pomiarami
    
    Returns:
        dict: Słownik z danymi do tabeli
    """
    if df.empty:
        return {}
    
    try:
        df['Rok-Miesiąc'] = df['Datetime'].dt.to_period('M').astype(str)
        
        summary = df.groupby('Rok-Miesiąc').agg({
            'SYS': ['mean', 'min', 'max', 'count'],
            'DIA': ['mean', 'min', 'max']
        }).round(0)
        
        summary.columns = ['SYS_śr', 'SYS_min', 'SYS_max', 'Pomiary', 
                          'DIA_śr', 'DIA_min', 'DIA_max']
        
        return summary.to_dict('records')
    
    except Exception as e:
        return {}
```

---

## 🔨 Krok 2: Aktualizuj `charts/__init__.py`

Dodaj import:

```python
"""
Moduł wykresów - centralny import wszystkich funkcji generujących wykresy
"""

from charts.trend import generate_trend_chart
from charts.circadian import generate_circadian_rhythm_chart
from charts.correlation import generate_correlation_chart
from charts.heatmap import generate_heatmap_chart
from charts.histogram import generate_histogram_chart
from charts.classification import (
    generate_classification_matrix_chart,
    generate_esc_category_bar_chart
)
from charts.comparison import generate_comparison_chart
from charts.summary import generate_summary_data
from charts.monthly_stats import generate_monthly_stats_chart  # ← NOWY

__all__ = [
    'generate_trend_chart',
    'generate_circadian_rhythm_chart',
    'generate_correlation_chart',
    'generate_heatmap_chart',
    'generate_histogram_chart',
    'generate_classification_matrix_chart',
    'generate_esc_category_bar_chart',
    'generate_comparison_chart',
    'generate_summary_data',
    'generate_monthly_stats_chart'  # ← NOWY
]
```

---

## 🔨 Krok 3: Aktualizuj `app.py` - Import

Na początku pliku, w sekcji importów:

```python
from charts import (
    generate_trend_chart,
    generate_circadian_rhythm_chart,
    generate_correlation_chart,
    generate_heatmap_chart,
    generate_histogram_chart,
    generate_classification_matrix_chart,
    generate_esc_category_bar_chart,
    generate_comparison_chart,
    generate_summary_data,
    generate_monthly_stats_chart  # ← NOWY
)
```

---

## 🔨 Krok 4: Aktualizuj `app.py` - Wygeneruj wykres początkowy

W sekcji "Generowanie wykresów startowych":

```python
# Generowanie wykresów startowych
initial_fig_trend = generate_trend_chart(initial_df)
initial_fig_hour = generate_circadian_rhythm_chart(initial_df)
initial_fig_scatter = generate_correlation_chart(initial_df)
initial_fig_heatmap = generate_heatmap_chart(initial_df)
initial_fig_histogram = generate_histogram_chart(initial_df, 'SYS')
initial_fig_classification_matrix = generate_classification_matrix_chart(initial_df)
initial_fig_comparison = generate_comparison_chart(initial_df, 'Godzina Pomiaru', 'box')
initial_fig_esc_bar = generate_esc_category_bar_chart(initial_df)
initial_kpis = generate_summary_data(initial_df)
initial_fig_monthly = generate_monthly_stats_chart(initial_df)  # ← NOWY
```

---

## 🔨 Krok 5: Aktualizuj `app.py` - Dodaj zakładkę

W layoutcie aplikacji, w sekcji `dcc.Tabs`:

```python
dcc.Tabs(id="tabs-container", children=[
    # ... pozostałe zakładki ...
    
    # ← NOWA ZAKŁADKA
    dcc.Tab(label='📅 Statystyki Miesięczne', children=[
        html.Div([
            html.H3("Analiza Miesięczna Pomiarów", 
                   style={'textAlign': 'center', 'marginTop': '20px'}),
            html.P("Wykres pokazuje średnie wartości ciśnienia dla każdego miesiąca "
                   "wraz z odchyleniem standardowym i liczbą pomiarów.",
                   style={'textAlign': 'center', 'color': '#666'}),
            dcc.Graph(id='graph-monthly', figure=initial_fig_monthly)
        ], style={'padding': '20px'})
    ])
])
```

---

## 🔨 Krok 6: Aktualizuj `app.py` - Dodaj callback

W sekcji callbacków:

```python
@callback(Output('graph-monthly', 'figure'), Input('data-store', 'data'))
def update_monthly(stored_data):
    """Aktualizuje wykres statystyk miesięcznych."""
    if stored_data is None:
        return {}
    df = pd.read_json(StringIO(stored_data), orient='split')
    return generate_monthly_stats_chart(df)
```

---

## 🔨 Krok 7: (Opcjonalnie) Dodaj do eksportu HTML

W funkcji `export_html`:

```python
def export_html(n_clicks, stored_data):
    # ...
    wykresy = {
        'Trend': generate_trend_chart(df),
        'Rytm_dobowy': generate_circadian_rhythm_chart(df),
        'Korelacja': generate_correlation_chart(df),
        'Heatmapa': generate_heatmap_chart(df),
        'Macierz': generate_classification_matrix_chart(df),
        'Klasyfikacja_ESC': generate_esc_category_bar_chart(df),
        'Statystyki_Miesięczne': generate_monthly_stats_chart(df),  # ← NOWY
    }
    # ...
```

---

## ✅ Gotowe!

Uruchom aplikację:

```bash
python app.py
```

Twoja nowa zakładka "📅 Statystyki Miesięczne" jest już dostępna!

---

## 🎨 Możliwe Rozszerzenia

1. **Dodaj tabelę** pod wykresem z dokładnymi wartościami
2. **Filtrowanie** po zakresie dat
3. **Porównanie** rok do roku
4. **Eksport** danych miesięcznych do CSV
5. **Alerty** gdy średnia przekracza próg

---

## 💡 Wskazówki

- ✅ Zawsze używaj `utworz_pusty_wykres()` dla pustych danych
- ✅ Dodaj `try-except` dla obsługi błędów
- ✅ Używaj stałych z `config.py` (kolory, wysokość)
- ✅ Dodaj docstringi do funkcji
- ✅ Testuj z pustym DataFrame
- ✅ Pamiętaj o aktualizacji `__all__` w `__init__.py`

---

**Ten przykład pokazuje pełny proces dodawania zakładki - od utworzenia wykresu do integracji z aplikacją!** 🚀