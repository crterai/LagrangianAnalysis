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

def CLDTOP_NdTCLDTOT_CAM5(SPNC,T,Z3,CLOUD,CLDTOP,TGCLDLWP,CLDTOT):
        cltop_idxmax=4
        cltop_idxmin=29
        
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

        CLDTOP_int=np.ceil(CLDTOP)
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
                        if (CloudyLWP>0.00005 and Cltop_index>cltop_idxmax and Cltop_index<=cltop_idxmin and CloudTOT>0.0 and CLOUD[t,Cltop_index,x,y]>0.0):  #set Cltop_index>34 for UPCAM
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

def create_P(ps,a,b,p0):
        P=cdu.reconstructPressureFromHybrid(ps,a,b,p0)
        return P

def Winds_hPa(U,V,P,pressurelevel):
        # Calculates and creates a file with pressurelevel hPa winds
        pressurelevel_pascal=pressurelevel*100.
        U_hPa=cdu.logLinearInterpolation(U,P,levels=pressurelevel_pascal)
        U_hPa.long_name=''.join(['U at ',str(pressurelevel),'hPa'])
        U_hPa.id='U'
        U_hPa.notes='U manipulated by cdutils.logLinearInterpolation'
        V_hPa=cdu.logLinearInterpolation(V,P,levels=pressurelevel_pascal)
        V_hPa.long_name=''.join(['V at ',str(pressurelevel),'hPa'])
        V_hPa.notes='V manipulated by cdutils.logLinearInterpolation'
        V_hPa.id='V'
        return U_hPa,V_hPa

def EIS_LTS(T,P,RELHUM):
        #Calculates the Lower Tropospheric Stability (LTS) and Estimated Inversion Strenght (EIS)
        Theta_700=cdu.logLinearInterpolation(T,P,levels=70000)*(1000./750.)**(2./7.)
        Theta_700=cdu.averager(Theta_700,axis='z')
        Theta_1000=cdu.logLinearInterpolation(T,P,levels=100000)
        Theta_1000=cdu.averager(Theta_1000,axis='z')
        LTS=Theta_700-Theta_1000
        LTS.id='LTS'
        LTS.long_name='Lower tropospheric stability'
        LTS.units='K'
        # !!! Still need to develop EIS !!!
        EIS=LTS
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
