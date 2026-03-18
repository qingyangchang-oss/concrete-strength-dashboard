import pandas as pd
import numpy as np
import os
from dash import Dash, dcc, html, callback, Output, Input
import plotly.graph_objects as go
import plotly.express as px

# Google Sheet URL - exports as CSV
GOOGLE_SHEET_ID = '1adlgl38PJWCIleBQulnZofVx-CJvbjFmejriJnwx9zY'
SHEET_NAME = 'masterSheet'
GOOGLE_SHEET_URL = f'https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'

def load_data():
    """Load data from Google Sheet"""
    try:
        df = pd.read_csv(GOOGLE_SHEET_URL)
        print(f"Loaded {len(df)} rows from Google Sheet")
    except Exception as e:
        print(f"Error loading from Google Sheet: {e}")
        raise e

    # Clean CuringCondition - strip whitespace
    df['CuringCondition'] = df['CuringCondition'].str.strip()

    # Filter for cube tests only and TMC/NC conditions
    df_cubes = df[df['Task'] == 'Cube test'].copy()
    df_filtered = df_cubes[df_cubes['CuringCondition'].isin(['TMC', 'NC'])].copy()

    # Convert numeric columns
    df_filtered['TestingAgeDays'] = pd.to_numeric(df_filtered['TestingAgeDays'], errors='coerce')
    df_filtered['AverageStrength_MPa'] = pd.to_numeric(df_filtered['AverageStrength_MPa'], errors='coerce')
    df_filtered['Cement'] = pd.to_numeric(df_filtered['Cement'], errors='coerce')
    df_filtered['GGBS'] = pd.to_numeric(df_filtered['GGBS'], errors='coerce')

    # Drop rows with missing strength values
    df_filtered = df_filtered.dropna(subset=['AverageStrength_MPa', 'TestingAgeDays'])

    # Create mix design label
    df_filtered['MixDesignLabel'] = df_filtered.apply(
        lambda row: f"{row['Cement Type']} ({row['Cement']*100:.0f}% Cement, {row['GGBS']*100:.0f}% GGBS)",
        axis=1
    )

    return df_filtered

# Load initial data
df_filtered = load_data()

# Initialize Dash app
app = Dash(__name__)
server = app.server  # For deployment with gunicorn

# Left sidebar style
sidebar_style = {
    'width': '280px',
    'minWidth': '280px',
    'padding': '20px',
    'backgroundColor': '#2c3e50',
    'color': 'white',
    'height': '100vh',
    'position': 'fixed',
    'left': 0,
    'top': 0,
    'overflowY': 'auto'
}

# Main content style
content_style = {
    'marginLeft': '300px',
    'padding': '20px',
    'backgroundColor': '#ecf0f1',
    'minHeight': '100vh'
}

app.layout = html.Div([
    # Left Sidebar - Filters
    html.Div([
        html.H2("Filters", style={'color': 'white', 'marginBottom': '20px', 'borderBottom': '2px solid #3498db', 'paddingBottom': '10px'}),

        html.Div([
            html.Label('Grade:', style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
            dcc.Dropdown(
                id='grade-filter',
                options=[{'label': 'All Grades', 'value': 'ALL'}],
                value='ALL',
                clearable=False,
                style={'color': '#2c3e50'}
            )
        ], style={'marginBottom': '20px'}),

        html.Div([
            html.Label('Curing Condition:', style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
            dcc.Dropdown(
                id='curing-filter',
                options=[
                    {'label': 'All (TMC & NC)', 'value': 'ALL'},
                    {'label': 'TMC (In-situ)', 'value': 'TMC'},
                    {'label': 'NC (Standard)', 'value': 'NC'}
                ],
                value='ALL',
                clearable=False,
                style={'color': '#2c3e50'}
            )
        ], style={'marginBottom': '20px'}),

        html.Div([
            html.Label('Thickness:', style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
            dcc.Dropdown(
                id='thickness-filter',
                options=[{'label': 'All Thicknesses', 'value': 'ALL'}],
                value='ALL',
                clearable=False,
                style={'color': '#2c3e50'}
            )
        ], style={'marginBottom': '20px'}),

        html.Div([
            html.Label('Concrete Mix:', style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
            dcc.Dropdown(
                id='mix-filter',
                options=[{'label': 'All Mixes', 'value': 'ALL'}],
                value='ALL',
                clearable=False,
                style={'color': '#2c3e50'}
            )
        ], style={'marginBottom': '20px'}),

        html.Div([
            html.Label('Project:', style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
            dcc.Dropdown(
                id='project-filter',
                options=[{'label': 'All Projects', 'value': 'ALL'}],
                value='ALL',
                clearable=False,
                style={'color': '#2c3e50'}
            )
        ], style={'marginBottom': '30px'}),

        # Data Summary in sidebar
        html.Div([
            html.H3("Data Summary", style={'color': 'white', 'marginBottom': '15px', 'borderBottom': '2px solid #3498db', 'paddingBottom': '10px'}),
            html.Div(id='data-summary')
        ])
    ], style=sidebar_style),

    # Right Content - Charts
    html.Div([
        html.H1("Concrete Strength Analysis Dashboard",
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '5px'}),
        html.P("Live data from Google Sheet | TMC (In-situ) vs NC (Standard)",
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '20px'}),

        # Main strength curve chart
        html.Div([
            dcc.Graph(id='strength-curve-chart', style={'height': '500px'})
        ], style={'backgroundColor': 'white', 'borderRadius': '10px', 'padding': '10px', 'marginBottom': '20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

        # Mix design comparison
        html.Div([
            dcc.Graph(id='mix-design-chart', style={'height': '450px'})
        ], style={'backgroundColor': 'white', 'borderRadius': '10px', 'padding': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})

    ], style=content_style)
], style={'fontFamily': 'Arial, sans-serif'})


def get_filtered_data(grade, curing, thickness, mix, project):
    """Apply filters and return filtered dataframe"""
    filtered = df_filtered.copy()

    if grade != 'ALL':
        filtered = filtered[filtered['Grade'] == grade]
    if curing != 'ALL':
        filtered = filtered[filtered['CuringCondition'] == curing]
    if thickness != 'ALL':
        filtered = filtered[filtered['Thickness'] == thickness]
    if mix != 'ALL':
        filtered = filtered[filtered['Concrete Mix'] == mix]
    if project != 'ALL':
        filtered = filtered[filtered['Project'] == project]

    return filtered


@callback(
    [Output('grade-filter', 'options'),
     Output('thickness-filter', 'options'),
     Output('mix-filter', 'options'),
     Output('project-filter', 'options'),
     Output('curing-filter', 'options')],
    [Input('grade-filter', 'value'),
     Input('curing-filter', 'value'),
     Input('thickness-filter', 'value'),
     Input('mix-filter', 'value'),
     Input('project-filter', 'value')]
)
def update_dropdown_options(grade, curing, thickness, mix, project):
    """Update dropdown options based on current selections"""

    # Grade options: filter by all others except grade
    grade_filtered = df_filtered.copy()
    if curing != 'ALL':
        grade_filtered = grade_filtered[grade_filtered['CuringCondition'] == curing]
    if thickness != 'ALL':
        grade_filtered = grade_filtered[grade_filtered['Thickness'] == thickness]
    if mix != 'ALL':
        grade_filtered = grade_filtered[grade_filtered['Concrete Mix'] == mix]
    if project != 'ALL':
        grade_filtered = grade_filtered[grade_filtered['Project'] == project]
    grades = sorted(grade_filtered['Grade'].dropna().unique().tolist())
    grade_options = [{'label': 'All Grades', 'value': 'ALL'}] + [{'label': g, 'value': g} for g in grades]

    # Thickness options: filter by all others except thickness
    thickness_filtered = df_filtered.copy()
    if grade != 'ALL':
        thickness_filtered = thickness_filtered[thickness_filtered['Grade'] == grade]
    if curing != 'ALL':
        thickness_filtered = thickness_filtered[thickness_filtered['CuringCondition'] == curing]
    if mix != 'ALL':
        thickness_filtered = thickness_filtered[thickness_filtered['Concrete Mix'] == mix]
    if project != 'ALL':
        thickness_filtered = thickness_filtered[thickness_filtered['Project'] == project]
    thicknesses = sorted(thickness_filtered['Thickness'].dropna().unique().tolist())
    thickness_options = [{'label': 'All Thicknesses', 'value': 'ALL'}] + [{'label': t, 'value': t} for t in thicknesses]

    # Mix options: filter by all others except mix
    mix_filtered = df_filtered.copy()
    if grade != 'ALL':
        mix_filtered = mix_filtered[mix_filtered['Grade'] == grade]
    if curing != 'ALL':
        mix_filtered = mix_filtered[mix_filtered['CuringCondition'] == curing]
    if thickness != 'ALL':
        mix_filtered = mix_filtered[mix_filtered['Thickness'] == thickness]
    if project != 'ALL':
        mix_filtered = mix_filtered[mix_filtered['Project'] == project]
    mixes = sorted(mix_filtered['Concrete Mix'].dropna().unique().tolist())
    mix_options = [{'label': 'All Mixes', 'value': 'ALL'}] + [
        {'label': m[:40] + '...' if len(m) > 40 else m, 'value': m} for m in mixes
    ]

    # Project options: filter by all others except project
    project_filtered = df_filtered.copy()
    if grade != 'ALL':
        project_filtered = project_filtered[project_filtered['Grade'] == grade]
    if curing != 'ALL':
        project_filtered = project_filtered[project_filtered['CuringCondition'] == curing]
    if thickness != 'ALL':
        project_filtered = project_filtered[project_filtered['Thickness'] == thickness]
    if mix != 'ALL':
        project_filtered = project_filtered[project_filtered['Concrete Mix'] == mix]
    projects = sorted(project_filtered['Project'].dropna().unique().tolist())
    project_options = [{'label': 'All Projects', 'value': 'ALL'}] + [{'label': p, 'value': p} for p in projects]

    # Curing options: filter by all others except curing
    curing_filtered = df_filtered.copy()
    if grade != 'ALL':
        curing_filtered = curing_filtered[curing_filtered['Grade'] == grade]
    if thickness != 'ALL':
        curing_filtered = curing_filtered[curing_filtered['Thickness'] == thickness]
    if mix != 'ALL':
        curing_filtered = curing_filtered[curing_filtered['Concrete Mix'] == mix]
    if project != 'ALL':
        curing_filtered = curing_filtered[curing_filtered['Project'] == project]
    curings = curing_filtered['CuringCondition'].dropna().unique().tolist()
    curing_options = [{'label': 'All (TMC & NC)', 'value': 'ALL'}]
    if 'TMC' in curings:
        curing_options.append({'label': 'TMC (In-situ)', 'value': 'TMC'})
    if 'NC' in curings:
        curing_options.append({'label': 'NC (Standard)', 'value': 'NC'})

    return grade_options, thickness_options, mix_options, project_options, curing_options


@callback(
    [Output('strength-curve-chart', 'figure'),
     Output('mix-design-chart', 'figure'),
     Output('data-summary', 'children')],
    [Input('grade-filter', 'value'),
     Input('curing-filter', 'value'),
     Input('thickness-filter', 'value'),
     Input('mix-filter', 'value'),
     Input('project-filter', 'value')]
)
def update_charts(grade, curing, thickness, mix, project):
    # Filter data
    filtered = get_filtered_data(grade, curing, thickness, mix, project)

    # Determine which curing conditions to show
    show_curings = ['TMC', 'NC'] if curing == 'ALL' else [curing]

    # Chart 1: Strength Curves (TMC vs NC over testing age)
    fig1 = go.Figure()

    if len(filtered) > 0:
        for cur in show_curings:
            curing_data = filtered[filtered['CuringCondition'] == cur]

            if len(curing_data) > 0:
                for batch_id in curing_data['BatchID'].unique():
                    batch_data = curing_data[curing_data['BatchID'] == batch_id].sort_values('TestingAgeDays')

                    color = '#e74c3c' if cur == 'TMC' else '#3498db'
                    name = f"{cur} - {batch_id[:20]}..." if len(batch_id) > 20 else f"{cur} - {batch_id}"

                    fig1.add_trace(go.Scatter(
                        x=batch_data['TestingAgeDays'],
                        y=batch_data['AverageStrength_MPa'],
                        mode='lines+markers',
                        name=name,
                        line=dict(color=color, width=2),
                        marker=dict(size=8),
                        hovertemplate=(
                            '<b>%{text}</b><br>' +
                            'Age: %{x:.1f} days<br>' +
                            'Strength: %{y:.1f} MPa<br>' +
                            '<extra></extra>'
                        ),
                        text=[f"{batch_id}<br>Grade: {batch_data['Grade'].iloc[0]}<br>Thickness: {batch_data['Thickness'].iloc[0]}"
                              for _ in range(len(batch_data))],
                        legendgroup=cur,
                        showlegend=True
                    ))

        # Add reference line for target strength
        if grade != 'ALL':
            grade_val = int(''.join(filter(str.isdigit, grade))) if any(c.isdigit() for c in grade) else 0
            if grade_val > 0:
                fig1.add_hline(y=grade_val, line_dash="dash", line_color="green",
                              annotation_text=f"Target: {grade_val} MPa")

    fig1.update_layout(
        title='Strength Development Curves',
        xaxis_title='Testing Age (Days)',
        yaxis_title='Average Strength (MPa)',
        hovermode='closest',
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02, font=dict(size=9)),
        margin=dict(r=200, l=50, t=50, b=50)
    )

    # Chart 2: Strength Curves by Concrete Type
    fig2 = go.Figure()

    if len(filtered) > 0:
        mix_summary = filtered.groupby(['Concrete Type', 'CuringCondition', 'TestingAgeDays']).agg({
            'AverageStrength_MPa': 'mean'
        }).reset_index()

        colors_tmc = px.colors.qualitative.Set1
        colors_nc = px.colors.qualitative.Pastel1

        for i, concrete_type in enumerate(mix_summary['Concrete Type'].unique()):
            type_data = mix_summary[mix_summary['Concrete Type'] == concrete_type]

            for cur in show_curings:
                cur_data = type_data[type_data['CuringCondition'] == cur].sort_values('TestingAgeDays')
                if len(cur_data) > 0:
                    colors = colors_tmc if cur == 'TMC' else colors_nc
                    dash = 'solid' if cur == 'TMC' else 'dash'
                    symbol = 'circle' if cur == 'TMC' else 'square'
                    fig2.add_trace(go.Scatter(
                        x=cur_data['TestingAgeDays'],
                        y=cur_data['AverageStrength_MPa'],
                        mode='lines+markers',
                        name=f'{concrete_type} ({cur})',
                        line=dict(color=colors[i % len(colors)], width=2, dash=dash),
                        marker=dict(size=8, symbol=symbol)
                    ))

    fig2.update_layout(
        title='Strength Curves by Concrete Type',
        xaxis_title='Testing Age (Days)',
        yaxis_title='Average Strength (MPa)',
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02, font=dict(size=10)),
        margin=dict(r=200, l=50, t=50, b=50)
    )

    # Data Summary
    if len(filtered) > 0:
        tmc_data = filtered[filtered['CuringCondition'] == 'TMC']
        nc_data = filtered[filtered['CuringCondition'] == 'NC']

        summary = html.Div([
            html.Div([
                html.Span("TMC Samples: ", style={'color': '#e74c3c', 'fontWeight': 'bold'}),
                html.Span(f"{len(tmc_data)}")
            ], style={'marginBottom': '5px'}),
            html.Div([
                html.Span("NC Samples: ", style={'color': '#3498db', 'fontWeight': 'bold'}),
                html.Span(f"{len(nc_data)}")
            ], style={'marginBottom': '10px'}),
            html.Hr(style={'borderColor': '#3498db'}),
            html.Div([
                html.Div("Grades:", style={'fontWeight': 'bold'}),
                html.Div(f"{', '.join(filtered['Grade'].unique())}", style={'fontSize': '12px'})
            ], style={'marginBottom': '5px'}),
            html.Div([
                html.Div("Thicknesses:", style={'fontWeight': 'bold'}),
                html.Div(f"{', '.join(filtered['Thickness'].dropna().unique())}", style={'fontSize': '12px'})
            ], style={'marginBottom': '5px'}),
            html.Div([
                html.Div("Age Range:", style={'fontWeight': 'bold'}),
                html.Div(f"{filtered['TestingAgeDays'].min():.1f} - {filtered['TestingAgeDays'].max():.1f} days", style={'fontSize': '12px'})
            ])
        ])
    else:
        summary = html.P("No data matching filters.", style={'color': '#e74c3c'})

    return fig1, fig2, summary


if __name__ == '__main__':
    print("Starting Concrete Strength Dashboard...")
    print("Connected to Google Sheet: masterSheet")
    port = int(os.environ.get('PORT', 8050))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    print(f"Open your browser and go to: http://127.0.0.1:{port}")
    app.run(debug=debug, host='0.0.0.0', port=port)
