#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 12:21:27 2017
@author: g3enhcdf
Script to reproject and resample netcdf data to Albers Equal Area for a 
specified domain. Data is output as ascii files with arc header
This script was adpated for air temperature, using hermite splines
to estimate 6-hourly values from Tmin and Tmax during the forecast period
Chris Frans Chris.D.Frans@usace.army.mil
"""

from netCDF4 import Dataset
import pyresample
import pandas as pd
import os
import numpy as np
import datetime
import subprocess
import string
import sys
import itertools
import scipy.interpolate


#execute on command line passing QPE and QPF netcdf grids for 1st and second arguemnt
# Otherwise edit below to specify paths
'''
Execute on command line passing QPE and QPF netcdf grids for 1st and second arguemnt
Otherwise edit below to specify paths, push outher inputs to arguments for more flexibility
###################################
######## Edit Inputs here #########'''
grids = {"QTE": sys.argv[1], "QTF": sys.argv[2]}
target_res = 2000.0  # meters, resolution of target grid
source_res = 2500.0  # meters, source resolution used in interpolation method
NODATA_value = -999.00000
buff = 10000.0  # buffer outside of model domain [m] (clip to larger extent)
tmax_time = 23 # GMT
tmin_time = 11 # GMT
Dt=6
loc2gmt = 420. #sift to GMT, minutes
''' ########## End Inputs ###############
##########################################'''

'''############# Functions to use ##############################'''
def temp(df_daily, df_disagg,
         t_t_min, t_t_max, ts,
         t_begin, t_end):
    """
    Disaggregate temperature using a Hermite polynomial
    interpolation scheme.

    Parameters
    ----------
    df_daily:
        A dataframe of daily values.
    df_disagg:
        A dataframe of sub-daily values.
    t_t_min:
        Times at which minimum daily
        temperatures are reached.
    t_t_max:
        Times at which maximum daily
        temperatures are reached.
    ts:
        Timestep for disaggregation
    t_begin: list
        List of t_min and t_max for day previous to the
        start of `df_daily`. None indicates no extension
        of the record.
    t_end: list
        List of t_min and t_max for day after the end
        of `df_daily`. None indicates no extension of
        the record.

    Returns
    -------
    temps:
        A sub-daily timeseries of temperature.
    """
    # Calculate times of min/max temps
    time = np.array(list(next(it) for it in itertools.cycle(
                [iter(t_t_min), iter(t_t_max)])))
    temp = np.array(list(next(it) for it in itertools.cycle(
                [iter(df_daily['t_min']), iter(df_daily['t_max'])])))
    # Account for end points
    ts_ends = 1440
    time = np.append(np.insert(time, 0, time[0:2]-ts_ends), time[-2:]+ts_ends)

    # If no start or end data is provided to extend the record repeat values
    # This provides space at the ends so that extrapolation doesn't continue
    # in strange ways at the end points
    if t_begin is None:
        t_begin = temp[0:2]
    if t_end is None:
        t_end = temp[-2:]
    temp = np.append(np.insert(temp, 0, t_begin), t_end)

    # Interpolate the values
    interp = scipy.interpolate.PchipInterpolator(time, temp, extrapolate=True)
    temps = interp(ts * np.arange(0, len(df_disagg.index)))
    return temps
        
    


'''############# End of functions ##############################'''


#Load master list of CWMS basins and attributes for clipping
basin_data=pd.read_csv('basins2clip.csv')

for index, row in basin_data.iterrows():
    project = row['Basin']
    ncols = row['ncols']
    nrows = row['nrows']
    xllcorner = row['xllcorner']
    yllcorner = row['yllcorner']
    
    # Make target arrays for cell centroids
    lon_targ = np.arange(xllcorner-buff+target_res*0.5,((ncols+buff*2/target_res)*2000.0)+(xllcorner-buff+target_res*0.5),2000.0)
    lat_targ = np.arange(yllcorner-buff+target_res*0.5,((nrows+buff*2/target_res)*2000.0)+yllcorner-buff+target_res*0.5,2000.0)

    outdir = '../temp/'
    # Make output directory if it doesn't exist 
    if not os.path.exists(outdir):
      os.makedirs(outdir)

    
    for variable in ['QTE', 'QTF']:  # variable name to resample in source file
          # load lat-lon-value of the origin data, 
          # may need to change 'XLONG' 'XLAT' to be consistent with source netcdf
          fr = Dataset(grids[variable])
          print fr
          #ppt = fr.variables[variable][:, :, :]
          if variable == 'QTE':
		ta = fr.variables[variable][:, :, :]
          else:
		TAMX = fr.variables['TFMX'][:, :, :]
		TAMN = fr.variables['TFMN'][:, :, :]
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
												   
		#Here we need to convert forecast TMIN/TMAX to 6 hourly (not needed for estimated(observed))
          if variable == 'QTF':
            tmin_resample = np.empty([len(time)/2-2,y_size,x_size])
            tmax_resample = np.empty([len(time)/2-2,y_size,x_size])
            hourlyts = np.empty([(len(time)/2-2)*(24/Dt),y_size,x_size])
            t_t_min = np.empty(len(tmax_resample[:,0,0]))
            t_t_max = np.empty(len(tmax_resample[:,0,0]))
            ind_mn=0
            ind_mx=0
            for t in range(2,len(time)-2):
                    if(datetime.datetime.fromtimestamp(time[t] * 60).hour==10):
 				 tmin_resample[ind_mn,:,:] = pyresample.kd_tree.resample_gauss(origin_grid,TAMN[t],targ_def,radius_of_influence=source_res, sigmas=source_res / 2)
 				 ind_mn+=1
                    if(datetime.datetime.fromtimestamp(time[t] * 60).hour==21):        
                        tmax_resample[ind_mx,:,:] = pyresample.kd_tree.resample_gauss(origin_grid,TAMX[t],targ_def,radius_of_influence=source_res,
                            sigmas=source_res / 2)
                        ind_mx+=1
		# Now that they have been resampled and stored in new arrays, we can loop through each cell
		# and interpolate temperature
            for k in range(len(tmax_resample[:,0,0])):
                t_t_min[k] = (tmin_time+k*24)*60
                t_t_max[k] = (tmax_time+k*24)*60
            

            # Make dataframes for interpolation function
            days =  pd.date_range(datetime.datetime.fromtimestamp(time[2] * 60).strftime('%Y%m%d'), datetime.datetime.fromtimestamp(time[len(time)-3] * 60).strftime('%Y%m%d'),freq='D')

            for i in range(len(tmin_resample[0,:,0])):
                for j in range(len(tmax_resample[0,0,:])):
                   df_daily = {'t_min': pd.Series(tmin_resample[:,i,j],index=days), 't_max': pd.Series(tmax_resample[:,i,j],index=days)}
                   dates_disagg = pd.date_range(df_daily['t_min'].index[0], df_daily['t_min'].index[-1] + pd.Timedelta('1 days'), freq='{}T'.format(Dt*60))
                   df_disagg = pd.DataFrame(index=dates_disagg)[1:41]
                   hourlyts[:,i,j] = temp(df_daily,df_disagg, t_t_min, t_t_max,Dt*60,None,None)

            for t in(range(len(hourlyts))):
                date = dates_disagg[t+1].strftime('%Y%m%d%H')
                year = dates_disagg[t+1].strftime("%Y")
                month = dates_disagg[t+1].strftime("%m")
                hr = dates_disagg[t+1].strftime("%H")
                filename = outdir + project + "_" + variable + date + '.asc'
                TheFile = open(filename, "w")
                TheFile.write("ncols %d\n" % x_size)
                TheFile.write("nrows %d\n" % y_size)
                TheFile.write("xllcorner     %d\n" % (xllcorner))
                TheFile.write("yllcorner     %d\n" % (yllcorner))
                TheFile.write("cellsize      %d\n" % target_res)
                TheFile.write("NODATA_value  %.5f\n" % NODATA_value)       
                np.savetxt(TheFile, hourlyts[t,:,:], fmt='%.5f', delimiter=" ")
                TheFile.close()
                  #now convert the asc and store in dss file
                dss_out = outdir + 'NWD_temp.' + year + '.' + month + '.dss'
                starttime = dates_disagg[t].strftime('%d%b%Y:%H%M')
                  # Some manipulation of date strings to get the 23-24 hour in correct format for DSS
                if  hr=="00":
                    endtime = string.replace(dates_disagg[t-3].strftime('%d%b%Y:%H%M'), '0000', '2400')
                    print "starttime=" + starttime + "endtime="+endtime
                else:
                    endtime = dates_disagg[t+1].strftime('%d%b%Y:%H%M')
                  
                dss_path = "/SHG/" + project + "/TEMPERATURE/" + starttime + "/" + endtime + "/RFC-"+variable+"/"

                gridconvert = os.path.join(
    				os.getcwd(), 'asc2DssGrid.sh'
    				) + " zlib=true GRID=SHG in=" + filename + " dss=" + dss_out + " path=" + dss_path
                print gridconvert
                subprocess.call(gridconvert, shell=True)

                
             
             
          #Now do it for QPE, which comes in at 6-hourly increments            
          else:
              time += loc2gmt
              for t in range(len(time)):
                ta_resample = pyresample.kd_tree.resample_gauss(
                    origin_grid,
                    ta[t],
                    targ_def,
                    radius_of_influence=source_res,
                    sigmas=source_res / 2)
				#If masked arrays, fill with nodata values
                if(isinstance(ta_resample,np.ma.MaskedArray)):
					ta_resample.set_fill_value(NODATA_value)
					ta_resample = ta_resample.filled()            
                #now write out the data in asc
                
                date = datetime.datetime.fromtimestamp(time[t] * 60).strftime('%Y%m%d%H')
                year = str(datetime.datetime.fromtimestamp(time[t] * 60 ).year)
                month = str(datetime.datetime.fromtimestamp(time[t] * 60).strftime("%m"))
                hr = datetime.datetime.fromtimestamp(time[t] * 60).hour
                filename = outdir + project + "_" + variable + date + '.asc'
                TheFile = open(filename, "w")
                TheFile.write("ncols %d\n" % (x_size))
                TheFile.write("nrows %d\n" % (y_size))
                TheFile.write("xllcorner     %d\n" % xllcorner)
                TheFile.write("yllcorner     %d\n" % yllcorner)
                TheFile.write("cellsize      %d\n" % target_res)
                TheFile.write("NODATA_value  %.5f\n" % NODATA_value)       
                np.savetxt(TheFile, ta_resample, fmt='%.5f', delimiter=" ")
                TheFile.close()
                  #now convert the asc and store in dss file
                dss_out = outdir + 'NWD_temp.' + year + '.' + month + '.dss'
                starttime = datetime.datetime.fromtimestamp(time[t] * 60 - 21600).strftime('%d%b%Y:%H%M')
                  # Some manipulation of date strings to get the 23-24 hour in correct format for DSS
                if  hr==0:
                    endtime = string.replace(
                          datetime.datetime.fromtimestamp(time[t] * 60  - 86400).strftime(
                          '%d%b%Y:%H%M'), '0000', '2400')
                    print "starttime=" + starttime + "endtime="+endtime
                else:
                    endtime = datetime.datetime.fromtimestamp(time[t] * 60).strftime(
                          '%d%b%Y:%H%M')                  
                  
                dss_path = "/SHG/" + project + "/TEMPERATURE/" + starttime + "/" + endtime + "/RFC-"+variable+"/"
            
                
                gridconvert = os.path.join(
    				os.getcwd(), 'asc2DssGrid.sh'
    				) + " zlib=true GRID=SHG in=" + filename + " dss=" + dss_out + " path=" + dss_path
                print gridconvert
                subprocess.call(gridconvert, shell=True)
