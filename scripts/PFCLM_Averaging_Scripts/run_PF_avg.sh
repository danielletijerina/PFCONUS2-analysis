#!/bin/bash
#PBS -N oct_PF_avg_Casper
#PBS -A UCSM0009
#PBS -q casper 
#PBS -m bae
#PBS -M dtijerina@princeton.edu
#PBS -l walltime=12:00:00 
#PBS -l select=1:ncpus=1:mem=100GB
#PBS -j oe

#PBS -o logPF.oe

source /etc/profile.d/modules.sh
ml conda
conda activate parflow-npl

source /glade/u/home/tijerina/.parflow.3.12.bashrc

cd /glade/work/tijerina/PFCONUS2-analysis/scripts/PFCLM_Averaging_Scripts
python3 compute_daily_PF_averages.py > RUNLOG_PF_avg.txt