#!/usr/bin/env python
"""
Created by: Chris Terai - rterai@uci.edu

This is a library of functions that are used in the creation of new netcdf files.
Many functions in this libary attach meta-data onto netcdf files.

Tested on python-2.7 with UVCDAT.
"""

import cdat_info,cdtime,code,datetime,gc,inspect,os,pytz,re,string,sys
import cdms2 as cdm
import MV2 as MV     #stuff for dealing with masked values.
import cdutil as cdu
import glob
import os
from string import replace
import numpy as np
from socket import gethostname
import subprocess

def globalAttWrite(file_handle):
    """
    Documentation for globalAttWrite():
     -------
    The globalAttWrite() function writes standard global_attributes to an
    open netcdf specified by file_handle
    
    Original author: Paul J. Durack : pauldurack@llnl.gov
    Originally in  durolib.py

    Modifed by: Chris Terai - rterai@uci.edu
    Returns:
    -------
           Updated file_handle
    Usage: 
    ------
        >>> from create_netcdfs import globalAttWrite
        >>> file_handle=globalAttWrite(file_handle)
    
    Where file_handle is a handle to an open, writeable netcdf file
    
    Examples:
    ---------
        >>> from create_netcdfs import globalAttWrite
        >>> f = cdms2.open('data_file_name','w')
        >>> f = globalAttWrite(f)
        # Writes standard global attributes to the netcdf file specified by file_handle
            
    Notes:
    -----
        When ...
    """
    # Create timestamp, corrected to UTC for history
    local                       = pytz.timezone("America/Los_Angeles")
    time_now                    = datetime.datetime.now();
    local_time_now              = time_now.replace(tzinfo = local)
    utc_time_now                = local_time_now.astimezone(pytz.utc)
    time_format                 = utc_time_now.strftime("%d-%m-%Y %H:%M:%S %p")
    setattr(file_handle,'institution',"Department of Earth System Science, UC-Irvine")
    setattr(file_handle,'data_contact',"Chris Terai; rterai@uci.edu")
    setattr(file_handle,'history',"".join(['File processed: ',time_format,' UTC; Irvine, CA, USA']))
    setattr(file_handle,'analysis_host',"".join([gethostname(),'; UVCDAT version: ',".".join(["%s" % el for el in cdat_info.version()]), \
                                           '; Python version: ',replace(replace(sys.version,'\n','; '),') ;',');')])
    return file_handle

def transfer_attributes(f_in,f_out):
    """
    f_out = transfer_attributes(f_in,f_out)
    f_in and f_out point to netcdfs
    This function transfers the netcdf attributes from f_in to f_out
    """
    att_keys = f_in.attributes.keys()
    att_dic = {}
    for i in range(len(att_keys)):
        att_dic[i]=att_keys[i],f_in.attributes[att_keys[i]]
        to_out = att_dic[i]
        setattr(f_out,to_out[0],to_out[1])
    return f_out

def add_git_hash(f_out):
    """
    Adds the git hash (version of the code) to the f_out
    """
    label = subprocess.check_output(["git", "describe","--always"]).strip()
    setattr(f_out,'git_hash',label)
    return f_out

def add_scriptname(f_out):
    """
    Adds the name of the script that is used to create the output in the global
    attributes of the file
    """
    filename=os.path.basename(__file__)
    setattr(f_out,'script_used',filename)
    return f_out

def return_git_hash():
    """
    Returns the git hash of the current commit
    """
    label = subprocess.check_output(["git", "describe","--always"]).strip()
    return label
