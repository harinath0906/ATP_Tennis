#The following code produces geospatial view of winning matches / losing matches / winning player / losing players
#Author: Hari Nath Bingi (hbin7552)

#Loading libraries

import pandas as pd
import numpy as np
import os
from collections import defaultdict
import plotly.graph_objects as go
import dash
#from jupyter_dash import JupyterDash

#import jupyter_dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import plotly.express as px

def renderGraphPage():
    #print("Preprocessing data....")
    #print("Please wait....")
    alldata = []
    parentDir=os.pardir
    #
    #directory = os.getcwd()+'/dataset/' #dataset directory
    directory = os.getcwd()+'/../data/ATP_Matches/' #dataset directory
    for filename in os.listdir(directory):
        if filename.endswith(".csv") and filename.startswith("atp"):
            #print(os.path.join(directory, filename))
            year= filename.split("_")[2].split(".")[0]  #Getting year from filename to add in dataframe in Year column
            file1 = open(os.path.join(directory, filename), 'r')
            Lines = file1.readlines() 
            file_list = []
            for line in Lines: 
                list_lin = line.rstrip("\n").rstrip(',').split(",") #Stripping out additional comma at the end of line
                file_list.append(list_lin) #appending cleaned lies to a temp list 
            tempdf=pd.DataFrame(file_list[1:],columns=file_list[0]) #converting temp list (excluding first line as headings) into dataframe
            tempdf['year']= int(year) #Adding year into dataframe columns
            alldata.append(tempdf) #adding dataframe to a list
        else:
            continue
    tennis_df = pd.concat(alldata) #Concatenating all data frame
    tennis_df.reset_index(drop=True,inplace=True) #Resetting index



    # # Countries df for creating map

    # In[3]:


    countries_df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv')
    countries_df['new_name']=countries_df['COUNTRY'].str.upper().apply(lambda y: y[0:3])


    # In[4]:


    countries_df[countries_df['COUNTRY'].str.contains("Ne")]


    # # Winner Count per country per year

    # In[5]:


    winning_country_year_df=[] #We will have seperate dataframe for every year, all dataframe to be stored in this list
    year_key = {}
    count = 0

    for year in set(list(tennis_df['year'])): #Looping through countries
        tmp_list = []
        for country in set(list(tennis_df[tennis_df['year'] == year]['winner_ioc'])): #Looping through years
          if country != None:
            tmp_list.append([country,len(tennis_df[(tennis_df['winner_ioc'] == country) & (tennis_df['year'] == year)])]) #Addding country name and number of winners
        winning_country_year_df.append(pd.DataFrame(tmp_list,columns=['Country','Winner_Count'])) #converting to a dataframe and storing to list
        year_key[count] = year  #Creating index to year dictionary for future reference
        count+=1


    # In[6]:





    winning_country_year_geometry_df = [] #List to hold dataframe for every year. Each dataframe will be an extension of world df with winner count as additional column

    #Below are some hard coded values to map with the ones in world dataframe
    #
    unavailable_Country_codes = [] #To save country codes which are not available


    #AHO belong to netherlands antilles, which is not available in world dataframe hence mapping it to USA

    #Dictionary to map ATP country code to ISO country code for the ones which are tricky
    some_known_dict = {'INA':'IDN','PUR':'PRI','ESA':'EST','RSA':'ZAF','MAS':'MYS','NED':'NLD','TPE':'TWN','SUI':'CHE'                   ,'CRC':'CRI','IRI':'IRN','UAE':'ARE',                   'NGR':'NGA'}
    some_known_dict_ambigous = {'AHO':'USA'}
    #df['CODE']

    for e in range(len(winning_country_year_df)):
      geom_col = []  #We want to create a new column which will have the iso_a3 country code for a given country
      for each_count in list(winning_country_year_df[e]['Country']): #each_count is each_country
        subsetdf = countries_df[countries_df['CODE'] == each_count] #Checking is the ATP country code is same as iso country code
        if len(subsetdf) == 1:
          geom_col.append(subsetdf.iloc[0]['CODE'])  #Appending the iso country code
        else:
          subsetdf = countries_df[countries_df['new_name'] == each_count]  #We created a new columns with the first 3 letters of every country. Checking to see if it matches ATP code
          if len(subsetdf) > 0:
            geom_col.append(subsetdf.iloc[0]['CODE']) #In case of a match, Appending its iso country code
          else:
            try:
              subsetdf = countries_df[countries_df['CODE'] == some_known_dict[each_count]] #Else checking in out dictonary for the ATP country code
              if len(subsetdf) > 0:
                geom_col.append(some_known_dict[each_count])  #In case of a match appending its iso_a3 country code
              else:
                #print(each_count," could not be found")  #Else printing to check manually
                unavailable_Country_codes.append(each_count)
                #print(e)
                geom_col.append("")
            except:  #Else printing to check manually
              #print(each_count," could not be found")
              unavailable_Country_codes.append(each_count)
              #print(e)
              geom_col.append("")
      winning_country_year_df[e]['matching_col'] = geom_col  #Appending the new column to the dataframe
      tmp_world_df = countries_df.merge(winning_country_year_df[e], how='left', left_on="CODE", right_on="matching_col")
      tmp_world_df['Winner_Count'] = tmp_world_df['Winner_Count'].fillna(0)
      winning_country_year_geometry_df.append(tmp_world_df)
    unavailable_Country_codes =set(unavailable_Country_codes)
    #if len(unavailable_Country_codes) > 0:
      #print("Unavailable country codes",unavailable_Country_codes)


    # # Loser Count Per Country

    # In[7]:


    losing_country_year_df=[] #We will have seperate dataframe for every year, all dataframe to be stored in this list

    for year in set(list(tennis_df['year'])): #Looping through countries
        tmp_list = []
        for country in set(list(tennis_df[tennis_df['year'] == year]['loser_ioc'])): #Looping through years
          if country != None:
            tmp_list.append([country,len(tennis_df[(tennis_df['loser_ioc'] == country) & (tennis_df['year'] == year)])]) #Addding country name and number of winners
        losing_country_year_df.append(pd.DataFrame(tmp_list,columns=['Country','Loser_Count'])) #converting to a dataframe and storing to list




    losing_country_year_geometry_df = [] #List to hold dataframe for every year. Each dataframe will be an extension of world df with winner count as additional column

    #Below are some hard coded values to map with the ones in world dataframe
    #
    unavailable_Country_codes = [] #To save country codes which are not available


    #AHO belong to netherlands antilles, which is not available in world dataframe hence mapping it to USA

    #Dictionary to map ATP country code to ISO country code for the ones which are tricky
    some_known_dict = {'INA':'IDN','PUR':'PRI','ESA':'EST','RSA':'ZAF','MAS':'MYS','NED':'NLD','TPE':'TWN','SUI':'CHE'                   ,'CRC':'CRI','IRI':'IRN','UAE':'ARE',                   'NGR':'NGA'}
    some_known_dict_ambigous = {'AHO':'USA'}
    #df['CODE']

    for e in range(len(losing_country_year_df)):
      geom_col = []  #We want to create a new column which will have the iso_a3 country code for a given country
      for each_count in list(losing_country_year_df[e]['Country']): #each_count is each_country
        subsetdf = countries_df[countries_df['CODE'] == each_count] #Checking is the ATP country code is same as iso country code
        if len(subsetdf) == 1:
          geom_col.append(subsetdf.iloc[0]['CODE'])  #Appending the iso country code
        else:
          subsetdf = countries_df[countries_df['new_name'] == each_count]  #We created a new columns with the first 3 letters of every country. Checking to see if it matches ATP code
          if len(subsetdf) > 0:
            geom_col.append(subsetdf.iloc[0]['CODE']) #In case of a match, Appending its iso country code
          else:
            try:
              subsetdf = countries_df[countries_df['CODE'] == some_known_dict[each_count]] #Else checking in out dictonary for the ATP country code
              if len(subsetdf) > 0:
                geom_col.append(some_known_dict[each_count])  #In case of a match appending its iso_a3 country code
              else:
                #print(each_count," could not be found")  #Else printing to check manually
                unavailable_Country_codes.append(each_count)
                #print(e)
                geom_col.append("")
            except:  #Else printing to check manually
              #print(each_count," could not be found")
              unavailable_Country_codes.append(each_count)
              #print(e)
              geom_col.append("")
      losing_country_year_df[e]['matching_col'] = geom_col  #Appending the new column to the dataframe
      tmp_world_df = countries_df.merge(losing_country_year_df[e], how='left', left_on="CODE", right_on="matching_col")
      tmp_world_df['Loser_Count'] = tmp_world_df['Loser_Count'].fillna(0)
      losing_country_year_geometry_df.append(tmp_world_df)
    unavailable_Country_codes =set(unavailable_Country_codes)
    #if len(unavailable_Country_codes) > 0:
      #print("Unavailable country codes",unavailable_Country_codes)


    # # Total players in a country

    # In[8]:





    country_dict = defaultdict(set)
    for k, g in tennis_df.groupby(["winner_name", "winner_ioc"]):
        country_dict[k[1]].add(k[0])
    for k, g in tennis_df.groupby(["loser_name", "loser_ioc"]):
        country_dict[k[1]].add(k[0])
    out = [[k, len(country_dict[k])]for k in country_dict]
    player_count = pd.DataFrame(out, columns=["country","no_players"])


    # # Winning Count - Normalised

    # In[9]:




    winning_country_year_norm_df=[] #We will have seperate dataframe for every year, all dataframe to be stored in this list


    for year in set(list(tennis_df['year'])): #Looping through countries
        tmp_list = []
        country_dict = defaultdict(set)
        for k, g in tennis_df[tennis_df['year'] == year].groupby(["winner_name", "winner_ioc"]):
            country_dict[k[1]].add(k[0])
        out = [[k, len(country_dict[k])]for k in country_dict]
        winning_country_year_norm_df.append(pd.DataFrame(out, columns=["Country","Winner_Count"]))


    for e in range(len(winning_country_year_norm_df)):
      for country in list(winning_country_year_norm_df[e]['Country']):
        winning_country_year_norm_df[e].loc[winning_country_year_norm_df[e]['Country'] == country,'Winner_Count']/=np.array(player_count[player_count['country']==country]['no_players'])[0]
        #break
      #break


    # In[10]:


    winning_country_year_geometry_norm_df = [] #List to hold dataframe for every year. Each dataframe will be an extension of world df with winner count as additional column

    #Below are some hard coded values to map with the ones in world dataframe
    #
    unavailable_Country_codes = [] #To save country codes which are not available


    #AHO belong to netherlands antilles, which is not available in world dataframe hence mapping it to USA

    #Dictionary to map ATP country code to ISO country code for the ones which are tricky
    some_known_dict = {'INA':'IDN','PUR':'PRI','ESA':'EST','RSA':'ZAF','MAS':'MYS','NED':'NLD','TPE':'TWN','SUI':'CHE'                   ,'CRC':'CRI','IRI':'IRN','UAE':'ARE',                   'NGR':'NGA'}
    some_known_dict_ambigous = {'AHO':'USA'}
    #df['CODE']

    for e in range(len(winning_country_year_norm_df)):
      geom_col = []  #We want to create a new column which will have the iso_a3 country code for a given country
      for each_count in list(winning_country_year_norm_df[e]['Country']): #each_count is each_country
        subsetdf = countries_df[countries_df['CODE'] == each_count] #Checking is the ATP country code is same as iso country code
        if len(subsetdf) == 1:
          geom_col.append(subsetdf.iloc[0]['CODE'])  #Appending the iso country code
        else:
          subsetdf = countries_df[countries_df['new_name'] == each_count]  #We created a new columns with the first 3 letters of every country. Checking to see if it matches ATP code
          if len(subsetdf) > 0:
            geom_col.append(subsetdf.iloc[0]['CODE']) #In case of a match, Appending its iso country code
          else:
            try:
              subsetdf = countries_df[countries_df['CODE'] == some_known_dict[each_count]] #Else checking in out dictonary for the ATP country code
              if len(subsetdf) > 0:
                geom_col.append(some_known_dict[each_count])  #In case of a match appending its iso_a3 country code
              else:
                #print(each_count," could not be found")  #Else printing to check manually
                unavailable_Country_codes.append(each_count)
                #print(e)
                geom_col.append("")
            except:  #Else printing to check manually
              #print(each_count," could not be found")
              unavailable_Country_codes.append(each_count)
              #print(e)
              geom_col.append("")
      winning_country_year_norm_df[e]['matching_col'] = geom_col  #Appending the new column to the dataframe
      tmp_world_df = countries_df.merge(winning_country_year_norm_df[e], how='left', left_on="CODE", right_on="matching_col")
      tmp_world_df['Winner_Count'] = tmp_world_df['Winner_Count'].fillna(0)
      winning_country_year_geometry_norm_df.append(tmp_world_df)
    unavailable_Country_codes =set(unavailable_Country_codes)
    #if len(unavailable_Country_codes) > 0:
      #print("Unavailable country codes",unavailable_Country_codes)


    # # Losers Count - Normalised

    # In[11]:


    losing_country_year_norm_df=[] #We will have seperate dataframe for every year, all dataframe to be stored in this list


    for year in set(list(tennis_df['year'])): #Looping through countries
        tmp_list = []
        country_dict = defaultdict(set)
        for k, g in tennis_df[tennis_df['year'] == year].groupby(["loser_name", "loser_ioc"]):
            country_dict[k[1]].add(k[0])
        out = [[k, len(country_dict[k])]for k in country_dict]
        losing_country_year_norm_df.append(pd.DataFrame(out, columns=["Country","Loser_Count"]))


    for e in range(len(losing_country_year_norm_df)):
      for country in list(losing_country_year_norm_df[e]['Country']):
        losing_country_year_norm_df[e].loc[losing_country_year_norm_df[e]['Country'] == country,'Loser_Count']/=np.array(player_count[player_count['country']==country]['no_players'])[0]
        #break
      #break


    # In[12]:


    losing_country_year_geometry_norm_df = [] #List to hold dataframe for every year. Each dataframe will be an extension of world df with winner count as additional column

    #Below are some hard coded values to map with the ones in world dataframe
    #
    unavailable_Country_codes = [] #To save country codes which are not available


    #AHO belong to netherlands antilles, which is not available in world dataframe hence mapping it to USA

    #Dictionary to map ATP country code to ISO country code for the ones which are tricky
    some_known_dict = {'INA':'IDN','PUR':'PRI','ESA':'EST','RSA':'ZAF','MAS':'MYS','NED':'NLD','TPE':'TWN','SUI':'CHE'                   ,'CRC':'CRI','IRI':'IRN','UAE':'ARE',                   'NGR':'NGA'}
    some_known_dict_ambigous = {'AHO':'USA'}
    #df['CODE']

    for e in range(len(losing_country_year_norm_df)):
      geom_col = []  #We want to create a new column which will have the iso_a3 country code for a given country
      for each_count in list(losing_country_year_norm_df[e]['Country']): #each_count is each_country
        subsetdf = countries_df[countries_df['CODE'] == each_count] #Checking is the ATP country code is same as iso country code
        if len(subsetdf) == 1:
          geom_col.append(subsetdf.iloc[0]['CODE'])  #Appending the iso country code
        else:
          subsetdf = countries_df[countries_df['new_name'] == each_count]  #We created a new columns with the first 3 letters of every country. Checking to see if it matches ATP code
          if len(subsetdf) > 0:
            geom_col.append(subsetdf.iloc[0]['CODE']) #In case of a match, Appending its iso country code
          else:
            try:
              subsetdf = countries_df[countries_df['CODE'] == some_known_dict[each_count]] #Else checking in out dictonary for the ATP country code
              if len(subsetdf) > 0:
                geom_col.append(some_known_dict[each_count])  #In case of a match appending its iso_a3 country code
              else:
                #print(each_count," could not be found")  #Else printing to check manually
                unavailable_Country_codes.append(each_count)
                #print(e)
                geom_col.append("")
            except:  #Else printing to check manually
              #print(each_count," could not be found")
              unavailable_Country_codes.append(each_count)
              #print(e)
              geom_col.append("")
      losing_country_year_norm_df[e]['matching_col'] = geom_col  #Appending the new column to the dataframe
      tmp_world_df = countries_df.merge(losing_country_year_norm_df[e], how='left', left_on="CODE", right_on="matching_col")
      tmp_world_df['Loser_Count'] = tmp_world_df['Loser_Count'].fillna(0)
      losing_country_year_geometry_norm_df.append(tmp_world_df)
    unavailable_Country_codes =set(unavailable_Country_codes)
    #if len(unavailable_Country_codes) > 0:
      #print("Unavailable country codes",unavailable_Country_codes)


    # # Default fig

    # In[13]:




    year_value=max(year_key.values())
    reverse_year_key = {}
    for g in year_key.keys():
        reverse_year_key[year_key[g]]=g

    def_fig = go.Figure(data=go.Choropleth(
    locations = winning_country_year_geometry_df[reverse_year_key[year_value]]['CODE'],
    z = winning_country_year_geometry_df[reverse_year_key[year_value]]['Winner_Count'],
    text = winning_country_year_geometry_df[reverse_year_key[year_value]]['COUNTRY'],
    colorscale = 'Blues',
    autocolorscale=False,
    reversescale=False,
    marker_line_color='darkgray',
    marker_line_width=0.5,
    #colorbar_tickprefix = '$',
    colorbar_title = 'Winning macthes',
    ))

    def_fig.update_layout(
        title_text='Winners of ATP matches - '+str(year_value),
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
    )


    # In[14]:






    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

    df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')

    #available_indicators = df['Indicator Name'].unique()

    app.layout = html.Div([

        html.Div([
            dcc.Graph(id='winner_count', figure=def_fig),
            #dcc.Graph(id='y-time-series'),
        ], style={'display': 'inline-block', 'width': '100%'}),

        

        
        html.Div(dcc.Slider(
            id='crossfilter-year--slider',
            min=min(year_key.values()),
            max=max(year_key.values()),
            value=max(year_key.values()),
            marks={str(year): str(year) for year in set(year_key.values())},
            included=False,
            step=None
        ), style={'width': '100%', 'padding': '0px 20px 20px 20px'}),
        
        html.Div(    dcc.Dropdown(
            id='type-dropdown',
            options=[
                {'label': 'Winning Matches', 'value': 'W1'},
                {'label': 'Losing Matches', 'value': 'L1'},
                {'label': 'Winners to Total players', 'value': 'W2'},
                {'label': 'Losers to Total players', 'value': 'L2'}
            ],
            value='W1'
        ), style={'width': '100%', 'padding': '0px 20px 20px 20px'})
        
        
    ])


    @app.callback(
        dash.dependencies.Output('winner_count', 'figure'),
        [dash.dependencies.Input('crossfilter-year--slider', 'value'),
         dash.dependencies.Input('type-dropdown', 'value')]
        )

    def update_figure(year_value,type_of_view):
        reverse_year_key = {}
        for g in year_key.keys():
            reverse_year_key[year_key[g]]=g
            
        data_to_use = {'W1':winning_country_year_geometry_df,
                       'L1':losing_country_year_geometry_df,
                       'W2':winning_country_year_geometry_norm_df,
                       'L2':losing_country_year_geometry_norm_df}
        
        color_bar_title_dict = {'W1':'Winning Matches',
                       'L1':'Losing Matches',
                       'W2':'Winners:Total ratio',
                       'L2':'Losers:Total ratio'}
        
        fig_title_dict = {'W1':'Winning Matches of ATP',
                       'L1':'Losing Matches of ATP',
                       'W2':'Winners (to total players) of ATP',
                       'L2':'Losers (to total players) of ATP'}
        key_to_use_dict = {'W1':'Winner_Count',
                       'L1':'Loser_Count',
                       'W2':'Winner_Count',
                       'L2':'Loser_Count'}
        
        df_array_to_use = data_to_use[type_of_view]
        fig = go.Figure(data=go.Choropleth(
        locations = df_array_to_use[reverse_year_key[year_value]]['CODE'],
        z = df_array_to_use[reverse_year_key[year_value]][key_to_use_dict[type_of_view]],
        text = df_array_to_use[reverse_year_key[year_value]]['COUNTRY'],
        colorscale = 'Blues',
        autocolorscale=False,
        reversescale=False,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        #colorbar_tickprefix = '$',
        colorbar_title = color_bar_title_dict[type_of_view],
        ))

        fig.update_layout(
            title_text=fig_title_dict[type_of_view]+' - '+str(year_value),
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='equirectangular'
            ),
        )
        return fig



    app.run_server(debug=True, use_reloader=True)#,port=8060)

if __name__ == "__main__":
   renderGraphPage()