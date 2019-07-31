#!/usr/bin/env python
# coding: utf-8

# # Remove limb darkening for whole dataset
# For detailed instruction see limb_darkening notebook with more detailed instruction for every step, this is only "wraper" around that notebook, written more pythonic and scalable

# In[1]:


import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits as pf
import os
import glob

coef_limb_6205 = np.array(
    [0.32519, 1.26432, -1.44591, 1.55723, -0.87415, 0.173333])

def limb_dark(r, koef=coef_limb_6205):
    # r is normalized distance from center [0,1]
    if len(koef) != 6:
        raise ValueErrror("koef len should be exactly 6")
    if np.max(r) > 1 or np.min(r) < 0:
        raise ValueError("r should be in [0,1] range") 
    mu = np.sqrt(1-r**2) # mu = cos(theta)
    return koef[0]+koef[1]*mu+koef[2]*mu**2+koef[3]*mu**3+koef[4]*mu**4+koef[5]*mu**5

data_dir_CEA = os.path.abspath(
    "/home/lazar/Fak(s)/AF/prakse/SDSA/data/3481_11923_SHARP_CEA")

data_dir_new = os.path.abspath(
    "/home/lazar/Fak(s)/AF/prakse/SDSA/data/3481_11923_SHARP_CEA_ld_removed")

search_criterium = "continuum"
sufix = "_ld_removed"

data_list_CEA = sorted(glob.glob(os.path.join(data_dir_CEA, "*"+search_criterium+"*")))

#Use this to extract folder name so you can change it later when outputing images
#os.path.dirname(data_list_CEA[1])

#use replace to change search_criterum with sc+sufix, it works ok
#print(data_list_CEA[1].replace(search_criterium, search_criterium+sufix))


# In[1]:


import sunpy.map
import sunpy.coordinates.transformations
from sunpy.coordinates import frames


# In[2]:


def correct_for_limb(sunpy_map):
    #transform coordinates for map
    #If there is no observer_coordinate it will use earth coordinates
    #This is ok for SDO
    helioproj_limb = sunpy.map.all_coordinates_from_map(sunpy_map).transform_to(
    frames.Helioprojective(observer=sunpy_map.observer_coordinate))
    #extract sun radii in arcsec calculated by HMI
    #If value does not exists in header, use solar radii obs_date as seen from earth
    rsun_hp_limb = sunpy_map.rsun_obs.value
    #Calculate distance for every pixel 
    distance_from_limb = np.sqrt(
    helioproj_limb.Tx.value**2+helioproj_limb.Ty.value**2)/rsun_hp_limb

    limb_cor_data = sunpy_map.data / limb_dark(distance_from_limb)
    
    return sunpy.map.Map(limb_cor_data, sunpy_map.meta)


# In[ ]:


from multiprocessing import Pool
nproc = 8 #i have 4 cores + hyperthreading

#lets create wraper function for loading data into map and saving it
#this is type void function (idl procedure) because i want to save everything from here
#not to relay on return values from p.map

def wraper_func(filename):
    my_map = sunpy.map.Map(filename)
    my_corrected_map = correct_for_limb(my_map)
    new_name = os.path.basename(filename).replace(search_criterium, search_criterium+sufix)
    my_corrected_map.save(os.path.join(data_dir_new, new_name))
    

if __name__ == '__main__':
    p = Pool(nrpoc)
    p.map(wraper_func, data_list_CEA)

