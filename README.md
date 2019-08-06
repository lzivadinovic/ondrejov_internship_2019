

## Tue 16 Jul 2019 12:32:42 AM CEST
Decided to go with HMI HARPs because they are extracted patches of active region; They are standard HMI vectorgram but they extracted patches where they found AR;
There is kind of 1:1 NOAA AR to HARPNUM mapping, but some AR can be in multiple NOAA AR; Got full list of AR -> HARPNUM;

TO DO: Find all HARPNUMP for all AR that Jan sent you so you can make JSOC query. (Think about python vs ssw for data retrival; Python has nice and clean API)

## Sat 20 Jul 2019 05:06:54 PM CEST

Created a query to map NOAA AR to HARPS list:
```
cat AR_LIST | grep -Ev "^#" | awk '{ print $1 }' | xargs -I '{}' grep '{}' HARPNUM_NOAA.txt  | awk '{ printf "%.4d\n", $1 }'
```

It will take first column from AR_LIST sent by Jan, and map it to HARPNUM_NOAA.txt file retrived from JSOC.
Note that some HARPS will have multiple NOAA AR regions in it, in our case that is one `(HARPS:284  NOAA:11133,11134)`

## Tue 23 Jul 2019 11:38:21 AM CEST

If you want to create query on HMI sharp/harp but you only know NOAA AR number and start date, you can write down query like this 

```hmi.sharp_720s_nrt[][2013.12.07/21d][? NOAA_ARS ~ "11923" ?]{**ALL**}```

- `[]` is HARPNUM; Empty because we dont know it
- `[2013.12.07/21d]` - Start date and duration
- `[? NOAA_ARS ~ "11923" ?]` - Query string to filter specific AR
- `{**ALL**}` - i think this is record limit, but im not sure.


Also, manual is here http://jsoc2.stanford.edu/ajax/RecordSetHelp.html (example 6)



## Tue 23 Jul 2019 12:17:36 PM CEST

Problem with query above is that we are using nrt (near real time data) its fast track pipeline for live checking of data (i assume), if we change to regular 720 sharp, query is working with HARPS number as expected.

You can see different sharps formats here http://jsoc.stanford.edu/doc/data/hmi/sharp/sharp.htm, i've opet out for trying hmi.sharp_720s (and later on hmi.sharps_cea_720s) and abandon nrt.

So SHARP query at the end should be like ```hmi.sharp_720s[3604]{**ALL**}```

Also, this fixes missing NOAA -> HARPNUM problem and removes query by date and NOAA_ARS number; Its cool

## Tue 23 Jul 2019 04:04:14 PM CEST

Downloaded SHARP data for HARPNUM 3481 and 3604 (corresponding to NOAA AR 11923 and 11950); We downloaded both SHARP 720s and SHARP CEA 720s; Currently on `chromosphere:/seismo4/lzivadinovic`

| HARP |  NOAA  | JSOC_ID           | CEA_JSOC_ID      |
| -----|--------|-------------------|------------------|
| 3604 |  11950 | JSOC_20190723_431 | JSOC_20190723_505| 
| 3481 |  11923 | JSOC_20190723_429 | JSOC_20190723_489|

CEA - are reprojected to local frame, ambiguity resolved magnetic data (Br, Bp, Bt) see sharp webpage for more details; They are also rotated for 180 degrees so that north is up, and east is right. TAKE CARE WHEN COMPARING TO REGULAR SHARP DATA!

This data is bassicaly prepared for analysis.

## Tue 23 Jul 2019 11:30:05 PM CEST

Tried this out https://github.com/cdiazbas/enhance looks fun and works well. Tested on sunspots with lightbridges, looks really good on enhanced images. Note that you get better results if you normalize data by quiet sun. In the end, i dont see any use of it because we are not interested in small scale structures evolution.

## Wed 24 Jul 2019 11:27:45 AM CEST

Created ipynotebook for creating mp4 files that represents data animation/evolution. 

Add requirements.txt (its mess, but at least its working with enhance)

#### Note on requirements provided 

Please use virtualenv if you dont want to mess your system!

You need to install specif version of packages, simple `pip install -r requirements.txt` will not work because there are packages that were compiled/installed via git

IIRC, these are onyl two i used (keras and tf contrib)

```bash
sudo apt install imagemagic imagemagick-common ghostscrip libtk-img libtk8.6 libcfitsio
pip install sunpy[all] #in zshell use pip install sunpy\[all\]
pip install astropy[all] # -||-

pip install git+https://www.github.com/keras-team/keras-contrib.git

#also you need to clone repo and run this https://github.com/keras-team/keras-contrib#install-keras_contrib-for-tensorflowkeras
#its some wraper thing i dont quite understand
```

I recommend going `pip install -r requirements.txt` untill you encounter error for some package, remove that package from txt file, and rinse and repeat with pip install unitl you get over all packages. Then run install `sunpy[all]` and `astropy[all]` and keras contrib with both pip and cloned repo (this conversion stuff) and that should be it



## Wed 24 Jul 2019 02:07:32 PM CEST

Tried PCA reduction for removing limb darkening, it only works with data that are near limb. (comment bellow pasted from animate.ipynb, see animate.html for prerendered notebook with data and comments)

Idea is that because there is no obvious intensity gradient, primary component of SVD is not actually limb darkening but some small scale variation across image. This leads to adding some artifacts that are not related to limb darkening, so this method is not suitable for removing limb darkening near disk center. Better idea is to create limb darkening function for this specific filter using some curve $f(r,\lambda)$, where $r$ is distance from disk center, and find $r$ for every pixel and reduce it that way.



## Wed 24 Jul 2019 04:35:32 PM CEST

Quick memo: DONT FORGET TO FIX HEADER ON IMAGES ONCE YOU RUN ENHANCE! When running enhance, your images are upscaled by factor of 2, so crval1/2 and crpix1/2 changes acordingly

## Wed 24 Jul 2019 05:55:17 PM CEST

Created function for limb darkening using http://articles.adsabs.harvard.edu/pdf/1977SoPh...51...25P (see limb_darkening.html/ipynb) for more details;

I cant figure out coordinate system mapping of SHARP CEA. Im having problem calculating distance from sun center in r_sun using CRVAL, near limb and center images have very similar values for this keyword. Not sure what is happening, but i found out that someone wrote conversion http://hmi.stanford.edu/hminuggets/?p=1428 (look at [S1] reference). I thought that it should be crpix = center pixel coordinate in pixels, crval = centar pixel coordinate in some coordinate system (Carrington in this case, but comparing near limb and center images shows different results). Need to read conversion to figure out what is happening. Also, http://jsoc.stanford.edu/doc/keywords/JSOC_Keywords_for_metadata.pdf crunit2 (y axis) for CEA should be sin latitude (or something like that) but in our data is degrees. IDK.


## Thu 25 Jul 2019 06:34:18 PM CEST

Finally figured how to easily and quicky transform images to helioprojective coordinates (distance from disk center in arcsecond) so we can now easily correct for limb darkening.

There are some concerns regarding general coordinate transformation for HMI data. Some people say that SDO does not report (in header) same satelite possiotion for HMI and AIA data taken at the same time, and also there is still discussion on how carrington system is deffined (if i understood correctly some guy in chatroom) (see https://github.com/sunpy/sunpy/issues/3057) 

Albert Y. Shih:
"Re HMI, do keep in mind that we don't have a good observer coordinate from the FITS headers (see  issue #3057), so conversions between HPC and HGC in SunPy may not match whatever is done elsewhere (and that's on top of the fact that people don't necessarily agree on the definition of Carrington longitude"

Big thanks to Stuart Mumford, lead developer of sunpy for helping me figure this out (https://github.com/Cadair).

General comments regarding code detalis and procedures were added to limb_darkening notebook. (for non interactive preview open limb_darkening.html)


## Thu 25 Jul 2019 06:43:29 PM CEST

Reading material (helpers):

https://arxiv.org/pdf/1309.2392.pdf

https://nbviewer.jupyter.org/github/mbobra/calculating-spaceweather-keywords/blob/master/feature_extraction.ipynb

http://jsoc.stanford.edu/relevant_papers/ThompsonWT_coordSys.pdf


## Fri 26 Jul 2019 02:59:25 PM CEST

Wrote wraper function that will do limb darkening clearing of images. Its bassicaly nicely written wrapper for stuff we did yesterday. Note that we did not change header of original images (for example mean intensity keyword is incorect, etc...) everything else should be fine.

I did not wrote comments in script, because limb_darkening.ipynb/html contains detailed instruction for one image reduction; Also, to convert ipynb to actuall python script that you can actually run with `python script.py` one can use `jupyter nbconvert --to script remove_limb_darkening_for_dataset.ipynb` it will create file with same name but with .py extension and removing all json embedded data.

## Fri 26 Jul 2019 09:32:17 PM CEST

Tried https://docs.sunpy.org/en/stable/api/sunpy.map.GenericMap.html#sunpy.map.GenericMap.resample and its working as expected. It's even updating headers, so that coordinate frame stays fixed and you can use it later on. It does not update naxis1/2 (dimension of image), but that is no big deal, coordinate delta per pixel, and reference center pixel is updated. Would recommend further usage of this procedure! (maybe submit PR to fix this issue?)

There is also small artifact, that shows up as 0 value padding on the outtermost pixels. So your whole image (rescaled to finner grid using cubic interpolation) is sorounded by 1px box with value 0, but we can just ignore those, normalized histograms looks identical.

Also, i've changed enhance codebase to allow writing back fits headers from enhanced images. I will need to transform header to perserve resampled data coordinate grid, my plan is to use code from sunpy.map.resample as base because they have it very clearly written how they transform header to perserve coordinate grid. But, for now, you insert image, you get back image with headers, original enhance removed headers from image and only saved data back.

## Sat 27 Jul 2019 07:29:24 PM CEST

Fixed enhance header data and write header, if PR doesn't get merged, we could use my fork. https://github.com/lzivadinovic/enhance

## Mon 29 Jul 2019 10:28:37 AM CEST

There is 0 pixel boundary after resampling images using sunpy.map resample method. 

Sunpy resample has minusone flag that can NOT be passed while invoking resample method on sunpy map, but if using raw resample function it works. Problem with using resample function is that it does not auto create new coordinate mesh grid and it does not update header of new map. I've created manual 2d interpolation using scipy, and there is no boundary box so i've investigated source code and figured out what is actually happening (minusone flag :( );

Idea is to replace all 0 with mean values of "intensity" of image (in br, it should be mean value of magnetic field...); In worst case scenario, just ignore it because its around 1 promile "err".

Also, we have created normalized histograms of resampled (upscaled) and original HMI data and they are identical!!! So offseting pixels are 0.001678862 area of the whole image, like 1‰!

## Mon 29 Jul 2019 04:07:35 PM CEST

Wrote script for resampling dataset for magnetic data and run trough two dataset, data is on seismo4. It uses cubic spline interpolation to upscale magnetic data to double its size.

Sara wrote script for data normalization of continuum images using histogram. It will create histogram of dataset and find value of flux for maximum of histogram. We decided that 100 bins is OK for this pourpose.

Need to figure out how to run enhance in parallel so we dont wait for like 2hr for one dataset!

## Tue 30 Jul 2019 03:52:21 PM CEST

Data preparation was completed for two regions. It was done in following maner:

- Limb darkening reduction on whole dataset using `remove_limb_darkening_for_dataset.py` procedures (Br, Bp, Bt was not reduced for limb darkening)
- Data was normalized to quiet sun flux with normalize_continuum_images.py (Br, Bp, Bt was not normalized)
- Normalized images were enhanced using `enhance_dataset.py` procedure, note that you need to use my fork of project and put `enhance_dataset.py` file into that folder (and data should also be there) so this procedure and enhance can work. Problem was hardcoded import in enhance codebase. (Br, Bp, Bt was not enhanced by this method)
- Magnetic data were upscaled to enhanced data dimensions using `upscale_magnetic_data_with_spline2d.py` which apply cubic spline interpolation to dataset and upscales images by factor of 2 so they match in size/shape enhanced data
- Enhanced data had to be normalized again to quiet sun and this is done via `normalize_continuum_images.py` procedures

Note that every of this process takes one dataset in terms of folder where data is, search pattern (`continuum` for continuum images for example) and outputs in user specified directory with new naming scheme (ld removed images becomes `continuum_ld_removed` for example). This way, you only need to change input and output folder of dataset on which you want to perform some operation.

Detailed explaination of every reduction can be found above in readme.md or in appropriate `.ipynb` file.

There is also some helper ipynb that were used for quick preview of data, which are not translated to .py file.

Notable example is `compare_enhanced_with_spline` which shows data cutouts and histograms before and after normalisation, and such. Read ipynb for more detailed insight.

## Wed 31 Jul 2019 11:20:24 AM CEST

### CHANGED PROJECT STRUCTURE!

Its getting messy, example notebooks and testing stuff is in `helper_testing_notebooks` folder

Created master prep script `dataset_prep.py`. It uses one folder from HMI dataset, search for contiuum images, and performs reduction explained above.
There are few drawbacks; To make it work (to be more specific, to make enhance work) you need to put this script into enhance folder root, but you also need to use my modified fork (sunpy.map and header support) https://github.com/lzivadinovic/enhance, you should use master branch from this repo. 

After that, you need to modify script variables that are pointing to data input and output folder, also, you can change search criterium, but for this master script, its only working on continuum data, so be careful.

There is also master upscale Bx script, it works the same way as `dataset_prep.py`, it runs trough all [Br, Bp, Bt] files and upscales them to 2x size

## Fri 02 Aug 2019 09:12:59 AM CEST

Yesterday i wrote routines for detecting active regions and labeling them by numbers. Threshold was 0.5 of quiet sun intensity and groupation of pixel is considered pore if it has more than 20px of surface. That is ~2.5pix in radii on enhanced image. Pixel size on HMI data is 1", but on enhanced, they were upscaled by factor of 2, so we consider pore if object is 5px accross => 2.5".

Also, wrote routines for calculating center of mass of each patch. Also, there are routines for calculating <Br>, <Bp>, <Bt> for each polygon.

I need to thing about merging and tracking polygons.



## Fri 02 Aug 2019 05:59:24 PM CEST

Finished `region_fill_master_wrap.py` that handles patches discovery and labeling for every fits intensity file and calculates mean values for magnetic field. Its extensible, you can select fill structure, intensity treshold, how small patches (in pixels) to ignore. This can be used in main pipeline for extracting patches of interest. 

This function also return labeld masked array for discovered patches, in wraper we are just using it to write patches data into txt files. It's gonna be usefull also for tracking algorithm, but we will need full mask because of possible separation and merging of pores and objects on sun surfaces. But we can simply import function from that file with `from region_fill.... import function_name...` and handle outputs ourselves because its always returns two matrices (patches and labeled array, both are zero matrices if there is no patch for selected criteria)

Read the code for more info, functions have documentation for input/output!

## Tue 06 Aug 2019 09:27:18 AM CEST

Small fixes and tweaks in `region_fill_master_wrap.py`. Added area of patch as output, fixed inverted x and y cmasses and random fixes.

Currently working on region tracking. I decided to go with LCT way, creating 2D gaussian map and doing correlation in local neighbour (dx=dy=20pix => 40 pix search window). 

This failed misserably, because i was tracking labeled features, not intensity maps, so if one is larger than another, correlation hits peak. Also, problem was not normalazing everything to one (all reagions were marked as 1 or 2 or 3 or 4 ...) so correlation functions prefered big numbers. This was resolved and tested again, but it still looks messy.

## Tue 06 Aug 2019 03:31:44 PM CEST

Currently trying to implement nearest neibhour search with additional conditions for merges and creation/dissapirance of regions. 

My main consideration (trying to do in in parallel, because i cant concentrate on stuff above) is using DBSCAN clusttering on multiple timeframes of centers masses for each region. This should provide easy way of grouping traces of each spot. This is mostly inspired by https://www.reddit.com/r/algorithms/comments/bgt57a/identification_algorithm_with_coordinates_as_input/
