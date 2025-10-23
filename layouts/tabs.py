"""
Definicje layoutów wszystkich zakładek aplikacji
"""

from dash import dcc, html
from config import KOLORY_ESC


def create_app_layout(initial_df_json, initial_status, initial_kpis, initial_figures):
    """
    Tworzy pełny layout aplikacji.

    Args:
        initial_df_json: DataFrame w formacie JSON
        initial_status: Komunikat statusu
        initial_kpis: Tuple z wartościami KPI (avg_sys, avg_dia, max_reading, norm_percent, fig_pie)
        initial_figures: Dict z wykresami {'trend': fig, 'hour': fig, ...}

    Returns:
        html.Div: Główny layout aplikacji
    """

    return html.Div([
        # Magazyn danych
        dcc.Store(id='data-store', data=initial_df_json),

        # Nagłówek
        create_header(initial_status),

        # Zakładki
        dcc.Tabs(id="tabs-container", children=[
            create_summary_tab(initial_kpis),
            create_esc_classification_tab(initial_figures['esc_bar']),
            create_matrix_tab(initial_figures['matrix']),
            create_trend_tab(initial_figures['trend']),
            create_circadian_tab(initial_figures['hour']),
            create_correlation_tab(initial_figures['scatter']),
            create_heatmap_tab(initial_figures['heatmap']),
            create_comparison_tab(initial_figures['comparison']),
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
        'textAlign': 'center',
        'padding': '20px',
        'borderBottom': '2px solid #ddd',
        'backgroundColor': '#f8f9fa'
    })


def create_summary_tab(initial_kpis):
    """Tworzy zakładkę podsumowania."""
    avg_sys, avg_dia, max_reading, norm_percent, fig_pie = initial_kpis

    return dcc.Tab(label='📊 Podsumowanie', children=[
        html.Div([
            # KPI Cards
            html.Div([
                html.Div([
                    html.H5("Średnie SYS"),
                    html.H3(id='kpi-avg-sys', children=avg_sys)
                ], className="kpi-card"),
                html.Div([
                    html.H5("Średnie DIA"),
                    html.H3(id='kpi-avg-dia', children=avg_dia)
                ], className="kpi-card"),
                html.Div([
                    html.H5("Najwyższy pomiar"),
                    html.H3(id='kpi-max-reading', children=max_reading)
                ], className="kpi-card"),
                html.Div([
                    html.H5("% w normie (<140/90)"),
                    html.H3(id='kpi-norm-percent', children=norm_percent)
                ], className="kpi-card"),
            ], style={
                'display': 'flex',
                'justifyContent': 'space-around',
                'padding': '20px',
                'flexWrap': 'wrap'
            }),

            # Wykres kołowy
            dcc.Graph(id='graph-classification-pie', figure=fig_pie)
        ])
    ])


def create_esc_classification_tab(initial_fig_esc_bar):
    """Tworzy zakładkę klasyfikacji ESC."""
    return dcc.Tab(label='🏥 Klasyfikacja', children=[
        html.Div([
            html.H3(
                "📋 Aktualne Wytyczne Dotyczące Ciśnienia Tętniczego",
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginTop': '20px'}
            ),

            # Tabela wytycznych
            html.Div([
                html.Table([
                    html.Thead(
                        html.Tr([
                            html.Th("Kategoria",
                                    style={'padding': '12px', 'borderBottom': '2px solid #ddd', 'fontWeight': 'bold'}),
                            html.Th("Ciśnienie skurczowe (mmHg)",
                                    style={'padding': '12px', 'borderBottom': '2px solid #ddd', 'fontWeight': 'bold'}),
                            html.Th("Ciśnienie rozkurczowe (mmHg)",
                                    style={'padding': '12px', 'borderBottom': '2px solid #ddd', 'fontWeight': 'bold'}),
                        ], style={'backgroundColor': '#f8f9fa'})
                    ),
                    html.Tbody([
                        html.Tr([
                            html.Td("Optymalne", style={'padding': '10px', 'borderBottom': '1px solid #eee',
                                                        'color': KOLORY_ESC['Optymalne'], 'fontWeight': 'bold'}),
                            html.Td("< 120", style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                            html.Td("< 70", style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                        ]),
                        html.Tr([
                            html.Td("Prawidłowe", style={'padding': '10px', 'borderBottom': '1px solid #eee',
                                                         'color': KOLORY_ESC['Prawidłowe'], 'fontWeight': 'bold'}),
                            html.Td("120-129", style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                            html.Td("70-79", style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                        ]),
                        html.Tr([
                            html.Td("Podwyższone", style={'padding': '10px', 'borderBottom': '1px solid #eee',
                                                          'color': KOLORY_ESC['Podwyższone'], 'fontWeight': 'bold'}),
                            html.Td("130-139", style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                            html.Td("80-89", style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                        ]),
                        html.Tr([
                            html.Td("Nadciśnienie 1°", style={'padding': '10px', 'borderBottom': '1px solid #eee',
                                                              'color': KOLORY_ESC['Nadciśnienie 1°'],
                                                              'fontWeight': 'bold'}),
                            html.Td("140-159", style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                            html.Td("90-99", style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                        ]),
                        html.Tr([
                            html.Td("Nadciśnienie 2°", style={'padding': '10px', 'borderBottom': '1px solid #eee',
                                                              'color': KOLORY_ESC['Nadciśnienie 2°'],
                                                              'fontWeight': 'bold'}),
                            html.Td("160-179", style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                            html.Td("100-109", style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                        ]),
                        html.Tr([
                            html.Td("Nadciśnienie 3°", style={'padding': '10px', 'borderBottom': '1px solid #eee',
                                                              'color': KOLORY_ESC['Nadciśnienie 3°'],
                                                              'fontWeight': 'bold'}),
                            html.Td("≥ 180", style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                            html.Td("≥ 110", style={'padding': '10px', 'borderBottom': '1px solid #eee'}),
                        ]),
                        html.Tr([
                            html.Td("Izolowane nadciśnienie skurczowe",
                                    style={'padding': '10px', 'color': KOLORY_ESC['Izolowane nadciśnienie skurczowe'],
                                           'fontWeight': 'bold'}),
                            html.Td("≥ 140", style={'padding': '10px'}),
                            html.Td("< 90", style={'padding': '10px'}),
                        ]),
                    ])
                ], style={
                    'width': '100%',
                    'borderCollapse': 'collapse',
                    'marginTop': '20px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                })
            ], style={
                'maxWidth': '900px',
                'margin': '0 auto',
                'padding': '20px',
                'backgroundColor': 'white',
                'borderRadius': '10px'
            }),

            # Notatka kliniczna
            html.Div([
                html.P([
                    html.Strong("⚕️ Zasada kliniczna: "),
                    "Przy niejednoznacznych parach (np. SYS w jednej kategorii, DIA w innej, zwłaszcza niższej) ",
                    html.Strong("klasyfikacja następuje do wyższej kategorii"),
                    "."
                ], style={
                    'fontSize': '14px',
                    'color': '#666',
                    'fontStyle': 'italic',
                    'marginTop': '15px',
                    'padding': '15px',
                    'backgroundColor': '#fff3cd',
                    'borderLeft': '4px solid #ffc107',
                    'borderRadius': '5px'
                })
            ], style={'maxWidth': '900px', 'margin': '20px auto'}),

            html.Hr(),

            # Wykres słupkowy
            dcc.Graph(id='graph-esc-bar', figure=initial_fig_esc_bar)
        ])
    ])


def create_matrix_tab(initial_fig_matrix):
    """Tworzy zakładkę macierzy klasyfikacji."""
    return dcc.Tab(label='🗺️ Macierz', children=[
        dcc.Graph(id='graph-classification-matrix', figure=initial_fig_matrix)
    ])


def create_trend_tab(initial_fig_trend):
    """Tworzy zakładkę trendu w czasie."""
    return dcc.Tab(label='📈 Trend', children=[
        dcc.Graph(id='graph-trend', figure=initial_fig_trend)
    ])


def create_circadian_tab(initial_fig_hour):
    """Tworzy zakładkę rytmu dobowego."""
    return dcc.Tab(label='🕒 Rytm dobowy', children=[
        dcc.Graph(id='graph-hour', figure=initial_fig_hour)
    ])


def create_correlation_tab(initial_fig_scatter):
    """Tworzy zakładkę korelacji."""
    return dcc.Tab(label='❤️ Korelacje', children=[
        dcc.Graph(id='graph-scatter', figure=initial_fig_scatter)
    ])


def create_heatmap_tab(initial_fig_heatmap):
    """Tworzy zakładkę heatmapy."""
    return dcc.Tab(label='🌡️ Heatmapa', children=[
        dcc.Graph(id='graph-heatmap', figure=initial_fig_heatmap)
    ])


def create_comparison_tab(initial_fig_comparison):
    """Tworzy zakładkę porównań."""
    return dcc.Tab(label='⚖️ Porównanie', children=[
        html.Div([
            html.H5("Wybierz tryb porównania:", style={'textAlign': 'center', 'marginTop': '20px'}),
            dcc.RadioItems(
                id='boxplot-radio',
                options=[
                    {'label': 'Godziny pomiarów', 'value': 'Godzina Pomiaru'},
                    {'label': 'Dzień roboczy / Weekend', 'value': 'Typ Dnia'}
                ],
                value='Godzina Pomiaru',
                labelStyle={'display': 'inline-block', 'marginRight': '20px'},
                style={'textAlign': 'center'}
            ),

            html.Hr(),

            html.H5("Wybierz typ wykresu:", style={'textAlign': 'center'}),
            dcc.RadioItems(
                id='comparison-chart-type-radio',
                options=[
                    {'label': 'Pudełkowy (Box)', 'value': 'box'},
                    {'label': 'Skrzypcowy (Violin)', 'value': 'violin'}
                ],
                value='box',
                labelStyle={'display': 'inline-block', 'marginRight': '20px'},
                style={'textAlign': 'center'}
            ),

            dcc.Graph(id='graph-comparison', figure=initial_fig_comparison)
        ], style={'padding': '20px'})
    ])


def create_histogram_tab(initial_fig_histogram):
    """Tworzy zakładkę rozkładu danych."""
    return dcc.Tab(label='📊 Rozkład', children=[
        html.Div([
            html.H4("Wybierz parametr do analizy:", style={'textAlign': 'center', 'marginTop': '20px'}),
            dcc.RadioItems(
                id='histogram-radio',
                options=[
                    {'label': 'Ciśnienie Skurczowe (SYS)', 'value': 'SYS'},
                    {'label': 'Ciśnienie Rozkurczowe (DIA)', 'value': 'DIA'},
                    {'label': 'Tętno (PUL)', 'value': 'PUL'}
                ],
                value='SYS',
                labelStyle={'display': 'inline-block', 'marginRight': '20px'},
                style={'textAlign': 'center'}
            ),

            dcc.Graph(id='graph-histogram', figure=initial_fig_histogram)
        ], style={'padding': '20px'})
    ])