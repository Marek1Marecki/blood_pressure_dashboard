"""
Definicje layoutów wszystkich zakładek aplikacji
"""

from dash import dcc, html
from config import KOLORY_ESC
from charts import generate_comparison_chart


def create_app_layout(initial_df_json, initial_status, initial_kpis, initial_figures, initial_df):
    """
    Tworzy pełny layout aplikacji.
    """
    return html.Div([
        dcc.Store(id='data-store', data=initial_df_json),
        create_header(initial_status),
        dcc.Tabs(id="tabs-container", children=[
            create_summary_tab(initial_kpis),
            create_esc_classification_tab(initial_figures['esc_bar']),
            create_matrix_tab(initial_figures['matrix']),
            create_trend_tab(initial_figures['trend']),
            create_circadian_tab(initial_figures['hour']),
            create_hemodynamics_tab(initial_figures['hemodynamics']),
            create_correlation_tab(initial_figures['scatter']),
            create_heatmap_tab(initial_figures['heatmap']),
            create_comparison_tab(initial_df),
            create_histogram_tab(initial_figures['histogram'])
        ])
    ])


def create_header(initial_status):
    """Tworzy nagłówek aplikacji."""
    return html.Div([
        html.H1("💓 Dashboard Pomiarów Ciśnienia Krwi"),
        html.Div([
            html.Button('🔄 Odśwież dane', id='refresh-button'),
            html.Button('📥 Eksport HTML', id='export-button', style={'marginLeft': '10px'}),
        ], style={'display': 'flex', 'justifyContent': 'center'}),
        html.Div(
            id='status-output',
            children=initial_status,
            style={'marginTop': '10px', 'fontSize': '14px'}
        )
    ], style={
        'textAlign': 'center', 'padding': '20px', 'borderBottom': '2px solid #ddd', 'backgroundColor': '#f8f9fa'
    })


def create_summary_tab(initial_kpis):
    """Tworzy zakładkę podsumowania."""
    avg_sys, avg_dia, max_reading, norm_percent, fig_pie = initial_kpis
    return dcc.Tab(label='📊 Podsumowanie', children=[
        html.Div([
            html.Div([
                html.Div([html.H5("Średnie SYS"), html.H3(id='kpi-avg-sys', children=avg_sys)], className="kpi-card"),
                html.Div([html.H5("Średnie DIA"), html.H3(id='kpi-avg-dia', children=avg_dia)], className="kpi-card"),
                html.Div([html.H5("Najwyższy pomiar"), html.H3(id='kpi-max-reading', children=max_reading)], className="kpi-card"),
                html.Div([html.H5("% w normie (<130/80)"), html.H3(id='kpi-norm-percent', children=norm_percent)], className="kpi-card"),
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'padding': '20px', 'flexWrap': 'wrap'}),
            html.Div([
                html.Div([
                    html.H4("📋 Aktualne Wytyczne Ciśnienia Tętniczego", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '15px', 'fontSize': '1.1em'}),
                    html.Table([
                        html.Thead(html.Tr([html.Th("Kategoria"), html.Th("SYS (mmHg)"), html.Th("DIA (mmHg)")])),
                        html.Tbody([
                            html.Tr([html.Td("Optymalne", style={'color': KOLORY_ESC['Optymalne'], 'fontWeight': 'bold'}), html.Td("< 120"), html.Td("< 70")]),
                            html.Tr([html.Td("Prawidłowe", style={'color': KOLORY_ESC['Prawidłowe'], 'fontWeight': 'bold'}), html.Td("120-129"), html.Td("70-79")]),
                            html.Tr([html.Td("Podwyższone", style={'color': KOLORY_ESC['Podwyższone'], 'fontWeight': 'bold'}), html.Td("130-139"), html.Td("80-89")]),
                            html.Tr([html.Td("Nadciśnienie 1°", style={'color': KOLORY_ESC['Nadciśnienie 1°'], 'fontWeight': 'bold'}), html.Td("140-159"), html.Td("90-99")]),
                            html.Tr([html.Td("Nadciśnienie 2°", style={'color': KOLORY_ESC['Nadciśnienie 2°'], 'fontWeight': 'bold'}), html.Td("160-179"), html.Td("100-109")]),
                            html.Tr([html.Td("Nadciśnienie 3°", style={'color': KOLORY_ESC['Nadciśnienie 3°'], 'fontWeight': 'bold'}), html.Td("≥ 180"), html.Td("≥ 110")]),
                            html.Tr([html.Td("Izolowane nadciśnienie skurczowe", style={'color': KOLORY_ESC['Izolowane nadciśnienie skurczowe'], 'fontWeight': 'bold'}), html.Td("≥ 140"), html.Td("< 90")]),
                        ])
                    ], className='guidelines-table'),
                    html.Div([html.P(["⚕️ Przy niejednoznacznych parach klasyfikacja następuje do ", html.Strong("wyższej kategorii"), "."])], className='note-box')
                ], style={'width': '45%', 'padding': '15px', 'display': 'inline-block', 'verticalAlign': 'top'}),
                html.Div([dcc.Graph(id='graph-classification-pie', figure=fig_pie, style={'height': '500px'})], style={'width': '50%', 'padding': '15px', 'display': 'inline-block', 'verticalAlign': 'top'})
            ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'flex-start', 'padding': '20px'})
        ])
    ])


def create_esc_classification_tab(initial_fig_esc_bar):
    """Tworzy zakładkę klasyfikacji ESC."""
    return dcc.Tab(label='🏥 Klasyfikacja', children=[
        html.Div([
            html.H3("📋 Klasyfikacja Pomiarów (wg ESC/ESH)", style={'textAlign': 'center', 'color': '#2c3e50', 'marginTop': '20px'}),
            # USUNIĘTO OPIS Z TEGO MIEJSCA
            html.Hr(),
            dcc.Graph(id='graph-esc-bar', figure=initial_fig_esc_bar)
        ])
    ])


def create_matrix_tab(initial_fig_matrix):
    """Tworzy zakładkę macierzy klasyfikacji."""
    legend_items = []
    for category, color in KOLORY_ESC.items():
        legend_items.append(
            html.Div([
                html.Span(style={'display': 'inline-block', 'width': '16px', 'height': '16px', 'backgroundColor': color, 'marginRight': '8px', 'border': '1px solid #ddd', 'opacity': '0.6'}),
                html.Span(category, style={'fontWeight': 'bold', 'color': color, 'fontSize': '13px'})
            ], style={'display': 'inline-block', 'margin': '4px 12px'})
        )

    return dcc.Tab(label='🗺️ Macierz', children=[
        html.Div([
            dcc.Graph(id='graph-classification-matrix', figure=initial_fig_matrix),
            html.Div([
                html.H5("🎨 Legenda Kolorów:", style={'textAlign': 'center', 'marginBottom': '15px', 'fontSize': '16px'}),
                # ZMIENIONO STYL WEWNĘTRZNEGO DIVA
                html.Div(legend_items, style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap', 'gap': '15px'})
            ], style={ # ZMIENIONO STYL GŁÓWNEGO KONTENERA LEGENDY
                'maxWidth': '1200px', 'margin': '20px auto', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'border': '1px solid #ddd'
            })
        ])
    ])


def create_trend_tab(initial_fig_trend):
    """Tworzy zakładkę trendu w czasie."""
    return dcc.Tab(label='📈 Trend', children=[dcc.Graph(id='graph-trend', figure=initial_fig_trend)])


def create_circadian_tab(initial_fig_hour):
    """Tworzy zakładkę rytmu dobowego z przełącznikiem trybu."""
    return dcc.Tab(label='🕒 Rytm dobowy', children=[
        html.Div([
            html.H4("Wybierz tryb analizy", style={'textAlign': 'center', 'marginTop': '20px'}),
            dcc.RadioItems(
                id='circadian-mode-radio',
                options=[
                    {'label': 'Statyczny (cały okres)', 'value': 'static'},
                    {'label': 'Animacja (okno 7-dniowe)', 'value': 'animated'},
                ],
                value='static',
                labelStyle={'display': 'inline-block', 'marginRight': '20px'},
                style={'textAlign': 'center', 'marginBottom': '20px'}
            ),

            # Kontener dla widoku statycznego
            html.Div(
                id='static-circadian-container',
                children=[dcc.Graph(id='graph-hour-static', figure=initial_fig_hour)],
                style={'display': 'block'} # Domyślnie widoczny
            ),

            # Kontener dla widoku animowanego
            html.Div(
                id='animated-circadian-container',
                children=[
                    dcc.Graph(id='graph-hour-animated'),
                    html.Div([
                        html.H5("Animacja krocząca (okno 7-dniowe)", style={'textAlign': 'center', 'marginBottom': '20px'}),
                        dcc.Slider(id='day-slider', min=0, max=1, step=1, value=0, marks=None),
                        html.Div([
                            html.Button('▶️ Play', id='play-button', n_clicks=0, style={'marginRight': '10px'}),
                            html.Button('⏸️ Pause', id='pause-button', n_clicks=0),
                        ], style={'textAlign': 'center', 'marginTop': '20px'}),
                        dcc.Interval(id='animation-interval', interval=800, n_intervals=0, disabled=True),
                    ], style={
                        'maxWidth': '800px', 'margin': '30px auto', 'padding': '20px',
                        'border': '1px solid #ddd', 'borderRadius': '10px', 'backgroundColor': '#f9f9f9'
                    })
                ],
                style={'display': 'none'} # Domyślnie ukryty
            ),
        ])
    ])


def create_correlation_tab(initial_fig_scatter):
    """Tworzy zakładkę korelacji."""
    return dcc.Tab(label='❤️ Korelacje', children=[dcc.Graph(id='graph-scatter', figure=initial_fig_scatter)])


def create_heatmap_tab(initial_fig_heatmap):
    """Tworzy zakładkę heatmapy."""
    return dcc.Tab(label='🌡️ Heatmapa', children=[dcc.Graph(id='graph-heatmap', figure=initial_fig_heatmap)])


def create_hemodynamics_tab(initial_fig_hemodynamics):
    """Tworzy zakładkę analizy hemodynamicznej."""
    return dcc.Tab(label='🔬 Analiza Hemodynamiczna', children=[html.Div([
            html.H4("Analiza Zależności Hemodynamicznych", style={'textAlign': 'center', 'marginTop': '20px', 'color': '#2c3e50'}),
            html.P(["Wykres pokazuje trend ", html.Strong("Ciśnienia Tętna (PP)"), " oraz ", html.Strong("Średniego Ciśnienia Tętniczego (MAP)"), " w czasie."], style={'textAlign': 'center', 'color': '#666', 'marginBottom': '20px'}),
            html.Div([html.Ul([
                    html.Li([html.Strong("PP (Pulse Pressure)"), " = SYS - DIA"]),
                    html.Li([html.Strong("MAP (Mean Arterial Pressure)"), " = (SYS + 2×DIA) / 3"]),
                ])], style={'maxWidth': '800px', 'margin': '0 auto 20px auto', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'borderLeft': '4px solid #17a2b8'}),
            dcc.Graph(id='graph-hemodynamics', figure=initial_fig_hemodynamics)
        ], style={'padding': '20px'})
    ])


def create_comparison_tab(df):
    """Tworzy zakładkę porównań."""
    initial_fig_comparison = generate_comparison_chart(df, 'Godzina Pomiaru', 'violin')
    return dcc.Tab(label='⚖️ Porównanie', children=[html.Div([
            html.H5("Wybierz tryb porównania:", style={'textAlign': 'center', 'marginTop': '20px'}),
            dcc.RadioItems(id='boxplot-radio', options=[{'label': 'Godziny pomiarów', 'value': 'Godzina Pomiaru'}, {'label': 'Dzień roboczy / Weekend', 'value': 'Typ Dnia'}], value='Godzina Pomiaru', labelStyle={'display': 'inline-block', 'marginRight': '20px'}, style={'textAlign': 'center'}),
            dcc.Graph(id='graph-comparison', figure=initial_fig_comparison)
        ], style={'padding': '20px'})
    ])


def create_histogram_tab(initial_fig_histogram):
    """Tworzy zakładkę rozkładu danych."""
    return dcc.Tab(label='📊 Rozkład', children=[html.Div([
            html.H4("Wybierz parametr do analizy:", style={'textAlign': 'center', 'marginTop': '20px'}),
            dcc.RadioItems(id='histogram-radio', options=[{'label': 'Ciśnienie Skurczowe (SYS)', 'value': 'SYS'}, {'label': 'Ciśnienie Rozkurczowe (DIA)', 'value': 'DIA'}, {'label': 'Tętno (PUL)', 'value': 'PUL'}], value='SYS', labelStyle={'display': 'inline-block', 'marginRight': '20px'}, style={'textAlign': 'center'}),
            dcc.Graph(id='graph-histogram', figure=initial_fig_histogram)
        ], style={'padding': '20px'})
    ])

