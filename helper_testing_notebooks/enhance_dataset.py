#!/usr/bin/env python
# coding: utf-8

# # For this to work, you need to put this .py script into enhance folder
# 
# Their naming and refferences are messed up, and they didn't create importable code, just some wrapper around model
# 
# There is no need to run in parallel because tensorflow does this automatically per image, so you will only slow your PC until it dies

# In[ ]:


from enhance import enhance
import os
import glob

#Dir with normalized dataset
data_dir_CEA = os.path.abspath(
    "/home/lazar/Fak(s)/AF/prakse/SDSA/enhance/3481_11923_SHARP_CEA_normalized")
# hmi.sharp_cea_720s.3481.20131218_161200_TAI.continuum_ld_removed_normalized.fits
search_criterium = "normalized" #Bp, Bt
sufix = "_enhanced"
data_list = sorted(glob.glob(os.path.join(
    data_dir_CEA, "*"+search_criterium+"*")))

#outdir

data_output_dir = os.path.abspath(
    "/home/lazar/Fak(s)/AF/prakse/SDSA/enhance/3481_11923_SHARP_CEA_enhanced")


# In[ ]:


#these are default values as provided when you run
#./enhance.py -i input.fits -t intensity -o out.fits

depth = 5
model = "keepsize"
activation = "relu"
ntype = "intensity"

def wraper_func(filename):
    outfile = os.path.basename(filename).replace(search_criterium, search_criterium+sufix)
    ofile = os.path.join(data_output_dir, outfile)
    out = enhance(inputFile=filename, depth=depth, model=model, activation=activation,ntype=ntype, output=ofile)
    out.define_network()
    out.predict()

for i in data_list:
    print(i)
    wraper_func(i)

