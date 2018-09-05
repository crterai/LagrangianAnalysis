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
import subprocess

def transfer_attributes(f_in,f_out)
    """
    f_in and f_out point to netcdfs
    This function transfers the netcdf attributes from f_in to f_out
    """
    att_keys = f_in1.attributes.keys()
    att_dic = {}
    for i in range(len(att_keys)):
        att_dic[i]=att_keys[i],f_in1.attributes[att_keys[i]]
        to_out = att_dic[i]
    setattr(f_out,to_out[0],to_out[1])
    return f_out

def add_git_hash(f_out)
    """
    Adds the git hash (version of the code) to the f_out
    """
    label = subprocess.check_output(["git", "describe","--always"]).strip()
    setattr(f_out,'git_hash',label)
    return f_out

def return_git_hash
    """
    Returns the git hash of the current commit
    """
    label = subprocess.check_output(["git", "describe","--always"]).strip()
    return label

    
