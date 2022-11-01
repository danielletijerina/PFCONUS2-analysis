#!/bin/bash
#PBS -N oct_PF_avg
#PBS -A UCSM0009
#PBS -q regular 
#PBS -m bae
#PBS -M dtijerina@princeton.edu
#PBS -l walltime=12:00:00 
#PBS -l select=1:mpiprocs=36
#PBS -j oe

#PBS -o log.oe

source /etc/profile.d/modules.sh
ml conda
conda activate parflow-npl

source /glade/u/home/tijerina/.parflow.3.11.bashrc

cd /glade/work/tijerina/PFCONUS2-analysis/scripts/PFCLM_Averaging_Scripts
python3 compute_daily_PF_averages.py