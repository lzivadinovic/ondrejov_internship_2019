

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

## Wed 24 Jul 2019 02:07:32 PM CEST

Tried PCA reduction for removing limb darkening, it only works with data that are near limb. (comment bellow pasted from animate.ipynb, see animate.html for prerendered notebook with data and comments)

Idea is that because there is no obvious intensity gradient, primary component of SVD is not actually limb darkening but some small scale variation across image. This leads to adding some artifacts that are not related to limb darkening, so this method is not suitable for removing limb darkening near disk center. Better idea is to create limb darkening function for this specific filter using some curve $f(r,\lambda)$, where $r$ is distance from disk center, and find $r$ for every pixel and reduce it that way.



## Wed 24 Jul 2019 04:35:32 PM CEST

Quick memo: DONT FORGET TO FIX HEADER ON IMAGES ONCE YOU RUN ENHANCE! When running enhance, your images are upscaled by factor of 2, so crval1/2 and crpix1/2 changes acordingly

## Wed 24 Jul 2019 05:55:17 PM CEST

Created function for limb darkening using http://articles.adsabs.harvard.edu/pdf/1977SoPh...51...25P (see limb_darkening.html/ipynb) for more details;

I cant figure out coordinate system mapping of SHARP CEA. Im having problem calculating distance from sun center in r_sun using CRVAL, near limb and center images have very similar values for this keyword. Not sure what is happening, but i found out that someone wrote conversion http://hmi.stanford.edu/hminuggets/?p=1428 (look at [S1] reference). I thought that it should be crpix = center pixel coordinate in pixels, crval = centar pixel coordinate in some coordinate system (Carrington in this case, but comparing near limb and center images shows different results). Need to read conversion to figure out what is happening. Also, http://jsoc.stanford.edu/doc/keywords/JSOC_Keywords_for_metadata.pdf crunit2 (y axis) for CEA should be sin latitude (or something like that) but in our data is degrees. IDK.

