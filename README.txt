# Created 2018-08-20
# Updated 2020-09-28

A workflow outline and the list of files in this directory that are written to apply Ryan Eastman's analysis of the evolution of observational cloud fields to climate model output. 

Necessary set up

Obtain CDAT (Community Data Analysis Tools), a python based package which these set of operations depends on. 
Installation instructions using conda can be found here: https://github.com/CDAT/cdat/wiki/install

Workflow

First load cdat environment

Calculate appropriate variables for diagnosis
1)BLH, entraining qv, radiative qv, EIS, LTS -- create_SPNC_CAM5.py, create_variables.py, create_LTS_Q_netcdfs.py

Initializing boxes
1) Determine boxes that fall within study area -- 
2) Determine MODIS snapshots 0130 or 1330 local time
3) Create boxes to track forward in time
This set of operations are done by Ryan Eastman.

Running trajectories
1) Read in U,V @ 925 hPa every Xhrs and push boxes forward
2) Locate box after 12, 24, 36, 48, 60, 72 hrs
This set is also done by Ryan Eastman.

Analyze the before and after 
1) Calculate anomalies with respect to 100 day running mean at each grid box -- make_100day_means.sh, make_100day_means_atEnds.sh
2) Using the location of the boxes from the forward trajectories, retrieve variable for each trajectory. 


The list of files and brief descriptions follow below:
LIST_OF_VARIABLES.txt - includes a list of variables needed for the analysis
analysis_lib.py - includes functions for analysis and includes a function that calculates the anomalies of a field with respect to 100 day running mean at each grid box
create_variables.py - includes functions that create relevant 2D variables based on 3D variables (e.g. U,V at 925hPa, cloud top T, BLH from cloud top T minus SST, 
create_netcdfs.py - includes functions that add metadata to the netcdfs when creating datasets

trajectories.py - calculates trajectories of the boxes based on gridded U and V fields
subset_data.py - creates subsets and boxes that fall within the study area (lat0,lon0,lat1,lon1) and determines which time snapshot to initialize the boxes based on the mean latitude and longitude
