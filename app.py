import pandas as pd 
import os as os 
from pathlib import Path
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
import plotly.graph_objects as go 
# from ipywidgets import widgets
import datetime as dt
from sklearn.metrics import r2_score
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

rootdir_os = 'IHME_projections/Unzipped'
rootdir_p = Path(r'IHME_projections/Unzipped')

CDCdf = pd.read_csv('CDC_data/Provisional_COVID-19_Death_Counts_by_Week_Ending_Date_and_State.csv')
covtrkrdf = pd.read_csv('covidtracking/historic_US_0511.csv')

#### CDC Data clean and pre-process ####
CDCdf = CDCdf[CDCdf['State'] == 'United States']
weekending_dat = CDCdf[CDCdf['Indicator'] == 'Week-ending']
y_weekending_dat = weekending_dat['COVID Deaths']
x_weekending_dat = weekending_dat['Start week']
vals = []
x_dates = []

for i in (range(2, len(x_weekending_dat))):
    # print(i)
    # if (i < (len(x_weekending_dat)-1)):
    stop = pd.to_datetime(x_weekending_dat[i])
    delt = pd.to_timedelta(7, unit='d')
    start = stop - delt
    date_holder = pd.date_range(start, stop)
    vals[7*(i-1):(7*i)-1] = [y_weekending_dat[i]/7]*7
    x_dates.append(date_holder)
    # elif (i == (len(x_weekending_dat))):
    #     print('hi')

new_x = pd.date_range(x_dates[0][1], x_dates[-1][-1])

#### COVIDTracker.com Data clean and pre-process ####
covtrkrdf.date = pd.to_datetime(covtrkrdf.date, format = '%Y%m%d')
cov_x = covtrkrdf.date 
cov_y = covtrkrdf.deathIncrease

sp = rootdir_p.parts
print(sp)


dfs = {}
df_names = list()
for subdir, dirs, files in os.walk(rootdir_os):
    for file in files:
        ext = os.path.splitext(file)[-1].lower()
        p = Path(subdir)
        date = p.parts[-1][:10]
        date = date[5:]
        if ext == '.csv':
            
            # print (os.path.join(subdir, file))
            # print(date)
            df_name = str('df_' + date) 
            df_names.append(df_name)
            dfs[str(df_name)]=pd.read_csv(subdir + "//" + file)

df_names.sort()

names = {}
names['ihme'] = df_names

states = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado",
  "Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois",
  "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland",
  "Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana",
  "Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York",
  "North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania",
  "Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah",
  "Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming", 
  "District of Columbia"]

lcstates = [x.lower() for x in states]

# df = dfs[df_names[-1]][dfs[df_names[-1]]['location_name'].isin(states)]

# x = df['date'].unique()
# x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in x]


rootdir_os = 'Los Alamos projections'
rootdir_p = Path(r'Los Alamos projections')

#### Los Alamos Model Ingest ####
ladfs = {}
ladf_names = list()
for subdir, dirs, files in os.walk(rootdir_os):
    for file in files:
        ext = os.path.splitext(file)[-1].lower()
        date = file[:10]
        if ext == '.csv':
            
            # print (os.path.join(subdir, file))
            # print(date)
            ladf_name = str('df_' + date) 
            ladf_names.append(ladf_name)
            ladfs[str(ladf_name)]=pd.read_csv(subdir + "//" + file)
            ladfs[str(ladf_name)].dates = pd.to_datetime(ladfs[str(ladf_name)].dates)
            ladfs[str(ladf_name)] = ladfs[str(ladf_name)][ladfs[str(ladf_name)].state.isin(states)]

ladf_names.sort()

names['los_alamos'] = ladf_names

for i in range(len(ladf_names)):
    ladfs[ladf_names[i]]['daily_deaths'] = ladfs[ladf_names[i]].groupby(['state'])['q.50'].diff()
    ladfs[ladf_names[i]]['daily_95CI'] = ladfs[ladf_names[i]].groupby(['state'])['q.95'].diff()
    ladfs[ladf_names[i]]['daily_05CI'] = ladfs[ladf_names[i]].groupby(['state'])['q.05'].diff()

#### Make Plots ####
# Slider for date of projection
# Dropdown for projection (IHME, other if I find one with historical projections)
# Dropdown for deaths count source (covidtracker.com or CDC)
# [Optional] color forecasted line (based on slider date) in a different color

##### Sam's Suggestion #####
"""
    I think the play is to add another level to the traces{n} data structure so
    that you can look up the IHME projections with something like traces['ihme'][1][i]
    instead of traces1[i]. The traces dictionary below fits this structure.
"""
traces = {
    'ihme': [
        [0]*(len(df_names)),
        [0]*(len(df_names)),
        [0]*(len(df_names)),
        [0]*(len(df_names))
    ],
    'los_alamos': [
        [0]*(len(ladf_names)),
        [0]*(len(ladf_names)),
        [0]*(len(ladf_names)),
        [0]*(len(ladf_names))
    ]
}


def MAPE(predict,target):
    return ( abs((target - predict) / target).mean())


mape = {
    'ihme': [0]*len(df_names),
    'los_alamos': [0]*len(ladf_names)
}

artoo = {
    'ihme': [0]*len(df_names),
    'los_alamos': [0]*len(ladf_names)
}

for i in range(len(df_names)):
    df = dfs[df_names[i]][dfs[df_names[i]]['location_name'].isin(states)]
    max_date = max(cov_x)
    mon = df_names[i][3:5]
    day = df_names[i][6:]
    pred_date = pd.to_datetime(str('2020'+mon+day), format = '%Y%m%d')
    date_rng = pd.date_range(pred_date, max_date)
    cov_mask = covtrkrdf.date.isin(date_rng)
    covdf = covtrkrdf[cov_mask].set_index('date').iloc[::-1]
    artoo_y = covdf.deathIncrease
    try:
        x = df['date'].unique()
        y = df.groupby(['date'])['deaths_mean'].sum()
        CI_upper = df.groupby(['date'])['deaths_upper'].sum()
        CI_lower = df.groupby(['date'])['deaths_lower'].sum()
        mask = pd.to_datetime(df.date.values).isin(date_rng)
        little_df = df[mask]
        pred_y = little_df.groupby(['date'])['deaths_mean'].sum()
    except:
        x = df['date_reported'].unique()
        y = df.groupby(['date_reported'])['deaths_mean'].sum()
        CI_upper = df.groupby(['date_reported'])['deaths_upper'].sum()
        CI_lower = df.groupby(['date_reported'])['deaths_lower'].sum()
        mask = pd.to_datetime(df.date_reported.values).isin(date_rng)
        little_df = df[mask]
        pred_y = little_df.groupby(['date_reported'])['deaths_mean'].sum()
    finally:
        # x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in x]
        traces['ihme'][0][i] = go.Scatter(x = x, y = y, opacity= 0.8, name = 'Projected COVID19 Daily Deaths')
        traces['ihme'][1][i] = go.Scatter(x = cov_x, y = cov_y, opacity = 0.8, name = 'COVIDtracker.com Recorded Daily Deaths')
        traces['ihme'][2][i] = go.Scatter(x = x, y = CI_upper, opacity = 0.2, name = '95% CI Upper Limit', line = dict(dash = 'dash'))
        traces['ihme'][3][i] = go.Scatter(x = x, y = CI_lower, opacity = 0.2, fill = 'tonexty', name = '95% CI Lower Limit', line = dict(dash = 'dash'))
        
        # Duplicating ihme for los alamos to test dropdown
        
        artoo['ihme'][i] = r2_score(artoo_y, pred_y).round(4)
        mape['ihme'][i] = np.round(MAPE(artoo_y, pred_y), 4)

for i in range(len(ladf_names)):
    df = ladfs[ladf_names[i]]
    max_date = max(cov_x)
    year = ladf_names[i][3:7]
    mon = ladf_names[i][8:10]
    day = ladf_names[i][11:13]
    pred_date = pd.to_datetime(str(year+mon+day), format = '%Y%m%d')
    date_rng = pd.date_range(pred_date, max_date)
    cov_mask = covtrkrdf.date.isin(date_rng)
    covdf = covtrkrdf[cov_mask].set_index('date').iloc[::-1]
    artoo_y = covdf.deathIncrease
    x = [str(d)[:10] for d in df['dates'].unique()]
    y = df.groupby(['dates'])['daily_deaths'].sum()
    CI_upper = df.groupby(['dates'])['daily_95CI'].sum()
    CI_lower = df.groupby(['dates'])['daily_05CI'].sum()
    mask = pd.to_datetime(df.dates.values).isin(date_rng)
    little_df = df[mask]
    pred_y = little_df.groupby(['dates'])['daily_deaths'].sum()
    traces['los_alamos'][0][i] = go.Scatter(x = x, y = y, opacity= 0.8, name = str('IHME projected deaths for '+ ladf_names[i]))
    traces['los_alamos'][1][i] = go.Scatter(x = cov_x, y = cov_y, opacity = 0.8, name = 'COVIDtracker.com recorded deaths')
    traces['los_alamos'][2][i] = go.Scatter(x = x, y = CI_upper, opacity = 0.2, name = '95% CI', line = dict(dash = 'dash'))
    traces['los_alamos'][3][i] = go.Scatter(x = x, y = CI_lower, opacity = 0.2, fill = 'tonexty', name = '95% CI', line = dict(dash = 'dash'))

    artoo['los_alamos'][i] = r2_score(artoo_y, pred_y).round(4)
    mape['los_alamos'][i] = np.round(MAPE(artoo_y, pred_y), 4)

# Create Dash app
app = dash.Dash()

dropdown = dcc.Dropdown(
    id='dropdown',
    options=[
        {'label': 'IHME Projections', 'value': 'ihme'},
        {'label': 'Los Alamos Projections', 'value': 'los_alamos'},
    ],
    value='ihme'
)

titles = {
    'ihme': 'IHME',
    'los_alamos': 'Los Alamos'
}

scatterplot = dcc.Graph(
    id='scatterplot',
    figure=go.Figure(
        data=[trace[0] for trace in traces['ihme']],
        layout=go.Layout(title = dict(text = f"{titles['ihme']} model projection"))
    ),
    animate=False
)

marks = {
    'ihme': {i: name[3:].replace('_', '/') for i, name in enumerate(names['ihme'])},
    'los_alamos': {i: name[8:].replace('-', '/') for i, name in enumerate(names['los_alamos'])}
}


slider = dcc.Slider(
    id='date-slider',
    min=0,
    max=len(names['ihme'])-1,
    marks=marks['ihme'],
    value=0,
    updatemode='drag'
)


def generate_info_markdown(model, date):
    return f'''
        **MAPE:** {mape[model][date]}
        **R2:** {artoo[model][date]}
    '''

info = dcc.Markdown(
    generate_info_markdown('ihme', 0),
    id='info'
)

app.layout = html.Div([
    dropdown,
    scatterplot,
    info,
    slider
])

@app.callback(Output('scatterplot', 'figure'),
              [Input('dropdown', 'value'),
               Input('date-slider', 'value')])
def display_value(model, date):
    if date > len(marks[model]) - 1:
        date = len(marks[model]) - 1
    _traces = [trace[date] for trace in traces[model]]
    return {'data': _traces, 'layout': go.Layout(dict(title = f"{titles[model]} Model Projection as of {marks[model][date]}"))}

@app.callback(Output('date-slider', 'max'),
              [Input('dropdown', 'value')])
def update_slider_range(model):
    return len(names[model]) - 1

@app.callback(Output('date-slider', 'marks'),
              [Input('dropdown', 'value')])
def update_slider_range(model):
    return marks[model]

@app.callback(Output('info', 'children'),
              [Input('dropdown', 'value'),
               Input('date-slider', 'value')])
def update_info(model, date):
    if date > len(marks[model]) - 1:
        date = len(marks[model]) - 1
    return generate_info_markdown(model, date)

app.title = 'IHME Model Projections'
app.run_server(debug=True, use_reloader=True)