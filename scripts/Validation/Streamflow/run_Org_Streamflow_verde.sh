#!/bin/bash
#SBATCH --job-name=Org_streamflow         # create a short name for your job
#SBATCH --nodes=1                # node count
#SBATCH --ntasks=1               # total number of tasks across all nodes
#SBATCH --cpus-per-task=1        # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --mem-per-cpu=20G         # memory per cpu-core (4G is default)
#SBATCH --time=12:00:00          # total run time limit (HH:MM:SS)
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=dtijerina@princeton.edu


module purge
module load parflow-ml

cd /home/dtt2/CONUS2/PFCONUS2-analysis/scripts/Validation/Streamflow/
python3 1_Organize_Streamflow.py > RUNLOG_org_streamflow.txt