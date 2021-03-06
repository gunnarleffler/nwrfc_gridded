#!/bin/env python3
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
import pytz

#execute on command line passing QPE and QPF netcdf grids for 1st and second arguemnt
# Otherwise edit below to specify paths
'''
Execute on command line passing QPE and QPF netcdf grids for 1st and second arguemnt
Otherwise edit below to specify paths, push outher inputs to arguments for more flexibility
###################################
######## Edit Inputs here #########'''
try:
  grids = {"QPE": sys.argv[1], "QPF": sys.argv[2]}
  gridkeys = ["QPF", "QPE"]
except:
  grids = {"QPE": sys.argv[1]}
  gridkeys = ["QPE"]
target_res = 2000.0  # meters, resolution of target grid
source_res = 2500.0  # meters, source resolution used in interpolation method
NODATA_value = -999.0
buff = 10000.0  # buffer outside of model domain [m] (clip to larger extent)
in2mm = 25.4
''' ########## End Inputs ###############
##########################################'''

def timeOffset (dt):
  """
    dt is a datetime object
    function will return 480 if in Standard time or 420 if in Daylight Savings time.
  """
  localtime = pytz.timezone('US/Pacific')
  if bool(localtime.localize(dt).dst()):
    return 420.
  return 480.

def snap (value, interval):
  return int(round (value/float(interval))*interval)

#Load master list of CWMS basins and attributes for clipping
basin_data = pd.read_csv('basins2clip.csv')

for index, row in basin_data.iterrows():
  project = row['Basin']
  ncols = row['ncols']
  nrows = row['nrows']
  xllcorner = row['xllcorner']
  yllcorner = row['yllcorner']
  # Make target arrays for cell centroids
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

  for variable in gridkeys:  # variable name to resample in source file
    # load lat-lon-value of the origin data, 
    # may need to change 'XLONG' 'XLAT' to be consistent with source netcdf
    fr = Dataset(grids[variable])
    print(fr)
    try:
      ppt = fr.variables[variable][:, :, :] * in2mm
    except:
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
      time[t] += timeOffset(datetime.datetime.fromtimestamp(time[t] * 60))
      t_stamp = datetime.datetime.fromtimestamp(time[t] * 60)
      t_stamp = t_stamp.replace(hour=snap(t_stamp.hour,6))

      date = t_stamp.strftime('%Y%m%d%H')
      year = str(t_stamp.year)
      month = t_stamp.strftime("%m")
      hr = t_stamp.hour
      filename = outdir + project + "_" + variable + date + '.asc'
      TheFile = open(filename, "w")
      TheFile.write("ncols %d\n" % x_size)
      TheFile.write("nrows %d\n" % y_size)
      TheFile.write("xllcorner     %d\n" % (xllcorner-buff))
      TheFile.write("yllcorner     %d\n" % (yllcorner-buff))
      TheFile.write("cellsize      %d\n" % target_res)
      TheFile.write("NODATA_value  %d\n" % NODATA_value)
      #Note divide precip grid by 6 to convert to hourly        
      np.savetxt(TheFile, ppt_resample, fmt='%.5f', delimiter=" ")
      TheFile.close()
      #now convert the asc and store in dss file
      dss_out = outdir + 'NWD_precip.' + year + '.' + month + '.dss'
      # Some manipulation of date strings to get the 24 hour in correct format for DSS
      if hr == 0:
        endtime = (t_stamp - datetime.timedelta(hours=24)).strftime('%d%b%Y:%H%M').replace( '0000', '2400')
        starttime = (t_stamp - datetime.timedelta(hours=6)).strftime('%d%b%Y:%H%M')
        print("starttime=" + starttime + "endtime=" + endtime)
      else:
        endtime = t_stamp.strftime('%d%b%Y:%H%M')
        starttime = (t_stamp - datetime.timedelta(hours=6)).strftime('%d%b%Y:%H%M')
      dss_path = "/SHG/" + project + "/PRECIP/" + starttime + "/" + endtime + "/RFC-" + variable + "/"
      gridconvert = os.path.join(
            os.getcwd(), 'asc2DssGrid.sh'
        ) + " zlib=true GRID=SHG in=" + filename + " dss=" + dss_out + " path=" + dss_path
      subprocess.call(gridconvert, shell=True)

      #The following block is for writing blended paths
      dss_path = "/SHG/" + project + "/PRECIP/" + starttime + "/" + endtime + "/RFC-QPB/"
      gridconvert = os.path.join(
            os.getcwd(), 'asc2DssGrid.sh'
        ) + " zlib=true GRID=SHG in=" + filename + " dss=" + dss_out + " path=" + dss_path
      print(gridconvert)
      subprocess.call(gridconvert, shell=True)
