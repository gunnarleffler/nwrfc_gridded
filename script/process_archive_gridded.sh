#!/bin/bash
# process_archive_gridded.sh
#
# converts to a .DSS file. 

. ~/.env_vars

# Resample netCDF gridded data to dss
#---------------------------------------------------
. env/bin/activate

cd $DX_HOME/nwdp/nwrfc_gridded/script

DATELIST=`ls -1 ../archive | awk -F"." '{print $2}' | sort -u`

for DATE in $DATELIST; do
  echo $DATE

  gunzip -v ../archive/*${DATE}.nc.gz

  ./resample_tempair.py ../archive/QTE.${DATE}.nc ../archive/QTF.${DATE}.nc
  ./resample.py ../archive/QPE.${DATE}.nc ../archive/QPF.${DATE}.nc

  gzip -v ../archive/*${DATE}.nc

  rm ../temp/*.asc

done

cp ../temp/*.dss ../data
