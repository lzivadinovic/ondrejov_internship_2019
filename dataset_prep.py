#!/usr/bin/env python
# coding: utf-8
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
import sunpy.map
from astropy import units as u
import sunpy.coordinates.transformations
from sunpy.coordinates import frames

from enhance import enhance


input_dir = os.path.abspath(
    "/home/lazar/Fak(s)/AF/prakse/SDSA/enhance/3481_11923_SHARP_CEA")
search_criterium = "continuum"
sufix = "_reduced"
data_list = sorted(glob.glob(os.path.join(
    input_dir, "*"+search_criterium+"*")))
# outdir
output_dir = os.path.abspath(
    "/home/lazar/Fak(s)/AF/prakse/SDSA/enhance/3481_11923_SHARP_CEA_enhanced")



# Create array for holding limb darkening coef
# 6205.90 A
coef_limb_hmi = np.array(
    [0.32519, 1.26432, -1.44591, 1.55723, -0.87415, 0.173333])


def limb_dark(r, koef=coef_limb_hmi):
    # r is normalized distance from center [0,1]
    if len(koef) != 6:
        raise ValueErrror("koef len should be exactly 6")
    if np.max(r) > 1 or np.min(r) < 0:
        raise ValueError("r should be in [0,1] range")
    mu = np.sqrt(1-r**2)  # mu = cos(theta)
    return koef[0]+koef[1]*mu+koef[2]*mu**2+koef[3]*mu**3+koef[4]*mu**4+koef[5]*mu**5


def correct_for_limb(sunpy_map):
    '''
    This function takes sunpy map and removes limb darkening from it
    It transfer coordinate mesh to helioprojective coordinate (using data from header)
    Calucalates distance from sun center in units of sun radii at the time of observation
    Uses limb_dark function with given coeffitiens and divides by that value

    Input: sunpy_map (sunpy.map) - input data
    Returns: sunpy.map - output data object
    '''
    helioproj_limb = sunpy.map.all_coordinates_from_map(sunpy_map).transform_to(
        frames.Helioprojective(observer=sunpy_map.observer_coordinate))
    rsun_hp_limb = sunpy_map.rsun_obs.value
    distance_from_limb = np.sqrt(
        helioproj_limb.Tx.value**2+helioproj_limb.Ty.value**2)/rsun_hp_limb
    limb_cor_data = sunpy_map.data / limb_dark(distance_from_limb)
    return sunpy.map.Map(limb_cor_data, sunpy_map.meta)



# AVERAGE
def normalize(sunpy_map, header_keyword='AVG_F_NO', NBINS=100):
    '''
    This function normalizes sunpy map
    It first creates histogram of data
    Finds maximum of histogram and divide whole dataset with that number
    This is efectevly normalization to quiet sun

    input:  sunpy_map (sunpy.map) - input data
            header_keyword (string) - name of header keyword in which maximum of histogram will be written to 
                                      This allows users to later on, revert to unnormalized image, default is AVG_F_NO
            NBINS (int) - How many bins you want for your histogram, default is 100
    output: sunpy.map - output data object
    '''
    weights, bin_edges = np.histogram(
        sunpy_map.data.flatten(), bins=NBINS, density=True)
    # MAGIC I SAY!
    # find maximum of histogram
    k = (weights == np.max(weights)).nonzero()[0][0]
    # find flux value for maximum of histogram
    I_avg = (bin_edges[k+1]+bin_edges[k])/2
    # update data
    I_new = sunpy_map.data/I_avg
    # create new keyword in header
    # AVG_F_ON
    # AVG_F_EN
    sunpy_map.meta[header_keyword] = I_avg
    # create new map
    return sunpy.map.Map(I_new, sunpy_map.meta)



def enhance_wrapper(sunpy_map, depth=5, model="keepsize", activation="relu", ntype="intensity"):
    '''
    This procedures run enhance https://github.com/cdiazbas/enhance (it works only from my fork https://github.com/lzivadinovic/enhance)
    on input sunpy map
    Check source code for explanation of code and input parameters

    input: sunpy_map (sunpy.map) - input data set
    output: sunpy.map - output data object (enhanced)
    '''
    # if rtype is spmap, there is no need for output, it will return sunpy.map object (lzivadinovic/enhance fork - master branch)
    out = enhance(inputFile=sunpy_map, depth=depth, model=model,
                  activation=activation, ntype=ntype, output='1.fits', rtype='spmap')
    out.define_network()
    return out.predict()


def master_wrap(filename):
    '''
    This function is just simple wrapper for all privided functions
    
    input: filename (string) -  fits file path that correction shoud be performed on
    output: ofile (string) - string with path to new file
    '''
    # load data
    sunpy_data = sunpy.map.Map(filename)
    # correct map for limb
    mid_data = correct_for_limb(sunpy_data)
    # Normalize
    mid_data = normalize(mid_data, header_keyword='AVG_F_ON')
    # enhance
    mid_data = enhance_wrapper(mid_data)
    # normalize again, enhance can make mess with flux
    mid_data = normalize(mid_data, header_keyword='AVG_F_EN')
    # Create new filename
    outfile = os.path.basename(filename).replace(
        search_criterium, search_criterium+sufix)
    ofile = os.path.join(output_dir, outfile)
    # save map
    mid_data.save(ofile)
    return ofile

# if you want to go crazy, you can do
#normalize(enhance_wrapper(normalize(correct_for_limb(sunpy_data), header_keyword='AVG_F_ON')), header_keyword='AVG_F_EN').save(some_filename)
# :D


if __name__ == '__main__':
    for i in data_list:
        master_wrap(i)
