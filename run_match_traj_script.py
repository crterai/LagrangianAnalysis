#!/usr/bin/env python
"""
This script takes the Start_time passed through by run_match_traj_exec.sh, adds 2500 to get end_index, and runs the match_traj_parallelized_general script that produces the text files with the output.
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
import pandas
from match_traj_parallelized_general_library import match_traj_parallelized_general,match_traj_parallelized_general_NoAnom,match_traj_parallelized_windSST

Start_index=int(sys.argv[1])
#End_index=Start_index+2500   #Add 2500 to get the End_index (this 2500 is an arbritary choice and can be modified)
End_index=int(sys.argv[2])
match_traj_parallelized_general(Start_index,End_index)
