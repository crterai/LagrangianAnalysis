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

def CLDTOP_NdTCLDTOT(SPNC,T,Z3,CLOUD,CLDTOP,TGCLDLWP,optionType='SP')
        mv_time=SPNC.getTime()
        mv_lat=SPNC.getAxis(2)
        mv_lon=SPNC.getAxis(3)
        spnc_units=SPNC.units
        z3_units=Z3.units
        t_units=T.units
        mv_typecode=SPNC.typecode()
  
        Z3=np.array(Z3)
        CLOUD=np.array(CLOUD)
        SPNC=np.array(SPNC)
        CLDTOT_output=CLDTOT
        TGCLDLWP_output=TGCLDLWP
        CLDTOP=np.array(CLDTOP)
        CLDTOT=np.array(CLDTOT)
        TGCLDLWP=np.array(TGCLDLWP)
        T=np.array(T)

        CLDTOP_int=np.ceil(CLDTOP)+1
        CLDTOPSPNC=np.zeros(CLDTOP.shape)
        CLDTOPZ3=np.zeros(CLDTOP.shape)
        CLDTOPT=np.zeros(CLDTOP.shape)
        for x in np.arange(Z3.shape[2]):
            for y in np.arange(Z3.shape[3]):
                TGCLDLWP_sum=np.sum(np.squeeze(TGCLDLWP[:,x,y]))
                if (TGCLDLWP_sum > 0.000001):
                    for t in np.arange(Z3.shape[0]):
                        Cltop_index=np.int(CLDTOP_int[t,x,y])
                        CloudTOT=np.squeeze(CLDTOT[t,x,y])
                        CloudyLWP=TGCLDLWP[t,x,y]/CloudTOT
                        if (CloudyLWP>0.005 and Cltop_index>cltop_idxmax and Cltop_index<cltop_idxmin and CloudTOT>0.0 and CLOUD[t,Cltop_index,x,y]>0.0):  #set Cltop_index>34 for UPCAM
                            if (optionType == 'SP'):
                                CLDTOPSPNC[t,x,y]=SPNC[t,Cltop_index,x,y]/CLOUD[t,Cltop_index,x,y]
                            else:
                                CLDTOPSPNC[t,x,y]=SPNC[t,Cltop_index,x,y]
                            CLDTOPZ3[t,x,y]=Z3[t,Cltop_index,x,y]
                            CLDTOPT[t,x,y]=T[t,Cltop_index,x,y]
                        else:
                            CLDTOPSPNC[t,x,y]=-1e15
                            CLDTOPZ3[t,x,y]=-1e15
                            CLDTOPT[t,x,y]=-1e15
                else:
                    CLDTOPSPNC[:,x,y]=-1e15
                    CLDTOPZ3[:,x,y]=-1e15
                    CLDTOPT[:,x,y]=-1e15
        CLDTOPSPNC=np.ma.masked_less(CLDTOPSPNC,-100)
        CLDTOPZ3=np.ma.masked_less(CLDTOPZ3,-100)
        CLDTOPT=np.ma.masked_less(CLDTOPT,-100)
        #cloudbase
        CLDTOT_var=CLDTOT_output
        TGCLDLWP_var=TGCLDLWP_output
        CLDTOPSPNC_var=cdm.createVariable(CLDTOPSPNC,typecode=mv_typecode,axes=[mv_time,mv_lat,mv_lon],id='CltopSPNC')
        CLDTOPZ3_var=cdm.createVariable(CLDTOPZ3,typecode=mv_typecode,axes=[mv_time,mv_lat,mv_lon],id='CltopZ3')
        CLDTOPT_var=cdm.createVariable(CLDTOPT,typecode=mv_typecode,axes=[mv_time,mv_lat,mv_lon],id='CltopT')
        CLDTOPSPNC_var.units=spnc_units
        CLDTOPZ3_var.units=z3_units
        CLDTOPT_var.units=t_units
        CLDTOPSPNC_var.long_name='Cloud drop number at cloud top'
        CLDTOPZ3_var.long_name='Cloud top height'
        CLDTOPT_var.long_name='Cloud top temperature'
        return CLDTOPSPNC_var,CLDTOPT_var,CLDTOPZ3_var,CLDTOT_var,TGCLDLWP_var

def Entrainingq_Radiativeq(Q,P,Theta):
        #Calculates the Q at the entrainment layer and the Q above that, but below 700 hPa

        return EntrainingQ,RadiativeQ

def EIS_LTS(Theta,P,RELHUM):
        #Calculates the Lower Tropospheric Stability (LTS) and Estimated Inversion Strenght (EIS)
        return LTS,EIS

def BLH(P,Theta,Z3):
        # Calculates the boundary layer height (BLH), which is defined as the 
        mv_time=Z3.getTime()
        mv_lat=Z3.getAxis(2)
        mv_lon=Z3.getAxis(3)
        z3_units=Z3.units
        mv_typecode=Z3.typecode()
  
        Z3=np.array(Z3)
        P=np.array(P)
        SPNC=np.array(SPNC)
        mv_time=SPNC.getTime()
        mv_lat=SPNC.getAxis(2)
        mv_lon=SPNC.getAxis(3)
        spnc_units=SPNC.units
        z3_units=Z3.units
        t_units=T.units
        mv_typecode=SPNC.typecode()
  
        Z3=np.array(Z3)
        CLOUD=np.array(CLOUD)
        SPNC=np.array(SPNC)
