###########################################
### Process and save CLM daily averages
###########################################

# This script takes hourly CLM outputs as PFB files and computes the daily averages to be saved as PFB files.
# DTT & EL, 10/2022

# Inputs:
# - Directory where CLM outputs are and directory where you want to save output
# - Hourly PFB files of CLM outputs
# - Water year and day start/end

# Outputs:
# - PFB files for daily average of each USER SELECTED variable. This is defined with `variables_clm`  
# - The outputs important for CONUS2 (DTT, from MMF CONUS1 outputs)  
#     - Latent heat (LH) – CLM out layer 1 [W/m^2]
#     - Sensible heat flux (SH) – CLM out layer 3 [W/m^2]
#     - ground evaporation without condensation (qflx_grnd) – CLM out layer 6 [mm/s]
#     - Vegetation transpiration (qflx_trans) – CLM out layer 9 [mm/s]
#     - Snow water equivalent (SWE) – CLM out layer 11 [mm]
#     - Ground temperature (Tgrnd) – CLM out layer 12 [K] skin temp
#     - Soil temperature (Tsoil) – CLM out layer 14 - last layer [K] *** This script outputs all soil temp layers as a 3D array
#     - Total evapotranspiration (qflx_evap_tot) - CLM out layer 5 [mm/s] *** NOT converted in this script  


# Notes (10/23/22):  
# - ET from qflx_evap_tot is just the direct CLM output. Do we want to convert this here? Is there a different way we want to calculate ET? 
#   (PFTools' `calculate_evapotranspiration` currently has weird units, so was recommended against using this).  
#   - Kept the ET calculation in as a comment, but you don't need this here because you can just output `qflx_evap_tot`
# - Soil Temp in this script is saved as a 3D array (temp for each soil layer), which is different than the Fortran scripts 
#   which only saved the CLM layer 14, temp @5cm


import numpy as np
from parflow import Run
import sys
from parflow.tools.io import read_pfb,write_pfb
import parflow.tools.hydrology as hydro


NCLMOUTPUTS = 13 + 4 #13 (number variables) + number of layers over which CLM is active, NZ root

### DEFINE WATER YEAR, START DAY, & END DAY ###
water_year = 1999
day_start = 364 #day_start = 0 is the first day of the water year, Oct 1 (e.g., day_start = 2 starts at hour 49)
day_end = 365 #day_end = 365 is the final day of the water year, Sept 30

#these 3 entries (year, day start and day end) will eventually be argv to the script so that it can be run from bash script
# water_year = int(sys.argv[1])
# day_start = int(sys.argv[1])
# day_end = int(sys.argv[1])


### DEFINE PATHS ###
## path to CLM hourly outputs
#path_outputs = '/glade/scratch/tijerina/CONUS2/spinup_WY2003/run_inputs/'
path_outputs = f'/hydrodata/PFCLM/Taylor/simulations/{water_year}/' #f'/WY{water_year}/'

## PFCLM run name
runname = f'Taylor_{water_year}' #f'CONUS2_{water_year}'
# runname = 'spinup.wy2003'


## directory to save averages to
#directory_out = f'/glade/scratch/tijerina/CONUS2/spinup_WY2003/averages'
directory_out = '/home/dtt2/CONUS2/analysis_scripts/Taylor_test_outputs'


### READING ALL STATIC VARIABLES AND DOMAIN INFO NEEDED ###
####### TAYLOR ########

nz = 5 #10
ny = 47 #3256
nx = 45 #4442

dx = 1000
dy = 1000
dz = 5 # 200
#dz_3d = data.dz

# apparently it's good to use high numbers when saving files to speed up reading?
# for write_pfb function
p = 5 #72
q = 5 #48
r = 1

#### CONUS #######

# nz = 10
# ny = 3256
# nx = 4442

# dx = 1000
# dy = 1000
# dz = 200
## dz_3d = data.dz

# #apparently it's good to use high numbers when saving files to speed up reading?
# p = 48
# q = 36
# r = 1


### DEFINE CLM AVERAGES TO BE COMPUTED ###
#list of clm variables you want
variables_clm = ['eflx_lh_tot', 'eflx_sh_tot', 'qflx_evap_grnd','qflx_tran_veg', 'swe_out', 't_grnd', 't_soil']

## indication for whether you want the mean (1) or the sum (0)
## The order here should correspond to the list made in `variables_clm` 
variables_clm_mean = [1,1,0,0,1,1,1] 

# Don't change this
ALL_CLM = ['eflx_lh_tot','eflx_lwrad_out','eflx_sh_tot','eflx_soil_grnd','qflx_evap_tot','qflx_evap_grnd','qflx_evap_soi','qflx_evap_veg','qflx_tran_veg','qflx_infl','swe_out','t_grnd','qflx_qirr','t_soil']

### CLM Outputs for reference ###
# eflx_lh_tot    # CLM 1 / Py[0]   # latent heat flux total [W/m2] using the silo variable LatentHeat;
# eflx_lwrad_out # CLM 2 / Py[1]   # outgoing long-wave radiation [W/m2] using the silo variable LongWave;
# eflx_sh_tot    # CLM 3 / Py[2]   # sensible heat flux total [W/m2] using the silo variable SensibleHeat;
# eflx_soil_grnd # CLM 4 / Py[3]   # ground heat flux [W/m2] using the silo variable GroundHeat;
# qflx_evap_tot  # CLM 5 / Py[4]   # total evaporation [mm/s] using the silo variable EvaporationTotal;
# qflx_evap_grnd # CLM 6 / Py[5]   # ground evaporation without condensation [mm/s] using the silo variable EvaporationGround- NoSublimation;
# qflx_evap_soi  # CLM 7 / Py[6]   # soil evaporation [mm/s] using the silo variable EvaporationGround;
# qflx_evap_veg  # CLM 8 / Py[7]   # vegetation evaporation (canopy) and transpiration (mms-1) using the silo variable EvaporationCanopy;
# qflx_tran_veg  # CLM 9 / Py[8]   # vegetation transpiration [mm/s] using the silo variable Transpiration;
# qflx_infl      # CLM 10 / Py[9]  # soil infiltration [mm/s] using the silo variable Infiltration;
# swe_out        # CLM 11 / Py[10] # snow water equivalent [mm] using the silo variable SWE;
# t_grnd         # CLM 12 / Py[11] # ground surface temperature [K] using the silo variable TemperatureGround;
# qflx_qirr      # CLM 13 / Py[12] # irrigation flux
# t_soil         # CLM 14-top layer #soil temperature by layer


### COMPUTE AVERAGES AND SAVE PFB FILES ### 
for day in range(day_start,day_end):

    timestamp_day_out = str(int(day+1)).rjust(3, '0')

    ##INITIALIZE WHATEVER DYNAMIC VARIABLES THAT NEED HOURLY READING 
    #et = np.zeros((ny,nx)) 
    
    if not variables_clm == False:
        clm_output = np.zeros((NCLMOUTPUTS,ny,nx))
    for h in range(day*24+1,(day+1)*24+1):
        timestamp_reading = str(int(h)).rjust(5, '0')

        #CLM Variables
        clm_output += read_pfb(f'{path_outputs}{runname}.out.clm_output.{timestamp_reading}.C.pfb')
        print(f'reading {path_outputs}{runname}.out.clm_output.{timestamp_reading}.C.pfb')
        
        ## Calculate evapotranspiration from qflx_evap_tot
        #et += clm_output[4, ...] # NO CONVERSION [mm/s]
        #et += clm_output[4, ...] * 3600 / 1000 #mm/s > mm/h > [m/h]
        #et += clm_output[4, ...] * 3600 / 1000 * dx * dy #mm/s > mm/h > [m^3/h]
        

    # ### compute average for average variables
    #et /= 24

    # ### SAVE VARIABLES
    #write_pfb(f'{directory_out}/ET.{water_year}.daily.{timestamp_day_out}.pfb',et,dx=dx,dy=dy,dz=dz,P=p,Q=q,R=r,dist=False)
   

    #Compute averages CLM outputs
    for ind_clm in range(len(variables_clm)):
        #Check if it's t_soil, then it's 3D!
        if variables_clm[ind_clm] == 't_soil':
            clm_save = clm_output[14:,:,:]
        else:
            ind_in_clmoutput = ALL_CLM.index(variables_clm[ind_clm])
            clm_save = clm_output[ind_in_clmoutput,:,:]
        if variables_clm_mean[ind_clm]==1:
            clm_save/=24
        
        #SAVE VARIABLES CLM outputs
        write_pfb(f'{directory_out}/{variables_clm[ind_clm]}.{water_year}.daily.{timestamp_day_out}.pfb',clm_save,dx=dx,dy=dy,dz=dz,P=p,Q=q,R=r,dist=False)

    