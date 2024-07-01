import os
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

files = [
    'almeria.csv', 'cadiz.csv', 'cordoba.csv', 'granada.csv',
    'huelva.csv', 'jaen.csv', 'malaga.csv', 'sevilla.csv'
]

dfs = []
for file in files:
    df = pd.read_csv(file)
    province = file.split('/')[-1].replace('.csv', '')
    df = df.melt(id_vars=["Sector"], var_name="Año", value_name="Volumen")
    df["Provincia"] = province.capitalize()
    dfs.append(df)

df = pd.concat(dfs)
df['Volumen'] = df['Volumen'].str.replace('.', '').str.replace(',', '.').astype(float)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Exportaciones en Andalucía por Provincia y Sector"),
    html.Div([
        html.Label("Seleccione las Provincias"),
        dcc.Dropdown(
            id='province-dropdown',
            options=[{'label': province, 'value': province} for province in df['Provincia'].unique()],
            value=[df['Provincia'].unique()[0]],
            multi=True
        )
    ]),
    html.Div([
        html.Label("Seleccione los Sectores"),
        dcc.Dropdown(
            id='sector-dropdown',
            options=[{'label': sector, 'value': sector} for sector in df['Sector'].unique()],
            value=[df['Sector'].unique()[0]],
            multi=True
        )
    ]),
    dcc.Graph(id='export-line-chart'),
    html.Hr(),
    html.H2("Consulta específica de ventas"),
    html.Div([
        html.Label("Seleccione una Provincia"),
        dcc.Dropdown(
            id='single-province-dropdown',
            options=[{'label': province, 'value': province} for province in df['Provincia'].unique()],
            value=df['Provincia'].unique()[0]
        )
    ]),
    html.Div([
        html.Label("Seleccione un Año"),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in df['Año'].unique()],
            value=df['Año'].unique()[0]
        )
    ]),
    html.Div([
        html.Label("Seleccione un Sector"),
        dcc.Dropdown(
            id='single-sector-dropdown',
            options=[{'label': sector, 'value': sector} for sector in df['Sector'].unique()],
            value=df['Sector'].unique()[0]
        )
    ]),
    html.Div(id='result-output', style={'margin-top': '20px', 'font-weight': 'bold', 'font-size': '20px'})
])

@app.callback(
    Output('export-line-chart', 'figure'),
    [Input('province-dropdown', 'value'),
     Input('sector-dropdown', 'value')]
)
def update_line_chart(selected_provinces, selected_sectors):
    filtered_df = df[df['Provincia'].isin(selected_provinces) & df['Sector'].isin(selected_sectors)]
    aggregated_df = filtered_df.groupby(['Año']).sum().reset_index()
    fig = px.line(aggregated_df, x='Año', y='Volumen', title='Sumatorio de Exportaciones por Año')
    fig.update_layout(
        yaxis_title='Volumen de Exportaciones (€)',
        xaxis_title='Año'
    )
    fig.update_traces(hovertemplate='Año=%{x}<br>Volumen=%{y:,.2f} €')
    return fig

@app.callback(
    Output('result-output', 'children'),
    [Input('single-province-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('single-sector-dropdown', 'value')]
)
def update_specific_query(province, year, sector):
    filtered_df = df[(df['Provincia'] == province) & (df['Año'] == year) & (df['Sector'] == sector)]
    if not filtered_df.empty:
        volume = filtered_df['Volumen'].values[0]
        return f"En {year}, la venta de {sector} en {province} fue de {volume:,.2f} €"
    else:
        return "No hay datos disponibles para la selección hecha."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host='0.0.0.0', port=port)
