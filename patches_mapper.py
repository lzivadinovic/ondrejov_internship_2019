import numpy as np
from scipy.spatial import distance_matrix
import os
import glob

#Top data directory
data_dir = os.path.abspath("/home/lazar/Fak(s)/AF/prakse/SDSA/data")

#patches folder in that data directory
patches_dir = os.path.join(data_dir, "3481_11923_SHARP_CEA_patches")

#Search for files containing patches in their name
patches_list = sorted(glob.glob(os.path.join(patches_dir, "*patches*")))

def mapper_2(centers_1, centers_2, r_search=11):
    '''
    C1 - Matrix of centers that get_patches_and_vectors returns
    C2 - Matrix of centers that get_patches_and_vectors returns for second image
    r_search - search radius for nearest neighbour in pixel distance
    - it search for 
    
    returns:
    mapper - Array of tuples containing mappings between two images
    first element of tuple is patch on first image
    '''

    mapper = [] #Fucking hate doing append and empty array creation!
    
    # because distance_matrix requires 2d arrays of vectors
    # if centers_1.ndim == 1 or/and centers_2.ndim == 1 
    # i will pad them to dimension 2 with some crazy values that i can filter
    # i really hate 1000000 if / elif 
    # This is NOT a good practice

    padder_array = np.array([1e6,1e6])

    print("THIS IS CENTERS_1")
    print(centers_1)

    if centers_1.shape[0] == 0:
        return mapper
    elif centers_1.ndim == 1:
        C1 = centers_1[0:2]
        C1 = np.vstack((C1,padder_array))
    else:
        C1 = centers_1[:,0:2]

    print("THIS IS CENTERS_2")
    print(centers_2)

    if centers_2.shape[0] == 0:
        for i in range(C1.shape[0]):
            if not np.array_equal(C1[i], padder_array):
                mapper.append((i,'X'))
        return mapper
    elif centers_2.ndim == 1:
        C2 = centers_2[0:2]
        C2 = np.vstack((C2,padder_array))
    else:
        C2 = centers_2[:,0:2]

    DM = distance_matrix(C1,C2)

    #Loop trough all rows of cost matrix 
    for first in range(DM.shape[0]):
        # if for this index C1 == padder array, we know that we are done and that we hit padder

        if np.array_equal(C1[first],padder_array):
            return mapper
            
        #if in that row, we have entries that are smaller than r_search
        #we put it in tuple
        second = (DM[first] < r_search).nonzero()[0]

        if np.array_equal(C2[second],padder_array):
            #skip this for loop because this mapped to padder
            continue
        #If there is no entries, mark it as NOT MAPPED (disapeared or whatever)

        if second.shape[0] == 0:
            #print("ovaj nije mapiran")
            mapper.append((first, 'X'))
            #Skip that row for executing on code bellow
            continue
        #If we have multiple values (or signle, we dont care)
        #mark those as MAPPED
        for i in second:
            mapper.append((first,i))

    return mapper



def map_between_images(centers_1, centers_2, r_search=11):
    '''
    C1 - Matrix of centers that get_patches_and_vectors returns
    C2 - Matrix of centers that get_patches_and_vectors returns for second image
    r_search - search radius for nearest neighbour in pixel distance
    - it search for 
    
    returns:
    mapper - Array of tuples containing mappings between two images
    first element of tuple is patch on first image
    '''
    mapper = [] #Fucking hate doing append and empty array creation!
    
    #if centers_1 have no entries
    #Return empty array
    if centers_1.ndim == 0:
        return mapper
    elif centers_1.ndim == 1:
        #If it has something, extract X and Y coordinates
        C1 = centers_1[0:2]
        if centers_2.ndim == 0:
            mapper.append((0,'X'))
            return mapper
        elif centers_2.ndim == 1:
            C2 = centers_2[0:2]
            DM = np.linalg.norm(C1-C2)
            if DM < r_search:
                mapper.append((0,0))
                return mapper
            else:
                mapper.append((0,'X'))
                return mapper
        else:
            C2 = centers_2[:,0:2]
            DM = np.asarray(list(map(lambda x: np.linalg.norm(C1 - x), C2)))
            second = (DM < r_search).nonzero()[0]
            if second.ndim == 0:
                mapper.append((0,'X'))
                return mapper
            for i in second:
                mapper.append((0,i))

            return mapper
    else:
        #Extract multiple values into array
        C1 = centers_1[:,0:2]

    #if centers_2 have no entries
    #we know that everything from first image dissapeared
    #so we return tuples (cent_1, 'X')
    if centers_2.ndim == 0:
        #i know that center_1.ndim != 0
        #bcz of above if
        #But if its 1 (one entry) return 0 -> 'X'
        if C1.ndim == 1:
            mapper.append((0,'X'))
            #Exit after this
            return mapper
        #But if we have more, map all of them into X
        for i in range(C1.shape[0]):
            mapper.append((i, 'X'))
        return mapper
    elif centers_2.ndim == 1:
        C2 = centers_2[0:2]
        # here C1 is multi dimensional, but C2 is len = 1
        DM = np.asarray(list(map(lambda x: np.linalg.norm(x - C2), C1)))
        second = (DM < r_search).nonzero()[0]
        #So if second is empty here, that means that none frome C1 mapps into C2
        #so every patch should map to X
        if second.ndim == 0:
            for i in range(C1.shape[0]):
                mapper.append((i,'X'))
            return mapper
        #But if there exists mapping
        #Ok this is bullshit, need to thing over it again
        for i in second:
            mapper.append((i,0))

        return mapper

    else:
        C2 = centers_2[:,0:2]
    #Calculate distance matrix
        DM = distance_matrix(C1,C2)
    
    #Loop trough all rows of cost matrix 
    for first in range(DM.shape[0]):
        #if in that row, we have entries that are smaller than r_search
        #we put it in tuple
        second = (DM[first] < r_search).nonzero()[0]
        #If there is no entries, mark it as NOT MAPPED (disapeared or whatever)
        
        
        if second.shape[0] == 0:
            #print("ovaj nije mapiran")
            mapper.append((first, 'X'))
            #Skip that row for executing on code bellow
            continue
        #If we have multiple values (or signle, we dont care)
        #mark those as MAPPED
        for i in second:
            mapper.append((first,i))
            
    #I need one more check
       
    #Imagine you have two points in C1 and two in C2
    #Distance C1_1 to C2_1 and C2_2 are both < r_search
    #This will say:
    #"ok, C1_1 is mapped into both C2_1 and C2_2 and C1_2 also maps into C2_1 and C2_2"
        
            
    return mapper

from multiprocessing import Pool
nproc = 4  # i have 4 cores + hyperthreading

#meeeeh, to lazy to think, lets create new list for data that has tuples of two consecutive files
#for example if you have patches list which is list of names of files eg: ['1.txt','2.txt','3.txt','4.txt'....]
#this will create following list [('1,txt','2.txt'),('2.txt','3.txt'),('3.txt','4.txt')....]

patches_list = patches_list[600:605]
data_tuple = list(zip(patches_list,patches_list[1:]))

def wraper_func(data):
    C1 = np.loadtxt(data[0])
    C2 = np.loadtxt(data[1])
    print(mapper_2(C1,C2))


for i in data_tuple:
    wraper_func(i)
#if __name__ == '__main__':
#    p = Pool(nproc)
#    p.map(wraper_func, data_tuple)
