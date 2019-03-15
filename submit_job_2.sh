#!/bin/bash -l
#SBATCH --job-name=make_100day_means2
#SBATCH --time=05:00:00
#SBATCH --nodes=9
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
###SBATCH --mail-user=xyz@abc.com
#SBATCH --licenses=cscratch1
#SBATCH -C haswell 
#SBATCH -A m2840 
#SBATCH --qos=premium

srun -N 1 ./run_match_traj_exec.sh 18000 20000 &
srun -N 1 ./run_match_traj_exec.sh 20000 22000 &
srun -N 1 ./run_match_traj_exec.sh 22000 24000 &
srun -N 1 ./run_match_traj_exec.sh 24000 26000 &
srun -N 1 ./run_match_traj_exec.sh 26000 28000 &
srun -N 1 ./run_match_traj_exec.sh 28000 30000 &
srun -N 1 ./run_match_traj_exec.sh 30000 32000 &
srun -N 1 ./run_match_traj_exec.sh 32000 34000 &
srun -N 1 ./run_match_traj_exec.sh 34000 34570 &
wait
