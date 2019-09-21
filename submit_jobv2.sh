#!/bin/bash -l
#SBATCH --job-name=make_100daymeans_SfcWinds
#SBATCH --time=02:30:00
#SBATCH --nodes=4
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
###SBATCH --mail-user=xyz@abc.com
#SBATCH --licenses=cscratch1
#SBATCH -C haswell 
#SBATCH -A m3306
#SBATCH -p regular

srun -N 1 ./make_100day_means.sh SfcWinds 00000  &
srun -N 1 ./make_100day_means.sh SfcWinds 21600  &
srun -N 1 ./make_100day_means.sh SfcWinds 43200  &
srun -N 1 ./make_100day_means.sh SfcWinds 64800  &
wait
