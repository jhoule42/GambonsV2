# Find available SAND data
# Author : Julien-Pierre Houle
# May 2022


import os
import os.path
import shutil
import numpy as np
from scipy import integrate
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit



PATH_SAND = '/home/jhoule42/Documents/Stage/SAND/All'
PATH_FILTER = "/home/jhoule42/Documents/Stage/SAND/Filter"


# Check for available files
spectra_files = []

for root, dirs, files in os.walk(PATH_SAND):
    for file in files:
        if file.endswith("sp_cs_cp_re.cxy"):
            spectra_files.append(os.path.join(root, file))
            

# Check for valid spectra
to_remove = []
for file in spectra_files:
    wl, values = np.loadtxt(file).T
    hist, bin_edges = np.histogram(values, bins=100)
    
    if hist.max() > 200: # constants values
        to_remove.append(file)
        
    if len(values[values == 0]) > 50: # to  many zeros values
        if file not in to_remove:
            to_remove.append(file)

spectra_files = [f for f in spectra_files if f not in to_remove]


# Copy to 'Filter' dir
for file in spectra_files:
    f = file.split('/')[-1]
    if os.path.exists(f"{PATH_FILTER}/{f}") == False:
        print(f"Copy: {f}")
        shutil.copyfile(file, f"{PATH_FILTER}/{f}")




# Remove background contributions
def gauss(x, a, x0, sigma):
    return a * np.exp(-(x - x0)**2 / (2 * sigma**2))


time = '2016-07-07'  # get files from a certain date
files = [f for f in os.listdir(PATH_FILTER) if time in f][0]

# airglow_wl = [557, 630, 636]
# for i in airglow_wl:
# for file in spectra_files:
wl, vals = np.loadtxt(f"{PATH_FILTER}/{files}").T

i = 557
mask = (wl >= i-3) & (wl <= i+3)
x, y = wl[mask], vals[mask]
sigma = np.sqrt(sum(y * (x - i)**2) / sum(y))
x_fit = np.linspace(i-2, i+2, 100)

try:
    params, pcov = curve_fit(gauss, x, y, p0=[max(y), i, sigma])
    plt.plot(x_fit, gauss(x_fit, *params), 'r-', label='fit')
except:
    print('Error fitting wl:',i)
    

plt.plot(wl, vals, 'b+:', label='data')
plt.legend()
# plt.xlim(475, 675)
plt.xlim(550, 570)
plt.xlabel('Wavelength (nm)')
plt.show()
        
# # Integrate Flux
# cste = (y[0] + y[-1]) / 2
# Int_corr = cste * (x[-1] - x[0])  # correction of the constant  
# I, err = integrate.quad(gauss, 555, 560, args=(params[0], params[1], params[2]))
# flux = I - Int_corr






# Produce file of all the nights with datas
times = []
for file in os.listdir(PATH_FILTER):
    f = file.split('_')
    times.append(f[5]+' '+f[6])
times = sorted(times)
np.savetxt('/home/jhoule42/Documents/Stage/SAND/data_avail.txt', np.array(times), fmt='%s')


# ----------------------------------------------------


# PLOT VALID SPECTRA
wl, values = np.loadtxt(spectra_files[300]).T
plt.figure()
plt.plot(wl, values)
plt.xlabel('Wavelength')
plt.ylabel('Flux')
plt.savefig('Figures/SAND/good_spectra_6')


# PLOT INVALID SPECTRA
wl, values = np.loadtxt(to_remove[1500]).T
plt.figure()
plt.plot(wl, values)
plt.xlabel('Wavelength')
plt.ylabel('Flux')
plt.savefig('Figures/SAND/bad_spectra_5')