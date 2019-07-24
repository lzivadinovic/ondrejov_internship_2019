#!/usr/bin/env python
# coding: utf-8

# In[54]:


import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits as pf
import os
import glob
# This makes nice big plots 
import matplotlib as mpl
params = {'font.size'     : 14,
          'figure.figsize':(15.0, 8.0),
          'lines.linewidth': 2.,
          'lines.markersize': 15,
          'animation.embed_limit': 2048,}
mpl.rcParams.keys()
mpl.rcParams.update(params)
np.set_printoptions(suppress=True)



# In[78]:


#Load not processed SHARPS
data_dir_NP = os.path.abspath("/home/lazar/Fak(s)/AF/prakse/SDSA/data/3481_11923_SHARP_NP")
data_list_NP = sorted(glob.glob(os.path.join(data_dir_NP,'*continuum*')))


# In[67]:


#import matplotlib.animation as animation
#3rd party library that is wrapper for matplotlib animate (works with ffmpeg)
from celluloid import Camera
fig, ax = plt.subplots()
camera = Camera(fig)
ax.set_xlim(0,700)
ax.set_ylim(0,500)
for i in data_list_NP:
    hdu = pf.open(i)
    hdu.verify('silentfix')
    plt.imshow(hdu[1].data)
    #print(hdu[1].data.shape)
    camera.snap()

animation = camera.animate(interval=30)
animation.save('4381_raw.mp4')

from IPython.display import HTML
HTML(animation.to_html5_video())


# In[90]:


#Load projected SHARPS
data_dir_CEA = os.path.abspath("/home/lazar/Fak(s)/AF/prakse/SDSA/data/3481_11923_SHARP_CEA")
data_list_CEA = sorted(glob.glob(os.path.join(data_dir_CEA,'*continuum*')))


# In[91]:


fig1, ax1 = plt.subplots()
camera1 = Camera(fig1)
for i in data_list_CEA:
    hdu = pf.open(i)
    hdu.verify('silentfix')
    plt.imshow(hdu[1].data, cmap='gray')
    #print(hdu[1].data.shape)
    camera1.snap()

animation1 = camera1.animate(interval=30)
animation1.save('4381_CEA.mp4')

from IPython.display import HTML
HTML(animation1.to_html5_video())


# In[ ]:





# In[ ]:




