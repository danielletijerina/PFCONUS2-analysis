This directory contains three notebooks for PFCLM output processing:  

`compute_daily_PF_averages.py`  
Computes daily average flow, water table depth, soil moisture, surface water storage, and subsurface storage from hourly PF outputs in PFB format. This mirrors the `parflow_averages.f90` script.    

`compute_daily_CLM_averages.ipynb`  
Computes daily averages from hourly CLM output PFB files. The outputs that are selected can be user defined in the top portion of the script. The current outputs are outlined in the script description and mirror the `clm_averages.f90` postprocessing script.  

`compute_Total_Water_Storage.ipynb`  
Computes daily and yearly average total water storage, which is the sum of surface water storage, subsurface storage, and SWE (converted to a storage in this script). This can't be run until the `compute_daily_variables_PF_Taylor.ipynb` and `compute_daily_variables_CLM_Taylor.ipynb` have been executed (unless you already have post processed outputs.)  
  
  
A couple notes:
Not sure the TWS is correct. Need to look into this one again. 