

import plotly.express as px
import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import os



def TourneyLevelData():
    data=[]
    data.append({'label': 'Grand Slams', 'value': 'G'})
    data.append({'label': 'ATP Finals', 'value': 'F'})
    data.append({'label': 'ATP Tour Masters', 'value': 'M'})
    data.append({'label': 'ATP Tour', 'value': 'A'})
    data.append({'label': 'ATP Challenger', 'value': 'C'})
    return data


def renderGraphPage():
    app = dash.Dash(__name__, title='Treemap Chart', external_stylesheets=[dbc.themes.CERULEAN])

    @app.callback(
        [Output("levelselectionvalue", "children"),
         Output("atp_treemap", "figure")],
        [Input("ddlevel", "value")],
    )
    def update_options(value):
        display_year = '{} Level Tennis'.format(value)
        parentDir = os.path.dirname(__file__)
        homeDir = os.path.dirname(parentDir)
        df = pd.read_csv(os.path.join(homeDir, 'data\\ATP_matches','all_matches.csv'))
        #df = pd.read_csv('all_matches.csv')
        df = df.replace('Us Open', 'US Open')
        df_level = df.query("tourney_level in @value")
        df_finals = df_level.query("round in ['F']")
        fig = px.treemap(df_finals,
                         path=['tourney_level', 'tourney_name', 'winner_name', 'loser_name', 'score'],
                         color=df_finals['minutes'],
                         color_continuous_scale='blues',
                         color_continuous_midpoint=np.average(df_finals['minutes']),
                         maxdepth=-5,
                         custom_data={'tourney_date', 'surface'}
                         )
        fig.update_traces(hovertemplate='<b>%{label}</b>'+ '<br> %{id}'+ '<br>Number of Finals Played: %{value}')
        fig.update_layout(
            margin=dict(t=75, l=10, r=10, b=10)
        )
        #fig.write_image('treemap_time.svg')
        return display_year, fig

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
                children='Tree Map Visualisation for Finals Games',
                style={
                    'textAlign': 'center',
                }
            ),
            html.Div(style={'padding': '10px', 'display': 'flex', 'align-items': 'flex-start'}, children=[
                dcc.Dropdown(
                    id='ddlevel',
                    options=TourneyLevelData(),
                    multi=False,
                    value=['G'],
                    style={'width': '100%'}
                ),
                html.Div(style={'height': '20px', 'text-align': 'center'}, id='levelselectionvalue')
            ]),
            html.Div(id='clickdata', style={'display': 'none'})
        ]),

    ])
    app.run_server(debug=True, use_reloader=True)


if __name__ == "__main__":
    renderGraphPage()
