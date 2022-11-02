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

###################################
# File locations and inputs

# Path to GHCND file with list of observations and years available
ghcnd_inventory_path = "/glade/p/univ/ucsm0002/CONUS_modern/Analysis_Validation/Validation/GHCND_MetStations/ghcnd-inventory.txt"

# Path to GHCND file with list of stations 
ghcnd_stations_path = "/glade/p/univ/ucsm0002/CONUS_modern/Analysis_Validation/Validation/GHCND_MetStations/ghcnd-stations.txt"

# Water years you want included when choosing stations
# NOTE: GHCND file inventory uses calendar years, not water years
start = 2003 # start water year
end = 2005 # end water year
yrs = list(range(start,end+1))

print(f'Water Years to include for GHCND: {yrs}')

# Path to lat/lon grid file
CONUSlatlon = latlon = np.loadtxt('/glade/p/univ/ucsm0002/CONUS2/domain_files/CONUS2.0.Final.LatLong.sa',skiprows=1)

# Output file 
# this will be a csv containing list of stations for comparison:
# station ID, lat/lon of station, station name, station elevation,
# availability of core variables - TMIN/TAVG/TMAX/PRCP/WESD/SNOW/SNWD/AWND,
# and the CONUS index, x-index and y-index for comparison cells
outfile = "./GHCND_mapped_CONUS2.csv"


