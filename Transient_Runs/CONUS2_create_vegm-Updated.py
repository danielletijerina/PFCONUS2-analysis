 from asyncore import write
import numpy as np
from parflow.tools.io import read_pfb,write_pfb
from PIL import Image
import matplotlib.pyplot as plt
import sys 
import os
from scipy import stats

"""
SCRIPT TO WRITE THE CONUS2 vegm FILE (or a subset of it).
NOTES: it does NOT check the coordinates or the ordering of the points in the files. It assumes the mask
is ready to be used to subset the CONUS2 domain (will only give an error if Nx and Ny don't match)

DESCRIPTION vegm
The outputs lines are:
each a PF-domain cell, starting from the South-West corner and looping over x first (W to E) and for each x over y (S to N).
The outputs columns are: 
x: x-coordinate of the cell relative to 1 (which is the W domain side)
y: y-coordinate of the cell relative to 1 (which is the S domain side)
lat: latitude point
long: longitude point
sand: sand %
clay: clay %
color: color
18*fractional coverage of grid, by vegetation class (Must/Should Add to 1.0)\n'): 18 columns with vegetation class
"""


### CHOOSING THE NAME OF THE vegm FILE TO SAVE
#filename_vegm_out = 'drv_vegm.HOMOGENEOUS.dat'
filename_vegm_out = 'drv_vegm.CONUS2_723.dat'
#filename_vegm_out = 'drv_vegm.UCRB.dat'

### CHOOSING THE FILE PATH TO THE LANDCOVER MAP (this is the PFB file the VEGM is directly created from)
landcover_path = '1km_CONUS2_landcover_IGBP_723.pfb'

### CHOOSING IF YOU WANT PNGs OF THE DIFFERENT MAPS TO BE SAVED (good check to make sure everything is correct) AND THE PATH WHERE TO SAVE THEM
make_pngs = False
path_png = 'images/'
name_subset = 'UCRB' #name of sub-domain, will be used to save the pngs

### SET SUBSET to True AND FILL IN ALL INFO HERE IF YOU WANT A SUBSET OF CONUS2 DOMAIN
#IF YOU WANT CONUS2, Set subset=False (and path_subset won't matter)
subset = False #True creates vegm only for the subdomain identified in the mask
path_subset = 'UCRB_CONUS2.0.Final1km_Mask.pfb' #path to where you mask is
value_domain_in_mask = 1 #value associated with the subdomain in the mask
path_latlon = '' #if you have files Latitude_CONUS2.pfb and Longitude_CONUS2.pfb indicate here the path
save_latitude_longitude = True #set to true if you want Latitude_CONUS2.pfb and Longitude_CONUS2.pfb (makes vegm creation much faster for next time)




"""
1) LANDCOVER: simply read from the CONUS2 pfb
"""
# This is a 2D map with values 1-18 indicating the vegetation class number
landcover = np.squeeze(read_pfb(landcover_path))



"""
2) % SAND and % CLAY: reading the tif which are created resampling SSURGO and GSDE data to the CONUS2.0 grid
default value set to 0.16 sand and 0.26 clay
Values inside the USA are set using SSURGO data
Values outside the USA are set using the GSDE data
"""
# READING CONUS 2.0 SOIL INPUTS
# % sand outside of US borders
GSDE_sand = np.flip(np.array(Image.open('GSDE_sand.tif')),0)  #flipping to match with PF y axis; stored as fraction
# % clay outside of US borders
GSDE_clay = np.flip(np.array(Image.open('GSDE_clay.tif')),0)  #flipping to match with PF y axis; stored as fraction
# % sand inside of US borders
SSURGO_sand = np.flip(np.array(Image.open('SSURGO_sand.tif')),0) / 100 #flipping to match with PF y axis; stored as percent
# % clay inside of US borders
SSURGO_clay = np.flip(np.array(Image.open('SSURGO_clay.tif')),0) / 100 #flipping to match with PF y axis; stored as percent

# Renaming (adding pointer) for clarity
CONUS2_sand = SSURGO_sand
CONUS2_clay = SSURGO_clay

# nodata value is negative, so we Use GSDE data where data SSURGO is missing
CONUS2_sand[CONUS2_sand < 0] = GSDE_sand[CONUS2_sand < 0] # Applying GSDE data outside of US
CONUS2_clay[CONUS2_clay < 0] = GSDE_clay[CONUS2_clay < 0] # Applying GSDE data outside of US

### NEW CODE: nodata value is negative (OR ZERO!!!), so we apply the CONUS 1.0 defualt value where there is nodata
CONUS2_sand[CONUS2_sand<=0] = 0.16 # Applying default where there is no data at all
CONUS2_clay[CONUS2_clay<=0] = 0.26 # Applying default where there is no data at all

### OLD CODE: this doesn't apply the default values to zeros, only negatives, so it will not work over CONUS
#CONUS2_sand[CONUS2_sand<0] = 0.16 # Applying default where there is no data at all
#CONUS2_clay[CONUS2_clay<0] = 0.26 # Applying default where there is no data at all


### NEW CODE: does rounding ahead of time for 2 decimal precision
CONUS2_sand = np.around(CONUS2_sand,decimals=2)
CONUS2_clay = np.around(CONUS2_clay,decimals=2)
#creating a mask of where both the %sand and %clay are less than 0.005, meaning they will be rounded to 0 in the vegm file which uses 2 decimal precision
mask_both_will_be_zeros = np.ones(CONUS2_sand.shape)
mask_both_will_be_zeros[CONUS2_sand>0]=0
mask_both_will_be_zeros[CONUS2_clay>0]=0

### OLD CODE
# #creating a mask of where both the %sand and %clay are less than 0.005, meaning they will be rounded to 0 in the vegm file which uses 2 decimal precision
# mask_both_will_be_zeros = np.ones(CONUS2_sand.shape)
# mask_both_will_be_zeros[CONUS2_sand>0.005]=0
# mask_both_will_be_zeros[CONUS2_clay>0.005]=0

# nodata value is negative, so we apply the CONUS 1.0 defualt value where they would be rounded to 0 % as CLM can't handle both sand and clay 0%
CONUS2_sand[mask_both_will_be_zeros==1] = 0.16 # Applying default where there is no data at all
CONUS2_clay[mask_both_will_be_zeros==1] = 0.26 # Applying default where there is no data at all

###################################################################################


"""
3) Soil Color: reading the R-G-B tifs which are created resampling SSURGO map of soil colors to CONUS2.0 grid
- RGB is transformed to Photometric/digital ITU BT.709 (one Lightness value)
- colors are reclassified into 1-8 soil darkness classes (8 being the darkest)
- Values inside the USA are taken directly from the 1-8 classes
- To get values outside the USA, the mode of the class color for each soil region (based on the indicator file id) is computed
"""
#reading in the rgb of the soil color SSURGO product (this was resampled to the CONUS2.0 grid and split into the 3 bands)
rr=np.array(Image.open(f'soil_color_band_1_red.tif'))
gg=np.array(Image.open(f'soil_color_band_2_green.tif'))
bb=np.array(Image.open(f'soil_color_band_3_blue.tif'))

#setting the nan values (which are 0 in the rgb) to nan
rr[rr<1]=np.nan
gg[gg<1]=np.nan
bb[bb<1]=np.nan

#Using RGB -> Luma conversion formula. To go from RGB to just one "Lightness" number

#Photometric/digital ITU BT.709:
Y1 = 0.2126 *rr + 0.7152 *gg + 0.0722 *bb

#transforming it to "darkness" index (we want the highest numbers to be the darkest soils)
Y1 = np.nanmax(Y1)-Y1

#alternative method, was giving basically the same results
###Digital ITU BT.601 (gives mor1e weight to the R and B components)
###Y1 = 0.299 *rr + 0.587 *gg + 0.114 *bb

#creating a mask to identify rivers and lakes (don't want this to affect my min and max Darkness values) --> Blue so r will be 1 and g also will be 1
mask_values = np.zeros(rr.shape)
mask_values[rr>1]=1
mask_values[gg>1]=1

#computing the min and max values ignoring nan and ignoring blue bodies
min_val = np.nanmin(Y1[mask_values==1])
max_val = np.nanmax(Y1[mask_values==1])

#transforming the darkness level into 1 to 8 classes (this is what CLM version in ParFlow wants)
ind_max = 8
ind_min = 1
Y_class = ind_min + (Y1-min_val) / (max_val) * (ind_max-ind_min)
Y_class = np.rint(Y_class)

#setting "lakes" values to nan, we don't want to consider them when we find the mode of each indicator class
Y_class[mask_values==0]=np.nan

#flipping color map to match PF in python y axis
Y_class = np.flip(Y_class,0)

#reading rhe indicator file for CONUS2.0. This should be /hydrodata/PFCLM/CONUS2_Baseline/inputs/CONUS2.0.Final1km.Subsurface.pfb 
indicator = read_pfb('CONUS2.0.Final1km.Subsurface.pfb')[9,:,:]

#create array to store the final color map
soil_color_map = np.zeros(indicator.shape)
soil_color_map[:] = 2 #setting the default value

soil_classes = np.unique(indicator)

#for each indicator id, finding the mode of the color (ignoring nan and )
for id in soil_classes:
    tmp_color = Y_class[indicator==id] #selecting colors of regions with current indicator id
    tmp_color = tmp_color[np.isnan(tmp_color)==False] #removing the nan values
    mode,count = stats.mode(tmp_color) #finding the mode
    
    soil_color_map[indicator==id]=mode # in the final color map setting all regions with the current indicator id to the mode color

#overwriting the values within the USA for which we can use the darkness class derived from SSURGO
soil_color_map[np.isnan(Y_class)==False]=Y_class[np.isnan(Y_class)==False]



"""
Preparing the subsetting mask, if needed
"""

if subset == True:
    extension = os.path.splitext(path_subset)[-1]
    if extension =='.tif':
        mask_watershed = np.flip(np.array(Image.open(path_subset)),0) #flipping to match with PF y axis
    elif extension == '.pfb':
        mask_watershed = np.squeeze(read_pfb(path_subset))
    else:
        print(f'The format {extension} is not yet implemented, currently can only use pfb or tif masks')
        sys.exit(0)
    if mask_watershed.shape!=landcover.shape:
        print('The mask is not of correct size!!!!')
        print(f'The mask is of shape: {mask_watershed.shape}, while it should be: {landcover.shape}')
        print(sys.exit(0))
    #FINDING xmin xmax ymin ymax WITHIN WATERSHED (bounding box around it)
    where = np.array(np.where(mask_watershed>0))
    x1, y1 = np.amin(where, axis=1)
    x2, y2 = np.amax(where, axis=1)
    #correct coordinates because python does not include last value
    x2 = x2+1
    y2 = y2+1
    if make_pngs: 
        plt.imshow(mask_watershed,origin='lower',interpolation=None)
        plt.savefig(f'{path_png}Mask_wathershed_CONUS2.png')
        plt.close()

ny,nx = landcover.shape

"""
READING THE LAT LON COORDINATES OF CONUS2.0 (.pfb, if they exist, .sa otherwise)
"""

if os.path.exists(f'{path_latlon}Latitude_CONUS2.pfb') and os.path.exists(f'{path_latlon}Latitude_CONUS2.pfb'):
    print('The files for latitude and longitude exist!')
    lats = np.squeeze(read_pfb(f'{path_latlon}Latitude_CONUS2.pfb'))
    longs = np.squeeze(read_pfb(f'{path_latlon}Longitude_CONUS2.pfb'))

else:
    print('The files for latitude and longitude do not exist')
    ## READING THE LAT-LONG .sa FILE FOR CONUS 2
    latlon = np.loadtxt('/hydrodata/PFCLM/CONUS2_baseline/inputs/domain_files/CONUS2.0.Final.LatLong.sa',skiprows=1)

    lats = np.zeros(landcover.shape)
    longs = np.zeros(landcover.shape)

    count_lines = 0
    for yy in range(ny):
        for xx in range(nx):
            lats[yy,xx]=latlon[count_lines,0]
            longs[yy,xx]=latlon[count_lines,1]
            count_lines+=1
    print("LATLON read")

    if save_latitude_longitude:
        write_pfb(f'{path_latlon}Latitude_CONUS2.pfb',lats,dx=1000,dy=1000,dz=200,dist=False)
        write_pfb(f'{path_latlon}Longitude_CONUS2.pfb',longs,dx=1000,dy=1000,dz=200,dist=False)

"""
SUBSETTING, if needed
"""

if subset: #cutting to the subset domain if chosen to subset
    landcover = landcover[x1:x2,y1:y2]
    lats = lats[x1:x2,y1:y2]
    longs = longs[x1:x2,y1:y2]
    CONUS2_sand = CONUS2_sand[x1:x2,y1:y2]
    CONUS2_clay = CONUS2_clay[x1:x2,y1:y2]
    soil_color_map = soil_color_map[x1:x2,y1:y2]
    ny,nx = landcover.shape
    print(f'Subset dimensions: {ny},{nx}')
    if save_latitude_longitude:
        write_pfb(f'{path_latlon}Latitude_CONUS2_UCRB.pfb',lats,dx=1000,dy=1000,dz=200)
        write_pfb(f'{path_latlon}Longitude_CONUS2_UCRB.pfb',longs,dx=1000,dy=1000,dz=200)

"""
SAVING PNGs, if needed
"""
if make_pngs: 
    plt.imshow(landcover,origin='lower',interpolation=None)
    plt.savefig(f'{path_png}Landcover_CONUS2{name_subset}.png')
    plt.colorbar()
    plt.close()

    plt.imshow(CONUS2_sand,origin='lower',interpolation=None)
    plt.savefig(f'{path_png}Sand_CONUS2{name_subset}.png')
    plt.colorbar()
    plt.close()

    plt.imshow(CONUS2_clay,origin='lower',interpolation=None)
    plt.savefig(f'{path_png}Clay_CONUS2{name_subset}.png')
    plt.colorbar()
    plt.close()

    plt.imshow(soil_color_map,origin='lower',interpolation=None)
    plt.savefig(f'{path_png}SoilColor_CONUS2{name_subset}.png')
    plt.colorbar()
    plt.close()


"""
WRITING VEGM, if needed
"""

#CREATING/OPENING OUTPUT FILE
out_file = open(filename_vegm_out, "w")

print(f'Writing vegm: {filename_vegm_out}')
#WRITING FIRST TWO LINES WHICH ARE FIXED
out_file.write('x y lat lon sand clay color fractional coverage of grid, by vegetation class (Must/Should Add to 1.0)\n')
out_file.write('  (Deg) (Deg) (%/100)  index 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18\n')


for yy in range(ny):
    if yy%100 ==0:
        print(f'Out of {ny} cells in y, we are now at: {yy}')
    for xx in range(nx):
        #WRITING THE vegm ENTRIES FOR THE CURRENT POINT
        #x_ and y_ are the indices of the current point

        #creating vegetation class entries for current 
        curr_landcover = np.zeros((1,18))
        #setting the entry for the vegetation class identified in landcover to 1 
        curr_landcover[0,int(landcover[yy,xx])-1] = 1 #-1 needed because the landcover entries go 1 to 18 but python indices start at 0
        
        out_file.write(f'{xx+1} {yy+1} ' \
        #this is the latitude, every domain cell is a new line in the latlon file
        f'{lats[yy,xx]:.6f} ' \
        #this is the longitude, every domain cell is a new line in the latlon file
        f'{longs[yy,xx]:.6f} ' \
        # percent sand
        f'{CONUS2_sand[yy,xx]:.2f} ' \
        # percent clay
        f'{CONUS2_clay[yy,xx]:.2f} ' \
        # soil color
        f'{int(soil_color_map[yy,xx])} ' \
        f'{int(curr_landcover[0,0])} ' \
        f'{int(curr_landcover[0,1])} ' \
        f'{int(curr_landcover[0,2])} ' \
        f'{int(curr_landcover[0,3])} ' \
        f'{int(curr_landcover[0,4])} ' \
        f'{int(curr_landcover[0,5])} ' \
        f'{int(curr_landcover[0,6])} ' \
        f'{int(curr_landcover[0,7])} ' \
        f'{int(curr_landcover[0,8])} ' \
        f'{int(curr_landcover[0,9])} ' \
        f'{int(curr_landcover[0,10])} ' \
        f'{int(curr_landcover[0,11])} ' \
        f'{int(curr_landcover[0,12])} ' \
        f'{int(curr_landcover[0,13])} ' \
        f'{int(curr_landcover[0,14])} ' \
        f'{int(curr_landcover[0,15])} ' \
        f'{int(curr_landcover[0,16])} ' \
        f'{int(curr_landcover[0,17])}\n')
out_file.close()
