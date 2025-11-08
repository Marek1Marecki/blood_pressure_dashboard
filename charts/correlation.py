"""
=== charts/correlation.py ===
Wykres korelacji SYS-DIA
"""

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from .utils import utworz_pusty_wykres
from config import TEMPLATE_PLOTLY


def generate_correlation_chart(df):
    """Generuje wykres korelacji SYS-DIA z uwzględnieniem pulsu."""
    if df.empty:
        return utworz_pusty_wykres()

    try:
        # Create scatter plot
        fig = px.scatter(
            df, x='DIA', y='SYS', color='PUL',
            title="Zależność SYS–DIA (kolor = puls) z linią regresji",
            labels={'SYS': 'Ciśnienie Skurczowe (mmHg)', 'DIA': 'Ciśnienie Rozkurczowe (mmHg)', 'PUL': 'Puls (bpm)'},
            color_continuous_scale='Viridis',
            size_max=12,
            trendline=None  # Disable default trendline to add custom one
        )
        
        # Calculate linear regression
        x = df['DIA'].values
        y = df['SYS'].values
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # Add regression line
        x_range = np.linspace(x.min(), x.max(), 100)
        y_pred = slope * x_range + intercept
        
        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=y_pred,
                mode='lines',
                line=dict(color='red', width=2, dash='dash'),
                name=f'Regresja liniowa<br>r = {r_value:.2f}, p = {p_value:.3f}',
                showlegend=True
            )
        )
        
        # Update layout and traces
        fig.update_traces(marker=dict(size=10))
        fig.update_layout(
            template=TEMPLATE_PLOTLY,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255, 255, 255, 0.7)'
            )
        )
        return fig
    except Exception as e:
        return utworz_pusty_wykres(f"Błąd: {e}")
