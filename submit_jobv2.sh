#!/bin/bash -l
#SBATCH --job-name=make_100day_means2
#SBATCH --time=00:30:00
#SBATCH --nodes=4
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
###SBATCH --mail-user=xyz@abc.com
#SBATCH --licenses=cscratch1
#SBATCH -C haswell 
#SBATCH -A m2840 
#SBATCH --qos=premium

srun -N 1 ./make_100day_means_atEnds.sh CloudTopv2 00000  &
srun -N 1 ./make_100day_means_atEnds.sh CloudTopv2 21600  &
srun -N 1 ./make_100day_means_atEnds.sh CloudTopv2 43200  &
srun -N 1 ./make_100day_means_atEnds.sh CloudTopv2 64800  &
wait
