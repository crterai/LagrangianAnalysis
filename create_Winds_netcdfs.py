#!/usr/bin/env python
"""
This is an example program which loops over data 
in the CMIP5 archive and extracts some info. This 
version focuses on a specific variable and deomonstrates
how glob.glob can be used to select specific files from
a directory.
"""

import argparse,datetime,gc,re,sys,time
import cdms2 as cdm
import MV2 as MV     #stuff for dealing with masked values.
import cdutil as cdu
import glob
import os
from string import replace
import numpy as np
from durolib import writeToLog,trimModelList
from socket import gethostname
import create_variables
import create_netcdfs

model_output_location='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg_run2/'
model_prefix='longcam5I_L30_20081001_0Z_f09_g16_828'
derived_output_location='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg_run2/Winds/'
year='2009'
months=['01','02','03','04','05','06','07','08','09','10','11','12']
#months=['11','12']
#datestr=['30','31']
datestr=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
timestr=['00000','21600','43200','64800']
#timestr=['03600','25200','46800','68400']

for i in months: #np.arange(4):
    mo_date=i
    print i
    for j in datestr:
        print j
        date=j
        for k in timestr:
            time=k
            try:
                f_in1=cdm.open("".join([model_output_location,model_prefix,'.cam.h1.',year,'-',mo_date,'-',date,'-',time,'.nc']))
            except:
                print ''.join(['Tried for',mo_date,'-',date,'-',time,': moving on'])
                continue
            T=f_in1('T')
            U=f_in1('U')
            V=f_in1('V')
            p0=f_in1('P0')
            a=f_in1('hyam')
            b=f_in1('hybm')
            ps=f_in1('PS')
            P=create_variables.create_P(ps,a,b,p0)
            U_hPa,V_hPa=create_variables.Winds_hPa(U,V,P,925)
            outfile=''.join([derived_output_location,'Winds_',model_prefix,'.cam.h1.',year,'-',mo_date,'-',date,'-',time,'.nc'])
            f_out=cdm.open(outfile,'w')
            
            f_out.write(U_hPa)
            f_out.write(V_hPa)
            #f_out.write(V)
            f_out=create_netcdfs.transfer_attributes(f_in1,f_out)
            f_out=create_netcdfs.globalAttWrite(f_out) ; # Use function to write standard global atts to output file
            setattr(f_out,'script_URL','https://github.com/crterai/LagrangianAnalysis/commit/')
            setattr(f_out,'script','create_Winds_netcdfs.py')
            f_out=create_netcdfs.add_git_hash(f_out)
            #filename=os.path.basename(__file__)
            #setattr(f_out,'script_used',filename)

            f_in1.close()
            f_out.close()
