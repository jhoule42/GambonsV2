# Find when the data is available to run Gambons
# Author : Julien-Pierre Houle
# Mai 2022

import os
import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
import subprocess
from astropy.coordinates import get_moon, EarthLocation
from astroplan import Observer
import astropy.time
import matplotlib.pyplot as plt
from datetimerange import DateTimeRange
from src.astrotimes_filter import filter_astrotimes


# PARAMETERS
AOD_PATH  = '/home/jhoule42/Documents/Stage/AERONET/AOD/AOD20'
SQM_PATH  = '/home/jhoule42/Documents/Stage/SQM'
SAND_PATH = '/home/jhoule42/Documents/Stage/SAND/Filter'
PROJECT_PATH = '/home/jhoule42/Documents/Stage'

start, end = '2016-01-02 12:00:00', '2016-02-03 12:00:00'
SQM_resample = 60  # keep data every n minutes


# Get availability of all datas
df_avail = pd.read_csv(f'{PROJECT_PATH}/date_avail_all.txt',names=['Time'])


# READ AERONET DATA
df_AOD = pd.read_csv(f'{AOD_PATH}/ALL_POINTS/20110101_20211231_Montsec.lev20',\
                     skiprows=6,  encoding='latin-1')

df_AOD.index = pd.to_datetime(df_AOD["Date(dd:mm:yyyy)"]+' '+df_AOD["Time(hh:mm:ss)"],
                              format='%d:%m:%Y %H:%M:%S')

# Diff previous & next datas
df_AOD['prev_timediff'] = df_AOD.index.to_series().diff().fillna(pd.Timedelta(0))
df_AOD['next_timediff'] = df_AOD.index.to_series().diff(-1).fillna(pd.Timedelta(0))

idx_miss_prev = df_AOD['prev_timediff'].loc[df_AOD['prev_timediff'] > timedelta(days=5)].index
idx_miss_next = df_AOD['next_timediff'].loc[df_AOD['next_timediff'] < timedelta(days=-5)].index
# df_AOD = df_AOD.drop(index_missing_data) # delete rows with big time difference
# df_AOD.loc[start:end] # filter time



# READ ALL SQM DATAS
df_SQM = pd.DataFrame()
for file in os.listdir(f"{SQM_PATH}/Filter"):   

    df = pd.read_csv(f"{SQM_PATH}/Filter/{file}",
                    names=['UTC Time', 'Local Time', 'Temperature (celcius)', 'Counts',
                             'Freq (Hz)', 'MSAS (mag/arcsec^2)'],
                    skiprows=35,  delimiter=';', parse_dates=True, index_col=1 )
    df_SQM = pd.concat([df_SQM, df])

df_SQM.index = pd.to_datetime(df_SQM.index, errors='coerce')
df_SQM = df_SQM.drop_duplicates(keep='last').sort_index().dropna()

df_SQM = filter_astrotimes(df_SQM, PROJECT_PATH) # filter astronomical times


# Select the data for all the corresponding day
df_SQM2 = pd.DataFrame()
for d in df_avail['Time'].values:
        
    t1 = pd.to_datetime(d) + datetime.timedelta(hours=12)
    t2 = t1 + datetime.timedelta(days=1)
    df = df_SQM[t1:t2]
    df_SQM2 = pd.concat([df_SQM2, df])
    
df_SQM2 = df_SQM2.sort_index()

df_SQM = df_SQM2.resample(f'{SQM_resample}min').mean() # keep data every SQM_resample min
df_SQM = df_SQM.dropna(subset=['MSAS (mag/arcsec^2)'])
df_SQM = df_SQM[start:end]


# # GET SAND DATA
# time_range = DateTimeRange(start, end)
# time_range = [t.strftime("%Y-%m-%d") for t in list(time_range.range(timedelta(days=1)))]
# files_SAND = [f for f in os.listdir(SAND_PATH) if f.split('_')[5] in df_SQM['Date'].values]




    

# RUNNING GAMBONS
times = df_SQM.index.values

N = len(times)
MAG_SQM = np.zeros(N)

for i, t in enumerate(times):
    t = np.datetime_as_string(t, unit='s')
    print(t)    

    process = subprocess.Popen(['java', '-jar', 'Gambons.jar',
                                '-time', t,
                                '-ow','true', 
                                '-ind','true',
                                '-map','false',
                                '-verbose','false'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = process.communicate()[0].decode('utf-8').split('\n')[1:-1]
    r_split = [r.split(': ') for r in result]

    # Extract results from string
    MAG_SQM[i] = float(r_split[0][1])
    

# OUTPUT comparaisons Gambons & Montsec datas
location = EarthLocation.from_geodetic(0.729677, 42.051669, 1560)
observer = Observer(location=location, name='Montsec')

sun_height, moon_height = np.zeros(N), np.zeros(N)

for i, t in enumerate(times):
    time = astropy.time.Time(t)
    moon_height[i] = get_moon(time, location).dec.deg
    sun_height[i] = observer.sun_altaz(time).alt.deg

df_AERONET = pd.DataFrame({'SQM_model': MAG_SQM,
                          'SQM_Data' : df_SQM['MSAS (mag/arcsec^2)'].values,
                          'Delta_SQM': abs(MAG_SQM - df_SQM['MSAS (mag/arcsec^2)'].values),
                          'Sun_height': sun_height,
                          'Moon_height': moon_height}, index=times)



df_OPAC = pd.read_csv("/home/jhoule42/Documents/Stage/src/test.csv", parse_dates=True,
                        index_col=0)



# PLOT MODEL & DATA COMPARAISONS
plt.figure()
plt.scatter(df_OPAC.index, df_OPAC['SQM_model'].values, label='Gambons')
plt.scatter(df_AERONET.index, df_AERONET['SQM_model'].values, label='Gambons')
plt.scatter(df_AERONET.index, df_AERONET['SQM_Data'].values,  label='Data')
plt.legend()
plt.xlabel('Time')
plt.ylabel('MSAS (mag/arcsec^2)')
plt.title('AERONET')
plt.ylim(19, 24)
plt.show()
# plt.savefig(f"{PROJECT_PATH}/Figures/Gambons_OPAC")
# plt.close()



# # SQM PLOT
# df1_SQM =  df_SQM.loc['2021-10-1 12:00:00':'2021-12-8 12:00:00']
# # df1_SQM =  df_SQM.loc[start:end]

# plt.figure()
# plt.plot(df1_SQM.index, df1_SQM['MSAS (mag/arcsec^2)'].values, label='SQM')
# plt.legend()
# plt.xlabel('Time')
# plt.ylabel('MSAS (mag/arcsec^2)')
# plt.savefig(f"{PROJECT_PATH}/Figures/sqm_data")
# plt.show()
# plt.close()


