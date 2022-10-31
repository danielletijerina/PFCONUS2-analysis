### Scripts Folder Directory  

/PFCLM_Averaging_Scripts  
- Averaging scripts for daily ParFlow and CLM variables from hourly outputs: `compute_daily_***_averages.py`  
- Notebooks tested on the Taylor watershed outputs, which were copied over to the final python scripts  
- Monthly and yearly averaging notebook (script coming sooooooon)  
- TWS daily and yearly (need to add monthly) averaging from daily PFCLM outputs processed with the `compute_daily_***_averages.py`

/Validation
- Scripts used for validation of water balance components, including forcing
    /GHCND

/pressure_checks
- Notebooks used pre-transient spin-up runs to debug the pressure problems

/quick_scripts
- `pfb.array_to_geotiff.ipynb` - create a geotiff from a PFB  
- `quick_vis_outputs.ipynb` - look at single pressure, clm, evaptrans files  
- `restart_parflow-clm.ipynb` - help for restarting PFCLM and renaming CLM files  

/old
- keeping just in case or maybe to use later