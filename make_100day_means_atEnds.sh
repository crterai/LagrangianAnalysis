#!/bin/bash
#$ -cwd

#Loads NCO module and creates the 100 day means 
# inputs ($1 and $2) are the prefix (e.g. CloudTopv2) 
# and the time slot (00000, 21600,..)

module load nco/4.7.9-intel

cd /global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg_run2/Processed

# Within each of the directories, take the average (nces) over 100days,
# which corresponds to 100 consecutive files because they are sorted by time
# Name each file based on day 50
for time in $2 #00000 21600 43200 64800
do
      cd ./Files_${time}_${1} 
      ALLFILES=($(ls ${1}_*.nc))
      #ALLFILESarray = ($ALLFILES)
      indexi=0
            while [ $indexi -lt 50 ] 
            do
                i50=50+indexi
                filei=${ALLFILES[${indexi}]}
                #echo $file50
                filestoanalyze=${ALLFILES[@]:1:${i50}}
                nces $filestoanalyze AVG100days_${filei} 
                (( indexi++ ))
            done
      cd ../
done

for time in $2 #00000 21600 43200 64800
do
      cd ./Files_${time}_${1} 
      ALLFILES=($(ls ${1}_*.nc))
      #ALLFILESarray = ($ALLFILES)
      indexi=315
            while [ $indexi -lt 366 ] 
            do
                im50=indexi-50
                filei=${ALLFILES[${indexi}]}
                #echo $file50
                i100=99+indexi
                filestoanalyze=${ALLFILES[@]:${im50}:365}
                nces $filestoanalyze AVG100days_${filei} 
                (( indexi++ ))
            done
done
