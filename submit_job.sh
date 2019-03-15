#!/bin/bash -l
#SBATCH --job-name=make_100day_means1
#SBATCH --time=05:00:00
#SBATCH --nodes=9
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
###SBATCH --mail-user=xyz@abc.com
#SBATCH --licenses=cscratch1
#SBATCH -C haswell 
#SBATCH -A m2840 
#SBATCH --qos=premium

srun -N 1 ./run_match_traj_exec.sh 0 2000 &
srun -N 1 ./run_match_traj_exec.sh 2000 4000 &
srun -N 1 ./run_match_traj_exec.sh 4000 6000 &
srun -N 1 ./run_match_traj_exec.sh 6000 8000 &
srun -N 1 ./run_match_traj_exec.sh 8000 10000 &
srun -N 1 ./run_match_traj_exec.sh 10000 12000 &
srun -N 1 ./run_match_traj_exec.sh 12000 14000 &
srun -N 1 ./run_match_traj_exec.sh 14000 16000 &
srun -N 1 ./run_match_traj_exec.sh 16000 18000 &
wait
