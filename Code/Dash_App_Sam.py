# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 17:16:54 2020

@author: SamCurtis
"""
import os
try:
    os.chdir('./Google Drive/Files/Uni/Masters_Data_Science/Sem2/COMP5048 - Visual Analytics/Assignments/Assignment 2')
except FileNotFoundError:
    pass
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
print(dcc.__version__)
from dash.dependencies import Input, Output
from dash_table import DataTable




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## READ IN DATA
df = pd.read_csv('./data/ATP_matches/all_matches.csv')
df['tourney_date'] = pd.to_datetime(df.tourney_date)
df['year'] = df.tourney_date.dt.year
df['winner_age'] = np.round(df.winner_age,2)
df['loser_age'] = np.round(df.loser_age,2)

## Remove duplicate players in each year because it skews the data
df = df.drop_duplicates(subset=['winner_name','year'])

## Create a DF for referencing which is just the unique players from the winners
df_unique = df.drop_duplicates(subset=['winner_name'])


#df = df_original[['surface', 'tourney_level','score','best_of','winner_name','winner_hand','winner_ht','winner_age','winner_rank',
#         'loser_name','loser_hand','loser_ht','loser_age','loser_rank']].copy()
df.winner_rank.hist()   # too much spread

# Take only top 200 players
df = df[(df.winner_rank <= 200) & (df.loser_rank <= 200)]
df = df[~pd.Series(df["score"]).str.contains("RET", na=False)]

#df.winner_rank.hist()
#df.loser_rank.describe()
df['shock_factor'] = (df.winner_rank - df.loser_rank) / (df.winner_rank + df.loser_rank)
#df['rank_differential_poly'] = (df.winner_rank - df.loser_rank)**2 / (df.winner_rank + df.loser_rank)**3
df['height_diff'] = (df.winner_ht - df.loser_ht) / df.loser_ht
df['upset'] = np.where(df.winner_rank < df.loser_rank,1,0)

variables = ['Name','Rank','Age','Handedness','Height']

#'''
#print('Rank Differential Stats:')
#df.rank_differential.hist()   # observe the asymmetric nature of how often higher ranked players win, etc.
#df.rank_differential.describe()
#print('---------------------')
#print('Height Difference')
#df.height_diff.hist()
#df.height_diff.describe()
#
## Remove any 'epected' results... ie win player rank > lose player rank
#df = df[df.rank_differential > 0]
#print(df.sort_values(by='rank_differential', ascending=False).head())
#'''

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# VARIABLES BY WHICH TO SUBSET DATA
court_types = df.surface.unique()
handedness = df.loser_hand.unique()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTIONS TO CALL IN APP



#fig = px.histogram(df, x='winner_age', y='rank_differential', histfunc='avg', nbins=25)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#app = dash.Dash(external_stylesheets=dbc.themes.CERULEAN)

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = [dbc.themes.CERULEAN]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(children='Factors Attributing to Upsets'),
    
    html.Div(children='''
        An analysis of role different variables play on determining the unpredictability of match outcomes.
    '''),
    dcc.Dropdown(id='dropdown_value',
                 options=[
                     {'label':'Age', 'value':'winner_age'},
                     {'label':'Height', 'value':'winner_ht'},
                     {'label':'Handedness', 'value':'winner_hand'},
                     {'label':'Surface', 'value':'surface'},
                     {'label':'First Serves In', 'value':'w_1stIn'},
                     {'label':'Service Percentage', 'value':'w_svpt'},
                     {'label':'Aces', 'value':'w_ace'},
                     {'label':'Best Of', 'value':'best_of'}]),
    
    dcc.Graph(id='shock_graph'),
    dcc.Graph(id='dropdown_hist'),
    DataTable(id='rank_table'),
    DataTable(id='shock_table')
    

])


             
             
             
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## CALLBACKS
    
## RESULT SHOCK             
@app.callback(
    Output('shock_graph','figure'),
    [Input('dropdown_value','value')])
def update_shockgraph(value):
    dfa = px.data.tips()
    dfz = df.copy()
    if value == 'winner_ht':
        bins = 10
    elif value == 'best_of':
        bins = 2
    elif value == 'winner_hand':
        dfz = dfz[(dfz.winner_hand=='L') | (dfz.winner_hand=='R')]
        bins = 25
    else:
        bins = 25
    fig = px.histogram(dfz, x=value, y='shock_factor', histfunc='avg', nbins=bins)
    #fig = px.histogram(df, x=value, y='upset', histfunc='avg', nbins=bins)
    return fig


# HISTOGRAM OF DROPDOWN VALUE
@app.callback(
    Output('dropdown_hist','figure'),
    [Input('dropdown_value','value')])
def dropdown_graph(value):
    dfb = px.data.tips()
    dfzz = df.copy()
    dfzz = dfzz[(dfzz.winner_hand=='L') | (dfzz.winner_hand=='R')]
    fig = px.histogram(dfzz, x=value, y='winner_rank',histfunc='avg', nbins=25)
    return fig


# TABLE OF TOP RANKED PLAYERS AND THEIR DROPDOWN VALUE
@app.callback(
    [Output('rank_table','data'),
     Output('rank_table','columns')],
    [Input('dropdown_value','value')])
def rank_table(value):
    dfc = df[['winner_name','winner_rank',value]].copy()
    dfc = dfc.sort_values(by=['winner_rank', value], ascending=True)
    dfc = dfc.drop_duplicates(subset=['winner_name'])
    dfc = dfc.iloc[:10,:]
    return dfc.to_dict('records'), [{"name":i, "id":i} for i in dfc.columns]


## TABLE OF THE LARGEST SHOCKS BY THEIR DROPDOWN VALUE
@app.callback(
    [Output('shock_table', 'data'),
     Output('shock_table', 'columns')],
    [Input('dropdown_value','value')])
def shock_table(value):
    newcols = [('winner_%s'%value[7:]), ('loser_%s'%value[7:])]
    dfd = df.copy()
#    dfd['rank_diff'] = dfd.winner_rank - dfd.loser_rank
    dfd = dfd.sort_values(by=['shock_factor'])
    dfd = dfd[['winner_name','winner_rank', newcols[0], 'loser_name','loser_rank', newcols[1], 'tourney_name']]
    dfd = dfd.iloc[:10,:]
    return dfd.to_dict('records'), [{"name":i, "id":i} for i in dfd.columns]
             
if __name__ == '__main__':
    app.run_server(debug=True)

