#!/usr/bin/env python
"""
This script takes the trajectory times and locations from Ryan Eastman and outputs the LWP, cloudtop height, total cloud fraction, and cloud top Nc for the corresponding locations and times.
"""

import argparse,datetime,gc,re,sys,time
import cdms2 as cdm
import MV2 as MV     #stuff for dealing with masked values.
import cdutil as cdu
import glob
import os
from string import replace
import numpy as np
from durolib import globalAttWrite,writeToLog,trimModelList
from socket import gethostname
import pandas


def match_traj_parallelized_general(Start_index,End_index):
        """
        Takes the start index of a table with trajectory times and locations and prints out total cloud fraction, LWP, cloud top height, and cloud top Nc (in m-3) at those locations and times in a txt file with name CAM5_trajectory_CLDTOT_LWP_Cltop_Nc_STARTINDEX_ENDINDEX.txt
        """
        trajectory_file='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_trajectories.dms'    #trajectory file is already specified in this case
        # open table with trajectory times and location
        Traj_table=pandas.read_table(trajectory_file,delim_whitespace=True)  
        Traj_table_array=np.array(Traj_table[0:])
        
        # For regridding - take grid from GPCPv1pt2
        f_gpcp=cdm.open('~/Obs_datasets/GPCP_PDF/GPCPv1pt2_PREC_pdf.nc')
        obs_freq_pdf=f_gpcp('PRECFREQPDF')
        gpcp_grid=obs_freq_pdf.getGrid()
        
        
        f_log=open("".join(["log_traj_",str(Start_index),"_",str(End_index),".txt"]),"w+")
        #length_traj_table=Traj_table_array.shape[0]
        length_traj_table=End_index-Start_index
        Output_table=np.zeros((length_traj_table,29)) # Create table to output data
        Output_table[:,:]=np.nan                      # Set all data to nan
        start_index=Start_index
        for i in np.arange(start_index,End_index):   #loop from start to end index
            #print i
            Output_table[i-start_index,0]=int(Traj_table_array[i,0]) #write the traj number
            #In a log file, keep track of what trajectories get analyzed
            f_log=open("".join(["log_traj_",str(Start_index),"_",str(End_index),".txt"]),"a")
            f_log.write("".join([str(int(Traj_table_array[i,0]))," \n"]))
            f_log.close()
            for j in np.arange(7):   #loop across the 7 instances along trajectory
                #Retrieve days after 2008-12-31 and time in UTC
                Day0=Traj_table_array[i,2+j]
                Time0=Traj_table_array[i,9+j]
                # Add exception when Time is 24 hrs = 0 hrs the next day
                if Time0>=24:
                    Day0=Traj_table_array[i,2+j]+1
                relday0=cdu.cdtime.reltime(Day0,"days since 2008-12-31")
                comptime0=cdu.cdtime.r2c(relday0)
                str_comptime0month=str(comptime0.month)
                str_comptime0day=str(comptime0.day)
                if ~(Day0>0):
                    continue   #Skip cases where the date or time is NaN
                if comptime0.month<10:   #Add zero to single digit months
                    str_comptime0month=''.join(['0',str(comptime0.month)])
                if comptime0.day<10:     #Add zero to single digit days
                    str_comptime0day=''.join(['0',str(comptime0.day)])
                str_day=''.join(['2009-',str_comptime0month,'-',str_comptime0day])
                #Decide which file to access based on time of day
                if Time0<6:
                    str_time0='00000'
                    time_index0=np.floor(Time0)
                if Time0>=6 and Time0<12:
                    str_time0='21600'
                    time_index0=np.floor(Time0)-6
                if Time0>=12 and Time0<18:
                    str_time0='43200'
                    time_index0=np.floor(Time0)-12
                if Time0>=18 and Time0<24:
                    str_time0='64800'
                    time_index0=np.floor(Time0)-18
                if Time0>=24:
                    str_time0='00000'
                    time_index0=0
                str_time=''.join([str_day,'-',str_time0])
                filelocation='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg/'
                fileprefix='longcam5I_L30_20081001_00Z_f09_g16_1024.cam.h1.'
                # Access the dataset using cdms2 tools
                f_CloudTop=cdm.open(''.join([filelocation,'CloudTopv2_',fileprefix,str_time,'.nc']))
                time_index0=int(time_index0)  #Convert any decimals to integer to index
                lat0=Traj_table_array[i,16+j] #Locate the latitude from the trajectory table
                lon0=Traj_table_array[i,23+j]
                # Take the time slice and box with 5 x 5 deg. around interested area
                LWP_grid=f_CloudTop('TGCLDLWP',time=slice(time_index0,time_index0+1),lat=(lat0-5,lat0+5),lon=(lon0-5,lon0+5))
                CLDTOT_grid=f_CloudTop('CLDTOT',time=slice(time_index0,time_index0+1),lat=(lat0-5,lat0+5),lon=(lon0-5,lon0+5))
                CltopZ3_grid=f_CloudTop('CltopZ3',time=slice(time_index0,time_index0+1),lat=(lat0-5,lat0+5),lon=(lon0-5,lon0+5))
                CltopSPNC_grid=f_CloudTop('CltopSPNC',time=slice(time_index0,time_index0+1),lat=(lat0-5,lat0+5),lon=(lon0-5,lon0+5))
                # Regrid the data to 1x1 deg boxes using the grid from GPCP (see above)
                LWP_regridded=LWP_grid.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
                CLDTOT_regridded=CLDTOT_grid.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
                CltopZ3_regridded=CltopZ3_grid.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
                CltopSPNC_regridded=CltopSPNC_grid.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
                # Take the value from the grid box that lies within 1deg box around the point
                LWP=LWP_regridded(lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
                CLDTOT=CLDTOT_regridded(lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
                CltopZ3=CltopZ3_regridded(lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
                CltopSPNC=CltopSPNC_regridded(lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
                LWP_array=np.array(cdu.averager(LWP,axis='xyt'))
                CLDTOT_array=np.array(cdu.averager(CLDTOT,axis='xyt'))
                CltopZ3_array=np.array(cdu.averager(CltopZ3,axis='xyt'))
                CltopSPNC_array=np.array(cdu.averager(CltopSPNC,axis='xyt'))
                # Set all very small values of zeros to NaNs
                if LWP_array<0.0001:
                    LWP_array=np.nan
                if CLDTOT_array<0.0001:
                    CLDTOT_array=np.nan
                if CltopZ3_array<0.0001:
                    CltopZ3_array=np.nan
                if CltopSPNC_array<0.0001:
                    CltopSPNC_array=np.nan

                # ********  Repeat the steps above for the 100-day mean data
                f_CloudTop_100dm=cdm.open(''.join([filelocation,'AVG100days_CloudTopv2_',fileprefix,str_time,'.nc']))
                # Take the time slice and box with 5 x 5 deg. around interested area
                LWP_grid_100dm=f_CloudTop_100dm('TGCLDLWP',time=slice(time_index0,time_index0+1),lat=(lat0-5,lat0+5),lon=(lon0-5,lon0+5))
                CLDTOT_grid_100dm=f_CloudTop_100dm('CLDTOT',time=slice(time_index0,time_index0+1),lat=(lat0-5,lat0+5),lon=(lon0-5,lon0+5))
                CltopZ3_grid_100dm=f_CloudTop_100dm('CltopZ3',time=slice(time_index0,time_index0+1),lat=(lat0-5,lat0+5),lon=(lon0-5,lon0+5))
                CltopSPNC_grid_100dm=f_CloudTop_100dm('CltopSPNC',time=slice(time_index0,time_index0+1),lat=(lat0-5,lat0+5),lon=(lon0-5,lon0+5))
                # Regrid the data to 1x1 deg boxes using the grid from GPCP (see above)
                LWP_regridded_100dm=LWP_grid_100dm.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
                CLDTOT_regridded_100dm=CLDTOT_grid_100dm.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
                CltopZ3_regridded_100dm=CltopZ3_grid_100dm.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
                CltopSPNC_regridded_100dm=CltopSPNC_grid_100dm.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
                # Take the value from the grid box that lies within 1deg box around the point
                LWP_100dm=LWP_regridded_100dm(lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
                CLDTOT_100dm=CLDTOT_regridded_100dm(lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
                CltopZ3_100dm=CltopZ3_regridded_100dm(lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
                CltopSPNC_100dm=CltopSPNC_regridded_100dm(lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
                LWP_array_100dm=np.array(cdu.averager(LWP_100dm,axis='xyt'))
                CLDTOT_array_100dm=np.array(cdu.averager(CLDTOT_100dm,axis='xyt'))
                CltopZ3_array_100dm=np.array(cdu.averager(CltopZ3_100dm,axis='xyt'))
                CltopSPNC_array_100dm=np.array(cdu.averager(CltopSPNC_100dm,axis='xyt'))
                # **************************************************************

                # Enter values into the new output table
                Output_table[i-start_index,j+1]=CLDTOT_array-CLDTOT_array_100dm
                Output_table[i-start_index,j+8]=LWP_array-LWP_array_100dm
                Output_table[i-start_index,j+15]=CltopZ3_array-CltopZ3_array_100dm
                Output_table[i-start_index,j+22]=CltopSPNC_array-CltopSPNC_array_100dm
        np.set_printoptions(precision=5)
        # Save the table into a text file with 6 significant digits
        np.savetxt(''.join(['/global/homes/t/terai/UP_analysis/Eastman_analysis/Analysis/CAM5_trajectory_CLDTOT_LWP_Cltop_Nc_',str(Start_index),'_',str(End_index),'.txt']),Output_table,delimiter=',  ',fmt='%.5e')

def match_traj_parallelized_general_NoAnom(Start_index,End_index):
        """
        Takes the start index of a table with trajectory times and locations and prints out total cloud fraction, LWP, cloud top height, and cloud top Nc (in m-3) at those locations and times in a txt file with name CAM5_trajectory_CLDTOT_LWP_Cltop_Nc_STARTINDEX_ENDINDEX.txt
        """
        trajectory_file='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_trajectories.dms'    #trajectory file is already specified in this case
        # open table with trajectory times and location
        Traj_table=pandas.read_table(trajectory_file,delim_whitespace=True)  
        Traj_table_array=np.array(Traj_table[0:])
        
        # For regridding - take grid from GPCPv1pt2
        f_gpcp=cdm.open('~/Obs_datasets/GPCP_PDF/GPCPv1pt2_PREC_pdf.nc')
        obs_freq_pdf=f_gpcp('PRECFREQPDF')
        gpcp_grid=obs_freq_pdf.getGrid()
        
        
        f_log=open("".join(["log_traj_",str(Start_index),"_",str(End_index),".txt"]),"w+")
        #length_traj_table=Traj_table_array.shape[0]
        length_traj_table=End_index-Start_index
        Output_table=np.zeros((length_traj_table,29)) # Create table to output data
        Output_table[:,:]=np.nan                      # Set all data to nan
        start_index=Start_index
        for i in np.arange(start_index,End_index):   #loop from start to end index
            #print i
            Output_table[i-start_index,0]=int(Traj_table_array[i,0]) #write the traj number
            #In a log file, keep track of what trajectories get analyzed
            f_log=open("".join(["log_traj_",str(Start_index),"_",str(End_index),".txt"]),"a")
            f_log.write("".join([str(int(Traj_table_array[i,0]))," \n"]))
            f_log.close()
            for j in np.arange(7):   #loop across the 7 instances along trajectory
                #Retrieve days after 2008-12-31 and time in UTC
                Day0=Traj_table_array[i,2+j]
                Time0=Traj_table_array[i,9+j]
                # Add exception when Time is 24 hrs = 0 hrs the next day
                if Time0>=24:
                    Day0=Traj_table_array[i,2+j]+1
                relday0=cdu.cdtime.reltime(Day0,"days since 2008-12-31")
                comptime0=cdu.cdtime.r2c(relday0)
                str_comptime0month=str(comptime0.month)
                str_comptime0day=str(comptime0.day)
                if ~(Day0>0):
                    continue   #Skip cases where the date or time is NaN
                if comptime0.month<10:   #Add zero to single digit months
                    str_comptime0month=''.join(['0',str(comptime0.month)])
                if comptime0.day<10:     #Add zero to single digit days
                    str_comptime0day=''.join(['0',str(comptime0.day)])
                str_day=''.join(['2009-',str_comptime0month,'-',str_comptime0day])
                #Decide which file to access based on time of day
                if Time0<6:
                    str_time0='00000'
                    time_index0=np.floor(Time0)
                if Time0>=6 and Time0<12:
                    str_time0='21600'
                    time_index0=np.floor(Time0)-6
                if Time0>=12 and Time0<18:
                    str_time0='43200'
                    time_index0=np.floor(Time0)-12
                if Time0>=18 and Time0<24:
                    str_time0='64800'
                    time_index0=np.floor(Time0)-18
                if Time0>=24:
                    str_time0='00000'
                    time_index0=0
                str_time=''.join([str_day,'-',str_time0])
                filelocation='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg/'
                fileprefix='longcam5I_L30_20081001_00Z_f09_g16_1024.cam.h1.'
                # Access the dataset using cdms2 tools
                f_CloudTop=cdm.open(''.join([filelocation,'CloudTopv2_',fileprefix,str_time,'.nc']))
                time_index0=int(time_index0)  #Convert any decimals to integer to index
                lat0=Traj_table_array[i,16+j] #Locate the latitude from the trajectory table
                lon0=Traj_table_array[i,23+j]
                # Take the time slice and box with 5 x 5 deg. around interested area
                LWP_grid=f_CloudTop('TGCLDLWP',time=slice(time_index0,time_index0+1),lat=(lat0-5,lat0+5),lon=(lon0-5,lon0+5))
                CLDTOT_grid=f_CloudTop('CLDTOT',time=slice(time_index0,time_index0+1),lat=(lat0-5,lat0+5),lon=(lon0-5,lon0+5))
                CltopZ3_grid=f_CloudTop('CltopZ3',time=slice(time_index0,time_index0+1),lat=(lat0-5,lat0+5),lon=(lon0-5,lon0+5))
                CltopSPNC_grid=f_CloudTop('CltopSPNC',time=slice(time_index0,time_index0+1),lat=(lat0-5,lat0+5),lon=(lon0-5,lon0+5))
                # Regrid the data to 1x1 deg boxes using the grid from GPCP (see above)
                LWP_regridded=LWP_grid.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
                CLDTOT_regridded=CLDTOT_grid.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
                CltopZ3_regridded=CltopZ3_grid.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
                CltopSPNC_regridded=CltopSPNC_grid.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
                # Take the value from the grid box that lies within 1deg box around the point
                LWP=LWP_regridded(lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
                CLDTOT=CLDTOT_regridded(lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
                CltopZ3=CltopZ3_regridded(lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
                CltopSPNC=CltopSPNC_regridded(lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
                LWP_array=np.array(cdu.averager(LWP,axis='xyt'))
                CLDTOT_array=np.array(cdu.averager(CLDTOT,axis='xyt'))
                CltopZ3_array=np.array(cdu.averager(CltopZ3,axis='xyt'))
                CltopSPNC_array=np.array(cdu.averager(CltopSPNC,axis='xyt'))
                # Set all very small values of zeros to NaNs
                if LWP_array<0.0001:
                    LWP_array=np.nan
                if CLDTOT_array<0.0001:
                    CLDTOT_array=np.nan
                if CltopZ3_array<0.0001:
                    CltopZ3_array=np.nan
                if CltopSPNC_array<0.0001:
                    CltopSPNC_array=np.nan

                # Enter values into the new output table
                Output_table[i-start_index,j+1]=CLDTOT_array
                Output_table[i-start_index,j+8]=LWP_array
                Output_table[i-start_index,j+15]=CltopZ3_array
                Output_table[i-start_index,j+22]=CltopSPNC_array
        np.set_printoptions(precision=5)
        # Save the table into a text file with 6 significant digits
        np.savetxt(''.join(['/global/homes/t/terai/UP_analysis/Eastman_analysis/Analysis/CAM5_trajectory_raw_CLDTOT_LWP_Cltop_Nc_',str(Start_index),'_',str(End_index),'.txt']),Output_table,delimiter=',  ',fmt='%.5e')

def match_traj_parallelized_metvariables(Start_index,End_index):
        """
        Takes the start index of a table with trajectory times and locations and prints out the LTS  at those locations and times in a txt file with name CAM5_trajectory_LTS_STARTINDEX_ENDINDEX.txt
        """
        trajectory_file='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_trajectories.dms'    #trajectory file is already specified in this case
        # open table with trajectory times and location
        Traj_table=pandas.read_table(trajectory_file,delim_whitespace=True)  
        Traj_table_array=np.array(Traj_table[0:])
        
        # For regridding - take grid from GPCPv1pt2
        f_gpcp=cdm.open('~/Obs_datasets/GPCP_PDF/GPCPv1pt2_PREC_pdf.nc')
        obs_freq_pdf=f_gpcp('PRECFREQPDF')
        gpcp_grid=obs_freq_pdf.getGrid()
        
        
        f_log=open("".join(["log_traj_met_",str(Start_index),"_",str(End_index),".txt"]),"w+")
        #length_traj_table=Traj_table_array.shape[0]
        length_traj_table=End_index-Start_index
        Output_table=np.zeros((length_traj_table,8)) # Create table to output data
        Output_table[:,:]=np.nan                      # Set all data to nan
        start_index=Start_index
        for i in np.arange(start_index,End_index):   #loop from start to end index
            #print i
            Output_table[i-start_index,0]=int(Traj_table_array[i,0]) #write the traj number
            #In a log file, keep track of what trajectories get analyzed
            f_log=open("".join(["log_traj_met_",str(Start_index),"_",str(End_index),".txt"]),"a")
            f_log.write("".join([str(int(Traj_table_array[i,0]))," \n"]))
            f_log.close()
            for j in np.arange(7):   #loop across the 7 instances along trajectory
                #Retrieve days after 2008-12-31 and time in UTC
                Day0=Traj_table_array[i,2+j]
                Time0=Traj_table_array[i,9+j]
                # Add exception when Time is 24 hrs = 0 hrs the next day
                if Time0>=24:
                    Day0=Traj_table_array[i,2+j]+1
                relday0=cdu.cdtime.reltime(Day0,"days since 2008-12-31")
                comptime0=cdu.cdtime.r2c(relday0)
                str_comptime0month=str(comptime0.month)
                str_comptime0day=str(comptime0.day)
                if ~(Day0>0):
                    continue   #Skip cases where the date or time is NaN
                if comptime0.month<10:   #Add zero to single digit months
                    str_comptime0month=''.join(['0',str(comptime0.month)])
                if comptime0.day<10:     #Add zero to single digit days
                    str_comptime0day=''.join(['0',str(comptime0.day)])
                str_day=''.join(['2009-',str_comptime0month,'-',str_comptime0day])
                #Decide which file to access based on time of day
                if Time0<6:
                    str_time0='00000'
                    time_index0=np.floor(Time0)
                if Time0>=6 and Time0<12:
                    str_time0='21600'
                    time_index0=np.floor(Time0)-6
                if Time0>=12 and Time0<18:
                    str_time0='43200'
                    time_index0=np.floor(Time0)-12
                if Time0>=18 and Time0<24:
                    str_time0='64800'
                    time_index0=np.floor(Time0)-18
                if Time0>=24:
                    str_time0='00000'
                    time_index0=0
                str_time=''.join([str_day,'-',str_time0])
                filelocation='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg/'
                fileprefix='longcam5I_L30_20081001_00Z_f09_g16_1024.cam.h1.'
                # Access the dataset using cdms2 tools
                f_LTS=cdm.open(''.join([filelocation,'LTS_',fileprefix,str_time,'.nc']))
                time_index0=int(time_index0)  #Convert any decimals to integer to index
                lat0=Traj_table_array[i,16+j] #Locate the latitude from the trajectory table
                lon0=Traj_table_array[i,23+j]
                # Take the time slice and box with 5 x 5 deg. around interested area
                try:
                    LTS_grid=f_LTS('LTS',time=slice(time_index0,time_index0+1),lat=(lat0-5,lat0+5),lon=(lon0-5,lon0+5))
                except:
                    f_log=open("".join(["log_traj_met_",str(Start_index),"_",str(End_index),".txt"]),"a")
                    f_log.write("Failed getting LTS in box \n")
                    f_log.close()
                    continue
                # Regrid the data to 1x1 deg boxes using the grid from GPCP (see above)
                LTS_regridded=LTS_grid.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
                # Take the value from the grid box that lies within 1deg box around the point
                LTS=LTS_regridded(lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
                LTS_array=np.array(cdu.averager(LTS,axis='xyt'))
                # Set all very small values of zeros to NaNs
                if LTS_array<-999:
                    LTS_array=np.nan

                # ********  Repeat the steps above for the 100-day mean data
                f_LTS_100dm=cdm.open(''.join([filelocation,'AVG100days_LTS_',fileprefix,str_time,'.nc']))
                # Take the time slice and box with 5 x 5 deg. around interested area
                LTS_grid_100dm=f_LTS_100dm('LTS',time=slice(time_index0,time_index0+1),lat=(lat0-5,lat0+5),lon=(lon0-5,lon0+5))
                # Regrid the data to 1x1 deg boxes using the grid from GPCP (see above)
                LTS_regridded_100dm=LTS_grid_100dm.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
                # Take the value from the grid box that lies within 1deg box around the point
                try:
                    LTS_100dm=LTS_regridded_100dm(lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
                except:
                    LTS_100dm=LTS_regridded_100dm(lat=(lat0-0.5,lat0+0.6),lon=(lon0-0.5,lon0+0.6))
                # **************************************************************

                # Enter values into the new output table
                Output_table[i-start_index,j+1]=LTS_array-LTS_100dm
        np.set_printoptions(precision=5)
        # Save the table into a text file with 6 significant digits
        np.savetxt(''.join(['/global/homes/t/terai/UP_analysis/Eastman_analysis/Analysis/CAM5_trajectory_LTS_',str(Start_index),'_',str(End_index),'.txt']),Output_table,delimiter=',  ',fmt='%.5e')

def match_traj_parallelized_metvariables_NoAnom(Start_index,End_index):
        """
        Takes the start index of a table with trajectory times and locations and prints out the LTS  at those locations and times in a txt file with name CAM5_trajectory_LTS_STARTINDEX_ENDINDEX.txt
        """
        trajectory_file='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_trajectories.dms'    #trajectory file is already specified in this case
        # open table with trajectory times and location
        Traj_table=pandas.read_table(trajectory_file,delim_whitespace=True)  
        Traj_table_array=np.array(Traj_table[0:])
        
        # For regridding - take grid from GPCPv1pt2
        f_gpcp=cdm.open('~/Obs_datasets/GPCP_PDF/GPCPv1pt2_PREC_pdf.nc')
        obs_freq_pdf=f_gpcp('PRECFREQPDF')
        gpcp_grid=obs_freq_pdf.getGrid()
        
        
        f_log=open("".join(["log_traj_met_",str(Start_index),"_",str(End_index),".txt"]),"w+")
        #length_traj_table=Traj_table_array.shape[0]
        length_traj_table=End_index-Start_index
        Output_table=np.zeros((length_traj_table,8)) # Create table to output data - 8 is a changeable number
        Output_table[:,:]=np.nan                      # Set all data to nan
        start_index=Start_index
        for i in np.arange(start_index,End_index):   #loop from start to end index
            #print i
            Output_table[i-start_index,0]=int(Traj_table_array[i,0]) #write the traj number
            #In a log file, keep track of what trajectories get analyzed
            f_log=open("".join(["log_traj_met_",str(Start_index),"_",str(End_index),".txt"]),"a")
            f_log.write("".join([str(int(Traj_table_array[i,0]))," \n"]))
            f_log.close()
            for j in np.arange(7):   #loop across the 7 instances along trajectory
                #Retrieve days after 2008-12-31 and time in UTC
                Day0=Traj_table_array[i,2+j]
                Time0=Traj_table_array[i,9+j]
                # Add exception when Time is 24 hrs = 0 hrs the next day
                if Time0>=24:
                    Day0=Traj_table_array[i,2+j]+1
                relday0=cdu.cdtime.reltime(Day0,"days since 2008-12-31")
                comptime0=cdu.cdtime.r2c(relday0)
                str_comptime0month=str(comptime0.month)
                str_comptime0day=str(comptime0.day)
                if ~(Day0>0):
                    continue   #Skip cases where the date or time is NaN
                if comptime0.month<10:   #Add zero to single digit months
                    str_comptime0month=''.join(['0',str(comptime0.month)])
                if comptime0.day<10:     #Add zero to single digit days
                    str_comptime0day=''.join(['0',str(comptime0.day)])
                str_day=''.join(['2009-',str_comptime0month,'-',str_comptime0day])
                #Decide which file to access based on time of day
                if Time0<6:
                    str_time0='00000'
                    time_index0=np.floor(Time0)
                if Time0>=6 and Time0<12:
                    str_time0='21600'
                    time_index0=np.floor(Time0)-6
                if Time0>=12 and Time0<18:
                    str_time0='43200'
                    time_index0=np.floor(Time0)-12
                if Time0>=18 and Time0<24:
                    str_time0='64800'
                    time_index0=np.floor(Time0)-18
                if Time0>=24:
                    str_time0='00000'
                    time_index0=0
                str_time=''.join([str_day,'-',str_time0])
                filelocation='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg/'
                fileprefix='longcam5I_L30_20081001_00Z_f09_g16_1024.cam.h1.'
                # Access the dataset using cdms2 tools
                f_LTS=cdm.open(''.join([filelocation,'LTS_',fileprefix,str_time,'.nc']))
                time_index0=int(time_index0)  #Convert any decimals to integer to index
                lat0=Traj_table_array[i,16+j] #Locate the latitude from the trajectory table
                lon0=Traj_table_array[i,23+j]
                # Take the time slice and box with 5 x 5 deg. around interested area
                try:
                    LTS_grid=f_LTS('LTS',time=slice(time_index0,time_index0+1),lat=(lat0-5,lat0+5),lon=(lon0-5,lon0+5))
                except:
                    f_log=open("".join(["log_traj_met_",str(Start_index),"_",str(End_index),".txt"]),"a")
                    f_log.write("Failed getting LTS in box \n")
                    f_log.close()
                    continue
                # Regrid the data to 1x1 deg boxes using the grid from GPCP (see above)
                LTS_regridded=LTS_grid.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
                # Take the value from the grid box that lies within 1deg box around the point
                try:
                    LTS=LTS_regridded(lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
                except:
                    LTS=LTS_regridded(lat=(lat0-0.5,lat0+0.6),lon=(lon0-0.5,lon0+0.6))
                LTS_array=np.array(cdu.averager(LTS,axis='xyt'))
                # Set all very small values of zeros to NaNs
                if LTS_array<-999:
                    LTS_array=np.nan

                # Enter values into the new output table
                Output_table[i-start_index,j+1]=LTS_array
        np.set_printoptions(precision=5)
        # Save the table into a text file with 6 significant digits
        np.savetxt(''.join(['/global/homes/t/terai/UP_analysis/Eastman_analysis/Analysis/CAM5_trajectory_raw_LTS_',str(Start_index),'_',str(End_index),'.txt']),Output_table,delimiter=',  ',fmt='%.5e')
