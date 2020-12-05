import pandas as pd     #(version 1.0.0)
import plotly           #(version 4.5.0)
import plotly.express as px

import dash             #(version 1.8.0)
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

# import pandas as pd
# import plotly.express as px
df = pd.read_csv("combined_cssv.csv")

# df['year'] = pd.to_datetime(df['year'])

dff = df.groupby(['year','winner_name','surface', 'loser_name'], as_index=False)[['w_ace', 'w_df', 'w_svpt', 'l_ace','l_df','l_svpt']].mean()
# dffa = df.groupby(['year','winner_name','surface', 'loser_name'], as_index=False)[['l_ace','l_df','l_svpt']].mean()
# dff = dff.set_index('year')
# dff = dff.loc['2000':'2017']
# dff= dff.groupby([pd.Grouper(freq='M'), ['winner_name', 'surface']])[['w_ace', 'w_df', 'w_svpt']].mean().reset_index()
dff.reset_index(inplace=True)
# dffa.reset_index(inplace=True)
print(dff[:5])
# print(dffa[:5])


#======================================================


app.layout = html.Div([

    html.Div([
        dcc.Graph(id='our_graph'),
        dcc.Graph(id='our_graph2'),
        dcc.Graph(id='our_graph3'),
        dcc.Graph(id='our_graph4'),
        dcc.Graph(id='our_graph5'),
        dcc.Graph(id='our_graph6')
    ],className='nine columns'),

    html.Div([
        html.Br(),
        html.Label(['Choose a Winner:'], style={'font-weight': 'bold', "text-align": "center"}),
        dcc.Dropdown(id='select_player',
                     options=[{'label': x, 'value': x} for x in
                              df.sort_values('winner_name')['winner_name'].unique()],
                     # value='Andre Agassi',
                     multi=False,
                     disabled=False,
                     clearable=True,
                     searchable=True,
                     placeholder='Choose Player...',
                     # className='form-dropdown',
                     style={'width': "100%"}
                     ),



        html.Br(),
        html.Label(['Choose a Loser:'],style={'font-weight': 'bold', "text-align": "center"}),

        dcc.Dropdown(id='select_player2',
                     options=[{'label': y, 'value': y} for y in
                              df.sort_values('loser_name')['loser_name'].unique()],
                     # value='Andy Murray',
                     multi=False,
                     disabled=False,
                     clearable=True,
                     searchable=True,
                     placeholder='Choose Player...',
                     # className='form-dropdown',
                     style={'width': "100%"}
                     ),

        dcc.Dropdown(id='surface',
                     options=[{'label': x, 'value': x} for x in df.sort_values('surface')['surface'].unique()],
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
     Output('our_graph3','figure'),
     Output('our_graph4', 'figure'),
     Output('our_graph5', 'figure'),
     Output('our_graph6', 'figure')],
    [Input('select_player','value'),
    Input('select_player2','value'),
     Input('surface','value')]
)


def build_graph(player, player2, surface):
    # dff2 = dff[(dff['winner_name'] == player) &
    #            (dff['loser_name'] == player2)]
    #            # (dff['surface'] == surface)
    # dff3 = dff[(dff['winner_name'] == player) &
    #            (dff['loser_name'] == player2)]
    #            # (dff['surface'] == surface)]

    if surface is None:
        dff2 = dff[(dff['winner_name'] == player) & (dff['loser_name'] == player2)]
        dff3 = dff2
    else:
        dff2 = dff[(dff['winner_name'] == player) & (dff['loser_name'] == player2) & (dff['surface'].isin(surface))]
        dff3 = dff2
    # print(dff2[:5])


    fig = px.line(dff2, x="year", y="w_ace", color='surface', height=600)
    fig.update_layout(yaxis={'title': 'Winner Aces'},
                      title={'text': 'Average Winner Aces',
                             'font': {'size': 28}, 'x': 0.5, 'xanchor': 'center'})

    fig2 = px.line(dff3, x="year", y="l_ace", color='surface', height=600)
    fig2.update_layout(yaxis={'title': 'Loser Aces'},
                      title={'text': 'Average Loser Aces',
                             'font': {'size': 28}, 'x': 0.5, 'xanchor': 'center'})

    fig3 = px.line(dff2, x="year", y="w_svpt", color='surface', height=600)
    fig3.update_layout(yaxis={'title': 'Winner Serve Points'},
                       title={'text': 'Average Winner Serve Points',
                              'font': {'size': 28}, 'x': 0.5, 'xanchor': 'center'})


    fig4 = px.line(dff3, x="year", y="l_svpt", color='surface', height=600)
    fig4.update_layout(yaxis={'title': 'Loser Serve Points'},
                      title={'text': 'Average Loser Serve Points',
                             'font': {'size': 28}, 'x': 0.5, 'xanchor': 'center'})

    fig5 = px.line(dff2, x="year", y="w_df", color='surface', height=600)
    fig5.update_layout(yaxis={'title': 'Winner Double Faults'},
                      title={'text': 'Average  Winner Double Faults',
                             'font': {'size': 28}, 'x': 0.5, 'xanchor': 'center'})

    fig6 = px.line(dff3, x="year", y="l_df", color='surface', height=600)
    fig6.update_layout(yaxis={'title': 'Loser Serve Points'},
                       title={'text': 'Average Loser Serve Points',
                              'font': {'size': 28}, 'x': 0.5, 'xanchor': 'center'})
    return (fig, fig2, fig3, fig4, fig5, fig6)
# ---------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)