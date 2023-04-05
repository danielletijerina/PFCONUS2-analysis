#!/bin/bash
#PBS -N oct_CLM_avg
#PBS -A UCSM0009
#PBS -q casper 
#PBS -m bae
#PBS -M dtijerina@princeton.edu
#PBS -l walltime=5:00:00 
#PBS -l select=1:ncpus=1:mem=100GB
#PBS -j oe

#PBS -o logCLM.oe

source /etc/profile.d/modules.sh
ml conda
conda activate parflow-npl

source /glade/u/home/tijerina/.parflow.3.12.bashrc

cd /glade/work/tijerina/PFCONUS2-analysis/scripts/PFCLM_Averaging_Scripts
python3 compute_daily_CLM_averages.py > RUNLOG_CLM_avg.txt