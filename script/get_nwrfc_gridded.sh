#!/bin/bash
# get_nwrfc_gridded.sh
#
# Downloads gridded data in netCDF format and converts to a .DSS file. 
# //www.nwrfc.noaa.gov/weather/netcdf/

. /usr/dx/control/lib/dx_functions.sh

# Exit unless flag file indicates we run on this server
#------------------------------------------------------

feed_status nwdp nwrfc_gridded get_nwrfc_gridded.sh >/dev/null 2>&1
if [ "$?" -ne "0" ]; then
  echo nwdp/nwrfc_gridded/get_nwrfc_gridded.sh not configured for this node
  exit
fi

# Test/create a lock directory for mutual exclusion
#--------------------------------------------------

LOCK_DIR=/usr/dx/nwdp/nwrfc_gridded/logs/lock
/usr/dx/control/lib/lock_dir $LOCK_DIR 2
if [ $? -ne 0 ]; then
  exit
fi

# Downloads gridded data in netCDF format and untar
#---------------------------------------------------

cd /usr/dx/nwdp/nwrfc_gridded/raw/
wget https://www.nwrfc.noaa.gov/weather/netcdf/precip_ptr_grid_20170207.nc.gz
wget https://www.nwrfc.noaa.gov/weather/netcdf/qpf06f_has_20170207.nc.gz

gunzip *.gz
for i in $( ls *.nc ); do
  echo item: $i
  tar -xvf $i
done

cd ../temp
rm *.asc

# Downloads gridded data in netCDF format and untar
#---------------------------------------------------
cd ../script
. env/bin/activate
./resample.py

cp ../temp/nwd* ../data

rmdir $LOCK_DIR
