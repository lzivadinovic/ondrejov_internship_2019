#!/usr/bin/env python

import sunpy.map
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits as pf
import astropy.units as u
import os
import glob
#Replace this for dataset
data_dir_CEA = os.path.abspath(
    "/home/lazar/Fak(s)/AF/prakse/SDSA/data/3481_11923_SHARP_CEA")
data_output_dir = os.path.abspath(
    "/home/lazar/Fak(s)/AF/prakse/SDSA/data/3481_11923_SHARP_CEA_upscaled_magnetic_data")
search_criterium = ["Br", "Bp", "Bt"]
sufix = "_upscaled"
interp_method = "spline"


from multiprocessing import Pool
nproc = 4  # i have 4 cores + hyperthreading

# lets create wraper function for loading data into map and saving it
# this is type void function (idl procedure) because i want to save everything from here
# not to relay on return values from p.map


def wraper_func(filename):
    my_map = sunpy.map.Map(filename)
    new_dimension = u.Quantity([my_map.meta["naxis1"]*2, my_map.meta["naxis2"]*2], u.pixel)
    my_corrected_map = my_map.resample(new_dimension, method=interp_method)
    my_corrected_map.meta["naxis1"] *= 2
    my_corrected_map.meta["naxis2"] *= 2
    new_name = os.path.basename(filename).replace(prefix, prefix+sufix)
    my_corrected_map.save(os.path.join(data_output_dir, new_name))


if __name__ == '__main__':
    for prefix in search_criterium:
        data_list = sorted(glob.glob(os.path.join(data_dir_CEA, "*"+prefix+"*")))
        p = Pool(nproc)
        p.map(wraper_func, data_list)
