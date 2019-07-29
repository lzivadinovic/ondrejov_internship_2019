#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sunpy.map
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits as pf
import astropy.units as u
import os
import glob
# This makes nice big plots for matplotlib
import matplotlib as mpl
params = {'font.size': 14,
          'figure.figsize': (15.0, 8.0),
          'lines.linewidth': 2.,
          'lines.markersize': 15,
          'animation.embed_limit': 2048,
          }
mpl.rcParams.keys()
mpl.rcParams.update(params)
np.set_printoptions(suppress=True)

#Replace this for dataset
data_dir_CEA = os.path.abspath(
    "/home/lazar/Fak(s)/AF/prakse/SDSA/data/3481_11923_SHARP_CEA")

data_output_dir = os.path.abspath(
    "/home/lazar/Fak(s)/AF/prakse/SDSA/data/3481_11923_SHARP_CEA_upscaled_magnetic_data")
#search_criterium = "continuum"
#sufix = "_ld_removed"

#data_list_CEA = sorted(glob.glob(os.path.join(
#    data_dir_CEA, "*"+search_criterium+"*")))


# In[4]:


search_criterium = "Br" #Bp, Bt
sufix = "_upscaled"
data_br = sorted(glob.glob(os.path.join(
    data_dir_CEA, "*"+search_criterium+"*")))

#filename = data_br[0]
#new_name = os.path.basename(filename).replace(search_criterium, search_criterium+sufix)
#print(filename)
#print(new_name)
#print(len(data_br))
#hmi.sharp_cea_720s.3481.20131208_111200_TAI.Bp.fits
#hmi.sharp_cea_720s.3481.20131208_111200_TAI.Br.fits
#hmi.sharp_cea_720s.3481.20131208_111200_TAI.Bt.fits


# In[ ]:


from multiprocessing import Pool
nproc = 4  # i have 4 cores + hyperthreading

# lets create wraper function for loading data into map and saving it
# this is type void function (idl procedure) because i want to save everything from here
# not to relay on return values from p.map


def wraper_func(filename):
    my_map = sunpy.map.Map(filename)
    new_dimension = u.Quantity([my_map.meta["naxis1"]*2, my_map.meta["naxis2"]*2], u.pixel)
    my_corrected_map = my_map.resample(new_dimension, method='spline')
    new_name = os.path.basename(filename).replace(search_criterium, search_criterium+sufix)
    my_corrected_map.save(os.path.join(data_output_dir, new_name))


if __name__ == '__main__':
    p = Pool(nproc)
    p.map(wraper_func, data_br)

