# Find when we have cloud free nights
# Author : Julien-Pierre Houle
# May 2022

import os
import numpy as np
import pandas as pd
from src.sun_and_moon_filter import *


PATH_CLOUD = '/home/jhoule42/Documents/Stage/CLOUD'
PROJECT_PATH = '/home/jhoule42/Documents/Stage'


df_cloud = pd.DataFrame()
for file in os.listdir(PATH_CLOUD):  
    print(file)  
    # file = os.listdir(PATH_CLOUD)[0]
    df = pd.read_csv(f"{PATH_CLOUD}/{file}", parse_dates=True, index_col=0,
                        skiprows=1, names=['time', 'temp_diff'])

    df_cloud = pd.concat([df_cloud, df])
df_cloud = df_cloud.sort_index()

df_cloud = filter_astrotimes(df_cloud, PROJECT_PATH, avg_night=True)


# Check for temp_diff < -30 (no cloud)
nights_cloud_free =  df_cloud[df_cloud['temp_diff'] < -30].index
nights_cloud_free = nights_cloud_free.strftime('%Y/%m/%d').values # convert to string
np.savetxt(f'{PATH_CLOUD}/nights_cloud_free', nights_cloud_free, fmt='%s')