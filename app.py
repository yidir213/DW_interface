import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import os 
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import os


df_weather = pd.read_csv(os.path.join(os.getcwd(),'..','weatherfact.csv' ))

# Load the location data CSV file into a pandas DataFrame
df_location = pd.read_csv(os.path.join(os.getcwd(),'..','location.csv' ))

# Merge the weather and location data based on a common key, for example, 'STATION'
df = pd.merge(df_weather, df_location, on='STATION')


station_name_to_id = df.set_index('STATION')['NAME'].to_dict()
id_to_station_name = {name: station for station, name in station_name_to_id.items()}

# Convertir la colonne 'DATE' en datetime
df['DATE'] = pd.to_datetime(df['DATE'])

# Extraire l'année, la saison, le trimestre et le mois de la colonne 'DATE'
df['Year'] = df['DATE'].dt.year
df['Season'] = df['DATE'].dt.month % 12 // 3 + 1
df['Quarter'] = df['DATE'].dt.quarter
df['Month'] = df['DATE'].dt.month

# Initialisation de l'application Dash
app = dash.Dash(__name__)

# Configuration de la mise en page de l'application
app.layout = html.Div([
    html.H1('Weather Dashboard', style={'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.Label('Station'),
            dcc.Dropdown(
            id='station-dropdown',
            options=[{'label': station_name_to_id[station], 'value': station} for station in df['STATION'].unique()],
            value=df['STATION'].unique()[0]
        )
        ]),
        html.Div([
            html.Label('Year'),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': i, 'value': i} for i in df['Year'].unique()],
                value=df['Year'].unique()[0]
            )
        ]),
        html.Div([
            html.Label('Season'),
            dcc.Dropdown(
                id='season-dropdown',
                options=[{'label': f'Season {i}', 'value': i} for i in df['Season'].unique()],
                value=df['Season'].unique()[0]
            )
        ]),
        html.Div([
            html.Label('Quarter'),
            dcc.Dropdown(
                id='quarter-dropdown',
                options=[{'label': f'Quarter {i}', 'value': i} for i in df['Quarter'].unique()],
                value=df['Quarter'].unique()[0]
            )
        ]),
        html.Div([
            html.Label('Month'),
            dcc.Dropdown(
                id='month-dropdown',
                options=[{'label': f'Month {i}', 'value': i} for i in df['Month'].unique()],
                value=df['Month'].unique()[0]
            )
        ]),
    ], className='dropdown-container'),
    dcc.Graph(id='weather-graph'),
    dcc.Graph(id='map-graph')
])

# Mise à jour du graphique météo en fonction de la station sélectionnée
@app.callback(
    Output('weather-graph', 'figure'),
    [Input('station-dropdown', 'value')]
)
def update_weather_graph(selected_station):
    filtered_df = df[df['STATION'] == selected_station]
    
    fig = {
        'data': [
            {'x': filtered_df['DATE'], 'y': filtered_df['PRCP'], 'type': 'bar', 'name': 'Précipitation'},
            {'x': filtered_df['DATE'], 'y': filtered_df['TAVG'], 'type': 'line', 'name': 'Température moyenne'},
            {'x': filtered_df['DATE'], 'y': filtered_df['TMAX'], 'type': 'line', 'name': 'Température maximale'},
            {'x': filtered_df['DATE'], 'y': filtered_df['TMIN'], 'type': 'line', 'name': 'Température minimale'}
        ],
        'layout': {
            'title': f'Données météorologiques pour la station {station_name_to_id[selected_station]}',

            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Valeur'}
        }
    }
    return fig

# Mise à jour de la carte en fonction des filtres sélectionnés
@app.callback(
    Output('map-graph', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('season-dropdown', 'value'),
     Input('quarter-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_map(selected_year, selected_season, selected_quarter, selected_month):
    filtered_df = df[(df['Year'] == selected_year) &
                     (df['Season'] == selected_season) &
                     (df['Quarter'] == selected_quarter) &
                     (df['Month'] == selected_month)]
    
    # fig = px.scatter_mapbox(filtered_df, lat='LATITUDE', lon='LONGITUDE', hover_name='NAME',
    #                         hover_data=['PRCP', 'TAVG', 'TMAX', 'TMIN'], color='TMAX',
    #                         color_continuous_scale='Viridis', zoom=4, height=600)
    fig = px.density_mapbox(filtered_df, lat='LATITUDE', lon='LONGITUDE', z='TMAX',
                        radius=10,  # Ajustez le rayon pour le lissage de densité
                        center={'lat': filtered_df['LATITUDE'].mean(), 'lon': filtered_df['LONGITUDE'].mean()},
                        zoom=4,  # Ajustez le niveau de zoom
                        mapbox_style='carto-positron',  # Choisissez un style de carte Mapbox
                        color_continuous_scale='OrRd',  # Choisissez l'échelle de couleurs, ici 'OrRd' (orange-rouge)
                        )
    fig.update_layout(mapbox_style='open-street-map')
    fig.update_layout(
        mapbox={
            'center': {'lat': 30, 'lon': 5},
            'zoom': 4
        }
    )
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
