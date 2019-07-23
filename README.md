

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

- [] is HARPNUM; Empty because we dont know it
- [2013.12.07/21d] - Start date and duration
- [? NOAA_ARS ~ "11923" ?] - Query string to filter specific AR
- {**ALL**} - i think this is record limit, but im not sure.


Also, manual is here http://jsoc2.stanford.edu/ajax/RecordSetHelp.html (example 6)


