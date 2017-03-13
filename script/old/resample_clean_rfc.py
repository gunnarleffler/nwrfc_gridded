#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 12:21:27 2017
@author: g3enhcdf
Script to reproject and resample netcdf data to Albers Equal Area for a 
specified domain. Data is output as ascii files with arc header
Chris Frans Chris.D.Frans@usace.army.mil
"""

from netCDF4 import Dataset
import pyresample
import pandas as pd
import os
import numpy as np
import datetime
import subprocess
import time

'''###################################
######## Edit Inputs here #########'''
project = 'skagit'
targetgrid_nc = './skagit_grid.nc'    #Grid to reproject and resample to
QPF_grid = '2017020712_QPF6hr_NetCDF.nc'
QPE_grid = '2017020712_QPE6hr_NetCDF.nc'
target_res = 2000 # meters, resolution of target grid
source_res = 2500 # meters, source resolution used in interpolation method
VAR = ['QPF','QPE'] # variable name to resample in source file
#parameters for writing arc ascii output
xllcorner = -1960000
yllcorner = 3022000
NODATA_value = -9999
''' ########## End Inputs ###############
##########################################'''
now = time.strftime("%d%b%Y")
outdir = './'+project+'_'+now+'/'
# Make output directory if it doesn't exist 
if not os.path.exists(outdir):
    os.makedirs(outdir)


# load lat-lon of the target grid
fc = Dataset(targetgrid_nc)
lon_targ = fc.variables['XLON'][:]
lat_targ = fc.variables['XLAT'][:]
fc.close()

for variable in VAR:
    # load lat-lon-value of the origin data, 
    # may need to change 'XLONG' 'XLAT' to be consistent with source netcdf
    print eval(variable+'_grid')
    fr = Dataset(eval(variable+'_grid'))
    ppt = fr.variables[variable][:,:,:]
    lons = fr.variables['x'][:]
    lats = fr.variables['y'][:]
    time = fr.variables['time'][:]
    fr.close()
    
    lon, lat = np.meshgrid(lons, lats)
    
    # Define different projections to use
    proj4args_aea = '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 datum=NAD83 +towgs84=1,1,-1,0,0,0,0 +units=m'
    
    
    #Source Geometry
    origin_grid = pyresample.geometry.GridDefinition(lons=lon,lats=lat)
    
    
    #Target Geometry
    area_id = project
    name = 'Albers Equal Area'
    proj_id = 'aea'
    x_size = len(lon_targ)
    y_size = len(lat_targ)
    proj4_args = proj4args_aea
    area_extent = (min(lon_targ)-target_res*.5,min(lat_targ)-target_res*.5,max(lon_targ)+target_res*.5,max(lat_targ)+target_res*.5)
    targ_def = pyresample.utils.get_area_def(area_id, name, proj_id, proj4_args, x_size, y_size, area_extent)
    
    for t in range(len(time)):
        ppt_resample = pyresample.kd_tree.resample_gauss(origin_grid, ppt[t], targ_def, radius_of_influence=source_res, sigmas=source_res/2,fill_value=None)
     
      #now write out the data in asc
        for hour in range(6):
            date = datetime.datetime.fromtimestamp(time[t]*60+hour*3600).strftime('%Y%m%d%H')    
            filename = outdir + project + "_" + date + '.asc'
            print filename
            TheFile=open(filename,"w")
            TheFile.write("ncols %d\n" % x_size)
            TheFile.write("nrows %d\n" % y_size)
            TheFile.write("xllcorner     %d\n" % xllcorner)
            TheFile.write("yllcorner     %d\n" % yllcorner)
            TheFile.write("cellsize      %d\n" % target_res)
            TheFile.write("NODATA_value  %d\n" % NODATA_value)
            #Note divide precip grid by 6 to convert to hourly        
            np.savetxt(TheFile, ppt_resample/6, fmt='%.5f', delimiter=" ")
            TheFile.close()
      #now convert the asc and store in dss file
            dss_out = outdir + project + '_precip.dss'
            starttime=datetime.datetime.fromtimestamp(time[t]*60+hour*3600-3600).strftime('%d%b%Y:%H%M')
            endtime=datetime.datetime.fromtimestamp(time[t]*60+hour*3600).strftime('%d%b%Y:%H%M')
            dss_path = "/SHG/"+project+"/PRECIP/"+starttime+"/"+endtime+ "/NETCDF/"
            #gridconvert = os.path.join(os.getcwd(), 'asc2dssgrid.exe')+" GRID=SHG in="+filename+" dss="+dss_out+" path="+dss_path         
            #subprocess.call(gridconvert, shell=False)





