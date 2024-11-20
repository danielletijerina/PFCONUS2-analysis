# Calculate Daily Averages of Forcing Variables 
###############################################

# Inputs:
# - Interpolated NLDAS forcing as .pfb 

# Outputs:
# - File(s) that includes daily average of chosen forcing variable

#################################################################################

### Change these inputs and file paths: ###

#these 3 entries (year, day start and day end) will eventually be argv to the script so that it can be run from bash script
water_year = 2003
day_start = 0 # day_start = 0 is the first day of the water year, Oct 1 or 000001_000024
day_end = 364 # day_end = 364 is the final day of the water year, Sept 30 or 008737_to_008760

#list of forcing variables you want
variables_forcing = ['Temp']
#indication whether you want the mean (1) or the sum (0)
variables_forcing_mean = [1]

# directory where hourly forcing files are located
directory_in_forcing = f'/glade/p/univ/ucsm0002/CONUS2/Forcing'

# directory to save averages to
directory_out_forcing = f'/glade/scratch/tijerina/NLDAS_averages/WY{water_year}'

#################################################################################

### READING ALL STATIC VARIABLES NEEDED
nz = 10
ny = 3256
nx = 4442

dx = 1000
dy = 1000
dz = 200

#apparently it's good to use high numbers when saving files to speed up reading?
p = 48
q = 36
r = 1

#################################################################################

### Compute daily averages ###
for day in range(day_start,day_end):

    timestamp_day_out = str(int(day+1)).rjust(3, '0')

    #READING FORCING VARIABLES
    #timestamps beginning and ending of the day
    h_start_forcing = str(int(day*24+1)).rjust(6, '0')
    h_end_forcing = str(int((day+1)*24)).rjust(6, '0')
    
    #looping through the forcing variables you want an average for
    for ind_forcing in range(len(variables_forcing)):
        var=variables_forcing[ind_forcing]
        forcing = read_pfb(f'{directory_in_forcing}/WY{water_year}/NLDAS.{var}.{h_start_forcing}_to_{h_end_forcing}.pfb')
        #sum over the 24h and divide by 24
        if variables_forcing_mean[ind_forcing]==1:
            forcing = np.sum(forcing,axis=0)/24

        write_pfb(f'{directory_out_forcing}/NLDAS.{var}.daily.{timestamp_day_out}.pfb',forcing,dx=dx,dy=dy,dz=dz,P=p,Q=q,R=r,dist=False)
        print(f'Saving {var}: day {timestamp_day_out}')