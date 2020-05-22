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
model_output_location='/global/cscratch1/sd/terai/UP/archive/longcam5I_L30_20081001_00Z_f09_g16_1024/atm/hist/'
model_prefix='longcam5I_L30_20081001_00Z_f09_g16_1024'
derived_output_location='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg/'
year='2009'
#months=['01','02','03','04','05','06','07','08','09']
months=['10','11','12']
#datestr=['30','31']
datestr=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
timestr=['00000','21600','43200','64800']

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
            lts_prefix='LTS_longcam5I_L30_20081001_00Z_f09_g16_1024'
            f_in2=cdm.open("".join(['/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg/',lts_prefix,'.cam.h1.',year,'-',mo_date,'-',date,'-',time,'.nc']))
            Q=f_in1('Q',time=slice(0,1))
            OMEGA=f_in1('OMEGA',time=slice(0,1))
            prect=f_in1('PRECT',time=slice(0,1))
            lts=f_in2('LTS',time=slice(0,1))
            p0=f_in1('P0')
            a=f_in1('hyam')
            b=f_in1('hybm')
            ps=f_in1('PS',time=slice(0,1))
            P=create_variables.create_P(ps,a,b,p0)
            q700=create_variables.Variable_hPa(Q,P,700)
            omega700=create_variables.Variable_hPa(OMEGA,P,700)
            omega850=create_variables.Variable_hPa(OMEGA,P,850)
            var1=q700
            var2=omega700
            var3=omega850
            var4=prect
            var1_regrid=var1.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
            var2_regrid=var2.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
            var1_regrid=create_netcdfs.transfer_attributes(var1,var1_regrid)
            var2_regrid=create_netcdfs.transfer_attributes(var2,var2_regrid)
            var1_regrid.notes="".join(["Regridded data to 1degx1deg with regrid_variables.py",var1_regrid.notes])
            var2_regrid.notes="".join(["Regridded data to 1degx1deg with regrid_variables.py",var2_regrid.notes])
            
            var3_regrid=var3.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
            var4_regrid=var4.regrid(gpcp_grid,regridTool='esmf',regridMethod='bilinear')
            var3_regrid=create_netcdfs.transfer_attributes(var3,var3_regrid)
            var4_regrid=create_netcdfs.transfer_attributes(var4,var4_regrid)
            var3_regrid.notes="".join(["Regridded data to 1degx1deg with regrid_variables.py",var3_regrid.notes])
            var4_regrid.notes="".join(["Regridded data to 1degx1deg with regrid_variables.py",var4_regrid.notes])
            
            outfile=''.join([derived_output_location,'regridded_Explvariables_',model_prefix,'.cam.h1.',year,'-',mo_date,'-',date,'-',time,'.nc'])
            f_out=cdm.open(outfile,'w')
            
            f_out.write(var1_regrid)
            f_out.write(var2_regrid)
            f_out.write(var3_regrid)
            f_out.write(var4_regrid)
            f_out=create_netcdfs.transfer_attributes(f_in1,f_out)
            f_out=create_netcdfs.globalAttWrite(f_out) ; # Use function to write standard global atts to output file
            setattr(f_out,'script_URL','https://github.com/crterai/Analysis/commit/')
            f_out=create_netcdfs.add_git_hash(f_out)
            filename=os.path.basename(__file__)
            setattr(f_out,'script_used',filename)

            f_in1.close()
            f_out.close()
