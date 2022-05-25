# Produce a graph to show when all the datas are available at the same moment
# Author : Julien-Pierre Houle
# May 2022


import matplotlib
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


AOD_PATH = '/home/jhoule42/Documents/Stage/AERONET/AOD/AOD20'
PROJECT_PATH = '/home/jhoule42/Documents/Stage'

start_date = datetime(2012, 1, 1)
end_date   = datetime(2022, 1, 1)

time_range = pd.date_range(start_date, end_date-timedelta(days=1), freq='d')
time_range_str = [d.strftime('%Y-%m-%d') for d in time_range]


# READ AERONET DATA
df_AOD = pd.read_csv(f'{AOD_PATH}/ALL_POINTS/20110101_20211231_Montsec.lev20',
                     skiprows=6,  encoding='latin-1')

df_AOD.index = pd.to_datetime(df_AOD["Date(dd:mm:yyyy)"]+' '+df_AOD["Time(hh:mm:ss)"],
                              format='%d:%m:%Y %H:%M:%S')
AOD_unique_date = df_AOD.index.map(pd.Timestamp.date).unique().tolist()
AOD_unique_date = [d.strftime('%Y-%m-%d') for d in AOD_unique_date]


# READ SQM DATA AVAILABILITY
df_SQM = pd.read_csv(f"{PROJECT_PATH}/SQM/data_avail.txt", parse_dates=True, index_col=0)
SQM_unique_date = df_SQM.index.map(pd.Timestamp.date).unique().tolist()
SQM_unique_date = [d.strftime('%Y-%m-%d') for d in SQM_unique_date]

# READ SAND AVAILABILITY
df_SAND = pd.read_csv("/home/jhoule42/Documents/Stage/SAND/data_avail.txt",
                      names=['Time'], parse_dates=True, index_col=0)
SAND_unique_date = df_SAND.index.map(pd.Timestamp.date).unique().tolist()
SAND_unique_date = [d.strftime('%Y-%m-%d') for d in SAND_unique_date]


# LOOK FOR CORRESPONDING DATES
mask_AOD = np.ones(len(time_range))*-1
mask_SQM = np.ones(len(time_range))*-1
mask_SAND = np.ones(len(time_range))*-1
mask_ALL = np.ones(len(time_range))*-1


for idx, date in enumerate(time_range_str):    
    if date in AOD_unique_date:
        mask_AOD[idx] = 4
        
    if date in SQM_unique_date:
        mask_SQM[idx] = 3

    if date in SAND_unique_date:
        mask_SAND[idx] = 2
        
    if (date in SAND_unique_date) and (date in SQM_unique_date) \
        and (date in AOD_unique_date):
        mask_ALL[idx] = 1


mask_ALL[mask_ALL == -1] = 0
mask_ALL = np.array(mask_ALL, dtype=bool)
date_avail = np.array(time_range_str)[mask_ALL]

# Write data availability to file
np.savetxt(f'{PROJECT_PATH}/date_avail_all.txt', date_avail, fmt='%s')


# PLOTTING FIGURE
plt.figure(figsize=(7, 4))
ax = plt.gca()
l = [1, 2, 3, 4]
y_ticks = ['ALL', 'SAND', 'SQM', 'AERONET']
ax.set_yticks(l)
ax.set_yticklabels(y_ticks)

plt.scatter(time_range, mask_AOD, label='AERONET', marker='s', s=22)
plt.scatter(time_range, mask_SQM, label='SQM', marker='s', s=15)
plt.scatter(time_range, mask_SAND, label='SAND', marker='s', s=15)
plt.scatter(time_range, mask_ALL, label='ALL', marker='s', s=15)
plt.xlabel('Time')
plt.ylim(0)
plt.savefig(f"{PROJECT_PATH}/Figures/data_availability")