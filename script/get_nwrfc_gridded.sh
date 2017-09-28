#!/bin/bash
# get_nwrfc_gridded.sh
#
# Downloads gridded data in netCDF format and converts to a .DSS file. 
# //www.nwrfc.noaa.gov/weather/netcdf/

. ~/.env_vars
. $DX_HOME/control/lib/dx_functions.sh

# Exit unless flag file indicates we run on this server
#------------------------------------------------------

feed_status nwdp nwrfc_gridded get_nwrfc_gridded.sh >/dev/null 2>&1
if [ "$?" -ne "0" ]; then
  echo nwdp/nwrfc_gridded/get_nwrfc_gridded.sh not configured for this node
  exit
fi

# Test/create a lock directory for mutual exclusion
#--------------------------------------------------

LOCK_DIR=$DX_HOME/nwdp/nwrfc_gridded/logs/lock
$DX_LIB/lock_dir $LOCK_DIR 2
if [ $? -ne 0 ]; then
  exit
fi

# Downloads gridded data in netCDF format and unzip
#---------------------------------------------------

DATE=`date "+%Y%m%d"`
YEAR=`date "+%Y"`
URLBASE=https://www.nwrfc.noaa.gov/weather/netcdf/$YEAR/$DATE

cd $DX_HOME/nwdp/nwrfc_gridded/raw/
rm *.nc
rm *.gz
wget $URLBASE/QTF.${DATE}12.nc.gz
wget $URLBASE/QTE.${DATE}12.nc.gz
wget $URLBASE/QPF.${DATE}12.nc.gz
wget $URLBASE/QPE.${DATE}12.nc.gz

#cp *.gz ../archive

yes | gunzip *.gz

cd ../temp
#rm *.asc

# Resample netCDF gridded data to dss
#---------------------------------------------------
cd ../script
. env/bin/activate
./resample_tempair.py ../raw/QTE.${DATE}12.nc ../raw/QTF.${DATE}12.nc
./resample.py ../raw/QPE.${DATE}12.nc ../raw/QPF.${DATE}12.nc

cp ../temp/*.dss ../data

rm ../raw/*.nc
rm ../temp/*.asc

rmdir $LOCK_DIR
