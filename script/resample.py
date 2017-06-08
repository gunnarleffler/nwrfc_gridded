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
import string
import sys

#execute on command line passing QPE and QPF netcdf grids for 1st and second arguemnt
# Otherwise edit below to specify paths
'''
Execute on command line passing QPE and QPF netcdf grids for 1st and second arguemnt
Otherwise edit below to specify paths, push outher inputs to arguments for more flexibility
###################################
######## Edit Inputs here #########'''
grids = {"QPE": sys.argv[1], "QPF": sys.argv[2]}
target_res = 2000.0  # meters, resolution of target grid
source_res = 2500.0  # meters, source resolution used in interpolation method
NODATA_value = -999.0
buff = 10000.0  # buffer outside of model domain [m] (clip to larger extent)
in2mm = 25.4
''' ########## End Inputs ###############
##########################################'''

#Load master list of CWMS basins and attributes for clipping
basin_data = pd.read_csv('basins2clip.csv')

for index, row in basin_data.iterrows():
  project = row['Basin']
  ncols = row['ncols']
  nrows = row['nrows']
  xllcorner = row['xllcorner']
  yllcorner = row['yllcorner']

  #Make target arrays for cell centroids
  lon_targ = np.arange(xllcorner - buff + target_res * 0.5, (
      (ncols + buff * 2 / target_res) * 2000.0) +
                       (xllcorner - buff + target_res * 0.5), 2000.0)
  lat_targ = np.arange(yllcorner - buff + target_res * 0.5, (
      (nrows + buff * 2 / target_res) * 2000.0) + yllcorner - buff + target_res
                       * 0.5, 2000.0)

  outdir = '../temp/'
  # Make output directory if it doesn't exist 
  if not os.path.exists(outdir):
    os.makedirs(outdir)

  for variable in ['QPE', 'QPF']:  # variable name to resample in source file
    # load lat-lon-value of the origin data, 
    # may need to change 'XLONG' 'XLAT' to be consistent with source netcdf
    fr = Dataset(grids[variable])
    print fr
    #ppt = fr.variables[variable][:, :, :]
    #ppt = fr.variables[variable][:, :, :]*in2mm
    ppt = fr.variables['QPF'][:, :, :] * in2mm
    lons = fr.variables['x'][:]
    lats = fr.variables['y'][:]
    time = fr.variables['time'][:]
    fr.close()

    lon, lat = np.meshgrid(lons, lats)

    # Define different projections to use
    proj4args_aea = '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 datum=NAD83 +towgs84=1,1,-1,0,0,0,0 +units=m'

    #Source Geometry
    origin_grid = pyresample.geometry.GridDefinition(lons=lon, lats=lat)

    #Target Geometry
    area_id = project
    name = 'Albers Equal Area'
    proj_id = 'aea'
    x_size = len(lon_targ)
    y_size = len(lat_targ)
    proj4_args = proj4args_aea
    area_extent = (
        min(lon_targ) - target_res * .5, min(lat_targ) - target_res * .5,
        max(lon_targ) + target_res * .5, max(lat_targ) + target_res * .5)
    targ_def = pyresample.utils.get_area_def(area_id, name, proj_id, proj4_args,
                                             x_size, y_size, area_extent)

    for t in range(len(time)):
      ppt_resample = pyresample.kd_tree.resample_gauss(
          origin_grid,
          ppt[t],
          targ_def,
          radius_of_influence=source_res,
          sigmas=source_res / 2)

      #now write out the data in asc
      for hour in range(6):
        date = datetime.datetime.fromtimestamp(time[t] * 60 + hour *
                                               3600).strftime('%Y%m%d%H')
        year = str(
            datetime.datetime.fromtimestamp(time[t] * 60 + hour * 3600).year)
        month = datetime.datetime.fromtimestamp(time[t] * 60 + hour * 3600).strftime("%m")
        hr = datetime.datetime.fromtimestamp(time[t] * 60 + hour * 3600).hour
        filename = outdir + project + "_" + variable + date + '.asc'
        TheFile = open(filename, "w")
        TheFile.write("ncols %d\n" % x_size)
        TheFile.write("nrows %d\n" % y_size)
        TheFile.write("xllcorner     %d\n" % xllcorner)
        TheFile.write("yllcorner     %d\n" % yllcorner)
        TheFile.write("cellsize      %d\n" % target_res)
        TheFile.write("NODATA_value  %d\n" % NODATA_value)
        #Note divide precip grid by 6 to convert to hourly        
        np.savetxt(TheFile, ppt_resample / 6, fmt='%.5f', delimiter=" ")
        TheFile.close()
        #now convert the asc and store in dss file
        dss_out = outdir + 'NWD_precip.' + year + '.' + month + '.dss'
        starttime = datetime.datetime.fromtimestamp(time[
            t] * 60 + hour * 3600 - 3600).strftime('%d%b%Y:%H%M')
        # Some manipulation of date strings to get the 23-24 hour in correct format for DSS
        if hr == 0:
          endtime = string.replace(
              datetime.datetime.fromtimestamp(time[t] * 60 + hour * 3600 -
                                              86400).strftime('%d%b%Y:%H%M'),
              '0000', '2400')
          print "starttime=" + starttime + "endtime=" + endtime
        else:
          endtime = datetime.datetime.fromtimestamp(time[
              t] * 60 + hour * 3600).strftime('%d%b%Y:%H%M')

        dss_path = "/SHG/" + project + "/PRECIP/" + starttime + "/" + endtime + "/RFC-" + variable + "/"
        gridconvert = os.path.join(
            os.getcwd(), 'asc2DssGrid.sh'
        ) + " zlib=true GRID=SHG in=" + filename + " dss=" + dss_out + " path=" + dss_path
        print gridconvert
        subprocess.call(gridconvert, shell=True)
