#The following code produces sunburst data visualisation for GrandSlam tournaments from the ATP tennis dataset
#Author: Lupita Sahu(lsah8006)

#Loading libraries
import plotly.express as px
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import os
import json
import math

app = dash.Dash(__name__, title='Sunburst Chart', external_stylesheets=[dbc.themes.CERULEAN])

def processClickData(clickdata):
    points = clickdata['points']
    current_path = points[0]['id']
    sectors = current_path.split('/')
    return sectors

def createGraph(year):
    df_grandslam=getdata(year)
    fig = px.sunburst(df_grandslam, 
                path=['tourney_name','round', 'winner_name', 'loser_name'],
                color_discrete_sequence=px.colors.qualitative.Pastel,
                color='round',
                maxdepth=-1,
                hover_data={'winner_name': False}
            )
    fig.update_layout(
        margin = dict(t=10, l=10, r=10, b=10),
    )
    return fig

#Function to load the data for a specific year
def getdata(year):
    # get the root path
    parentDir=os.pardir
    # read the csv file from the relative path of the data folder
    df = pd.read_csv(os.path.join(parentDir,'data\ATP_matches','atp_matches_'+ str(year) +'.csv'))

    # filter the dataframe to get the grandslam tournaments
    return df[df.tourney_level.eq('G')]

#Function to load the years
def yearData():
    data=[]
    for year in range(2002,2018):
        data.append({'label': str(year), 'value': year})
    return data


@app.callback(
        [Output("yearselectionvalue", "children"),
            Output("atp_sunburst", "figure")],
        [Input("ddyear", "value"), Input('btnReset', 'n_clicks')],
)
def update_options(value, n_clicks):
    display_year = 'You have selected "{}"'.format(value)
    fig=createGraph(value)    
    return display_year, fig

def renderClickData(renderObject=None):
    if(renderObject is not None):
        row = renderObject['row']
        sectors = renderObject['sectors']
        year = renderObject['year']
        print(row)
        score = html.Ul([
                    html.Li(style={'flex-basis': '60%'}, children=[
                        html.H6('Tournament: {0} {1}'.format(sectors[0], year)),
                    ]),
                    html.Li(style={'flex-basis': '40%'}, children=[
                        html.H6('Round: {0}'.format(row['round'].values[0])),    
                    ]),
                    html.Li(style={'flex-basis': '100%'}, children=[
                        html.H6('Match score:{0}'.format(row['score'].values[0]))    
                    ])
                ])  
        header = [html.Tr(children=[
                            html.Th('Stats'),
                            html.Th('Winner'),
                            html.Th('Loser'),
                    ])]
        datarows = [
            html.Tr([html.Td('Name'),html.Td(row['winner_name']), html.Td(row['loser_name'])]),
            html.Tr([html.Td('Country'),html.Td(row['winner_ioc']), html.Td(row['loser_ioc'])]),
            html.Tr([html.Td('Rank'),html.Td(row['winner_rank']), html.Td(row['loser_rank'])]),
            html.Tr([html.Td('Hand'),html.Td(row['winner_hand']), html.Td(row['loser_hand'])]),
            html.Tr([html.Td('Age'),html.Td(math.floor(row['winner_age'].values[0])), html.Td(math.floor(row['loser_age']))]),
            html.Tr([html.Td('Height'),html.Td(row['winner_ht']), html.Td(row['loser_ht'])]),
            html.Tr([html.Td('Ace'),html.Td(row['w_ace']), html.Td(row['l_ace'])]),
            html.Tr([html.Td('Serve Points'),html.Td(row['w_svpt']), html.Td(row['l_svpt'])]),
            html.Tr([html.Td('Break Point Saved'),html.Td(row['w_bpSaved']), html.Td(row['l_bpSaved'])]),
            html.Tr([html.Td('Break Point Faced'),html.Td(row['w_bpFaced']), html.Td(row['l_bpFaced'])]),
            html.Tr([html.Td('Double Fault'),html.Td(row['w_df']), html.Td(row['l_df'])]),
            html.Tr([html.Td('1st serve in'),html.Td(row['w_1stIn']), html.Td(row['l_1stIn'])]),
            html.Tr([html.Td('Points won on 1st serve'),html.Td(row['w_1stWon']), html.Td(row['l_1stWon'])]),
            html.Tr([html.Td('Points won on 2nd serve'),html.Td(row['w_2ndWon']), html.Td(row['l_2ndWon'])]),
            html.Tr([html.Td('Serve games'),html.Td(row['w_SvGms']), html.Td(row['l_SvGms'])]),
            ] if (len(row) == 1) else [html.Tr([html.Td(''),html.Td(''), html.Td('')])]

        clickDataHtml = html.Div([
            html.Div(id='score', children=[score]),
            html.Table(style={ 'width': '100%'},children=[
                html.Thead(id='matchstats', children=header),
                html.Tbody(id='matchdatarows', children=datarows)
            ])
        ])
    else:
        clickDataHtml = html.Div([])

    return clickDataHtml

@app.callback(
    Output('clickdata', 'children'),
    [Input('atp_sunburst', 'clickData'), Input("ddyear", "value"), Input('btnReset', 'n_clicks')],
    prevent_initial_call=False
)
def display_click_data(clickData, year, n_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        control_id = 'No clicks yet'
    else:
        control_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if(control_id == 'ddyear' or control_id == 'btnReset'):
        return renderClickData()

    if(control_id == 'atp_sunburst' and clickData != None):
        df_grandslam = getdata(year)
        sectors=processClickData(clickData)
        matchdata=[]
        if(len(sectors) == 3 or len(sectors) == 4):
                matchdata=df_grandslam[
                (df_grandslam['tourney_name']==sectors[0]) & 
                (df_grandslam['round']==sectors[1]) & 
                (df_grandslam['winner_name']==sectors[2])]
        else: 
            return renderClickData()
        
        renderObject={}
        renderObject['row'] = matchdata
        renderObject['year'] = year
        renderObject['sectors'] = sectors
        return renderClickData(renderObject)

#Function for setting Graph specific details
def renderGraphPage():
    app.layout = html.Div(style={'display': 'flex', 'height': '97vh', 'width': '100vw', 'flex': 'auto', 'padding': '0px 10px 0px 10px'}, children=[
         html.Div(id='graphcontainer', style={ 'position': 'relative' },children=[
            html.Button('Reset',id='btnReset', className='btn-primary', style={
                'position': 'absolute',
                'top': '70px',
                'right': '20px',
                'z-index': '1000',
                'width': '70px',
            },n_clicks=0),
            html.P(id='displayresetclick'),
            dcc.Loading(
                type="default",
                children=dcc.Graph(id='atp_sunburst', figure={})
            )
        ]),
        html.Div(style={
                'border': '0px solid red', 
                'flex': 'auto',
                'display': 'flex',
                'flex-direction': 'column',
                'align-items': 'center',
            }, children=[
            html.H4(
                children='ATP Tennis Data visualisation for Grand Slam tournaments',
                style={
                    'textAlign': 'center',
                }
            ),
            html.Div(style={
                'padding': '10px', 
                'display': 'flex',
                'align-items': 'center', 
                'justify-content': 'center',
                'width': '100%',
                }, 
            children=[
                dcc.Dropdown(
                        id='ddyear',
                        options=yearData(),
                        multi=False,
                        value=2002,
                        style={'width': '40%', 'margin-right': '10px'}
                ),
                html.Div(style={'height': '20px','text-align': 'center'}, id='yearselectionvalue')
            ]),
            html.Div(id='clickdata', style={'display': 'flex','align-items': 'center', 'justify-content': 'center'}) 
        ]),
    ])
    app.run_server(debug=True, use_reloader=True)

if __name__ == "__main__":
   renderGraphPage()
