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
    dcc.Graph(id='export-line-chart')
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

# Exponer el servidor de Flask
server = app.server

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host='0.0.0.0', port=port)
