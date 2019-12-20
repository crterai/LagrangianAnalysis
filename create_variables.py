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
        cltop_idxmax=16
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
                        Cltop_cloud=np.squeeze(np.array(CLOUD[t,:,x,y]))
                        Cltop_cloud[Cltop_cloud<0.2]=0.
                        Cltop_index=np.nonzero(Cltop_cloud)[0]
                        #Cltop_index=np.int(CLDTOP_int[t,x,y])                  
                        if (Cltop_index.shape[0] > 1):
                            Cltop_index=Cltop_index[0]
                        if (Cltop_index<28 and CLOUD[t,Cltop_index+1,x,y]>0.0):
                            Cltop_index=Cltop_index
                        CloudTOT=np.squeeze(CLDTOT[t,x,y])
                        CloudyLWP=TGCLDLWP[t,x,y]/CloudTOT
                        if (CloudyLWP>0.005 and Cltop_index>cltop_idxmax and Cltop_index<=cltop_idxmin and CloudTOT>0.2 and CLOUD[t,Cltop_index,x,y]>0.0):  #set Cltop_index>34 for UPCAM                                                     
                            CLDTOPZ3[t,x,y]=Z3[t,Cltop_index,x,y]
                            CLDTOPSPNC[t,x,y]=SPNC[t,Cltop_index,x,y]
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

def Variable_hPa(var,P,pressurelevel):
        # Calculates and creates a file with pressurelevel hPa winds
        pressurelevel_pascal=pressurelevel*100.
        var_hPa=cdu.logLinearInterpolation(var,P,levels=pressurelevel_pascal)
        var_id=var.id
        var_hPa.long_name=''.join([var_id,' at ',str(pressurelevel),'hPa'])
        var_hPa.id=var_id
        var_hPa.notes=''.join([var_id,' manipulated by cdutils.logLinearInterpolation'])
        return var_hPa


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

def Winds_lowestLevel(U,V,Z):
        # Calculates and creates a file with pressurelevel hPa winds
        U_level1=U[:,-1,:,:]
        U_level1.long_name=''.join(['U at lowest model layer',''])
        U_level1.id='U'
        V_level1=V[:,-1,:,:]
        V_level1.long_name=''.join(['V at lowest model layer',''])
        V_level1.id='V'
        Windspeed_level1=(U_level1**2+V_level1**2)**0.5
        Windspeed_level1.long_name='Wind speed at lowest model layer'
        Windspeed_level1.notes='(U_level1**2+V_level1**2)**0.5'
        Windspeed_level1.units='m s-1'
        Windspeed_level1.id='WINDSPEED'
        Z_level1=Z[:,-1,:,:]
        Z_level1.long_name=''.join(['Z at lowest model layer',''])
        Z_level1.id='Z3'
        return U_level1,V_level1,Windspeed_level1,Z_level1

def EIS_LTS(T,P,RELHUM):
        #Calculates the Lower Tropospheric Stability (LTS) and Estimated Inversion Strenght (EIS)
        Theta_700=cdu.logLinearInterpolation(T,P,levels=70000)*(1000./700.)**(2./7.)
        Theta_700=cdu.averager(Theta_700,axis='z')
        Theta_1000=cdu.logLinearInterpolation(T,P,levels=100000)
        Theta_1000=cdu.averager(Theta_1000,axis='z')
        LTS=Theta_700-Theta_1000
        LTS.id='LTS'
        LTS.long_name='Lower tropospheric stability'
        LTS.units='K'
        Theta_700.long_name='Potential temperature at 700hPa'
        Theta_700.units='K'
        Theta_1000.long_name='Potential temperature at 1000hPa'
        Theta_1000.units='K'
        # !!! Still need to develop EIS !!!
        EIS=LTS
        return LTS,EIS,Theta_700,Theta_1000

def BLH(P,T,Z3):
        # Calculates the boundary layer height (BLH), which is defined as the level of maximum dTheta/dZ
        mv_time=Z3.getTime()
        mv_lat=Z3.getAxis(2)
        mv_lon=Z3.getAxis(3)
        z3_units=Z3.units
        mv_typecode=Z3.typecode()
        t_units=T.units
        T=np.array(T)
        Theta=T*(100000./P)**(2./7.)
        Z3=np.array(Z3)
        dThetadZ3=(Theta[:,1:,:,:]-Theta[:,:-1,:,:])/(Z3[:,1:,:,:]-Z3[:,:-1,:,:])
        Z3_avheight=(Z3[:,1:,:,:]+Z3[:,:-1,:,:])/2.
        BLH_array=np.zeros((Z3.shape[0],Z3.shape[2],Z3.shape[3]))
        dThetadZ3_array=np.zeros((Z3.shape[0],Z3.shape[2],Z3.shape[3]))

        id_max_dThetadZ3=np.argmax(dThetadZ3[:,13:,:,:],axis=1)
        max_dThetadZ3=np.amax(dThetadZ3[:,13:,:,:],axis=1)
        dThetadZ3_array=max_dThetadZ3
        Z3_avheight_subset=Z3_avheight[:,13:,:,:]
        for x in np.arange(Z3.shape[2]):
            for y in np.arange(Z3.shape[3]):
                for t in np.arange(Z3.shape[0]):
                    BLH_array[t,x,y]=Z3_avheight_subset[t,id_max_dThetadZ3[t,x,y],x,y]
        
        BLH_var=cdm.createVariable(BLH_array,typecode=mv_typecode,axes=[mv_time,mv_lat,mv_lon],id='BLH')
        BLH_var.units=z3_units
        BLH.long_name='Boundary Layer Height based on height with maximum dTheta/dZ below 10000 m'
        dThetadZ3_var=cdm.createVariable(dThetadZ3_array,typecode=mv_typecode,axes=[mv_time,mv_lat,mv_lon],id='dThetadZ')
        dThetadZ3_var.long_name='Maximum dTheta/dZ below 10000 m'
        dThetadZ3_var.units='K m-1'
        return BLH_var,dThetadZ3_var
