import pandas as pd 
import os as os 
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

rootdir_os = 'C:\\Users\\chris.mclean\\Documents\\Python Scripts\\COVID analysis\\IHME_projections\\Unzipped'
rootdir_p = Path(r'C:\Users\chris.mclean\Documents\Python Scripts\COVID analysis\IHME_projections\Unzipped')

CDCdf = pd.read_csv('C:/Users/chris.mclean\Documents/Python Scripts/COVID analysis/CDC_data/Provisional_Death_Counts_for_Coronavirus_Disease__COVID-19_.csv')

weekending_dat = CDCdf[CDCdf['Indicator'] == 'Week-ending']
y_weekending_dat = weekending_dat['All COVID-19 Deaths (U07.1)']
x_weekending_dat = weekending_dat['Start week']
vals = []
x_dates = []

for i in (range(2, len(x_weekending_dat) + 1)):
    print(i)
    # if (i < (len(x_weekending_dat)-1)):
    stop = pd.to_datetime(x_weekending_dat[i])
    delt = pd.to_timedelta(7, unit='d')
    start = stop - delt
    date_holder = pd.date_range(start, stop)
    vals[7*(i-1):(7*i)-1] = [float(y_weekending_dat[i].replace(',', ''))/7]*7
    x_dates.append(date_holder)
    # elif (i == (len(x_weekending_dat))):
    #     print('hi')

new_x = pd.date_range(x_dates[0][1], x_dates[-1][-1])

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


fig, ax = plt.subplots()
ax.plot(x, df.groupby(['date'])['deaths_mean'].sum(), linestyle = '-.')
ax.fill_between(x, df.groupby(['date'])['deaths_upper'].sum(), \
    df.groupby(['date'])['deaths_lower'].sum(), alpha = 0.2)
ax.plot(new_x, vals, linestyle = '-', alpha = 0.8)

plt.title(str('IHME Prediction vs. CDC Recorded COVID-19 Deaths as of '+ df_names[-1][3:]))

plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=14))
fig.autofmt_xdate()
ax.legend(['IHME predicted COVID deaths', 'CDC recorded COVID deaths'])

plt.show()

