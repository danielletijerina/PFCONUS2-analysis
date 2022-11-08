### Make CSV of CONUS2 flow at matched gages ###
### DTT, 10/22

# This script reads in CONUS2 gridded total (aggregated) daily flow for the full domain and creates a dataframe of CONUS2 flow for cells that have been matched with USGS gages in the `NWM_Gage_Adjustments_final.csv`. Note that flow is converted in this script from daily accumulated flow in [m^3/h] to daily mean flow in cms or [m^3/s].

### Inputs:
# - `NWM_Gage_Adjustments_final.csv` - this can be found on the CONUS2 Dropbox or in /glade/p/univ/ucsm0002/CONUS2/domain_files
# - Daily total streamflow PFCLM outputs as PFBs - processed using `compute_daily_PF_averages.py`

### Outputs:
# - CSV of PFCLM daily mean flow (cms) with gage ID, lat/long, and CONUS2 cell location
# - note that the CSV outputs with 'day 001' which starts at the water year (001 == October 1)***

# Notes:
# - need to fix the no_days, currently this will only be accurate if this is started at the begninning of a water year and need to add in some dictionary or if statement to specify num days in a month or something like that.
# - ***need to change day headings so that they are more descriptive than 'day 001' and have an actual date

import sys
from parflow.tools.io import read_pfb,write_pfb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Directory where PF flow PFBs are saved in
directory_out = '/glade/scratch/tijerina/CONUS2/spinup_WY2003/averages'

# need to change water year and number of days
water_year = 2003
no_days = 31 

### check gage locations for daily flow
NWM_gage_csv = pd.read_csv('/glade/p/univ/ucsm0002/CONUS2/domain_files/NWM_Gage_Adjustments_final.csv')


### set up pandas dataframe of gage ID, lat/long, CONUS2 x and y indices ###
flow_df = pd.DataFrame(columns = ['STNID', 'USGS_lat', 'USGS_lon', 'x_new_adj', 'y_new_adj'])
flow_df['STNID'] = NWM_gage_csv['STNID'].astype(int)
flow_df['USGS_lat'] = NWM_gage_csv['USGS_lat']
flow_df['USGS_lon'] = NWM_gage_csv['USGS_lon']
flow_df['x_new_adj'] = NWM_gage_csv['x_new_adj']
flow_df['y_new_adj'] = NWM_gage_csv['y_new_adj']

# add leading zeros to USGS gages
flow_df['STNID'] = flow_df['STNID'].astype('str').str.zfill(8)


### READ STREAMFLOW PFBs ###
# Read in CONUS2 daily streamflow PFBs and save as df in flow_df, convert to total accumulated in m^3/h to mean daily in cms
for i in range(no_days):
    step = str(int(i+1)).rjust(3, '0')
    flow_pfb = np.squeeze(read_pfb(f'{directory_out}/flow.2003.daily.{step}.pfb'))
    flow_df[f'day {step}'] = flow_pfb[flow_df['y_new_adj'],flow_df['x_new_adj']]/3600/24 # CONVERT FROM m^3/h to cms AND from daily accumulated to daily mean
    print(f'reading flow for day {step} and converting from total accumulated flow in m^3/h, to daily mean flow in cms')

    
# Create column for matching/have flow (=1) and not matching/have no flow (=0) gages
flow_df['matched'] = np.where(flow_df['day 001']>0, 1, 0)

# remove cells with no flow and make new pandas df with matching flow at CONUS2 cells and USGS gages
flow_df_matched = flow_df[flow_df.matched != 0]

# SAVE OUT PANDAS DF FOR CONUS2 FLOW
### save csv file of all matching gage locations and CONUS2 daily flow, note the USGS STNID's drop the leading zeros when saving
flow_df_matched.to_csv(f'CONUS2_daily_flow_cms_{water_year}.csv'.csv', sep = ",")