import os

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output


def TourneyLevelData():
    data = []
    data.append({'label': 'Grand Slam', 'value': 'G'})
    data.append({'label': 'ATP Finals', 'value': 'F'})
    data.append({'label': 'ATP Tour Masters', 'value': 'M'})
    data.append({'label': 'ATP Tour', 'value': 'A'})
    data.append({'label': 'ATP Challenger', 'value': 'C'})
    return data

def ReturnLabel(value):
    tmp = TourneyLevelData()
    label = 'Grand Slam'
    for x in tmp:
        if x['value'] == value:
            label = x['label']
    return label

value = ['G']
def renderGraphPage():
    app = dash.Dash(__name__, title='Treemap Chart', external_stylesheets=[dbc.themes.CERULEAN])

    @app.callback(
        [Output("levelselectionvalue", "children"),
         Output("atp_treemap", "figure")],
        [Input("ddlevel", "value")],
    )
    def update_options(value):
        #parentDir = os.path.dirname(__file__)
        #homeDir = os.path.dirname(parentDir)
        #df = pd.read_csv(os.path.join(homeDir, '/data/ATP_matches', 'all_matches.csv'))
        # get the root path
        parentDir = os.pardir
        # read the csv file from the relative path of the data folder
        df = pd.read_csv(os.path.join(parentDir, 'data/ATP_matches', 'all_matches.csv'))
        # df = pd.read_csv('all_matches.csv')
        df = df.replace('Us Open', 'US Open')
        df_level = df.query("tourney_level in @value")
        df_finals = df_level.query("round in ['F']")
        label = ReturnLabel(value)
        display_level = 'Viewing {} level Finals Games.' \
                        \
                        ' Exterior trees are for tournament name or location, interior are scores.'.format(label)
        fig = px.treemap(df_finals,
                         path=['tourney_level', 'tourney_name', 'winner_name', 'loser_name', 'score'],
                         color_discrete_sequence=px.colors.sequential.Blues_r,
                         maxdepth=-5,
                         custom_data={'tourney_date'}
                         )
        fig.update_traces(
            hovertemplate='<b>%{label}</b>' + '<br>Number of Finals Played: %{value}' + '<br>Date: %{customdata}')
        fig.update_layout(
            margin=dict(t=75, l=10, r=10, b=10)
        )
        return display_level, fig

    @app.callback(
        Output('clickdata', 'children'),
        [Input('atp_treemap', 'clickData')]
    )
    def display_click_data(clickData):
        print(clickData)
        return 'Click data - "{}"'.format(clickData)

    app.layout = html.Div(style={'display': 'flex', 'height': '97vh', 'width': '97vw'}, children=[
        html.Div(style={
            'height': '100%',
            'display': 'flex',
            'align-content': 'center',
            'justify-content': 'center',
            'border': '0px solid red'
        }, children=[
            dcc.Graph(id='atp_treemap', figure={})
        ]),
        html.Div(style={'overflow': 'hidden', 'border': '0px solid red'}, children=[
            html.H4(
                children='2000 - 2017 Finals Results Summary',
                style={
                    'textAlign': 'center',
                }
            ),
            html.Div(style={'padding': '50px', 'display': 'flex', 'align-items': 'flex-start'}, children=[
                dcc.Dropdown(
                    id='ddlevel',
                    options=TourneyLevelData(),
                    multi=False,
                    value=['G'],
                    style={'width': '80%'}
                ),
                html.Div(style={'height': '20px', 'text-align': 'center'}, id='levelselectionvalue')
            ]),
            html.Div(id='clickdata', style={'display': 'none'})
        ]),

    ])
    app.run_server(debug=True, use_reloader=True)


if __name__ == "__main__":
    renderGraphPage()
