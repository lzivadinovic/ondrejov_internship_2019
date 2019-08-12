import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
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
from mpl_toolkits.mplot3d import Axes3D
import sunpy.map

#loading patch data column by column

path_to_patch_data = '/home/sara/ondrejov/Clustering/arch/hmi.sharp_cea_720s.3481.20131213_111200_TAI.patches.txt'

#cx cy bx by bz A

cy, cx, Bx, By, Bz = np.loadtxt(path_to_patch_data, unpack=True)
#Bx, By, Bz will be in kG
Bx = Bx/1e3
By = By/1e3
Bz = Bz/1e3

#B magnitude
B = (np.sqrt(Bx**2+By**2+Bz**2))

#loading flux data
path_to_continuum_map = '/home/sara/ondrejov/Clustering/arch/hmi.sharp_cea_720s.3481.20131213_111200_TAI.enhanced_normalized.fits'
I = sunpy.map.Map(path_to_continuum_map).data

#number of pixels on y and x axis
y_length, x_length = I.shape

#choosing edges for patches;
x_patch = np.array([0,x_length])
y_patch = np.array([0,y_length])

#in case we don't want whole image; for this particular frame 800<x<1150 and 560<y<700 cover all patches
x_patch = np.array([800,1150])
y_patch = np.array([560,700])

#this creates array with evenly spaced values within a given interval - x and y coordinates
x = np.arange(x_patch[0],x_patch[1])
y = np.arange(y_patch[0],y_patch[1])

#creating z coordinates for mass centers; they're in xy plane so cz is zero for all of them; needed for plotting 3D vector
cz = np.zeros(len(cx))

#if whole image is used, I1=I 
I1 = I[y_patch[0]:y_patch[1],x_patch[0]:x_patch[1]]

#creates x_length*y_length dimension matrices needed for contour plot
xx, yy = np.meshgrid(x,y)

#next three lines plot intesity 3d; wasn't needed here
#fig = plt.figure(0)
#ax = fig.gca(projection='3d')
#ax.plot_surface(xx, yy, I1, alpha=0.5, cmap=cm.inferno)

#this plotes intensity projection on z=0 (offset=0) plane 
fig = plt.figure(1)
ax = fig.gca(projection='3d')
cset = ax.contourf(xx, yy, I1,  zdir='z', offset=0, alpha=0.3, cmap=cm.inferno)
fig.colorbar(cset, aspect=10, label=r'$I/I_{avg}$')

#plotting averaged vectors for every patch; if Bz<0 vector direction is swiched
#vector length is a kinda tricky and sensitive to changes, works well like this and that's why B is in kG  
for i in range(len(Bz)):
    if Bz[i]>0:
        plt.quiver(cx[i], cy[i], cz[i], Bx[i], By[i], Bz[i], length=B[i], pivot='tail', color='green')
    elif Bz[i]<0:
        plt.quiver(cx[i], cy[i], cz[i], -Bx[i], -By[i], -Bz[i], length=B[i], pivot='tail', color='purple')

#creating simple colorbar with two colors 
cmap= mpl.colors.ListedColormap(['purple', 'green'])
norm = mpl.colors.Normalize(vmin=-1, vmax=1)
mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
fig.colorbar(mappable, label='B polarity')

ax.set_xlim(x_patch[0],x_patch[1])
ax.set_ylim(y_patch[0],y_patch[1])
ax.set_zlim(0, 5)
ax.set_xlabel('x [pix]')
ax.set_ylabel('y [pix]')
ax.set_zlabel('z [arb]')
plt.title('Magnetic field vector averaged per patch')


plt.show()

