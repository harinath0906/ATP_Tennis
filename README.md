# ATP Tennis Analytic System
#### COMP5048 Assignment 2 Group 3

The following provides instructions to execute each python script.  Each will start a Dash server at http://127.0.0.1:8050/

Terminate each script before starting the next one. 
## 1. Setup environment using `conda`

`conda ATPTennis create -f environment.yml`

`conda activate ATPTennis`

## 2. Execute Visualisations

### Vis 1 Geospatial Representation of Performance
`cd ./vis_1_geospatial_view`

`python ATP_GeoSpatial_Visualisations_Dash.py`

### Vis 2 Sunburst chart
`cd ./vis_2_sunburst`

`python sunburst_tennis.py`

### Vis 3 Treemap chart
`cd ./vis_3_treemap`

`python treemap.py`

### Vis 4 Ranking and Rank Points Visualisation
#### Set PYTHONPATH env variable first 

For MacOSx and Linux execute this command from cwd directory.
`export PYTHONPATH=${PYTHONPATH}:../`

For Windows set environment variable through Windows interface.

#### Execute Dash script
`cd ./vis_4_rank_and_rankings`

`python app.py`

### Vis 5 Factors Contributing to Shock Results
`cd ./vis_5_upsets`

`python Shock_Analysis.py`


### Vis 6 Winners Averages per Surface

`cd ./vis_6_metrics`

`python All_Averages.py`

`python Winner-Losers.py`
