import pandas as pd
import datetime
import math
import numpy as np
from collections import defaultdict, Counter
import geopandas as gpd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns


class ATPTennisData:
    """Data class to load all ATP tennis data from 2000 to 2017.
    Option to load individual files and save a combined file OR
    load a combined file with added columns.

    To load data and create a combined file for quicker loading
    ATPTennisData(load_combined_file=False)
    This will create a combined file that can then be used for subsequent loads.

    To load data after combined file is created.
    ATPTennisData()
    """

    def __init__(self, dir="../data/ATP_matches/", file_prefix="atp_matches_",
                 load_combined_file=True, combined_file="all_matches.csv",
                 unknown_file="unknown_mappings.csv"):
        self.player_list = None
        self.player_stats_dict = None
        self.rank_df = None
        unknown_countries = pd.read_csv(dir + "unknown_mappings.csv")
        self.mapping_dict = {r.iso_a6: [r.country, r.continent] for _, r in unknown_countries.iterrows()}

        if load_combined_file:
            print("Loading saved combined file {}".format(dir + combined_file))
            self.all_df = pd.read_csv(dir + combined_file)
            self.all_df['tourney_date'] = pd.to_datetime(self.all_df['tourney_date'])
        else:
            print("Loading individual year files...")
            dfs = []
            for i in range(2000, 2018):
                tennis_file = "{}{}{}.csv".format(dir, file_prefix, i)
                df = pd.read_csv(tennis_file,
                                 skip_blank_lines=True,
                                 index_col=False,
                                 dtype={"tourney_date": str})
                df = df[pd.notna(df["tourney_id"])]  # Do this to remove blank entries in 2016 file
                df['tourney_date'] = pd.to_datetime(df['tourney_date'])
                df["year"] = [i] * len(df)  # Add a year column based on file it's from.
                dfs.append(df)
                print(tennis_file, df.shape)

            self.all_df = pd.concat(dfs)
            print("Adding country and continent data")
            self.map_country_continent()  # Add country and continent file
            print("Saving in a combined file {}...".format(dir + combined_file))
            self.save_alldata(dir + combined_file)

    def data(self):
        """Return a pandas dataframe containing all data"""
        return self.all_df

    def save_alldata(self, filename):
        self.all_df.to_csv(filename)

    def map_country_continent(self):
        unknown = []
        country_name_dict = {}
        continent_name_dict = {}
        world_data = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))  # This file has geography information
        world_data["iso_alt"] = [n[:3].upper() for n in world_data.name]  # Add additional lookup column
        countries = list(set(self.all_df.winner_ioc).union(set(self.all_df.loser_ioc)))
        for c in countries:
            row = world_data[world_data.iso_a3 == c]
            if len(row) > 0:
                country_name_dict[c] = row.name.iloc[0]
                continent_name_dict[c] = row.continent.iloc[0]
            else:
                row = world_data[world_data.iso_alt == c]
                if len(row) > 0:
                    country_name_dict[c] = row.name.iloc[0]
                    continent_name_dict[c] = row.continent.iloc[0]
                else:
                    if c in self.mapping_dict.keys():
                        country_name_dict[c] = self.mapping_dict[c][0]
                        continent_name_dict[c] = self.mapping_dict[c][1]
                    else:
                        unknown.append(c)
        print("No data found for {}".format(unknown))
        self.all_df["winner_country"] = [country_name_dict.get(c, c) for c in self.all_df.winner_ioc]
        self.all_df["loser_country"] = [country_name_dict.get(c, c) for c in self.all_df.loser_ioc]
        self.all_df["winner_continent"] = [continent_name_dict.get(c, "UNK") for c in self.all_df.winner_ioc]
        self.all_df["loser_continent"] = [continent_name_dict.get(c, "UNK") for c in self.all_df.loser_ioc]

    def tennis_players(self):
        if self.player_list is None:
            self.player_list = sorted(list(set(self.data()['winner_name']).union(set(self.data()["loser_name"]))))
        return self.player_list

    def player_stats(self):
        if self.player_stats_dict is None:
            self.player_stats_dict = {}
            for r in self.all_df.iterrows():
                row = r[1]
                self.player_stats_dict[row["winner_name"]] = [row["winner_hand"],
                                                              row["winner_ht"],
                                                              row["winner_country"],
                                                              row["winner_continent"]]
        return self.player_stats_dict

    def top_players_by_year(self):
        top_player_raw = defaultdict(list)
        top_players_by_year_dict = defaultdict(list)
        year_groups = self.rank().groupby(["year", "name"])
        for (year, player), group in year_groups:
            min_rank = np.mean(group["rank"])
            if not math.isnan(min_rank):
                top_player_raw[year].append([player, min_rank])
        for year in top_player_raw:
            players = top_player_raw[year]
            players.sort(key=lambda i: i[1])
            top_players_by_year_dict[year] = [r[0] for r in players if not math.isnan(r[1])]
        return top_players_by_year_dict

    def matches_for_players(self):
        match_dict = defaultdict(dict)
        for names, winning_group in self.all_df.groupby(["winner_name", "loser_name"]):
            #match_dict[names[0]][names[1]] = winning_group.sort_values(by="tourney_date")
            match_dict[names[0]][names[1]] = winning_group
        return match_dict

    def rank(self, save_csv=False, filename="../data/topranks.csv", use_saved=False):
        """
        Return a dataframe with ranking data.  Used in Ranking Interactive dashboard.

        :param save_csv: whether to save csv file for later user
        :param filename: filename of csv file
        :return: dataframe with year, name, rank and country
        """
        if self.rank_df is None:
            if use_saved:
                print("Loading saved toprank file : {}".format(filename))
                self.rank_df = pd.read_csv(filename)
                self.rank_df['date'] = pd.to_datetime(self.rank_df['date'])

            else:
                rows_winners = self.all_df.loc[:,
                               ["tourney_date", "winner_name", "winner_country", "winner_rank", "winner_continent",
                                "winner_hand", "winner_ht", "winner_age", "winner_rank_points"]]
                rows_losers = self.all_df.loc[:,
                              ["tourney_date", "loser_name", "loser_country", "loser_rank", "loser_continent",
                               "loser_hand", "loser_ht", "loser_age", "loser_rank_points"]]
                cols = ["date", "name", "country", "rank", "continent", "handed", "ht", "age", "rank_points"]
                rows_winners.columns = cols
                rows_losers.columns = cols
                toprank_df = pd.concat([rows_winners, rows_losers], ignore_index=True)
                toprank_df["year"] = [d.year for d in toprank_df.date]
                toprank_df.sort_values(inplace=True, by=["date", "name"])
                self.rank_df = toprank_df
            if save_csv:
                self.rank_df.to_csv(filename, index=False)
        return self.rank_df


if __name__ == '__main__':
    data = ATPTennisData(load_combined_file=True)
    print(data.data().describe())
    records_by_year = list(data.data()["year"])
