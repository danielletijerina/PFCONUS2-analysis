This directory contains three notebooks for PFCLM output processing:  

`compute_daily_variables_PF_Taylor.ipynb`  
Computes daily average flow, water table depth, soil moisture, surface water storage, and subsurface storage from hourly PF outputs. This mirrors the `parflow_averages.f90` script.    

`compute_daily_variables_CLM_Taylor.ipynb`  
Computes daily averages from hourly CLM outputs. The outputs that are selected can be user defined in the top portion of the script. The current outputs are outlined in the script description and mirror the `clm_averages.f90` postprocessing script.  

`compute_Total_Water_Storage.ipynb`  
Computes daily and yearly average total water storage, which is the sum of surface water storage, subsurface storage, and SWE (converted to a storage in this script). This can't be run until the `compute_daily_variables_PF_Taylor.ipynb` and `compute_daily_variables_CLM_Taylor.ipynb` have been executed (unless you already have post processed outputs.)  
  
  
A couple notes:
- These are still drafts
- The scripts are currently set up for Taylor outputs on Verde. The file paths to outputs, as well as the domain properties ((dx, dy, dz) and (nx, ny, nz)) and the processor topology settings (p,q,r) (which is only for writing out PFBs, and IDK what the correct setting is...) will need to be changed. 