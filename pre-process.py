import pandas as pd 
import os as os 
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

rootdir_os = 'C:\\Users\\chris.mclean\\Documents\\Python Scripts\\COVID analysis\\IHME_projections\\Unzipped'
rootdir_p = Path(r'C:\Users\chris.mclean\Documents\Python Scripts\COVID analysis\IHME_projections\Unzipped')

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



x = dfs[df_names[-1]]['date'].unique()
x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in x]

fig, ax = plt.subplots()
ax.plot(x, dfs[df_names[-1]].groupby(['date'])['deaths_mean'].sum(), linestyle = '-.')
ax.fill_between(x, dfs[df_names[-1]].groupby(['date'])['deaths_upper'].sum(), \
    dfs[df_names[-1]].groupby(['date'])['deaths_lower'].sum(), alpha = 0.2)

plt.title(str('IHME Prediction vs. Reality as of '+ df_names[-1][3:]))

plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=14))
fig.autofmt_xdate()

plt.show()

