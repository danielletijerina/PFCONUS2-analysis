import numpy as np
from parflow import Run
import sys
from parflow.tools.io import read_pfb,write_pfb

NCLMOUTPUTS = 13 + 4 #13 (number variables) + number of layers over which CLM is active, NZ root

#these 3 entries (year, day start and day end) will eventually be argv to the script so that it can be run from bash script
water_year = 1990
day_start = 0
day_end = 7

# water_year = int(sys.argv[1])
# day_start = int(sys.argv[1])
# day_end = int(sys.argv[1])

path_outputs_runs = f'/wherever_your_path_is/WY{water_year}/'
runname = f'CONUS2_{water_year}'

directory_out = f'where_you_want_averages_saved'
directory_out_forcing = f'where_you_want_forcing_averages_saved'

###READING ALL STATIC VARIABLES NEEDED
# Read in porosity data
porosity = read_pfb(f'{path_outputs_runs}{runname}.out.porosity.pfb')
#...
#etc.

nz,ny,nx = porosity.shape()

nz = 10
ny = 3256
nx = 4442

dx = 1000
dy = 1000
dz = 200

#apparently it's good to use high numbers when saving files to speed up reading?
p = 48
q = 48
r = 1


#list of forcing variables you want
variables_forcing = ['SPFH']
#indication whether you want the mean (1) or the sum (0)
variables_forcing_mean = [1]

#list of clm variables you want
variables_clm = ['eflx_lh_tot','qflx_evap_grnd','qflx_tran_veg','swe_out','t_grnd','t_soil']
#indication whether you want the mean (1) or the sum (0)
variables_clm_mean = [0,0,0,1,1,1]

ALL_CLM = ['eflx_lh_tot','eflx_lwrad_out','eflx_sh_tot','eflx_soil_grnd','qflx_evap_tot','qflx_evap_grnd','qflx_evap_soi','qflx_evap_veg','qflx_tran_veg','qflx_infl','swe_out','t_grnd','qflx_qirr','t_soil']

for day in range(day_start,day_end):

    timestamp_day_out = str(int(day)).rjust(3, '0')

    ##READING FORCING VARIABLES
    #timestamps beginning and ending of the day
    h_start_forcing = str(int(day*24+1)).rjust(6, '0')
    h_end_forcing = str(int((day+1)*24)).rjust(6, '0')
    
    #looping through the forcing variables you want an average for
    for ind_forcing in range(len(variables_forcing)):
        var=variables_forcing[ind_forcing]
        forcing = read_pfb(f'/hydrodata/forcing/processed_data/CONUS2/NLDAS3/hourly/WY{water_year}/NLDAS.{var}.{h_start_forcing}_to_{h_end_forcing}.pfb')
        #sum over the 24h and divide by 24
        if variables_forcing_mean[ind_forcing]==1:
            forcing = np.sum(forcing,axis=0)/24

        write_pfb(f'{directory_out_forcing}/NLDAS.{var}.{timestamp_day_out}.pfb',forcing,dx=dx,dy=dy,dz=dz,P=p,Q=q,R=r,dist=False)


    ##INITIALIZE WHATEVER DYNAMIC VARIABLES THAT NEED HOURLY READING
    soil_moisture = np.zeros((nz,ny,nx))
    if not variables_clm == False:
        clm_output = np.zeros((NCLMOUTPUTS,ny,nz))
    for h in range(day*24+1,(day+1)*24+1):
        timestamp_reading = str(int(h)).rjust(5, '0')

        #Soil Moisture
        saturation = read_pfb(f'{path_outputs_runs}{runname}.out.satur.{timestamp_reading}.pfb')
        soil_moisture += saturation * porosity

        #CLM Variables
        clm_output += read_pfb(f'{path_outputs_runs}{runname}.out.clm_output.{timestamp_reading}.C.pfb')

    #compute average for average variables
    soil_moisture /= 24
    ##SAVE VARIABLES
    write_pfb(f'{directory_out}/{runname}.out.SM.{timestamp_day_out}.pfb',soil_moisture,dx=dx,dy=dy,dz=dz,P=p,Q=q,R=r,dist=False)

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
        write_pfb(f'{directory_out}/{runname}.out.{variables_clm[ind_clm]}.{timestamp_day_out}.pfb',clm_save,dx=dx,dy=dy,dz=dz,P=p,Q=q,R=r,dist=False)

    