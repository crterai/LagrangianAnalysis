#!/usr/bin/env python
"""
This script regrids variables onto a common 1x1 deg grid
"""

import argparse,datetime,gc,re,sys,time
import cdms2 as cdm
import MV2 as MV     #stuff for dealing with masked values.
import cdutil as cdu
import glob
import os
from string import replace
import numpy as np
#from durolib import globalAttWrite,writeToLog,trimModelList
from socket import gethostname
import create_variables
import create_netcdfs

#model_output_location='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg/'
#model_prefix='longcam5I_L30_20081001_00Z_f09_g16_1024'
#derived_output_location='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg/'
model_output_location='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg/'
model_prefix='Winds_longcam5I_L30_20091230_00Z_f09_g16_1024'
derived_output_location='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg/'
year='2010'
months=['01','02','03','04','05','06','07','08','09','10','11','12']
#months=['10','11','12']
#datestr=['30','31']
datestr=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
timestr=['03600','25200','46800','68400']

f_gpcp=cdm.open('~/Obs_datasets/GPCP_PDF/GPCPv1pt2_PREC_pdf.nc')
obs_freq_pdf=f_gpcp('PRECFREQPDF')
gpcp_grid=obs_freq_pdf.getGrid()
        

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
            U=f_in1('U',time=slice(0,1))
            V=f_in1('V',time=slice(0,1))
            #p0=f_in1('P0')
            #a=f_in1('hyam')
            #b=f_in1('hybm')
            #ps=f_in1('PS',time=slice(0,1))
            #P=create_variables.create_P(ps,a,b,p0)
            #q700=create_variables.Variable_hPa(Q,P,700)
            var1=U
            var2=V
            var1id=var1.id
            var2id=var2.id
            var1_regrid=var1.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
            var2_regrid=var2.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
            var1_regrid=create_netcdfs.transfer_attributes(var1,var1_regrid)
            var2_regrid=create_netcdfs.transfer_attributes(var2,var2_regrid)
            var1_regrid.notes="".join(["Regridded data to 1degx1deg with regrid_variables.py",var1_regrid.notes])
            var2_regrid.notes="".join(["Regridded data to 1degx1deg with regrid_variables.py",var2_regrid.notes])
            var1_regrid.id=var1id
            var2_regrid.id=var2id
            outfile=''.join([derived_output_location,'regridded_',model_prefix,'.cam.h1.',year,'-',mo_date,'-',date,'-',time,'.nc'])
            f_out=cdm.open(outfile,'w')
            
            f_out.write(var1_regrid)
            f_out.write(var2_regrid)
            f_out=create_netcdfs.transfer_attributes(f_in1,f_out)
            f_out=create_netcdfs.globalAttWrite(f_out) ; # Use function to write standard global atts to output file
            setattr(f_out,'script_URL','https://github.com/crterai/Analysis/commit/')
            filename=os.path.basename(__file__)
            setattr(f_out,'script_used',filename)
            f_out=create_netcdfs.add_git_hash(f_out)

            f_in1.close()
            f_out.close()
