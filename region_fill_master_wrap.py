#!/usr/bin/env python
# coding: utf-8

# In[12]:


import sunpy.map
import numpy as np
import os
import glob
import time


from scipy.ndimage.measurements import label, find_objects, center_of_mass
from scipy.ndimage.morphology import generate_binary_structure


#Root data dir
data_dir = os.path.abspath("/home/lazar/Fak(s)/AF/prakse/SDSA/data")

#Bitmap folder in data dir and search pattern for bitmaps
#idk if we need this, but whatever
bitmaps = sorted(glob.glob(os.path.join(
    data_dir, "3481_11923_SHARP_CEA_bitmaps/*bitmap*")))

#Intensity images folder and search pattern
cont_list = sorted(glob.glob(os.path.join(
    data_dir, "3481_11923_SHARP_CEA_enhanced_norm/*enhanced_normalized*")))

#Is this messy?
#Search pattern for Br, Bp, Bt in data_dir+magnetic_data_dir
magnetic_data_dir = os.path.join(
    data_dir, "3481_11923_SHARP_CEA_upscaled_magnetic_data")
Br_list = sorted(glob.glob(os.path.join(
    magnetic_data_dir, "*Br*")))
Bp_list = sorted(glob.glob(os.path.join(
    magnetic_data_dir, "*Bp*")))
Bt_list = sorted(glob.glob(os.path.join(
    magnetic_data_dir, "*Bt*")))

#Tree should look something like this
#
#/data_dir/
#├── 3481_11923_SHARP_CEA_bitmaps/SOME_NAME*_bitmap_*.fits
#├── 3481_11923_SHARP_CEA_enhanced_norm/SOME_NAME*__enhanced_normalized__*.fits
#└── 3481_11923_SHARP_CEA_upscaled_magnetic_data/SOME_NAME*__[Br, Bp, Bt]__*.fits
#


# In[47]:


def get_patches_and_vectors(I, bx, by, bz, pixel_limit=20, thr=0.5, floodfill=4):
    '''
    I - intensity map for detecting pores; should be normalized to quiet sun
    bx - bx data (should be Bp from sharps) type should be sunpy map
    by - by data (should be Bt from sharps) type should be sunpy map. DO NOT CHANGE SIGN OF DATA, THIS FUNCTION WILL DO IT!
    bz - bz data (should be Br from sharps) type should be sunpy map
    pixel_limit - ignore patches that are smaller than this size
    thr - if I < thr => we assign it as pixel of interes; if data is normalized, 0.5 should work
    floodfill - in how many direction structure should perform flood fill
    https://en.wikipedia.org/wiki/Flood_fill
    
    floodfill = 4 looks in 4 direction and search structure looks like this
       [[0,1,0],
        [1,1,1],
        [0,1,0]]

    floodfill = 8 looks in 8 direction and search structure looks like this
        [[1,1,1],
         [1,1,1],
         [1,1,1]]
         
    Returns:
    
        This function returns two arrays:
        
        RETURN_MATRIX - Matrix that has data for patches center in dims [5xN] where N is number of patches.
        It is of folowing structure
        c_x[pix], c_y[pix], <Bx>[G], <By>[G], <Bz>[G]
        
        If there is no patches, this matrix is empty
        
        labeled_array - Matrix of same size as input intensity image
        if there are no patches this matrix is filled with zeros
         
    '''
    # Create masked array from I data
    if floodfill == 8:
        print("Using 8 directions search map %s" %(I.name))
        s = generate_binary_structure(2,2)
    else:
        print("Using 4 directions search map on %s" %(I.name))
        s = generate_binary_structure(2,1)
        
    
    X = np.ma.masked_where((I.data <= thr) & (I.data > 0), I.data)
    #LOL!
    #So, if mask is false (nothing satisfies condition), and you use structure in label
    #it will crash because its comparing structure off size [3,3] with 1D array
    #So lets handle it right here
    #And its faster at the end, we are leaving function right here
    if not X.mask.any():
        return np.zeros([]), np.zeros([I.data.shape[1],I.data.shape[0]])
    
    try:
        # sometimes this fails because of endianness
        # Select regions based on structures
        # labeled array is same dimension as input image
        labeled_array, num_features = label(X.mask, structure=s)
    except:
        labeled_array, num_features = label(X.mask.newbyteorder(), structure=s)

  
    # find how many pixel is in each patch
    regions, counts = np.unique(labeled_array, return_counts=True)
            
    # if pixel count for patch is smaller then pixel_limit
    # This labels of patches with small pixel count
    remove_patches = (counts < pixel_limit).nonzero()[0]
    # Set it to zero
    for i in remove_patches:
        labeled_array[labeled_array == i] = 0

    # THIS IS LAZY PROGRAMMING!!! DONT DO THIS!
    # i wanted smooth region labelin (0,1,2,3,4) not gapped (0,1,4,6,7), i could do that manually, but im lazy
    # I cant overwrite labeled_array variable because im using it later in cmass
    labeled_array1, num_features1 = label(labeled_array)
    #print(num_featurues)

    #Check again if we removed all features because of trh for region of interest
    #I tought that we are smarter than nested if/elif/else
    if num_features1 == 0:
        return np.zeros([]), np.zeros([I.data.shape[1],I.data.shape[0]])
      
    #######
    # lets calculate centers of patches
    # Actuall patches are marked as 1 and above, 0 is background
    elif num_features1 == 1:
        features_label = np.array([1])
    else:
        features_label = np.arange(1, num_features1, 1)
    cmass = center_of_mass(labeled_array, labeled_array1, features_label)
    # print(labeled_array)

    # Create placeholder matrix that has
    # cx[pix], cy[pix], <bx>[G], <by>[G], <bz>[G]
    # 
    #because 0 is not feature we are interested in
    #print(num_features1)
    RETURN_MATRIX = np.zeros([num_features1, 5])

    for pore_index in features_label:
        # valid pixels for that pore index over which we should average
        valid_pixels = np.argwhere(labeled_array1 == pore_index)
        # for some reason x is normal here
        RETURN_MATRIX[pore_index - 1][0] = cmass[pore_index-1][0]
        RETURN_MATRIX[pore_index - 1][1] = cmass[pore_index-1][1]
        RETURN_MATRIX[pore_index - 1][2] = np.mean(bx.data[valid_pixels[:, 0], valid_pixels[:, 1]])
        #Note that here we are using -by because Bt = -By
        RETURN_MATRIX[pore_index - 1][3] = np.mean(-by.data[valid_pixels[:, 0], valid_pixels[:, 1]])
        RETURN_MATRIX[pore_index - 1][4] = np.mean(bz.data[valid_pixels[:, 0], valid_pixels[:, 1]])

    return RETURN_MATRIX, labeled_array1

    #, labeled_array1

def touch(path):
    '''
    Create empty file
    '''
    with open(path, 'a'):
        os.utime(path, None)


# In[48]:



#lets make it work first

from multiprocessing import Pool
nproc = 4  # i have 4 cores + hyperthreading (dont want to set my pc on fire)

out_dir_for_patches = os.path.join(data_dir,'patches_dir_test')
#UGLY!!!!!
replace_this = 'enhanced_normalized.fits'
with_this = 'patches.txt'
def parallel_wrap(i):
    I = sunpy.map.Map(cont_list[i])
    #print(I.data.shape)
    bz = sunpy.map.Map(Br_list[i])
    #print(bz.data.shape)
    bx = sunpy.map.Map(Bp_list[i])
    #print(bx.data.shape)
    by = sunpy.map.Map(Bt_list[i])
    #print(by.data.shape)
    save_matrix, _ = get_patches_and_vectors(I, bx, by, bz)
    outfile = os.path.basename(cont_list[i]).replace(
        replace_this, with_this)
    ofile = os.path.join(out_dir_for_patches, outfile)
    if save_matrix.size == 1:# == None:
        touch(ofile)
        return
    #    continue
    np.savetxt(ofile, save_matrix)
    return


if __name__ == '__main__':
    p = Pool(nproc)
    start = time.time()
    p.map(parallel_wrap, np.arange(len(cont_list)))
    end = time.time()
    print(end - start)

