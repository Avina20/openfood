import dash
from dash import dcc, html
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np

# Define color scheme inspired by the reference image
colors = {
    'background': '#0A1022',  # Dark blue background
    'text': '#FFFFFF',        # White text
    'accent1': '#5D6CDF',     # Purple accent
    'accent2': '#46C9E5',     # Teal accent
    'accent3': '#FFC857',     # Yellow accent
    'panel': '#15213B',       # Slightly lighter background for panels
    'grid': '#1E2A45',        # Grid lines color
}

# Gradient colors for visualizations (similar to the flowing lines in the reference)
color_scale = px.colors.sequential.Plasma

# Custom CSS for better styling
external_stylesheets = [
    {
        'href': 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap',
        'rel': 'stylesheet'
    }
]

# Initialize the Dash app
app = dash.Dash(__name__, 
                external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True, 
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}])
server = app.server
app.title = 'OpenFoodFacts Explorer'

# Custom styles
tab_style = {
    'backgroundColor': colors['panel'],
    'color': colors['text'],
    'padding': '10px',
    'borderRadius': '5px 5px 0 0',
    'borderBottom': f'3px solid {colors["background"]}',
    'fontFamily': 'Montserrat, sans-serif',
    'fontWeight': '500',
}

tab_selected_style = {
    'backgroundColor': colors['panel'],
    'color': colors['accent2'],
    'padding': '10px',
    'borderRadius': '5px 5px 0 0',
    'borderBottom': f'3px solid {colors["accent2"]}',
    'fontFamily': 'Montserrat, sans-serif',
    'fontWeight': '600',
}

# Card component for consistent styling
def create_card(title, content, width='100%'):
    return html.Div([
        html.Div([
            html.H4(title, className='card-title')
        ], className='card-header'),
        html.Div(content, className='card-body')
    ], className='dashboard-card', style={'width': width})

# Helper function to convert HEX to RGBA
def hex_to_rgba(hex_color, alpha):
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    r, g, b = tuple(int(hex_color[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    return f'rgba({r},{g},{b},{alpha})'

# Layout for the Nutritional Overview tab
nutritional_overview_tab = html.Div([
    # Title & Introduction section
    html.Div([
        html.H2("Food Nutritional Overview", className="dashboard-title"),
        html.P("Explore nutritional trends across different food products and categories.", className="dashboard-subtitle")
    ], className="header-section"),
    
    # Filters row
    html.Div([
        html.Div([
            html.Label("Select Countries", className="filter-label"),
            dcc.Dropdown(
                id='country-selector',
                options=[{'label': 'All', 'value': 'all'}],  # Will be populated dynamically
                value=['us', 'fr', 'uk', 'de', 'es', 'it', 'cn', 'jp', 'in', 'br', 'au'],  # Default selected
                multi=True,
                className="filter-dropdown"
            )
        ], className="filter-item", style={'width': '32%'}),
        
        html.Div([
            html.Label("Select Categories", className="filter-label"),
            dcc.Dropdown(
                id='category-selector',
                options=[{'label': 'All', 'value': 'all'}],  # Will be populated dynamically 
                value='all',
                className="filter-dropdown"
            )
        ], className="filter-item", style={'width': '32%'}),
        
        html.Div([
            html.Label("NOVA Group Range", className="filter-label"),
            dcc.RangeSlider(
                id='nova-slider',
                min=1,
                max=4,
                step=1,
                marks={i: str(i) for i in range(1, 5)},
                value=[1, 4],
                className="filter-slider"
            )
        ], className="filter-item", style={'width': '32%'}),
    ], className="filters-container"),
    
    # Summary stats row - Key metrics
    html.Div([
        html.Div([
            html.H3("7.8", className="metric-value"),
            html.P("Avg Nutritional Score", className="metric-label")
        ], className="metric-card", style={'backgroundColor': colors['accent1']}),
        
        html.Div([
            html.H3("3.1g", className="metric-value"),
            html.P("Avg Sugar Content", className="metric-label")
        ], className="metric-card", style={'backgroundColor': colors['accent2']}),
        
        html.Div([
            html.H3("2.4", className="metric-value"),
            html.P("Avg NOVA Group", className="metric-label")
        ], className="metric-card", style={'backgroundColor': colors['accent3']}),
        
        html.Div([
            html.H3("B", className="metric-value"),
            html.P("Most Common Grade", className="metric-label")
        ], className="metric-card", style={'backgroundColor': '#DC3977'}),
    ], className="metrics-container"),
    
    # Main charts row - Top
    html.Div([
        # Left side: Nutrition Grade Distribution
        html.Div([
            create_card("Nutrition Grade Distribution", [
                dcc.Graph(
                    id='nutrition-grade-chart',
                    config={'displayModeBar': False},
                    className="chart-element"
                )
            ])
        ], className="chart-container-half"),
        
        # Right side: Macronutrient Comparison
        html.Div([
            create_card("Macronutrient Comparison", [
                dcc.Graph(
                    id='macronutrient-chart',
                    config={'displayModeBar': False},
                    className="chart-element"
                )            
            ])
        ], className="chart-container-half"),
    ], className="charts-row"),
    
    # Bottom chart row - Radar and sankey
    html.Div([
        # Left side: Nutritional Radar
        html.Div([
            create_card("Nutritional Radar by Food Category", [
                dcc.Dropdown(
                    id='radar-category-selector',
                    options=[{'label': 'Compare Categories', 'value': 'compare'}],
                    value='compare',
                    clearable=False,
                    className="in-card-dropdown"
                ),
                dcc.Graph(
                    id='nutrition-radar-chart',
                    config={'displayModeBar': False},
                    className="chart-element"
                )
            ])
        ], className="chart-container-half"),
        
        # Right side: Nutrition Flow (Similar to reference image)
        html.Div([
            create_card("Nutrition Flow Analysis", [
                dcc.Graph(
                    id='nutrition-flow-chart',
                    config={'displayModeBar': False},
                    className="chart-element"
                )
            ])
        ], className="chart-container-half"),
    ], className="charts-row"),
    
], className="dashboard-tab-content")

# Main app layout with tabs
app.layout = html.Div([
    # Header
    html.Div([
        html.Img(src='/assets/logo.png', className="logo"),
        html.H1("OpenFood Dataset Analysis", className="app-title"),
    ], className="app-header"),
    
    # Tabs
    dcc.Tabs([
        dcc.Tab(
            label='Nutritional Overview', 
            children=[nutritional_overview_tab],
            style=tab_style,
            selected_style=tab_selected_style
        ),
        # Other tabs would be defined similarly
    ], className="app-tabs"),
    
    # Footer
    html.Div([
        html.P("OpenFood Dataset Analysis • 2025", className="footer-text"),
    ], className="app-footer"),
    
], className="dashboard-container")

@app.callback(
    dash.dependencies.Output('nutrition-grade-chart', 'figure'),
    [dash.dependencies.Input('country-selector', 'value'),
     dash.dependencies.Input('category-selector', 'value'),
     dash.dependencies.Input('nova-slider', 'value')]
)
def update_nutrition_grade_chart(selected_countries, selected_category, nova_range):
    # This is a mockup function - you would replace with actual data processing
    grade_data = {'A': 32, 'B': 45, 'C': 28, 'D': 18, 'E': 7}
    
    # Create horizontal bar chart with custom styling
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=list(grade_data.keys()),
        x=list(grade_data.values()),
        orientation='h',
        marker=dict(
            color=[colors['accent1'], colors['accent2'], '#5ECDA0', colors['accent3'], '#E15759'],
            line=dict(width=0)
        ),
        hoverinfo='x+y',
        hovertemplate='<b>Grade %{y}</b><br>Products: %{x}<extra></extra>'
    ))
    
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font=dict(family="Montserrat, sans-serif", color=colors['text']),
        title=dict(
            text='',
            font=dict(size=16)
        ),
        xaxis=dict(
            title='Number of Products',
            showgrid=True,
            gridcolor=colors['grid'],
            gridwidth=0.5,
            zeroline=False,
        ),
        yaxis=dict(
            title='',
            categoryorder='array',
            categoryarray=['E', 'D', 'C', 'B', 'A'],  # Reverse order to show A at top
            showgrid=False,
        ),
        margin=dict(l=10, r=10, t=10, b=10),
        bargap=0.15,
    )
    
    return fig

# Example callback for Macronutrient Chart
@app.callback(
    dash.dependencies.Output('macronutrient-chart', 'figure'),
    [dash.dependencies.Input('country-selector', 'value'),
     dash.dependencies.Input('category-selector', 'value'),
     dash.dependencies.Input('nova-slider', 'value')]
)
def update_macronutrient_chart(selected_countries, selected_category, nova_range):
    # Mockup data - replace with actual processing
    nutrients = ['Protein', 'Carbs', 'Fat', 'Fiber', 'Sugar', 'Salt']
    values = [12, 38, 18, 7, 16, 9]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=nutrients,
        y=values,
        marker=dict(
            color=[colors['accent2'], colors['accent1'], colors['accent3'], 
                  '#5ECDA0', '#E15759', '#FF9D5C'],
            line=dict(width=0)
        ),
        text=values,
        texttemplate='%{text}g',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Average: %{y}g<extra></extra>'
    ))
    
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font=dict(family="Montserrat, sans-serif", color=colors['text']),
        title=dict(
            text='',
            font=dict(size=16)
        ),
        xaxis=dict(
            title='',
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            title='Average (g per 100g)',
            showgrid=True,
            gridcolor=colors['grid'],
            gridwidth=0.5,
            zeroline=False,
        ),
        margin=dict(l=10, r=10, t=10, b=10),
        bargap=0.4,
    )
    
    return fig

# Example callback for Radar Chart
@app.callback(
    dash.dependencies.Output('nutrition-radar-chart', 'figure'),
    [dash.dependencies.Input('country-selector', 'value'),
     dash.dependencies.Input('radar-category-selector', 'value'),
     dash.dependencies.Input('nova-slider', 'value')]
)
def update_radar_chart(selected_countries, radar_category, nova_range):
    # Mockup data - replace with actual processing
    categories = ['Protein', 'Carbs', 'Fat', 'Fiber', 'Vitamins', 'Minerals']
    
    # Create three sample food categories for comparison
    fig = go.Figure()
    # Opacity level
    alpha = 0.3
    # Dairy products
    fig.add_trace(go.Scatterpolar(
        r=[8, 4, 7, 2, 9, 6],
        theta=categories,
        fill='toself',
        name='Dairy',
        line=dict(color=colors['accent1']),
        fillcolor=hex_to_rgba(colors['accent1'], alpha),  # 30% opacity
    ))
    
    # Cereal products
    fig.add_trace(go.Scatterpolar(
        r=[5, 9, 3, 8, 4, 7],
        theta=categories,
        fill='toself',
        name='Cereals',
        line=dict(color=colors['accent2']),
        fillcolor=hex_to_rgba(colors['accent2'], alpha),  # 30% opacity
    ))
    
    # Meat products
    fig.add_trace(go.Scatterpolar(
        r=[9, 2, 6, 3, 4, 8],
        theta=categories,
        fill='toself',
        name='Meats',
        line=dict(color=colors['accent3']),
        fillcolor=hex_to_rgba(colors['accent3'], alpha),  # 30% opacity
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                showticklabels=False,
                gridcolor=colors['grid'],
            ),
            angularaxis=dict(
                gridcolor=colors['grid'],
            ),
            bgcolor=colors['background'],
        ),
        font=dict(family="Montserrat, sans-serif", color=colors['text']),
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=12),
        ),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    
    return fig

# Example callback for Flow Chart (similar to reference image)
@app.callback(
    dash.dependencies.Output('nutrition-flow-chart', 'figure'),
    [dash.dependencies.Input('country-selector', 'value'),
     dash.dependencies.Input('category-selector', 'value')]
)
def update_flow_chart(selected_countries, selected_category):
    # This is a mockup of a Sankey diagram similar to the reference image
    # You would replace with actual data processing
    
    # Define node labels
    labels = [
        # Source nodes (categories)
        "Dairy", "Cereals", "Meats", "Fruits", "Vegetables",
        # Mid-level nodes (nutrition properties)
        "High Protein", "Low Fat", "High Fiber", "Low Sugar", "High Vitamins",
        # Target nodes (nutrition grades)
        "Grade A", "Grade B", "Grade C", "Grade D", "Grade E"
    ]
    
    # Define links: source, target, value
    source = [0, 0, 0, 1, 1, 1, 2, 2, 3, 3, 4, 4,  # Categories to properties
              5, 5, 6, 6, 7, 7, 8, 8, 9, 9]         # Properties to grades
    
    target = [5, 6, 8, 5, 7, 8, 5, 6, 7, 9, 7, 9,   # Categories to properties
              10, 11, 10, 12, 11, 13, 12, 14, 10, 11] # Properties to grades
    
    value = [20, 15, 10, 15, 20, 10, 25, 10, 18, 12, 22, 15,
             20, 15, 10, 15, 25, 15, 10, 10, 15, 20]
    
    # Define gradient colors
    node_colors = [
        # Source nodes (food categories)
        colors['accent1'], colors['accent2'], colors['accent3'], '#5ECDA0', '#FF9D5C',
        # Mid nodes (nutrition properties)
        '#7986CB', '#64B5F6', '#4FC3F7', '#4DD0E1', '#4DB6AC',
        # Target nodes (grades)
        '#43A047', '#7CB342', '#C0CA33', '#FFA000', '#E53935'
    ]
    
    link_colors = []
    for i in range(len(source)):
        if target[i] >= 10:  # Links to grades
            # Use gradient based on target grade (A-E)
            color_index = target[i] - 10  # 0-4 for grades A-E
            link_colors.append(['#43A047', '#7CB342', '#C0CA33', '#FFA000', '#E53935'][color_index])
        else:
            # Use source node color with transparency
            link_colors.append(hex_to_rgba(node_colors[source[i]] ,0.5))  # 50% opacity
    
    # Create the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='black', width=0.5),
            label=labels,
            color=node_colors,
            customdata=["Food Category", "Food Category", "Food Category", "Food Category", "Food Category",
                       "Nutrition Property", "Nutrition Property", "Nutrition Property", "Nutrition Property", "Nutrition Property",
                       "Nutrition Grade", "Nutrition Grade", "Nutrition Grade", "Nutrition Grade", "Nutrition Grade"],
            hovertemplate='<b>%{label}</b><br>Type: %{customdata}<extra></extra>',
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors,
            hovertemplate='<b>%{source.label}</b> → <b>%{target.label}</b><br>Value: %{value}<extra></extra>',
        )
    )])
    
    fig.update_layout(
        font=dict(family="Montserrat, sans-serif", color=colors['text']),
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        margin=dict(l=5, r=5, t=5, b=5),
    )
    
    return fig

if __name__ == '__main__':
    app.run(debug=True)