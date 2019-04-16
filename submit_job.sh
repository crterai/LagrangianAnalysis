#!/bin/bash -l
#SBATCH --job-name=make_100day_means1
#SBATCH --time=04:20:00
#SBATCH --nodes=3
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
###SBATCH --mail-user=xyz@abc.com
#SBATCH --licenses=cscratch1
#SBATCH -p regular
#SBATCH --license SCRATCH,project
#SBATCH -C haswell 
#SBATCH -A m3306

srun -N 1 ./run_match_traj_exec.sh 0 2000 &
srun -N 1 ./run_match_traj_exec.sh 2000 4000 &
srun -N 1 ./run_match_traj_exec.sh 4000 6000 &
wait
