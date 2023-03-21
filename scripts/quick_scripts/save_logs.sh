#!/bin/bash

# This requires that you run this from within your run directory and have a ../logs directory 

run_name="surf-press-test.CONUS2"
endtime="00288"

cp log.oe ../logs/${endtime}.log.oe
cp ${run_name}.out.kinsol.log ../logs/${endtime}.${run_name}.out.kinsol.log
cp CLM.out.clm.log ../logs/${endtime}.CLM.out.clm.log
cp ${run_name}.out.txt ../logs/${endtime}.${run_name}.out.txt
cp ${run_name}.out.log ../logs/${endtime}.${run_name}.out.log


