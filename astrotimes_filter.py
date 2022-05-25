# Filter data according to sun and moon positions
# Author : Julien-Pierre Houle
# Mai 2022

import numpy as np
import astropy.time
from astropy.coordinates import get_moon, EarthLocation
from astroplan import Observer
from astropy import units
from datetime import datetime, timedelta
import pandas as pd


# start_date = datetime(2012, 1, 1)
# end_date   = datetime(2022, 1, 1)

# timestamp = pd.date_range(start_date, end_date-timedelta(days=1), freq='d').tolist()
# dates = [date_obj.strftime('%Y-%m-%d 00:00') for date_obj in timestamp] # list of dates in the interval

# sunset,  sunrise  = {}, {}
# moonset, moonrise = {}, {}

# location = EarthLocation.from_geodetic(0.729677, 42.051669, 1560)
# observer = Observer(location=location, name='Montsec')

# for i, d in enumerate(dates):

#     time = astropy.time.Time(d)
#     t = get_moon(time, location)

#     sunset.update({ d:  observer.sun_set_time(time, which='nearest',  horizon=units.deg*-18).iso }) 
#     sunrise.update({ d: observer.sun_rise_time(time, which='nearest', horizon=units.deg*-18).iso })

#     moonset.update({  d: observer.moon_set_time(time,  which='nearest', horizon=units.deg*-12).iso })
#     moonrise.update({ d: observer.moon_rise_time(time, which='nearest', horizon=units.deg*-12).iso })


# # Save data to CSV
# data = { 'sunset'  : list(sunset.values()),
#          'sunrise' : list(sunrise.values()),
#          'moonset' : list(moonset.values()),
#          'moonrise': list(moonrise.values()) }

# df = pd.DataFrame(data, index=dates)
# df.to_csv('sun_&_moon.txt')



# Filter astronomical times
def filter_astrotimes(df, PROJECT_PATH, avg_night=False):
        
    df_astrotime = pd.read_csv(f'{PROJECT_PATH}/sun_&_moon.txt', index_col=0, parse_dates=True)
    df_astrotime['start'] = df_astrotime[["sunset",  "moonset"]].max(axis=1)
    df_astrotime['end']   = df_astrotime[["sunrise", "moonrise"]].min(axis=1)
    df_astrotime = df_astrotime[df_astrotime['end'] != '--']
    
    start, end = df.index[0], df.index[-1]
    df_astrotime = df_astrotime.loc[start:end]


    df_all = pd.DataFrame()
    for i in df_astrotime.index:
        start_night = df_astrotime['start'].loc[i]
        end_night   = df_astrotime['end'].loc[i]
        
        df_tmp = df.loc[start_night:end_night]
        
        if avg_night:
            df_tmp = df_tmp.resample('2d').mean()  # return first date      
        
        df_all = pd.concat([df_all, df_tmp])

    return df_all