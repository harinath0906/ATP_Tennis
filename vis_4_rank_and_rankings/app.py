"""
COMP5048 Assignment 2 - Group 3 - Heather Doig

Create Dash dashboard (http://127.0.0.1:8050/) using ATP Tennis data.
Provide user ability to drill into changes in rankings of different players."""

import datetime


import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import seaborn as sns
from plotly.subplots import make_subplots
import plotly.graph_objects as go

print(dcc.__version__)
from dash.dependencies import Input, Output
from dash_table import DataTable
from vis_4_rank_and_rankings.ATPTennisData import ATPTennisData

# Load data files and dataset class ATPTennisData
tennis_data = ATPTennisData()
rank_df = tennis_data.rank(use_saved=True)
matches_by_players = tennis_data.matches_for_players()
player_list = tennis_data.tennis_players()
top_players_by_year = tennis_data.top_players_by_year()

# Set stylesheet for Dash webpage
app = dash.Dash(external_stylesheets=[dbc.themes.CERULEAN])

# Match table details
col_names = ["Tournament Date", "Winner", "Winner Rank", "Loser", "Loser Rank", "Score", "Surface"]
empty_row = pd.DataFrame([[""] * len(col_names)], columns=col_names)
columns = [{"id": i, "name": i} for i in col_names]


def generate_player_heatmap(players):
    """
    Generate heatmap of matches played between selected players
    :param: players: .
    :return: Match volume annotated heatmap.
    """

    x_axis = players.copy()
    x_axis.reverse()  # reverse
    y_axis = players

    # Get z value : sum(number of records) based on x, y,
    num_players = len(players)
    z = np.zeros((num_players, num_players))
    annotations = []

    for ind_x, winner in enumerate(x_axis):
        winners_matches = matches_by_players.get(winner, {})
        for ind_y, loser in enumerate(y_axis):
            losers_matches = winners_matches.get(loser, None)
            num_matches = 0
            if losers_matches is not None:
                num_matches = len(losers_matches)
                z[ind_y][ind_x] = num_matches

            annotation_dict = dict(
                showarrow=False,
                text="<b>" + str(num_matches) + "<b>",
                xref="Winner",
                yref="Loser",
                x=winner,
                y=loser,
                font=dict(family="sans-serif"),
            )
            annotations.append(annotation_dict)

    data = [
        dict(
            x=x_axis,
            y=y_axis,
            z=z,
            type="heatmap",
            name="",
            showscale=False,
            colorscale=[[0, "#caf3ff"], [1, "#2c82ff"]],
        )
    ]

    layout = dict(
        margin=dict(l=70, b=50, t=50, r=50),
        modebar={"orientation": "v"},
        font=dict(family="Open Sans"),
        annotations=annotations,
        # shapes=shapes,
        xaxis=dict(
            side="top",
            ticks="",
            ticklen=2,
            tickfont=dict(family="sans-serif"),
            tickcolor="#ffffff",
            title=dict(text="Winner", font=dict(family="sans-serif"))
        ),
        yaxis=dict(
            side="left", ticks="", tickfont=dict(family="sans-serif"), ticksuffix=" ",
            tickangle=60,
            title=dict(text="Loser", font=dict(family="sans-serif"))
        ),
        hovermode="closest",
        hovertemplate=
        '<b>Winner</b>: %{x}' +
        '<b>Loser</b>: %{y}',
        showlegend=False,
    )
    return {"data": data, "layout": layout}


## Create layout of Dash dashboard
# Card for selection details - number of top players, year and highest rank to diaplsy
top_player_card = dbc.Card(
    dbc.CardBody(
        dbc.Row([
            dbc.Col(html.Small('Display the Top')),
            dbc.Col(dcc.Dropdown(
                id="top_num--dropdown",
                options=[{'label': i, 'value': i} for i in range(1, 50)],
                value=4
            )),
            dbc.Col(html.Small('Players in')),
            dbc.Col(dcc.Dropdown(
                id="top_year--dropdown",
                options=[{'label': i, 'value': i} for i in range(2000, 2018)],
                value=2012
            )),
            dbc.Col(html.Small('up to Rank')),
            dbc.Col(dcc.Dropdown(
                id="rank--dropdown",
                options=[{'label': i, 'value': i} for i in [10, 20, 30, 40, 50]],
                value=10
            ))], justify="center")))

# Dash layout
app.layout = dbc.Container([
    dbc.Row(html.H3('  ')),
    #dbc.Row(html.H5('ATP Explorer')),
    dbc.Row(html.H5('Top Player Rank and Rank Points  by Year')),
    dbc.Row(html.P('''
            Select a year and number of top players and see how their rank and ranking points changed over this time period.
            Below see the matches played between these top players.
        ''')),
    dbc.Row([
        dbc.Col(top_player_card, width=12),
    ]),
    dbc.Row([
        dbc.Col([
            html.B("Rank and Ranking Points"),
            html.Hr(),
            dcc.Loading(dcc.Graph(id='ranking-graph',
                                  #config={"displayModeBar":False}
                                  #responsive=True
                                  ))]#, style={"height": "90vh"}
        )]),
    dbc.Row([
        dbc.Col(
            id="player--heatmap",
            children=[
                html.B("Player Match Results"),
                html.P("Click on a square to see the match details"),
                html.Hr(),
                dcc.Graph(id="player_hm"),
            ],
        ),
        dbc.Col([html.B('Matches'),
                 html.P('Upsets highlighted in orange'),
                 html.Hr(),
                 DataTable(
                     id='table',
                     data=[{}],
                     columns=columns,
                     style_data_conditional=[
                         {
                             'if': {'row_index': 'odd'},
                             'backgroundColor': 'rgb(248, 248, 248)'
                         },
                         {
                             'if': {
                                 'filter_query': '{Winner Rank} > {Loser Rank}',
                                 'column_id': 'Winner'
                             },
                             'backgroundColor': 'tomato',
                             'color': 'white'
                         }],
                     style_cell={
                         'font_family': 'sans-serif',
                         'font_size': '10px',
                         'text_align': 'center'
                     },
                     style_table={
                         'overflowY': 'scroll'
                     }
                 )])
    ])

])


@app.callback(
    [Output(component_id='ranking-graph', component_property='figure'),
     Output("player_hm", "figure")],
    [Input(component_id='top_num--dropdown', component_property='value'),
     Input(component_id='top_year--dropdown', component_property='value'),
     Input('rank--dropdown', 'value')]
)
def update_ranking_graph(top_num, top_year, rank):
    # rank = float(rank)
    top_by_year = top_players_by_year[top_year][:top_num]
    # joint_players = list(set(top_by_year + players))
    subset_df = rank_df.loc[rank_df["name"].isin(top_by_year)]

    if subset_df.shape[0] > 0:
        rank_point_by_year = [[key[0], datetime.date(key[1], 1, 1), np.mean(rows["rank_points"])]
                              for key, rows
                              in subset_df.groupby(["name", "year"])]
        rank_point_df = pd.DataFrame(rank_point_by_year, columns=["name", "date", "rank_points"])

        # Colour dictionary for player names
        colors = ["rgb({},{},{})".format(int(c[0] * 255), int(c[1] * 255), int(c[2] * 255))
                  for c in sns.color_palette(n_colors=len(top_by_year))]
        color_dict = {top_by_year[i]: colors[i] for i in range(len(top_by_year))}

        # Create two subplots
        fig = make_subplots(rows=2, cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.05,
                            subplot_titles=("Rank", "Rank Points (Annual Average)"))
        fig.update_layout(modebar={"orientation": "v"}, margin={'t': 30, 'b':50})
        ## Plot 1 - Rank line plot
        subset_df = subset_df[subset_df["rank"] <= rank]
        for name, rows in subset_df.groupby("name"):
            fig.add_trace(go.Scatter(x=rows["date"], y=rows["rank"],
                                     name=name,
                                     line={"shape": "spline",
                                           "color": color_dict[name]},
                                     showlegend=False,
                                     hovertemplate=
                                     '<b>Tournament Date</b>: %{x}' +
                                     '<br><b>Rank</b>: %{y}<br>'
                                     ),
                          row=1, col=1)
        fig.update_yaxes(autorange="reversed", range=[1, rank + 2],
                         title={"text": "Rank"},
                         row=1, col=1)

        ## Plot 2 - Stream plot of rank points

        # First, calculate to create symmetry around horizontal axis.
        x_offset = []
        y_offset = []
        for d, rows in rank_point_df.groupby("date"):
            x_offset.append(d)
            y_offset.append(np.sum(rows["rank_points"]))
        max_offset = np.max(y_offset) * 1.1
        y = (max_offset - y_offset) / 2

        # Add offset trace to centre stream
        fig.add_trace(go.Scatter(x=x_offset, y=y,
                                 line={"color": "white", "shape": "spline"},
                                 opacity=1,
                                 showlegend=False,
                                 hoverinfo="skip",
                                 stackgroup="top"),
                      row=2, col=1)  # fill down to xaxis

        # Plot each player
        for name in reversed(top_by_year):
            rows = rank_point_df[rank_point_df["name"] == name]
            fig.add_trace(go.Scatter(x=rows["date"], y=rows["rank_points"],
                                     line={"shape": "spline",
                                           "color": color_dict[name]},
                                     name=name,
                                     connectgaps=False,
                                     hovertemplate=
                                     '<b>Year</b>: %{x}' +
                                     '<br><b>Avg Rank Points</b>: %{y:.0f}<br>',
                                     stackgroup="top"),
                          row=2, col=1)
        fig.update_yaxes(visible=False, row=2, col=1)

        # Add vertical lines to show year chosen
        fig.add_trace(go.Scatter(x=[datetime.date(top_year, 1, 1)] * 20,
                                 y=np.linspace(rank, 1, 20),
                                 showlegend=False,
                                 hoverinfo="skip",
                                 line={"color": "darkblue",
                                       "shape": "spline",
                                       "dash": "dot",
                                       "width": 2}),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=[datetime.date(top_year, 1, 1)] * 20,
                                 y=np.linspace(0, max_offset, 20),
                                 showlegend=False,
                                 hoverinfo="skip",
                                 line={"color": "darkblue",
                                       "shape": "spline",
                                       "dash": "dot",
                                       "width": 2}),
                      row=2, col=1)
        fig.update_layout(transition_duration=500)

    # Heatmap
    heatmap = generate_player_heatmap(top_by_year)

    return fig, heatmap


@app.callback(
    Output("table", "data"),
    Input("player_hm", "clickData")
)
def update_table(heatmap_click):
    # Highlight click data's patients in this table
    if heatmap_click is not None:
        winner = heatmap_click["points"][0]["x"]
        loser = heatmap_click["points"][0]["y"]
        table_data = matches_by_players.get(winner, {}).get(loser, pd.DataFrame())
        if len(table_data) > 0:
            table_data["match_date"] = [t.strftime("%d %b %Y") for t in table_data["tourney_date"]]
            table_data = table_data.loc[:,
                         ["match_date", "winner_name", "winner_rank", "loser_name", "loser_rank", "score", "surface"]]
            table_data.columns = col_names
            return table_data.to_dict('records')
    return [{}]


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
