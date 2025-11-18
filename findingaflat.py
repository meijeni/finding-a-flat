import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

df = pd.read_csv('dataset_rightmove-scraper_cityoflondon.csv')

# Haversine formula to calculate distance
def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two points on Earth"""
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return R * c

# Initialize the Dash app
app = dash.Dash(__name__)

# Clean and prepare data
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce')
df['bathrooms'] = pd.to_numeric(df['bathrooms'], errors='coerce')
df['latitude'] = pd.to_numeric(df['coordinates/latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['coordinates/longitude'], errors='coerce')

# Drop rows with missing critical data
df_clean = df.dropna(subset=['price', 'latitude', 'longitude']).copy()

# Get unique values for filters
bedrooms_options = sorted([int(x) for x in df_clean['bedrooms'].dropna().unique() if x >= 0])
bathrooms_options = sorted([int(x) for x in df_clean['bathrooms'].dropna().unique() if x >= 0])

# Extract borough/area from displayAddress
if 'displayAddress' in df_clean.columns:
    df_clean['area'] = df_clean['displayAddress'].fillna('Unknown')

# App layout with improved styling
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🏠 London Rental Finder", 
                style={
                    'textAlign': 'center', 
                    'color': 'white', 
                    'marginBottom': '10px', 
                    'fontWeight': '600',
                    'fontSize': '42px',
                    'letterSpacing': '-1px'
                }),
        html.P("Discover your perfect London flat with interactive maps and smart filters",
               style={
                   'textAlign': 'center', 
                   'color': 'rgba(255, 255, 255, 0.95)', 
                   'marginBottom': '30px',
                   'fontSize': '16px'
               })
    ], style={
        'padding': '30px 20px 20px 20px',
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'color': 'white',
        'marginBottom': '30px',
        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
    }),
    
    html.Div([
        # Filters Panel
        html.Div([
            html.Div([
                html.H3("🎯 Filters", style={
                    'color': '#1a1a2e', 
                    'fontWeight': '600', 
                    'marginBottom': '25px',
                    'fontSize': '24px'
                }),
                
                # Bedrooms
                html.Label("Bedrooms", style={
                    'fontWeight': '600', 
                    'color': '#495057',
                    'marginBottom': '8px',
                    'display': 'block',
                    'fontSize': '14px'
                }),
                dcc.Dropdown(
                    id='bedrooms-filter',
                    options=[{'label': 'Any', 'value': 'all'}] + [{'label': f'{b} bed{"s" if b != 1 else ""}', 'value': b} for b in bedrooms_options],
                    value='all',
                    clearable=False,
                    style={'marginBottom': '20px'}
                ),
                
                # Bathrooms
                html.Label("Bathrooms", style={
                    'fontWeight': '600', 
                    'color': '#495057',
                    'marginBottom': '8px',
                    'display': 'block',
                    'fontSize': '14px'
                }),
                dcc.Dropdown(
                    id='bathrooms-filter',
                    options=[{'label': 'Any', 'value': 'all'}] + [{'label': f'{b} bath{"s" if b != 1 else ""}', 'value': b} for b in bathrooms_options],
                    value='all',
                    clearable=False,
                    style={'marginBottom': '20px'}
                ),
                
                # Price Range
                html.Label("Monthly Rent (£)", style={
                    'fontWeight': '600', 
                    'color': '#495057',
                    'marginBottom': '8px',
                    'display': 'block',
                    'fontSize': '14px'
                }),
                dcc.RangeSlider(
                    id='price-slider',
                    min=0,
                    max=10000,
                    step=100,
                    value=[2000, 4000],
                    marks={i: f'£{i//1000}k' if i > 0 else '£0' for i in range(0, 10001, 2000)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                html.Div(style={'marginBottom': '25px'}),
                
                # Distance Filter Section
                html.Div([
                    html.H4("📍 Distance Filter", style={
                        'color': '#1a1a2e', 
                        'fontWeight': '600', 
                        'marginTop': '10px',
                        'marginBottom': '20px',
                        'fontSize': '18px'
                    }),
                    
                    # Quick Location Buttons
                    html.Label("Quick Select Station", style={
                        'fontWeight': '600', 
                        'color': '#495057',
                        'marginBottom': '10px',
                        'display': 'block',
                        'fontSize': '14px'
                    }),
                    html.Div([
                        html.Button('🚇 Liverpool Street', 
                                   id='btn-liverpool-street', 
                                   n_clicks=0,
                                   style={
                                       'width': '100%', 
                                       'padding': '10px', 
                                       'marginBottom': '8px',
                                       'background': '#ffffff',
                                       'color': '#667eea', 
                                       'border': '2px solid #667eea', 
                                       'borderRadius': '6px',
                                       'cursor': 'pointer', 
                                       'fontWeight': '600',
                                       'fontSize': '13px',
                                       'transition': 'all 0.2s',
                                       'boxSizing': 'border-box'
                                   }),
                        html.Button('🚇 Moorgate', 
                                   id='btn-moorgate', 
                                   n_clicks=0,
                                   style={
                                       'width': '100%', 
                                       'padding': '10px', 
                                       'marginBottom': '8px',
                                       'background': '#ffffff',
                                       'color': '#667eea', 
                                       'border': '2px solid #667eea', 
                                       'borderRadius': '6px',
                                       'cursor': 'pointer', 
                                       'fontWeight': '600',
                                       'fontSize': '13px',
                                       'transition': 'all 0.2s',
                                       'boxSizing': 'border-box'
                                   }),
                        html.Button('🚇 Aldgate', 
                                   id='btn-aldgate', 
                                   n_clicks=0,
                                   style={
                                       'width': '100%', 
                                       'padding': '10px', 
                                       'marginBottom': '8px',
                                       'background': '#ffffff',
                                       'color': '#667eea', 
                                       'border': '2px solid #667eea', 
                                       'borderRadius': '6px',
                                       'cursor': 'pointer', 
                                       'fontWeight': '600',
                                       'fontSize': '13px',
                                       'transition': 'all 0.2s',
                                       'boxSizing': 'border-box'
                                   }),
                        html.Button('🚇 Bank', 
                                   id='btn-bank', 
                                   n_clicks=0,
                                   style={
                                       'width': '100%', 
                                       'padding': '10px', 
                                       'marginBottom': '8px',
                                       'background': '#ffffff',
                                       'color': '#667eea', 
                                       'border': '2px solid #667eea', 
                                       'borderRadius': '6px',
                                       'cursor': 'pointer', 
                                       'fontWeight': '600',
                                       'fontSize': '13px',
                                       'transition': 'all 0.2s',
                                       'boxSizing': 'border-box'
                                   }),
                        html.Button('🚇 Aldgate East', 
                                   id='btn-aldgate-east', 
                                   n_clicks=0,
                                   style={
                                       'width': '100%', 
                                       'padding': '10px', 
                                       'marginBottom': '8px',
                                       'background': '#ffffff',
                                       'color': '#667eea', 
                                       'border': '2px solid #667eea', 
                                       'borderRadius': '6px',
                                       'cursor': 'pointer', 
                                       'fontWeight': '600',
                                       'fontSize': '13px',
                                       'transition': 'all 0.2s',
                                       'boxSizing': 'border-box'
                                   }),
                        html.Button("🚇 King's Cross", 
                                   id='btn-kings-cross', 
                                   n_clicks=0,
                                   style={
                                       'width': '100%', 
                                       'padding': '10px', 
                                       'marginBottom': '8px',
                                       'background': '#ffffff',
                                       'color': '#667eea', 
                                       'border': '2px solid #667eea', 
                                       'borderRadius': '6px',
                                       'cursor': 'pointer', 
                                       'fontWeight': '600',
                                       'fontSize': '13px',
                                       'transition': 'all 0.2s',
                                       'boxSizing': 'border-box'
                                   }),
                        html.Button('🚇 Farringdon', 
                                   id='btn-farringdon', 
                                   n_clicks=0,
                                   style={
                                       'width': '100%', 
                                       'padding': '10px', 
                                       'marginBottom': '15px',
                                       'background': '#ffffff',
                                       'color': '#667eea', 
                                       'border': '2px solid #667eea', 
                                       'borderRadius': '6px',
                                       'cursor': 'pointer', 
                                       'fontWeight': '600',
                                       'fontSize': '13px',
                                       'transition': 'all 0.2s',
                                       'boxSizing': 'border-box'
                                   }),
                    ], style={'marginBottom': '15px'}),
                    
                    html.Label("Latitude", style={
                        'fontWeight': '600', 
                        'color': '#495057',
                        'marginBottom': '8px',
                        'display': 'block',
                        'fontSize': '14px'
                    }),
                    dcc.Input(
                        id='lat-input', 
                        type='number', 
                        value=51.5074, 
                        step=0.0001,
                        placeholder='e.g., 51.5074',
                        style={
                            'width': '100%', 
                            'marginBottom': '15px', 
                            'padding': '10px',
                            'border': '2px solid #e9ecef',
                            'borderRadius': '6px',
                            'fontSize': '14px',
                            'boxSizing': 'border-box'
                        }
                    ),
                    
                    html.Label("Longitude", style={
                        'fontWeight': '600', 
                        'color': '#495057',
                        'marginBottom': '8px',
                        'display': 'block',
                        'fontSize': '14px'
                    }),
                    dcc.Input(
                        id='lon-input', 
                        type='number', 
                        value=-0.1278, 
                        step=0.0001,
                        placeholder='e.g., -0.1278',
                        style={
                            'width': '100%', 
                            'marginBottom': '15px', 
                            'padding': '10px',
                            'border': '2px solid #e9ecef',
                            'borderRadius': '6px',
                            'fontSize': '14px',
                            'boxSizing': 'border-box'
                        }
                    ),
                    
                    html.Label("Max Distance (km)", style={
                        'fontWeight': '600', 
                        'color': '#495057',
                        'marginBottom': '8px',
                        'display': 'block',
                        'fontSize': '14px'
                    }),
                    dcc.Input(
                        id='distance-input', 
                        type='number', 
                        value=10, 
                        min=0, 
                        step=0.1,
                        placeholder='e.g., 10',
                        style={
                            'width': '100%', 
                            'marginBottom': '15px', 
                            'padding': '10px',
                            'border': '2px solid #e9ecef',
                            'borderRadius': '6px',
                            'fontSize': '14px',
                            'boxSizing': 'border-box'
                        }
                    ),
                    
                    html.Button('Apply Distance Filter', 
                               id='apply-distance-btn', 
                               n_clicks=0,
                               style={
                                   'width': '100%', 
                                   'padding': '12px', 
                                   'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                   'color': 'white', 
                                   'border': 'none', 
                                   'borderRadius': '6px',
                                   'cursor': 'pointer', 
                                   'fontWeight': '600',
                                   'fontSize': '15px',
                                   'transition': 'transform 0.2s',
                                   'boxShadow': '0 4px 6px rgba(102, 126, 234, 0.3)',
                                   'boxSizing': 'border-box'
                               })
                ], style={
                    'padding': '20px',
                    'backgroundColor': '#f8f9fa',
                    'borderRadius': '8px',
                    'marginTop': '10px'
                })
            ], style={
                'padding': '30px', 
                'backgroundColor': 'white', 
                'borderRadius': '12px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                'border': '1px solid #e9ecef',
                'height': '100%',
                'boxSizing': 'border-box'
            })
        ], style={
            'width': '25%', 
            'display': 'inline-block', 
            'verticalAlign': 'top', 
            'paddingRight': '15px',
            'boxSizing': 'border-box'
        }),
        
        # Main Content
        html.Div([
            # Summary Cards
            html.Div([
                html.Div([
                    html.Div("📊", style={'fontSize': '32px', 'marginBottom': '10px'}),
                    html.H4("Total Listings", style={
                        'color': '#6c757d', 
                        'fontSize': '13px', 
                        'margin': '0',
                        'fontWeight': '500',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px'
                    }),
                    html.H2(id='total-listings', style={
                        'color': '#1a1a2e', 
                        'margin': '8px 0 0 0',
                        'fontWeight': '700',
                        'fontSize': '32px'
                    })
                ], style={
                    'flex': '1', 
                    'padding': '25px', 
                    'backgroundColor': 'white', 
                    'borderRadius': '12px', 
                    'margin': '0 8px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                    'textAlign': 'center',
                    'border': '1px solid #e9ecef',
                    'boxSizing': 'border-box'
                }),
                
                html.Div([
                    html.Div("✅", style={'fontSize': '32px', 'marginBottom': '10px'}),
                    html.H4("Matching", style={
                        'color': '#6c757d', 
                        'fontSize': '13px', 
                        'margin': '0',
                        'fontWeight': '500',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px'
                    }),
                    html.H2(id='filtered-listings', style={
                        'color': '#28a745', 
                        'margin': '8px 0 0 0',
                        'fontWeight': '700',
                        'fontSize': '32px'
                    })
                ], style={
                    'flex': '1', 
                    'padding': '25px', 
                    'backgroundColor': 'white', 
                    'borderRadius': '12px', 
                    'margin': '0 8px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                    'textAlign': 'center',
                    'border': '1px solid #e9ecef',
                    'boxSizing': 'border-box'
                }),
                
                html.Div([
                    html.Div("💰", style={'fontSize': '32px', 'marginBottom': '10px'}),
                    html.H4("Avg Price", style={
                        'color': '#6c757d', 
                        'fontSize': '13px', 
                        'margin': '0',
                        'fontWeight': '500',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px'
                    }),
                    html.H2(id='avg-price', style={
                        'color': '#dc3545', 
                        'margin': '8px 0 0 0',
                        'fontWeight': '700',
                        'fontSize': '32px'
                    })
                ], style={
                    'flex': '1', 
                    'padding': '25px', 
                    'backgroundColor': 'white', 
                    'borderRadius': '12px', 
                    'margin': '0 8px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                    'textAlign': 'center',
                    'border': '1px solid #e9ecef',
                    'boxSizing': 'border-box'
                }),
                
                html.Div([
                    html.Div("📏", style={'fontSize': '32px', 'marginBottom': '10px'}),
                    html.H4("Avg Distance", style={
                        'color': '#6c757d', 
                        'fontSize': '13px', 
                        'margin': '0',
                        'fontWeight': '500',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px'
                    }),
                    html.H2(id='avg-distance', style={
                        'color': '#6f42c1', 
                        'margin': '8px 0 0 0',
                        'fontWeight': '700',
                        'fontSize': '32px'
                    })
                ], style={
                    'flex': '1', 
                    'padding': '25px', 
                    'backgroundColor': 'white', 
                    'borderRadius': '12px', 
                    'margin': '0 8px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                    'textAlign': 'center',
                    'border': '1px solid #e9ecef',
                    'boxSizing': 'border-box'
                }),
            ], style={
                'display': 'flex', 
                'marginBottom': '25px',
                'marginLeft': '-8px',
                'marginRight': '-8px'
            }),
            
            # Narrative Text
            html.Div(id='narrative-text', style={
                'padding': '20px 25px', 
                'background': 'linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%)',
                'borderRadius': '12px', 
                'marginBottom': '25px',
                'color': '#1a1a2e', 
                'lineHeight': '1.8',
                'fontSize': '15px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.05)',
                'border': '1px solid #e1bee7',
                'boxSizing': 'border-box'
            }),
            
            # Main Map
            html.Div([
                dcc.Graph(id='main-map', style={'height': '550px'}, config={'displayModeBar': False})
            ], style={
                'marginBottom': '25px', 
                'backgroundColor': 'white', 
                'borderRadius': '12px', 
                'padding': '20px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                'border': '1px solid #e9ecef',
                'boxSizing': 'border-box'
            }),
            
            # Price Distribution Chart (full width)
            html.Div([
                dcc.Graph(id='price-distribution', config={'displayModeBar': False})
            ], style={
                'marginBottom': '25px',
                'backgroundColor': 'white',
                'borderRadius': '12px', 
                'padding': '20px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                'border': '1px solid #e9ecef',
                'boxSizing': 'border-box'
            }),
            
            # Table Section
            html.Div([
                html.Div([
                    html.H3("📋 Property Listings", style={
                        'display': 'inline-block',
                        'color': '#1a1a2e',
                        'fontWeight': '600',
                        'fontSize': '22px',
                        'margin': '0'
                    }),
                    html.Div([
                        dcc.RadioItems(
                            id='table-toggle',
                            options=[
                                {'label': ' Filtered Only', 'value': 'filtered'},
                                {'label': ' All Listings', 'value': 'all'}
                            ],
                            value='filtered',
                            inline=True,
                            style={'fontSize': '14px'},
                            labelStyle={'marginLeft': '15px', 'fontWeight': '500'}
                        )
                    ], style={'display': 'inline-block', 'float': 'right'})
                ], style={'marginBottom': '20px', 'overflow': 'hidden'}),
                
                html.Div(id='listings-table-container'),
                
                # Pagination controls
                html.Div([
                    html.Button('← Previous', 
                               id='prev-page-btn', 
                               n_clicks=0,
                               style={
                                   'padding': '10px 20px', 
                                   'background': '#667eea',
                                   'color': 'white', 
                                   'border': 'none', 
                                   'borderRadius': '6px',
                                   'cursor': 'pointer', 
                                   'fontWeight': '600',
                                   'fontSize': '14px',
                                   'marginRight': '10px',
                                   'transition': 'all 0.2s'
                               }),
                    html.Span(id='page-info', 
                             style={
                                 'display': 'inline-block',
                                 'padding': '10px 20px',
                                 'fontWeight': '600',
                                 'fontSize': '14px',
                                 'color': '#1a1a2e'
                             }),
                    html.Button('Next →', 
                               id='next-page-btn', 
                               n_clicks=0,
                               style={
                                   'padding': '10px 20px', 
                                   'background': '#667eea',
                                   'color': 'white', 
                                   'border': 'none', 
                                   'borderRadius': '6px',
                                   'cursor': 'pointer', 
                                   'fontWeight': '600',
                                   'fontSize': '14px',
                                   'marginLeft': '10px',
                                   'transition': 'all 0.2s'
                               })
                ], style={
                    'textAlign': 'center',
                    'marginTop': '20px'
                }),
                
                # Hidden div to store current page
                dcc.Store(id='current-page', data=1)
                
            ], style={
                'backgroundColor': 'white', 
                'borderRadius': '12px', 
                'padding': '25px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                'border': '1px solid #e9ecef',
                'boxSizing': 'border-box',
                'width': '100%'
            })
            
        ], style={
            'width': '75%', 
            'display': 'inline-block', 
            'verticalAlign': 'top', 
            'paddingLeft': '15px',
            'boxSizing': 'border-box'
        }),
    ], style={
        'maxWidth': '1800px', 
        'margin': '0 auto', 
        'padding': '0 20px',
        'boxSizing': 'border-box'
    }),
    
    # Hidden div to store distance data
    dcc.Store(id='distance-data'),
    
    # Add Location component for opening URLs
    dcc.Location(id='url-redirect', refresh=False)
    
], style={
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    'backgroundColor': '#f8f9fa',
    'minHeight': '100vh',
    'padding': '0 0 40px 0',
    'boxSizing': 'border-box'
})

# Callback to update location inputs when station buttons are clicked
@app.callback(
    [Output('lat-input', 'value'),
     Output('lon-input', 'value')],
    [Input('btn-liverpool-street', 'n_clicks'),
     Input('btn-moorgate', 'n_clicks'),
     Input('btn-aldgate', 'n_clicks'),
     Input('btn-bank', 'n_clicks'),
     Input('btn-aldgate-east', 'n_clicks'),
     Input('btn-kings-cross', 'n_clicks'),
     Input('btn-farringdon', 'n_clicks')],
    [State('lat-input', 'value'),
     State('lon-input', 'value')]
)
def update_location_from_buttons(liverpool_clicks, moorgate_clicks, aldgate_clicks, 
                                 bank_clicks, aldgate_east_clicks, kings_cross_clicks,
                                 farringdon_clicks, current_lat, current_lon):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return current_lat, current_lon
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'btn-liverpool-street':
        return 51.5188, -0.0814
    elif button_id == 'btn-moorgate':
        return 51.5187, -0.0890
    elif button_id == 'btn-aldgate':
        return 51.5144, -0.0757
    elif button_id == 'btn-bank':
        return 51.5112, -0.0879
    elif button_id == 'btn-aldgate-east':
        return 51.5153, -0.0718
    elif button_id == 'btn-kings-cross':
        return 51.5316, -0.1236
    elif button_id == 'btn-farringdon':
        return 51.5203, -0.1055
    
    return current_lat, current_lon

# Callback to calculate distances
@app.callback(
    Output('distance-data', 'data'),
    Input('apply-distance-btn', 'n_clicks'),
    State('lat-input', 'value'),
    State('lon-input', 'value')
)
def calculate_distances(n_clicks, lat, lon):
    if lat is None or lon is None:
        return None
    
    distances = df_clean.apply(
        lambda row: haversine(lat, lon, row['latitude'], row['longitude']),
        axis=1
    )
    return {'lat': lat, 'lon': lon, 'distances': distances.tolist()}

# Callback to handle pagination
@app.callback(
    Output('current-page', 'data'),
    [Input('prev-page-btn', 'n_clicks'),
     Input('next-page-btn', 'n_clicks'),
     Input('bedrooms-filter', 'value'),
     Input('bathrooms-filter', 'value'),
     Input('price-slider', 'value'),
     Input('distance-data', 'data'),
     Input('distance-input', 'value'),
     Input('table-toggle', 'value')],
    State('current-page', 'data')
)
def update_page(prev_clicks, next_clicks, bedrooms, bathrooms, price_range, 
                distance_data, max_distance, table_toggle, current_page):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return 1
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Reset to page 1 if filters change
    if trigger_id not in ['prev-page-btn', 'next-page-btn']:
        return 1
    
    # Handle pagination buttons
    if trigger_id == 'prev-page-btn':
        return max(1, current_page - 1)
    elif trigger_id == 'next-page-btn':
        return current_page + 1
    
    return current_page

# Main callback to update all components
@app.callback(
    [Output('total-listings', 'children'),
     Output('filtered-listings', 'children'),
     Output('avg-price', 'children'),
     Output('avg-distance', 'children'),
     Output('narrative-text', 'children'),
     Output('main-map', 'figure'),
     Output('price-distribution', 'figure'),
     Output('listings-table-container', 'children'),
     Output('page-info', 'children'),
     Output('prev-page-btn', 'disabled'),
     Output('next-page-btn', 'disabled')],
    [Input('bedrooms-filter', 'value'),
     Input('bathrooms-filter', 'value'),
     Input('price-slider', 'value'),
     Input('distance-data', 'data'),
     Input('distance-input', 'value'),
     Input('table-toggle', 'value'),
     Input('current-page', 'data')]
)
def update_dashboard(bedrooms, bathrooms, price_range, distance_data, max_distance, table_toggle, current_page):
    # Start with clean data
    filtered_df = df_clean.copy()
    
    # Add distance column
    if distance_data and distance_data.get('distances'):
        filtered_df['distance_km'] = distance_data['distances']
    else:
        filtered_df['distance_km'] = 0
    
    # Apply filters
    if bedrooms != 'all':
        filtered_df = filtered_df[filtered_df['bedrooms'] == bedrooms]
    
    if bathrooms != 'all':
        filtered_df = filtered_df[filtered_df['bathrooms'] == bathrooms]
    
    filtered_df = filtered_df[(filtered_df['price'] >= price_range[0]) & 
                              (filtered_df['price'] <= price_range[1])]
    
    if distance_data and max_distance:
        filtered_df = filtered_df[filtered_df['distance_km'] <= max_distance]
    
    # Summary stats
    total_count = len(df_clean)
    filtered_count = len(filtered_df)
    avg_price = f"£{filtered_df['price'].mean():.0f}" if filtered_count > 0 else "N/A"
    avg_dist = f"{filtered_df['distance_km'].mean():.1f} km" if filtered_count > 0 and distance_data else "N/A"
    
    # Narrative
    narrative = f"🔍 Found {filtered_count} properties matching your criteria out of {total_count} total listings. "
    if filtered_count > 0:
        narrative += f"The average monthly rent is {avg_price}. "
        if distance_data:
            narrative += f"Properties are on average {avg_dist} from your selected location. "
        narrative += "Explore the map and charts below to find your perfect flat! 🏡"
    else:
        narrative += "Try adjusting your filters to see more results. 🔧"
    
    # Main map with clickable markers
    if filtered_count > 0:
        filtered_df_map = filtered_df.copy()
        
        # Create hover text
        hover_texts = []
        for idx, row in filtered_df_map.iterrows():
            hover_text = f"<b>Price:</b> £{row['price']:,.0f}<br>"
            hover_text += f"<b>Bedrooms:</b> {row['bedrooms']}<br>"
            hover_text += f"<b>Bathrooms:</b> {row['bathrooms']}<br>"
            hover_text += f"<b>Distance:</b> {row['distance_km']:.2f} km<br>"
            if 'area' in row and pd.notna(row['area']):
                hover_text += f"<b>Area:</b> {row['area']}<br>"
            hover_text += "<b>Click to view property</b>"
            hover_texts.append(hover_text)
        
        map_fig = go.Figure()
        
        # Add property markers with URLs in customdata
        map_fig.add_trace(go.Scattermap(
            lat=filtered_df_map['latitude'],
            lon=filtered_df_map['longitude'],
            mode='markers',
            marker=dict(
                size=filtered_df_map['bedrooms'] * 3 + 5,
                color=filtered_df_map['price'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Price (£)")
            ),
            text=hover_texts,
            hovertemplate='%{text}<extra></extra>',
            customdata=filtered_df_map['url'].values if 'url' in filtered_df_map.columns else None,
            name='Properties',
            selected=dict(marker=dict(opacity=1)),
            unselected=dict(marker=dict(opacity=1))
        ))
        
        # Add selected location marker if distance data exists
        if distance_data:
            map_fig.add_trace(go.Scattermap(
                lat=[distance_data['lat']],
                lon=[distance_data['lon']],
                mode='markers',
                marker=dict(size=15, color='red', symbol='star'),
                name='Selected Location',
                hovertemplate='<b>Selected Location</b><extra></extra>',
                showlegend=False
            ))
        
        map_fig.update_layout(
            map=dict(
                style='open-street-map',
                center=dict(
                    lat=filtered_df_map['latitude'].mean(),
                    lon=filtered_df_map['longitude'].mean()
                ),
                zoom=10
            ),
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            height=550,
            title='🗺️ Property Locations (Click markers to view listings)',
            title_font_size=20,
            title_font_family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto',
            title_font_color='#1a1a2e',
            font=dict(family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto'),
            showlegend=False,
            clickmode='event+select'
        )
        
        # Add JavaScript to handle clicks and open URLs
        map_fig.update_layout(
            updatemenus=[],
            annotations=[]
        )
        
    else:
        map_fig = go.Figure()
        map_fig.add_annotation(
            text="No properties match your filters 😔<br>Try adjusting your criteria",
            xref="paper", yref="paper", 
            x=0.5, y=0.5, 
            showarrow=False,
            font=dict(size=16, color='#6c757d')
        )
        map_fig.update_layout(height=550)
    
    # Price distribution with improved styling and prettier hover
    if filtered_count > 0:
        price_fig = px.histogram(
            filtered_df,
            x='price',
            nbins=30,
            title='💷 Price Distribution',
            labels={'price': 'Monthly Rent (£)', 'count': 'Count'},
            color_discrete_sequence=['#667eea']
        )
        
        # Update hover template for prettier display
        price_fig.update_traces(
            hovertemplate='<b>Price Range:</b> £%{x:,.0f}<br>' +
                         '<b>Count:</b> %{y} properties<br>' +
                         '<extra></extra>',
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto',
                font_color='#1a1a2e',
                bordercolor='#667eea'
            )
        )
        
        price_fig.update_layout(
            showlegend=False, 
            title_font_size=18,
            title_font_color='#1a1a2e',
            font=dict(family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode='closest'
        )
        price_fig.update_xaxes(showgrid=True, gridcolor='#e9ecef')
        price_fig.update_yaxes(showgrid=True, gridcolor='#e9ecef', title='Count')
    else:
        price_fig = go.Figure()
        price_fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper", 
            x=0.5, y=0.5, 
            showarrow=False,
            font=dict(size=14, color='#6c757d')
        )
    
    # Table - Use Dash DataTable with sorting only (no filtering)
    table_df = filtered_df if table_toggle == 'filtered' else df_clean.copy()
    if distance_data and distance_data.get('distances'):
        if table_toggle == 'all':
            table_df['distance_km'] = distance_data['distances']
    
    # Round distance_km to 3 decimal places
    if 'distance_km' in table_df.columns:
        table_df['distance_km'] = table_df['distance_km'].round(3)
    
    # Pagination settings
    items_per_page = 10
    total_items = len(table_df)
    total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
    
    # Ensure current_page is within bounds
    current_page = max(1, min(current_page, total_pages))
    
    # Calculate start and end indices
    start_idx = (current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Get page data
    page_df = table_df.iloc[start_idx:end_idx]
    
    # Select columns for display
    table_columns = ['price', 'bedrooms', 'bathrooms', 'distance_km']
    if 'area' in table_df.columns:
        table_columns.insert(3, 'area')
    if 'displayAddress' in table_df.columns:
        table_columns.append('displayAddress')
    if 'addedOn' in table_df.columns:
        table_columns.append('addedOn')
    if 'propertyType' in table_df.columns:
        table_columns.append('propertyType')
    if 'url' in table_df.columns:
        table_columns.append('url')
    
    # Keep only columns that exist
    table_columns = [col for col in table_columns if col in table_df.columns]
    
    # Prepare data for DataTable
    table_data = page_df[table_columns].to_dict('records')
    
    # Create column definitions with proper names
    columns = []
    for col in table_columns:
        if col == 'displayAddress':
            col_name = 'Display Address'
        elif col == 'addedOn':
            col_name = 'Added On'
        elif col == 'propertyType':
            col_name = 'Property Type'
        elif col == 'distance_km':
            col_name = 'Distance (km)'
        elif col == 'url':
            col_name = '🔗 View Property'
        else:
            col_name = col.replace('_', ' ').title()
        
        # Make URL column a presentation column with links
        if col == 'url':
            columns.append({
                'name': col_name,
                'id': col,
                'presentation': 'markdown'
            })
        else:
            columns.append({
                'name': col_name,
                'id': col
            })
    
    # Convert URLs to markdown links in the data with prettier styling
    if 'url' in table_columns:
        for row in table_data:
            if row.get('url') and pd.notna(row['url']):
                url_str = str(row['url']).strip()
                if url_str and (url_str.startswith('http://') or url_str.startswith('https://')):
                    row['url'] = f'[🏠 View Listing]({url_str})'
                else:
                    row['url'] = '❌ Invalid'
            else:
                row['url'] = '—'
    
    # Create DataTable with sorting only (no filtering)
    table_component = dash_table.DataTable(
        data=table_data,
        columns=columns,
        style_table={
            'overflowX': 'auto',
            'width': '100%'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '14px',
            'fontSize': '14px',
            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            'maxWidth': '300px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis'
        },
        style_header={
            'backgroundColor': '#1a1a2e',
            'color': 'white',
            'fontWeight': '600',
            'textTransform': 'uppercase',
            'fontSize': '12px',
            'letterSpacing': '0.5px',
            'padding': '14px',
            'border': '1px solid #1a1a2e'
        },
        style_data={
            'border': '1px solid #e9ecef'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8f9fa'
            },
            {
                'if': {'column_id': 'url'},
                'textAlign': 'center',
                'fontWeight': '600',
                'color': '#667eea'
            }
        ],
        style_cell_conditional=[
            {
                'if': {'column_id': 'url'},
                'width': '150px',
                'minWidth': '150px',
                'maxWidth': '150px'
            }
        ],
        sort_action='native',    # Enable sorting only
        page_action='none',      # We handle pagination ourselves
        markdown_options={'link_target': '_blank'}  # Open links in new tab
    )
    
    # Page info
    page_info_text = f"Page {current_page} of {total_pages} (Showing {start_idx + 1}-{end_idx} of {total_items} properties)"
    
    # Disable buttons
    prev_disabled = current_page <= 1
    next_disabled = current_page >= total_pages
    
    return (
        str(total_count),
        str(filtered_count),
        avg_price,
        avg_dist,
        narrative,
        map_fig,
        price_fig,
        table_component,
        page_info_text,
        prev_disabled,
        next_disabled
    )

# Add clientside callback to handle map clicks and open URLs
app.clientside_callback(
    """
    function(clickData) {
        if (clickData && clickData.points && clickData.points.length > 0) {
            var point = clickData.points[0];
            if (point.customdata) {
                var url = point.customdata;
                if (url && (url.startsWith('http://') || url.startsWith('https://'))) {
                    window.open(url, '_blank');
                }
            }
        }
        return '';
    }
    """,
    Output('url-redirect', 'href'),
    Input('main-map', 'clickData')
)

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8060)
