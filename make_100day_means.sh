#!/bin/bash
#$ -cwd

#Loads NCO module and creates the 100 day means 
# inputs ($1 and $2) are the prefix (e.g. CloudTopv2) 
# and the time slot (00000, 21600,..)

module load nco/4.6.9

cd /global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg

# First move files into a separate directory, separated by Time and Type
for time in $2  #00000 21600 43200 64800
do
      mkdir ./Files_${time}_${1}
      cp ${1}_longcam5I_*${time}.nc ./Files_${time}_${1}
done

# Within each of the directories, take the average (nces) over 100days,
# which corresponds to 100 consecutive files because they are sorted by time
# Name each file based on day 50
for time in $2 #00000 21600 43200 64800
do
      cd ./Files_${time}_${1} 
      ALLFILES=($(ls ${1}_*.nc))
      #ALLFILESarray = ($ALLFILES)
      indexi=0
            while [ $indexi -lt 265 ] 
            do
                i50=50+indexi
                file50=${ALLFILES[${i50}]}
                #echo $file50
                i100=99+indexi
                filestoanalyze=${ALLFILES[@]:${indexi}:${i100}}
                nces $filestoanalyze AVG100days_${file50} 
                (( indexi++ ))
            done
done
