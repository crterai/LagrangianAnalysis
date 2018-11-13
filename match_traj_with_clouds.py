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

trajectory_file='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_trajectories.dms'
Traj_table=pandas.read_table(trajectory_file,delim_whitespace=True)
Traj_table_array=np.array(Traj_table[1:])

#length_traj_table=Traj_table_array.shape[0]
length_traj_table=15
Output_table=np.zeros((length_traj_table,29))

for i in np.arange(length_traj_table):
    print i
    for j in np.arange(7):
        Day0=Traj_table_array[i,2+j]
        relday0=cdu.cdtime.reltime(Day0,"days since 2008-12-31")
        comptime0=cdu.cdtime.r2c(relday0)
        if comptime0.month<10:
            str_comptime0month=''.join(['0',str(comptime0.month)])
        if comptime0.day<10:
            str_comptime0day=''.join(['0',str(comptime0.day)])
        
        str_day=''.join(['2009-',str_comptime0month,'-',str_comptime0day])
        
        Time0=Traj_table_array[i,9+j]
        if Time0<6:
            str_time0='00000'
            time_index0=np.floor(Time0)
        if Time0>=6 and Time0<12:
            str_time0='21600'
            time_index0=np.floor(Time0)-6
        if Time0>=12 and Time0<18:
            str_time0='43200'
            time_index0=np.floor(Time0)-12
        if Time0>=18:
            str_time0='64800'
            time_index0=np.floor(Time0)-18
        str_time=''.join([str_day,'-',str_time0])
        filelocation='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg/'
        fileprefix='longcam5I_L30_20081001_00Z_f09_g16_1024.cam.h1.'
        f_CloudTop=cdm.open(''.join([filelocation,'CloudTopv2_',fileprefix,str_time,'.nc']))
        time_index0=int(time_index0)
        LWP=f_CloudTop('TGCLDLWP',time=slice(time_index0,time_index0+1),lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
        CLDTOT=f_CloudTop('CLDTOT',time=slice(time_index0,time_index0+1),lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
        CltopZ3=f_CloudTop('CltopZ3',time=slice(time_index0,time_index0+1),lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
        CltopSPNC=f_CloudTop('CltopSPNC',time=slice(time_index0,time_index0+1),lat=(lat0-0.5,lat0+0.5),lon=(lon0-0.5,lon0+0.5))
        LWP_array=np.array(LWP)
        CLDTOT_array=np.array(CLDTOT)
        CltopZ3_array=np.array(CltopZ3)
        CltopSPNC_array=np.array(CltopSPNC)
        Output_table[i,0]=int(Traj_table_array[i,0])
        Output_table[i,j+1]=CLDTOT_array
        Output_table[i,j+8]=LWP_array
        Output_table[i,j+15]=CLDTOT_array
        Output_table[i,j+23]=CltopSPNC_array
np.savetxt('CAM5_trajectory_CLDTOT_LWP_Cltop_Nc.txt',Output_table,delimiter=',  ')

