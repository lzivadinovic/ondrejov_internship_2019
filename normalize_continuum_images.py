#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import os
import glob
import sunpy.map

NBINS = 100

folder_path = os.path.abspath(
    '/home/lazar/Fak(s)/AF/prakse/SDSA/data/3481_11923_SHARP_CEA_ld_removed')
new_folder_path = os.path.abspath(
    '/home/lazar/Fak(s)/AF/prakse/SDSA/data/3481_11923_SHARP_CEA_normalized')


# In[ ]:


search_criterium = "continuum_ld_removed"
sufix = "_normalized"

data_list = sorted(glob.glob(os.path.join(
    folder_path, "*"+search_criterium+"*")))


# In[ ]:


def wraper_func(filename):
    # load sunpy map
    I = sunpy.map.Map(filename)
    # create histogram out of data
    # density is normalization flag
    weights, bin_edges = np.histogram(
        I.data.flatten(), bins=NBINS, density=True)
    # MAGIC I SAY!
    # find maximum of histogram
    k = (weights == np.max(weights)).nonzero()[0][0]
    # find flux value for maximum of histogram
    I_avg = (bin_edges[k+1]+bin_edges[k])/2
    # update data
    I_new = I.data/I_avg
    # create new keyword in header
    I.meta['AVG_F_ON'] = I_avg
    # create new map
    new_map = sunpy.map.Map(I_new, I.meta)
    new_name = os.path.basename(filename).replace(
        search_criterium, search_criterium+sufix)
    # save map
    new_map.save(os.path.join(new_folder_path, new_name))


# In[ ]:


from multiprocessing import Pool
nproc = 4  # i have 4 cores + hyperthreading

if __name__ == '__main__':
    p = Pool(nproc)
    p.map(wraper_func, data_list)

