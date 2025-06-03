import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, State, callback
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

# Create a stylesheet with custom colors
colors = {
    'background': '#F9F9F9',
    'text': '#333333',
    'primary': '#2C5282',  # Dark blue
    'secondary': '#4299E1',  # Light blue
    'accent': '#FBD38D',  # Light orange
    'positive': '#68D391',  # Green
    'negative': '#FC8181',  # Red
    'neutral': '#CBD5E0',  # Gray
}
# Gradient colors for visualizations (similar to the flowing lines in the reference)
color_scale = px.colors.sequential.Plasma

# Load the dataset
df = pd.read_csv('openfoodfacts_data.csv')

# Add some GDP per capita data for the countries
gdp_per_capita = {
    'us': 65000, 'fr': 38000, 'uk': 40000, 'de': 45000, 
    'es': 27000, 'it': 31000, 'cn': 10000, 'jp': 40000, 
    'in': 2000, 'br': 8000, 'au': 55000
}
df['gdp_per_capita'] = df['country_code'].map(gdp_per_capita)

def clean_country_name(code):
    country_map = {
        'us': 'United States', 'fr': 'France', 'uk': 'United Kingdom', 
        'de': 'Germany', 'es': 'Spain', 'it': 'Italy', 'cn': 'China', 
        'jp': 'Japan', 'in': 'India', 'br': 'Brazil', 'au': 'Australia'
    }
    return country_map.get(code, code.upper())

df['country_name'] = df['country_code'].apply(clean_country_name)

# Custom CSS for better styling
external_stylesheets = [
    {
        'href': 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap',
        'rel': 'stylesheet'
    }
]

# Initialize the Dash app
app = dash.Dash(__name__, 
                suppress_callback_exceptions=True, 
                external_stylesheets=external_stylesheets,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}])
server = app.server
app.title = 'OpenFoodFacts Explorer'

app.layout = html.Div(style={'backgroundColor': colors['background'], 'padding': '20px'}, children=[
    # Header
    html.Div([
        html.H1('OpenFoodFacts Explorer', 
                style={'textAlign': 'center', 'color': colors['primary'], 'marginBottom': '20px'}),
        html.P('Exploring nutritional data from around the world', 
               style={'textAlign': 'center', 'color': colors['text']})
    ]),
    
    # Filters
    html.Div([
        html.Div([
            html.Label('Select Countries:', style={'color': colors['text'], 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='country-selector',
                options=[{'label': clean_country_name(c), 'value': c} for c in df['country_code'].unique()],
                value=df['country_code'].unique().tolist()[:5],  # Default to first 5 countries
                multi=True
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '2%'}),
        
        html.Div([
            html.Label('Select Nutrition Grade:', style={'color': colors['text'], 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='nutrition-grade-selector',
                options=[{'label': f'Grade {g}', 'value': g} for g in sorted(df['nutrition_grade'].dropna().unique())],
                value=sorted(df['nutrition_grade'].dropna().unique()),
                multi=True
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '2%'}),
        
        html.Div([
            html.Label('Nova Group (Processing Level):', style={'color': colors['text'], 'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='nova-slider',
                min=1, max=4, step=1, value=[1, 4],
                marks={i: str(i) for i in range(1, 5)},
                tooltip={'placement': 'bottom', 'always_visible': True}
            )
        ], style={'width': '30%', 'display': 'inline-block'})
    ], style={'marginBottom': '20px', 'marginTop': '20px'}),
    
    # Dashboard Tabs
    dcc.Tabs([
        # Tab 1: Nutritional Overview
        dcc.Tab(label='Nutritional Overview', children=[
            html.Div([
                # Top row with two charts
                html.Div([
                    # Nutrition Grade Distribution
                    html.Div([
                        dcc.Graph(id='nutrition-grade-chart')
                    ], style={'width': '48%', 'display': 'inline-block'}),
                    
                    # Macronutrient Comparison
                    html.Div([
                        dcc.Graph(id='macronutrient-chart')
                    ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
                ]),
                
                # Bottom row with radar chart
                html.Div([
                    dcc.Graph(id='nutrition-radar-chart')
                ], style={'marginTop': '20px'})
            ])
        ], style={'padding': '20px'}),
        
        # Tab 2: Processing & Additives
        dcc.Tab(label='Processing & Additives', children=[
            html.Div([
                # Top row
                html.Div([
                    # NOVA Group Distribution
                    html.Div([
                        dcc.Graph(id='nova-group-chart')
                    ], style={'width': '48%', 'display': 'inline-block'}),
                    
                    # Additives Count
                    html.Div([
                        dcc.Graph(id='additives-chart')
                    ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
                ]),
                
                # Bottom row
                html.Div([
                    dcc.Graph(id='additives-vs-nutrition-chart')
                ], style={'marginTop': '20px'})
            ])
        ], style={'padding': '20px'}),
        
        # Tab 3: Global Comparisons
        dcc.Tab(label='Global Comparisons', children=[
            html.Div([
                # First chart
                html.Div([
                    dcc.Graph(id='gdp-vs-nutrition-chart')
                ]),
                
                # Second row with two charts
                html.Div([
                    # Continent-level comparison
                    html.Div([
                        dcc.Graph(id='continent-comparison-chart')
                    ], style={'width': '48%', 'display': 'inline-block'}),
                    
                    # Processing level by country
                    html.Div([
                        dcc.Graph(id='processing-by-country-chart')
                    ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
                ], style={'marginTop': '20px'})
            ])
        ], style={'padding': '20px'}),
    ])
])

@app.callback(
    Output('nutrition-grade-chart', 'figure'),
    [Input('country-selector', 'value'),
     Input('nova-slider', 'value')]
)
def update_nutrition_grade_chart(selected_countries, nova_range):
    filtered_df = df[(df['country_code'].isin(selected_countries)) & 
                    (df['nova_group'] >= nova_range[0]) & 
                    (df['nova_group'] <= nova_range[1])]
    
    # Group by nutrition grade and country
    grade_counts = filtered_df.groupby(['country_name', 'nutrition_grade']).size().reset_index(name='count')
    
    # Sort grades for better visualization
    grade_order = ['A', 'B', 'C', 'D', 'E']
    
    fig = px.bar(grade_counts, 
                x='country_name', 
                y='count', 
                color='nutrition_grade',
                color_discrete_map={'A': '#4CAF50', 'B': '#8BC34A', 'C': '#FFC107', 'D': '#FF9800', 'E': '#F44336'},
                category_orders={"nutrition_grade": grade_order},
                title='Nutrition Grade Distribution by Country',
                labels={'count': 'Number of Products', 'country_name': 'Country', 'nutrition_grade': 'Nutrition Grade'})
    
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        legend_title_text='Grade',
        barmode='stack'
    )
    
    return fig

# Callback for Macronutrient Comparison
@app.callback(
    Output('macronutrient-chart', 'figure'),
    [Input('country-selector', 'value'),
     Input('nutrition-grade-selector', 'value'),
     Input('nova-slider', 'value')]
)
def update_macronutrient_chart(selected_countries, selected_grades, nova_range):
    filtered_df = df[(df['country_code'].isin(selected_countries)) & 
                    (df['nutrition_grade'].isin(selected_grades)) &
                    (df['nova_group'] >= nova_range[0]) & 
                    (df['nova_group'] <= nova_range[1])]
    
    # Calculate average macronutrients by country
    macro_avg = filtered_df.groupby('country_name').agg({
        'nutriments.fat_100g': 'mean',
        'nutriments.sugars_100g': 'mean',
        'nutriments.proteins_100g': 'mean',
        'nutriments.carbohydrates_100g': 'mean',
        'nutriments.salt_100g': 'mean'
    }).reset_index()
    
    # Rename columns for better display
    macro_avg.columns = ['Country', 'Fat', 'Sugars', 'Proteins', 'Carbs', 'Salt']
    
    # Melt the dataframe for easier plotting
    melted_df = pd.melt(macro_avg, id_vars=['Country'], 
                         value_vars=['Fat', 'Sugars', 'Proteins', 'Carbs', 'Salt'],
                         var_name='Nutrient', value_name='Amount (g per 100g)')
    
    fig = px.bar(melted_df, 
                x='Country', 
                y='Amount (g per 100g)', 
                color='Nutrient',
                title='Average Macronutrient Content by Country',
                barmode='group',
                color_discrete_map={
                    'Fat': '#FF9800',
                    'Sugars': '#F44336',
                    'Proteins': '#4CAF50',
                    'Carbs': '#2196F3',
                    'Salt': '#9C27B0'
                })
    
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        legend_title_text='Nutrient'
    )
    
    return fig

# Callback for Nutrition Radar Chart
@app.callback(
    Output('nutrition-radar-chart', 'figure'),
    [Input('country-selector', 'value'),
     Input('nutrition-grade-selector', 'value'),
     Input('nova-slider', 'value')]
)
def update_nutrition_radar_chart(selected_countries, selected_grades, nova_range):
    filtered_df = df[(df['country_code'].isin(selected_countries)) & 
                    (df['nutrition_grade'].isin(selected_grades)) &
                    (df['nova_group'] >= nova_range[0]) & 
                    (df['nova_group'] <= nova_range[1])]
    
    # Calculate average nutritional values by country
    radar_data = filtered_df.groupby('country_name').agg({
        'nutriments.fat_100g': 'mean',
        'nutriments.sugars_100g': 'mean',
        'nutriments.proteins_100g': 'mean',
        'nutriments.carbohydrates_100g': 'mean',
        'nutriments.salt_100g': 'mean',
        'additives_n': 'mean',
        'nutrition_score': 'mean'
    }).reset_index()
    
    # Rename columns for better display
    radar_data.columns = ['Country', 'Fat', 'Sugars', 'Proteins', 'Carbs', 'Salt', 'Additives', 'Nutrition Score']
    
    # Create radar chart
    fig = go.Figure()
    
    categories = ['Fat', 'Sugars', 'Proteins', 'Carbs', 'Salt', 'Additives', 'Nutrition Score']
    
    # Add a trace for each country
    for country in radar_data['Country']:
        country_data = radar_data[radar_data['Country'] == country]
        values = country_data[categories].values.flatten().tolist()
        # Add the first value again to close the radar
        values.append(values[0])
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],  # Close the loop
            fill='toself',
            name=country
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, radar_data[categories].max().max() * 1.1]  # Add 10% margin
            )
        ),
        title='Nutritional Profile Comparison',
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    
    return fig

# Callback for NOVA Group Chart
@app.callback(
    Output('nova-group-chart', 'figure'),
    [Input('country-selector', 'value'),
     Input('nutrition-grade-selector', 'value')]
)
def update_nova_group_chart(selected_countries, selected_grades):
    filtered_df = df[(df['country_code'].isin(selected_countries)) & 
                    (df['nutrition_grade'].isin(selected_grades))]
    
    # Group by NOVA group and country
    nova_counts = filtered_df.groupby(['country_name', 'nova_group']).size().reset_index(name='count')
    
    # Add NOVA group descriptions
    nova_descriptions = {
        1: "Unprocessed/minimally processed",
        2: "Processed culinary ingredients",
        3: "Processed foods",
        4: "Ultra-processed foods"
    }
    
    nova_counts['description'] = nova_counts['nova_group'].map(lambda x: f"Group {int(x)}: {nova_descriptions.get(int(x), '')}")
    
    fig = px.bar(nova_counts, 
                x='country_name', 
                y='count', 
                color='description',
                title='Food Processing Level Distribution (NOVA Classification)',
                labels={'count': 'Number of Products', 'country_name': 'Country', 'description': 'NOVA Group'},
                color_discrete_map={
                    f"Group 1: {nova_descriptions[1]}": '#4CAF50',
                    f"Group 2: {nova_descriptions[2]}": '#8BC34A',
                    f"Group 3: {nova_descriptions[3]}": '#FFC107',
                    f"Group 4: {nova_descriptions[4]}": '#F44336'
                })
    
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        legend_title_text='NOVA Classification',
        barmode='stack'
    )
    
    return fig

# Callback for Additives Chart
@app.callback(
    Output('additives-chart', 'figure'),
    [Input('country-selector', 'value'),
     Input('nutrition-grade-selector', 'value'),
     Input('nova-slider', 'value')]
)
def update_additives_chart(selected_countries, selected_grades, nova_range):
    filtered_df = df[(df['country_code'].isin(selected_countries)) & 
                    (df['nutrition_grade'].isin(selected_grades)) &
                    (df['nova_group'] >= nova_range[0]) & 
                    (df['nova_group'] <= nova_range[1])]
    
    # Calculate average additives by country
    additives_avg = filtered_df.groupby('country_name')['additives_n'].mean().reset_index()
    additives_avg.columns = ['Country', 'Average Number of Additives']
    
    # Sort by average additives count
    additives_avg = additives_avg.sort_values('Average Number of Additives', ascending=False)
    
    fig = px.bar(additives_avg, 
                x='Country', 
                y='Average Number of Additives',
                title='Average Number of Additives by Country',
                color='Average Number of Additives',
                color_continuous_scale=['green', 'yellow', 'red'])
    
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    
    return fig


# Callback for Additives vs Nutrition Chart
@app.callback(
    Output('additives-vs-nutrition-chart', 'figure'),
    [Input('country-selector', 'value'),
     Input('nova-slider', 'value')]
)
def update_additives_vs_nutrition_chart(selected_countries, nova_range):
    filtered_df = df[(df['country_code'].isin(selected_countries))]
    
    # Filter for NOVA group if column exists
    if 'nova_group' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['nova_group'] >= nova_range[0]) & 
            (filtered_df['nova_group'] <= nova_range[1])
        ]
    
    # Further filter to ensure we have the needed columns with valid data
    if 'additives_n' in filtered_df.columns and 'nutrition_score' in filtered_df.columns:
        filtered_df = filtered_df[
            (~filtered_df['additives_n'].isna()) &
            (~filtered_df['nutrition_score'].isna())
        ]
    else:
        # If essential columns are missing, create a simple placeholder figure
        fig = go.Figure()
        fig.update_layout(
            title="Required data columns are missing for this visualization",
            xaxis_title="Number of Additives",
            yaxis_title="Nutrition Score",
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text']
        )
        return fig
    
    # Check if we have data after filtering
    if len(filtered_df) == 0:
        fig = go.Figure()
        fig.update_layout(
            title="No data available with current filters",
            xaxis_title="Number of Additives",
            yaxis_title="Nutrition Score",
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text']
        )
        return fig
    
    # Create scatter plot with available columns
    hover_data = []
    if 'brands' in filtered_df.columns: hover_data.append('brands')
    if 'nutrition_grade' in filtered_df.columns: hover_data.append('nutrition_grade')
    if 'nova_group' in filtered_df.columns: hover_data.append('nova_group')
    
    # FIX: Handle NaN values in the size column
    size_column = None
    if 'ingredients_count' in filtered_df.columns:
        # Check if there are non-NaN values in ingredients_count
        if not filtered_df['ingredients_count'].isna().all():
            # Create a copy of the column with NaN values replaced with the median
            filtered_df = filtered_df.copy()
            median_value = filtered_df['ingredients_count'].median()
            if pd.isna(median_value):  # If median is also NaN, use a default value
                median_value = 1.0
            filtered_df['ingredients_count_filled'] = filtered_df['ingredients_count'].fillna(median_value)
            size_column = 'ingredients_count_filled'
    
    # Create scatter plot with plotly express, handling missing columns
    fig = px.scatter(
        filtered_df, 
        x='additives_n', 
        y='nutrition_score',
        color='country_name' if 'country_name' in filtered_df.columns else None,
        size=size_column,  # Now using the NaN-free column or None
        hover_name='product_name' if 'product_name' in filtered_df.columns else None,
        hover_data=hover_data,
        title='Relationship Between Additives and Nutrition Grade',
        labels={
            'additives_n': 'Number of Additives', 
            'nutrition_score': 'Nutrition Score (higher is better)',
            'country_name': 'Country',
            'ingredients_count_filled': 'Ingredient Count'
        }
    )
    
    # Add trend line
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    
    # Add horizontal lines indicating nutrition grades if we have data to determine the range
    if 'nutrition_score' in filtered_df.columns:
        max_additives = filtered_df['additives_n'].max()
        for score, grade in [(5, 'A'), (4, 'B'), (3, 'C'), (2, 'D'), (1, 'E')]:
            fig.add_shape(
                type="line",
                x0=0,
                y0=score,
                x1=max_additives,
                y1=score,
                line=dict(color="gray", width=1, dash="dash"),
            )
            fig.add_annotation(
                x=0,
                y=score,
                text=f"Grade {grade}",
                showarrow=False,
                xshift=-30,
                font=dict(size=10)
            )
    
    return fig


# Callback for GDP vs Nutrition Chart
@app.callback(
    Output('gdp-vs-nutrition-chart', 'figure'),
    [Input('nutrition-grade-selector', 'value'),
     Input('nova-slider', 'value')]
)
def update_gdp_vs_nutrition_chart(selected_grades, nova_range):
    filtered_df = df[(df['nutrition_grade'].isin(selected_grades)) &
                    (df['nova_group'] >= nova_range[0]) & 
                    (df['nova_group'] <= nova_range[1]) &
                    (~df['gdp_per_capita'].isna())]
    
    # Calculate average nutrition score and NOVA group by country
    gdp_data = filtered_df.groupby(['country_name', 'gdp_per_capita']).agg({
        'nutrition_score': 'mean',
        'nova_group': 'mean',
        'additives_n': 'mean'
    }).reset_index()
    
    # Create bubble chart
    fig = px.scatter(gdp_data, 
                    x='gdp_per_capita', 
                    y='nutrition_score',
                    size='additives_n',
                    color='nova_group',
                    hover_name='country_name',
                    title='Economic Development vs Food Quality',
                    labels={'gdp_per_capita': 'GDP per Capita (USD)', 
                            'nutrition_score': 'Average Nutrition Score (higher is better)',
                            'nova_group': 'Average NOVA Group',
                            'additives_n': 'Avg. Additives Count'},
                    color_continuous_scale=['green', 'yellow', 'orange', 'red'])
    
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    
    # Add text labels for each country
    for i, row in gdp_data.iterrows():
        fig.add_annotation(
            x=row['gdp_per_capita'],
            y=row['nutrition_score'],
            text=row['country_name'],
            showarrow=False,
            yshift=10,
            font=dict(size=10)
        )
    
    return fig

        
# Callback for Continent Comparison Chart
@app.callback(
    Output('continent-comparison-chart', 'figure'),
    [Input('nutrition-grade-selector', 'value'),
     Input('nova-slider', 'value')]
)
def update_continent_comparison_chart(selected_grades, nova_range):
    filtered_df = df[(df['nutrition_grade'].isin(selected_grades)) &
                    (df['nova_group'] >= nova_range[0]) & 
                    (df['nova_group'] <= nova_range[1]) &
                    (~df['continent'].isna())]
    
    # Calculate nutrition metrics by continent
    continent_data = filtered_df.groupby('continent').agg({
        'nutrition_score': 'mean',
        'nova_group': 'mean',
        'additives_n': 'mean',
        'nutriments.sugars_100g': 'mean',
        'nutriments.fat_100g': 'mean'
    }).reset_index()
    
    # Rename for better display
    continent_data.columns = ['Continent', 'Nutrition Score', 'NOVA Group', 
                             'Additives Count', 'Sugar (g/100g)', 'Fat (g/100g)']
    
    # Create the subplot figure
    fig = make_subplots(rows=1, cols=3, 
                       subplot_titles=('Nutrition Score', 'Processing Level (NOVA)', 'Additives Count'))
    
    # Add bars for each metric
    fig.add_trace(
        go.Bar(x=continent_data['Continent'], y=continent_data['Nutrition Score'], 
              marker_color='green', showlegend=False),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=continent_data['Continent'], y=continent_data['NOVA Group'], 
              marker_color='orange', showlegend=False),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(x=continent_data['Continent'], y=continent_data['Additives Count'], 
              marker_color='red', showlegend=False),
        row=1, col=3
    )
    
    fig.update_layout(
        title_text='Food Quality Metrics by Continent',
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    
    # Update y-axis titles
    fig.update_yaxes(title_text='Score (higher is better)', row=1, col=1)
    fig.update_yaxes(title_text='NOVA Group (lower is better)', row=1, col=2)
    fig.update_yaxes(title_text='Average Count', row=1, col=3)
    
    return fig

# Callback for Processing by Country Chart
@app.callback(
    Output('processing-by-country-chart', 'figure'),
    [Input('country-selector', 'value'),
     Input('nutrition-grade-selector', 'value')]
)
def update_processing_by_country_chart(selected_countries, selected_grades):
    filtered_df = df[(df['country_code'].isin(selected_countries)) & 
                    (df['nutrition_grade'].isin(selected_grades))]
    
    # Calculate percentage of products in each NOVA group by country
    country_totals = filtered_df.groupby('country_name').size()
    nova_by_country = filtered_df.groupby(['country_name', 'nova_group']).size().unstack().fillna(0)
    
    # Calculate percentages
    for col in nova_by_country.columns:
        nova_by_country[col] = nova_by_country[col] / country_totals * 100
    
    nova_by_country = nova_by_country.reset_index()
    
    # Melt for easier plotting
    melted_df = pd.melt(nova_by_country, 
                         id_vars=['country_name'], 
                         value_vars=sorted(nova_by_country.columns[1:]),
                         var_name='NOVA Group', 
                         value_name='Percentage')
    
    # Create NOVA group descriptions
    nova_descriptions = {
        1.0: "Group 1: Unprocessed/minimally processed",
        2.0: "Group 2: Processed culinary ingredients",
        3.0: "Group 3: Processed foods",
        4.0: "Group 4: Ultra-processed foods"
    }
    
    melted_df['NOVA Description'] = melted_df['NOVA Group'].map(lambda x: nova_descriptions.get(x, f"Group {x}"))
    
    fig = px.bar(melted_df, 
                x='country_name', 
                y='Percentage', 
                color='NOVA Description',
                title='Food Processing Level Distribution by Country (% of Products)',
                labels={'country_name': 'Country', 'Percentage': '% of Products'},
                color_discrete_map={
                    nova_descriptions[1.0]: '#4CAF50',
                    nova_descriptions[2.0]: '#8BC34A',
                    nova_descriptions[3.0]: '#FFC107',
                    nova_descriptions[4.0]: '#F44336'
                })
    
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        legend_title_text='NOVA Classification',
        barmode='stack',
        yaxis=dict(ticksuffix='%')
    )
    
    return fig

app.run(debug=True)