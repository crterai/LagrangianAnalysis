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
from durolib import globalAttWrite,writeToLog,trimModelList
from socket import gethostname
import create_variables

model_output_location='/global/cscratch1/sd/terai/UP/archive/longcam5I_L30_20081001_00Z_f09_g16_1024/atm/hist/'
model_prefix='longcam5I_L30_20081001_00Z_f09_g16_1024'
derived_output_location='/global/cscratch1/sd/terai/UP_analysis/Eastman_analysis/CAM5_1deg/'
year='2009'
#months=['02','03','04','05','06','07','08','09']
months=['01']
datestr=['24','25','26','27','28','29','30','31']
#datestr=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
timestr=['00000','21600','43200','64800']
#timestr=['03600','25200','46800','68400']

for i in months: #np.arange(4):
    mo_date=i
    print i
    for j in datestr:
        date=j
        print j
        for k in timestr:
            time=k
            try:
                f_in1=cdm.open("".join([model_output_location,model_prefix,'.cam.h1.',year,'-',mo_date,'-',date,'-',time,'.nc']))
            except:
                print ''.join(['Tried for',mo_date,'-',date,'-',time,': moving on'])
                continue
            f_in2=cdm.open("".join([model_output_location,model_prefix,'.cam.h2.',year,'-',mo_date,'-',date,'-',time,'.nc']))
            Z3=f_in1('Z3')
            T=f_in1('T')
            CLDTOT=f_in1('CLDTOT')
            TGCLDLWP=f_in1('TGCLDLWP')
            CLDTOP=f_in1('CLDTOP')
            SPNC=f_in2('ICWNC')
            CLOUD=f_in1('CLOUD')
            cldtopspnc,cldtopt,cldtopz3,cldtot,tgcldlwp=create_variables.CLDTOP_NdTCLDTOT_CAM5(SPNC,T,Z3,CLOUD,CLDTOP,TGCLDLWP,CLDTOT)
            outfile=''.join([derived_output_location,'CloudTopv3_',model_prefix,'.cam.h1.',year,'-',mo_date,'-',date,'-',time,'.nc'])
            f_out=cdm.open(outfile,'w')
            
            att_keys = f_in1.attributes.keys()
            att_dic = {}
            for i in range(len(att_keys)):
                att_dic[i]=att_keys[i],f_in1.attributes[att_keys[i]]
                to_out = att_dic[i]
            setattr(f_out,to_out[0],to_out[1])
            setattr(f_out,'comments2','Used create_variable.CLDTOP_NdTCLDTOT_CAM5 to create cloud output')
            setattr(f_out,'comments3','Updated create_variable.CLDTOP_NdTCLDTOT_CAM5 to use hightest elevation with CLOUD>0.2 as teh cltop, rather than CLDTOP output')
            globalAttWrite(f_out,options=None) ; # Use function to write standard global atts to output file
            f_out.write(cldtopspnc)
            f_out.write(cldtopz3)
            f_out.write(cldtopt)
            f_out.write(cldtot)
            f_out.write(tgcldlwp)
            f_in1.close()
            f_in2.close()
            f_out.close()
