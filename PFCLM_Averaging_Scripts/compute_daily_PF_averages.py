###########################################
### Process and save ParFlow daily averages
###########################################

# This script takes hourly PF outputs as PFB files and computes the daily averages to be saved as PFB files.
# DTT & EL

# Inputs:
# - Directory where PF outputs are and directory where you want to save output
# - Hourly PFB files of PF outputs
# - water year and day start/end

# Outputs:
# - PFB files for daily average of each variable:  
#     - Overland flow at each grid cell (flow)
#     - Soil moisture (SM)  
#     - Water table depth (WTD)  
#     - Surface water storage (SURF_WATstorage)

#   - _Subsurface Storage Components:_
#     - Total Subsurface Storage (SUBstorage)
#     - GW storage (GWstorage)*
#     - Soil moisture storage (SMstorage)*

    
# Notes (10/21/22):
# - Need to determine when is the daily start and end for US time zone, NLDAS3 forcing is UTC
# - Need to add in monthly and yearly averages - Created new script for this since we are processing one month at a time `Compute_month-year_averages_PFCLM.ipynb`
# - ADD UNITS OF CALCULATIONS!
# - *Need to figure out the GW and SM Storage (which layers, do we even want to separate by layer, do by WTD???)


import numpy as np
from parflow import Run
import sys
from parflow.tools.io import read_pfb,write_pfb
import parflow.tools.hydrology as hydro


### DEFINE WATER YEAR, START DAY, & END DAY ###
water_year = 1999
day_start = 1 #day_start = 0 is the first day of the water year, Oct 1 (e.g., day_start = 2 starts at hour 49)
day_end = 3 #day_end = 365 is the final day of the water year, Sept 30

#these 3 entries (year, day start and day end) will eventually be argv to the script so that it can be run from bash script
# water_year = int(sys.argv[1])
# day_start = int(sys.argv[1])
# day_end = int(sys.argv[1])


### DEFINE PATHS ###
## path to PF outputs 
#path_outputs = '/glade/scratch/tijerina/CONUS2/spinup_WY2003/run_inputs/' 
path_outputs = f'/hydrodata/PFCLM/Taylor/simulations/{water_year}/' #f'/WY{water_year}/'

## PFCLM run name
runname = f'Taylor_{water_year}' #f'CONUS2_{water_year}'

## directory to save averages to
#directory_out = f'/glade/scratch/tijerina/CONUS2/spinup_WY2003/averages'
directory_out = '/home/dtt2/CONUS2/analysis_scripts/Taylor_test_outputs'


### READING ALL STATIC VARIABLES AND DOMAIN INFO NEEDED ###
## DATA ACCESSOR VARIABLES 
run = Run.from_definition(f'{path_outputs}/{runname}.pfidb') #CONUS2
#correcting the metfilepath (folder names where changed after Taylor runs, pfidb still have old paths)
run.Solver.CLM.MetFilePath = f'/hydrodata/PFCLM/Taylor/simulations/{water_year}/NLDAS/'
data = run.data_accessor
porosity = data.computed_porosity 
specific_storage = data.specific_storage 
###################################################mannings = data.mannings
mannings = run.Mannings.Geom.domain.Value
## remove input filenames for TopoSlopes to force the data accessor to read the output slopes
## this fixes a windows issue
run.TopoSlopesX.FileName = None
run.TopoSlopesY.FileName = None
slopex = data.slope_x 
slopey = data.slope_y 
mask = data.mask

## formatting the mask so that values outside the domain are NA and inside the domain are 1
## check with mask that has 0 and 1
active_mask=mask.copy()
active_mask[active_mask > 0] = 1

nz = 5 #10
ny = 47 #3256
nx = 45 #4442

dx = 1000
dy = 1000
dz = 5 # 200
dz_3d = data.dz

# apparently it's good to use high numbers when saving files to speed up reading?
# for write_pfb function
p = 5 #72
q = 5 #48
r = 1


### COMPUTE AVERAGES AND SAVE PFB FILES ### 
for day in range(day_start,day_end):

    timestamp_day_out = str(int(day+1)).rjust(3, '0')

    ##INITIALIZE WHATEVER DYNAMIC VARIABLES THAT NEED HOURLY READING
    overland_flow = np.zeros((ny, nx)) # Flow
    soil_moisture = np.zeros((nz,ny,nx)) # Soil Moisture
    wtd = np.zeros((ny, nx)) # Water Table Depth
    surface_storage = np.zeros((ny,nx)) # Surface Water Storage
    # Subsurface Storage Components
    subsurface_storage = np.zeros((nz,ny,nx)) # Total Subsurface Storage
    gw_storage = np.zeros((nz,ny,nx)) # Groundwater Storage
    sm_storage = np.zeros((nz,ny,nx)) # Soil Moisture Storage

    
    for h in range(day*24+1,(day+1)*24+1):
        #### I *THINK* that to average these for CONUS (so assuming UTC-6), this would change to range(day*24+1+6,(day+1)*24+1+6):
        timestamp_reading = str(int(h)).rjust(5, '0')
        
        #read pressure and saturation at timestep 
        saturation = read_pfb(f'{path_outputs}{runname}.out.satur.{timestamp_reading}.pfb') * active_mask
        pressure = read_pfb(f'{path_outputs}{runname}.out.press.{timestamp_reading}.pfb') * active_mask
        print(f'reading {path_outputs}{runname}.out... at time {timestamp_reading}')
        
        ################### 
        # Computations
        ###################
        # Flow [m^3/s] 
        overland_flow = hydro.calculate_overland_flow_grid(pressure, slopex, slopey, mannings, dx, dy, mask = active_mask)
        
        #Soil Moisture [-]
        soil_moisture += saturation * porosity
        
        # Water Table Depth
        wtd = hydro.calculate_water_table_depth(pressure, saturation, dz_3d)
        
        # Surface Storage
        ## total surface storage for this time step is the summation of substorage surface across all x/y slices <-- from other script, is this still TRUE??
        surface_storage += hydro.calculate_surface_storage(pressure, dx, dy, mask = active_mask)
        
        # Total Subsurface Storage
        subsurface_storage += hydro.calculate_subsurface_storage(porosity, pressure, saturation, specific_storage, dx, dy, dz_3d, mask = active_mask)
        
        # Groundwater Storage (THIS IS ONLY THE BOTTOM LAYER, SHOULD BE CHANGED WRT WTD)
        gw_storage += subsurface_storage[0,...]
        
        # Soil Moisture Storage (THIS IS ONLY THE SUM OF THE TOP 4 LAYERS, SHOULD BE CHANGED WRT WTD)
        sm_storage += np.sum(subsurface_storage[1:4,...], axis = 0)

               
    ### compute average for select variables ###
    # note: flow is ACCUMULATED, so no need to average here
    soil_moisture /= 24
    wtd /= 24 
    surface_storage /= 24
    subsurface_storage /= 24
    gw_storage /= 24
    sm_storage /= 24

    #subsurface[active_mask==0]=-10**(38) ### ???????????
    
    ### SAVE VARIABLES AS PFB FILES
    write_pfb(f'{directory_out}/flow.{water_year}.daily.{timestamp_day_out}.pfb',overland_flow,dx=dx,dy=dy,dz=dz,P=p,Q=q,R=r,dist=False)
    write_pfb(f'{directory_out}/SM.{water_year}.daily.{timestamp_day_out}.pfb',soil_moisture,dx=dx,dy=dy,dz=dz,P=p,Q=q,R=r,dist=False)
    write_pfb(f'{directory_out}/WTD.{water_year}.daily.{timestamp_day_out}.pfb',wtd,dx=dx,dy=dy,dz=dz,P=p,Q=q,R=r,dist=False)
    write_pfb(f'{directory_out}/SURF_WATstorage.{water_year}.daily.{timestamp_day_out}.pfb',surface_storage,dx=dx,dy=dy,dz=dz,P=p,Q=q,R=r,dist=False)
    write_pfb(f'{directory_out}/SUBstorage.{water_year}.daily.{timestamp_day_out}.pfb',subsurface_storage,dx=dx,dy=dy,dz=dz,P=p,Q=q,R=r,dist=False)
    write_pfb(f'{directory_out}/GWstorage.{water_year}.daily.{timestamp_day_out}.pfb',gw_storage,dx=dx,dy=dy,dz=dz,P=p,Q=q,R=r,dist=False)
    write_pfb(f'{directory_out}/SMstorage.{water_year}.daily.{timestamp_day_out}.pfb',sm_storage,dx=dx,dy=dy,dz=dz,P=p,Q=q,R=r,dist=False)
    

