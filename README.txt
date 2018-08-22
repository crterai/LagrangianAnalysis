# Created 2018-08-20

The list of files in this directory are written to apply Ryan Eastman's analysis of the evolution of observational cloud fields to climate model output. 

The list of files are brief descriptions follow below:
trajectories.py - calculates trajectories of the boxes based on gridded U and V fields
createboxes.py - creates boxes that fall within the study area (lat0,lon0,lat1,lon1) and determines which time snapshot to initialize the boxes based on the mean latitude and longitude
calc_anomalies.py - calculates the anomalies of a field with respect to 100 day running mean at each grid box
createvariables.py - creates relevant 2D variables based on 3D variables (e.g. U,V at 925hPa, cloud top T, BLH from cloud top T minus SST, 
