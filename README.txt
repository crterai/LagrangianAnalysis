# Created 2018-08-20

The list of files in this directory are written to apply Ryan Eastman's analysis of the evolution of observational cloud fields to climate model output. 

Workflow

Calculate appropriate variables for diagnosis
1)BLH, entraining qv, radiative qv, EIS, LTS
2)Calculate anomalies with respect to 100 day running mean at each grid box

Initializing boxes
1) Determine boxes that fall within study area
2) Determine snapshots 0130 or 1330 local time
3) Create boxes to track forward

Running trajectories
1) Read in U,V @ 925 hPa every Xhrs and push boxes forward
2) Locate box after 24hrs

Analyze the before and after
1) Bin/categorize data by initial X


The list of files are brief descriptions follow below:
trajectories.py - calculates trajectories of the boxes based on gridded U and V fields
createboxes.py - creates boxes that fall within the study area (lat0,lon0,lat1,lon1) and determines which time snapshot to initialize the boxes based on the mean latitude and longitude
calc_anomalies.py - calculates the anomalies of a field with respect to 100 day running mean at each grid box
createvariables.py - creates relevant 2D variables based on 3D variables (e.g. U,V at 925hPa, cloud top T, BLH from cloud top T minus SST, 
