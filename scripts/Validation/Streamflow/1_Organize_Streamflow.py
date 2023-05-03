### Make CSV of CONUS2 flow at matched gages ###
### DTT, 05/23

# This script is split into two main parts: 1) reading in CONUS2 gridded total (aggregated) daily flow for the full domain and creating a dataframe of CONUS2 flow for cells that have been matched with USGS gages in the `NWM_Gage_Adjustments_final.csv`. 2) matching the gages that both have flow between the PF csv and USGS csv retrieved from hydrodata. 
# Note that flow is converted in this script from daily accumulated flow in [m^3/h] to daily mean flow in cms or [m^3/s].

### Inputs:
# - NEED TO UPDATE THIS!!!
# - Daily total streamflow PFCLM outputs as PFBs - processed using `compute_daily_PF_averages.py`
# - USGS daily flow csv - from the hydrodata repository on Verde

### Outputs:
# - CSV of PFCLM daily mean flow (cms) with gage ID, lat/long, and CONUS2 cell location
# - two flow-matched CSVs for PF and USGS flow
# - note that the CSV outputs with 'day 001' which starts at the water year (001 == October 1)***

# Notes:
# - need to fix the no_days, currently this will only be accurate if this is started at the begninning of a water year and need to add in some dictionary or if statement to specify num days in a month or something like that.
# - ***need to change day headings so that they are more descriptive than 'day 001' and have an actual date

import sys
from parflow.tools.io import read_pfb,write_pfb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime


# Directory where PF flow PFBs are saved in
directory_out = '/glade/p/univ/ucsm0002/CONUS2/CONUS2.spinup.WY2003/averages'
organized_dir = '/glade/work/tijerina/PFCONUS2-analysis/scripts/Validation/Streamflow/Organized_Daily_Flow'

obs_data_file = 'Streamflow_USGS_obs_daily_avg_WY2003.csv' #csv of USGS flow from hydrodata
metadata_file = 'Streamflow_USGS_obs_metadata_daily_avg_WY2003.csv' #csv of USGS flow from hydrodata

ny = 3256
nx = 4442

# need to change water year and number of days
water_year = 2003
no_days = 364 


#########################################
# Read observation data and organize
obs_data = pd.read_csv(f'{organized_dir}/{obs_data_file}', index_col=['site_id'])
obs_data = obs_data.drop(columns=['Unnamed: 0'])
# remove sites with less than 365 days of observations
obs_data = obs_data.loc[(obs_data['num_obs']==365)]
# Read metadata and organize
metadata = pd.read_csv(f'{organized_dir}/{metadata_file}', index_col=['site_id'])
metadata = metadata.drop(columns=['Unnamed: 0'])
# also remove the sites with less than 365 obs from the metadata
metadata = metadata[metadata.index.isin(obs_data.index)]

# add number of observations column from the obs_data df
metadata['num_obs'] = obs_data['num_obs']
# remove num_obs from data so we can sum and calc stats
obs_data = obs_data.drop(columns=['num_obs'])


#########################################
# make CONUS2 x and y into arrays for the for loop
conusy = np.asarray(metadata['conus2_y'],dtype = 'int')
conusx = np.asarray(metadata['conus2_x'],dtype = 'int')
# Set up arrays 
pf_flow_array = np.zeros((no_days, ny, nx)) #array of full daily flow pfb
pf_flow_matched = np.zeros(obs_data.shape) #array of gage matched daily flow

### READ STREAMFLOW PFBs ###
#Read in CONUS2 daily streamflow PFBs and save as df in flow_df, convert to total accumulated in m^3/h to mean daily in cms
for i in range(no_days):
    step = str(int(i+1)).rjust(3, '0')
    print(f'{directory_out}/flow.2003.daily.{step}.pfb')
    pf_flow_pfb = np.squeeze(read_pfb(f'{directory_out}/flow.2003.daily.{step}.pfb'))
    pf_flow_array[i,...] = pf_flow_pfb/3600/24 # CONVERT FROM m^3/h to cms AND from daily accumulated to daily mean
    print(f'reading flow for day {step} and converting from total accumulated flow in m^3/h, to daily mean flow in cms')
    for j in range(len(obs_data.index)):
        if conusy[j] < 0:
            pf_flow_matched[j] = 'nan'
            #print('Gage is outside of CONUS2 range')
        else:
            pf_flow_matched[j,i] = pf_flow_array[i, conusy[j], conusx[j]]
            #print('Finding value in CONUS2 grid')

            
#########################################
### Organize and save
# Organize daily flow matched array with the same index and dates as the obs_data
pf_flow_match_df = pd.DataFrame(pf_flow_matched)
pf_flow_match_df = pf_flow_match_df.set_index(obs_data.index)
column_headers = list(obs_data.columns.values)
pf_flow_match_df.columns = column_headers
# save as csv
pf_flow_match_df.to_csv(f'{organized_dir}/PFCONUS2_Daily_matched_flow_cms{water_year}.csv', sep = ",")