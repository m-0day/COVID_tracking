import pandas as pd 
import os as os 
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from sklearn.metrics import r2_score

rootdir_os = 'C:\\Users\\chris.mclean\\Documents\\Python Scripts\\COVID analysis\\IHME_projections\\Unzipped'
rootdir_p = Path(r'C:\Users\chris.mclean\Documents\Python Scripts\COVID analysis\IHME_projections\Unzipped')

CDCdf = pd.read_csv('C:/Users/chris.mclean\Documents/Python Scripts/COVID analysis/CDC_data/Provisional_COVID-19_Death_Counts_by_Week_Ending_Date_and_State.csv')
covtrkrdf = pd.read_csv('C:/Users/chris.mclean/Documents/Python Scripts/COVID analysis/covidtracking/historic_US_0501.csv')

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

#### IHME model ingest ####

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

states = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado",
  "Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois",
  "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland",
  "Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana",
  "Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York",
  "North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania",
  "Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah",
  "Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]

df = dfs[df_names[-1]][dfs[df_names[-1]]['location_name'].isin(states)]

x = df['date'].unique()
x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in x]

#### Los Alamos model ingest ####

rootdir_os = 'C:\\Users\\chris.mclean\\Documents\\Python Scripts\\COVID analysis\\Los Alamos projections'
rootdir_p = Path(r'C:\Users\chris.mclean\Documents\Python Scripts\COVID analysis\Los Alamos projections')

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
            ladfs[str(ladf_name)] = ladfs[str(ladf_name)][ladfs[str(ladf_name)].simple_state.isin(states)]

ladf_names.sort()

# ladf = dfs[df_names[-1]][dfs[df_names[-1]]['location_name'].isin(states)]


# i = 0
# max_date = max(cov_x)
# mon = df_names[i][3:5]
# day = df_names[i][6:]
# pred_date = pd.to_datetime(str('2020'+mon+day), format = '%Y%m%d')
# date_rng = pd.date_range(pred_date, max_date)

# mask = pd.to_datetime(df.date.values).isin(date_rng)
# little_df = df[mask]
# pred_y = little_df.groupby(['date'])['deaths_mean'].sum()



# fig, ax = plt.subplots()
# ax.plot(x, df.groupby(['date'])['deaths_mean'].sum(), linestyle = '-.')
# ax.fill_between(x, df.groupby(['date'])['deaths_upper'].sum(), \
#     df.groupby(['date'])['deaths_lower'].sum(), alpha = 0.2)
# ax.plot(new_x, vals, linestyle = '-', alpha = 0.8, color = 'm')
# ax.plot(cov_x, cov_y, alpha = 0.8, color = 'r')

# plt.title(str('IHME Prediction vs. CDC Recorded COVID-19 Deaths as of '+ df_names[-1][3:]))

# plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=14))
# fig.autofmt_xdate()
# ax.legend(['IHME predicted COVID deaths', 'CDC recorded COVID deaths', 'COVIDtracker.com recorded deaths'])

# plt.show()

###############################################################################################
###############################################################################################

###############################################################################################
###############################################################################################

import plotly.graph_objects as go 
from ipywidgets import widgets

# fig = go.Figure()

#### Make Plots ####
# Slider for date of projection
# Dropdown for projection (IHME, other if I find one with historical projections)
# Dropdown for deaths count source (covidtracker.com or CDC)
# [Optional] color forecasted line (based on slider date) in a different color

traces1 = [0]*(len(df_names))
traces2 = [0]*(len(df_names))
traces3 = [0]*(len(df_names))
traces4 = [0]*(len(df_names))
artoo = [0]*len(df_names)

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
        x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in x]
        
        traces1[i] = go.Scatter(x = x, y = y, opacity= 0.8, name = str('IHME projected deaths for '+ df_names[i]))
        traces2[i] = go.Scatter(x = cov_x, y = cov_y, opacity = 0.8, name = "COVIDtracker.com recorded deaths")
        traces3[i] = go.Scatter(x = x, y = CI_upper, opacity = 0.2, name = "95% CI", line = dict(dash = 'dash'))
        traces4[i] = go.Scatter(x = x, y = CI_lower, opacity = 0.2, fill = 'tonexty', name = "95% CI", line = dict(dash = 'dash'))


        artoo[i] = r2_score(artoo_y, pred_y).round(4)
        
        

        
        

steps = []
for j in range(len(df_names)):
    step = dict(
        method="restyle",
        args=["visible", [False] * len(df_names)],
    )
    step["args"][1][j] = True  # Toggle i'th trace to "visible"
    steps.append(step)


Date = [dict(
    active = 0,
    currentvalue = {"prefix": "Projection Date: "},
    pad = {"t": 10},
    steps = steps
)]


fig = go.Figure(data = traces1+traces2+traces3+traces4, layout = go.Layout(
    title = dict(text = 'IHME model projection')
))

fig.update_layout(sliders = Date)

fig.show()

fig.write_html("plotly_graph.html")