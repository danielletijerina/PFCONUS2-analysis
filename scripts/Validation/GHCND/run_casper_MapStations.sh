#!/bin/bash
#PBS -N GHCND_CONUS2_mapstations
#PBS -A UCSM0009
#PBS -q casper 
#PBS -m bae
#PBS -M dtijerina@princeton.edu
#PBS -l walltime=24:00:00 
#PBS -l select=1:ncpus=1:mem=100GB
#PBS -j oe

#PBS -o logGHCNDMap.oe

source /etc/profile.d/modules.sh
ml conda
conda activate parflow-npl

source /glade/u/home/tijerina/.parflow.3.12.bashrc

cd /glade/work/tijerina/PFCONUS2-analysis/scripts/Validation/GHCND/
python3 MapStations.py > RUNLOG_GHCND_map.txt
