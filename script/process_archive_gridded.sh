#!/bin/bash
# process_archive_gridded.sh
#
# converts to a .DSS file. 

. ~/.env_vars

# Resample netCDF gridded data to dss
#---------------------------------------------------
. env/bin/activate

cd $DX_HOME/nwdp/nwrfc_gridded/archive

for DATE in *; do
  echo $DATE
  cd ../script
  pwd 
  ./resample_tempair.py ../archive/${DATE}/QTE.${DATE}12.nc ../archive/${DATE}/QTF.${DATE}12.nc
  ./resample.py ../archive/${DATE}/QPE.${DATE}12.nc ../archive/${DATE}/QPF.${DATE}12.nc

  rm ../temp/*.asc

done

cp ../temp/*.dss ../data
