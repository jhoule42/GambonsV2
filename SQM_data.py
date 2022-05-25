# SQM datas
# Author : Julien-Pierre Houle
# May 2022

import os
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


PATH_SQM = '/home/jhoule42/Documents/Stage/SQM'

# Check for available files
sqm_avail = []

for root, dirs, files in os.walk(f"{PATH_SQM}/All"):
    for file in files:
        if file.startswith("FC_FL") and file.endswith('.dat'):
            sqm_avail.append(os.path.join(root, file))
            

# Copy available files to Filter dir
for file in sqm_avail:
    name = file.split('/')[-1]
    if os.path.exists(f"{PATH_SQM}/Filter/{name}") == False:
        print(f"Copy: {name}")
        shutil.copyfile(file, f"{PATH_SQM}/Filter/{name}")

# Concatenate all times
df = pd.DataFrame()
for file in sqm_avail:
    try:    
        df_SQM = pd.read_csv(file, names=['UTC Time', 'Local Time', 'Temperature (celcius)',
                                          'Counts', 'Freq (Hz)', 'MSAS (mag/arcsec^2)'],
                                          skiprows=35, 
                                          delimiter=';',
                                          parse_dates=[0, 1],
                                          index_col=0 )
        
        df = pd.concat([df, df_SQM], axis=1) # only get the time index
        
    except:
        print(file)
        continue


# Extract time & write to file
time_day = df.index.map(lambda t: t.date()).unique()
time_day = np.array([t.strftime('%Y-%m-%d') for t in time_day])
np.savetxt(f"{PATH_SQM}/data_avail.txt", time_day, fmt='%s')