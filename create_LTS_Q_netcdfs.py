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

model_output_location='/global/cscratch1/sd/terai/UP/archive/longcam5I_L30_20081001_00Z_f09_g16_1024/atm/hist/'
model_prefix='longcam5I_L30_20081001_00Z_f09_g16_1024'
derived_output_location='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg/'
year='2009'
months=[str(sys.argv[1])]
#months=['01']
#months=['01']
#datestr=['23','24','25','26','27','28','29','30','31']
datestr=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
timestr=['00000','21600','43200','64800']

for i in months: #np.arange(4):
    mo_date=i
    #print i
    for j in datestr:
        #print j
        date=j
        for k in timestr:
            time=k
            try:
                f_in1=cdm.open("".join([model_output_location,model_prefix,'.cam.h1.',year,'-',mo_date,'-',date,'-',time,'.nc']))
            except:
                print ''.join(['Tried for',mo_date,'-',date,'-',time,': moving on'])
                continue
            T=f_in1('T')
            Q=f_in1('Q')
            OMEGA=f_in1('OMEGA')
            p0=f_in1('P0')
            a=f_in1('hyam')
            b=f_in1('hybm')
            ps=f_in1('PS')
            P=create_variables.create_P(ps,a,b,p0)
            LTS,EIS,Theta_700,Theta_1000=create_variables.EIS_LTS(T,P,Q)
            if len(LTS.shape) > 3:
                LTS=cdu.averager(LTS,axis=1)
            if len(Theta_700.shape) > 3:
                Theta_700=cdu.averager(Theta_700,axis=1)
                Theta_1000=cdu.averager(Theta_1000,axis=1)
            outfile=''.join([derived_output_location,'LTSplusQ_',model_prefix,'.cam.h1.',year,'-',mo_date,'-',date,'-',time,'.nc'])
            Q_700=create_variables.Variable_hPa(Q,P,700.)
            OMEGA_700=create_variables.Variable_hPa(OMEGA,P,700.)
            if len(Q_700.shape) > 3:
                Q_700=cdu.averager(Q_700,axis=1)
                OMEGA_700=cdu.averager(OMEGA_700,axis=1)
            f_out=cdm.open(outfile,'w')
            Q_700.id='Q700'
            Theta_700.id='THETA700'
            Theta_1000.id='THETA1000'
            OMEGA_700.id='OMEGA700'
            f_out.write(LTS)
            f_out.write(Q_700)
            f_out.write(Theta_700)
            f_out.write(Theta_1000)
            f_out.write(OMEGA_700)
            f_out=create_netcdfs.transfer_attributes(f_in1,f_out)
            f_out=create_netcdfs.globalAttWrite(f_out) ; # Use function to write standard global atts to output file
            setattr(f_out,'script_URL','https://github.com/crterai/Analysis/commit/')
            filename=os.path.basename(__file__)
            setattr(f_out,'script_used',filename)
            #f_out=create_netcdfs.add_git_hash(f_out)

            f_in1.close()
            f_out.close()
