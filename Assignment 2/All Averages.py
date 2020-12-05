import pandas as pd     #(version 1.0.0)
import plotly           #(version 4.5.0)
import plotly.express as px

import dash             #(version 1.8.0)
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])


df = pd.read_csv("combined_cssv.csv")

dff = df.groupby(['year','winner_name','surface'], as_index=False)[['w_ace', 'w_df', 'w_svpt']].mean()

dff.reset_index(inplace=True)
print(dff[:5])


#======================================================


app.layout = html.Div([

    html.Div([
        dcc.Graph(id='our_graph'),
        dcc.Graph(id='our_graph2'),
        dcc.Graph(id='our_graph3')
    ],className='nine columns'),

    html.Div([
        html.Br(),
        html.Label(['Choose a player:'], style={'font-weight': 'bold', "text-align": "center"}),
        dcc.Dropdown(id='select_player',
                     options=[{'label': x, 'value': x} for x in
                              df.sort_values('winner_name')['winner_name'].unique()],
                     value='Andre Agassi',
                     multi=False,
                     disabled=False,
                     clearable=True,
                     searchable=True,
                     placeholder='Choose Player...',
                     # className='form-dropdown',
                     style={'width': "100%"}
                     ),


            ],className='two columns'),
    html.Div([
        dcc.Dropdown(id='surface',
                     options=[{'label': i, 'value': i} for i in df.sort_values('surface')['surface'].unique()],
                     # value='Grass',
                     multi=True,
                     clearable=False,
                     persistence='string',
                     persistence_type='local')

],className='two columns')
    ])


@app.callback(
    [Output('our_graph','figure'),
    Output('our_graph2','figure'),
     Output('our_graph3','figure')],
    [Input('select_player','value'),
     Input('surface','value')]
)


def build_graph(player, surface):
    # dff2 = dff.copy()
    dff2=dff[(dff['winner_name']==player)|
             (dff['surface']==surface)]
    print(dff2[:5])


    fig = px.line(dff2, x="year", y="w_ace", color='surface', height=600)
    fig.update_layout(yaxis={'title': 'Aces'},
                      title={'text': 'Average Aces',
                             'font': {'size': 28}, 'x': 0.5, 'xanchor': 'center'})

    fig2 = px.line(dff2, x="year", y="w_df", color='surface', height=600)
    fig2.update_layout(yaxis={'title': 'Double Faults'},
                      title={'text': 'Average Double Faults',
                             'font': {'size': 28}, 'x': 0.5, 'xanchor': 'center'})

    fig3 = px.line(dff2, x="year", y="w_svpt", color='surface', height=600)
    fig3.update_layout(yaxis={'title': 'Serve Points'},
                       title={'text': 'Average Serve Points',
                              'font': {'size': 28}, 'x': 0.5, 'xanchor': 'center'})
    return (fig, fig2, fig3)
# ---------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)