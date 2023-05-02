# DTT, converted from R based on MMF MapStations.R
#
# Script will map GHCND stations to CONUS grid.
# Also, for each station, will list availability of daily temperature 
# observations (max/min/mean), wind speed, and SWE.
#
# Required inputs:
# - Must download all GHCND data - see readme.txt in GHCND folder
# - GHCND inventory - a list of observations and years available for each station
# - GHCND stations list - just lists all GHCND stations with location, elevation, etc.
# - Years of CONUS simulation (used to report temperature, snow, precip, wind speed
#   availability for each GHCND gauge)
# - Latitude and longitude for each CONUS grid cell center
#
# Outputs:
# - csv file with each row as a station. Columns report station metadata
#   (name, site ID, latitude, longitude, elevation) along with CONUS
#   mapping (CONUS pfb index, X index, Y index) and data availability
#   (whether temperature, precip, wind speed, and snow are available for
#   each GHCND station during the CONUS simulation period)

###################################
import numpy as np
import pandas as pd
import math

import xarray as xr
import parflow as pf
from parflow.tools.io import read_pfb

import matplotlib.pyplot as plt
# DTT, from MMF's R script

###################################
# File locations and inputs
Latitude_pf = np.squeeze(read_pfb('/glade/p/univ/ucsm0009/CONUS2/domain_files/Latitude_CONUS2.pfb'))
Longitude_pf = np.squeeze(read_pfb('/glade/p/univ/ucsm0009/CONUS2/domain_files/Longitude_CONUS2.pfb'))

# Path to GHCND file with list of observations and years available
ghcnd_inventory_path = "/glade/p/univ/ucsm0002/CONUS_modern/Analysis_Validation/Validation/GHCND_MetStations/ghcnd-inventory.txt"

# Path to GHCND file with list of stations 
ghcnd_stations_path = "/glade/p/univ/ucsm0002/CONUS_modern/Analysis_Validation/Validation/GHCND_MetStations/ghcnd-stations.txt"

# Water years you want included when choosing stations
# NOTE: GHCND file inventory uses calendar years, not water years
start = 2002 # start water year
end = 2003 # end water year
yrs = list(range(start,end+1))

# # Path to lat/lon grid file
# CONUSlatlon = latlon = np.loadtxt('/glade/p/univ/ucsm0002/CONUS2/domain_files/CONUS2.0.Final.LatLong.sa',skiprows=1)

# Output file 
# this will be a csv containing list of stations for comparison:
# station ID, lat/lon of station, station name, station elevation,
# availability of core variables - TMIN/TAVG/TMAX/PRCP/WESD/SNOW/SNWD/AWND,
# and the CONUS index, x-index and y-index for comparison cells

print(f'Water Years to include for GHCND: {yrs}')

###################################
# Read in station data

# Reading these in as fixed width 
ghcnd_inventory = pd.read_fwf(ghcnd_inventory_path,
                           names = ["ID","LATITUDE","LONGITUDE","ELEMENT","FIRSTYEAR","LASTYEAR"])

ghcnd_stations = pd.read_fwf(ghcnd_stations_path,
                            names = ["ID","LATITUDE","LONGITUDE","ELEVATION_m","STATE","NAME","GSN_FLAG","HCN_FLAG","WMO_ID"])#,comment='$') 

print(ghcnd_stations.shape)
ghcnd_stations

###################################
# select GHCND stations that are within CONUS1 (2) bounding box
# First, to make this a bit more efficient, do a cursory look at stations
# and remove all that are outside of a bounding box containing CONUS2
### CONUS 1 Bounding Box
### Need to update this, but doing this now because the `extract_station_indices_in_parflow_grid` function won't work when 
### lat/lon does NOT correspond to a CONUS2 grid cell (i.e. if the lat/long is WITHIN the bounding box, but OUTSIDE of the active domain)
maxlat = 51
minlat = 30
maxlon = -75
minlon = -122

out_domain1 = np.where((ghcnd_stations.LATITUDE > maxlat) | (ghcnd_stations.LATITUDE < minlat))
out_domain2 = np.where((ghcnd_stations.LONGITUDE > maxlon) | (ghcnd_stations.LONGITUDE < minlon))
out_domain = np.union1d(out_domain1[0], out_domain2[0])
# stations contained within CONUS2 (CONUS1 FOR NOW!!!) bounding box
ghcnd_stations = ghcnd_stations.drop(out_domain)
# change index to ID for creating dictionary
ghcnd_stations = ghcnd_stations.set_index('ID')

###################################
# Find CONUS2 indices that match GHCND Locations


from extract_CONUS2_indices import *

##CREATE DICT WITH THE LOCATIONS OF STATIONS

my_station_locations = {}
#my_station_locations = ghcnd_stations_latlon.to_dict

#my_station_locations['ID']=[lat,lon]
#my_station_locations['AR000087007']=[49.2833,-99.3000]
## Create dictionary from GHCND Station Locations
for i in range(len(ghcnd_stations.index)):
    my_station_locations[ghcnd_stations.index[i]]=[ghcnd_stations.LATITUDE[i],ghcnd_stations.LONGITUDE[i]]

dictionary_of_rows_cols = extract_station_indices_in_parflow_grid(my_station_locations, Latitude_pf, Longitude_pf)

###################################
# Create dataframe from dictionary containing CONUS2 x and y indices and save
conus2_index_for_sites = pd.DataFrame.from_dict(dictionary_of_rows_cols, orient = 'index', columns = ['CONUS_y', 'CONUS_x'])
conus2_index_for_sites.index.names = ['ID']
conus2_index_for_sites.to_csv('GHCND_mapped_CONUS2.csv')

ghcnd_stations_xy = ghcnd_stations.join(conus2_index_for_sites)
ghcnd_stations_xy.to_csv('GHCND_stations_full_WITH_INDICES.csv')


###
# Next steps:
# Find the stations that are within the bounding box that have avg temp and avg precip, save values for WY2003 for each ID/CONUS2 x and y