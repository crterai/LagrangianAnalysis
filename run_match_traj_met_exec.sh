#!/bin/bash
#$ -cwd

# Loads the appropriate python environment using conda and runs the run_match_traj_script.py python script

module load python/2.7-anaconda-4.4
source activate myuvcdat

python run_match_traj_met_script.py $1 $2
