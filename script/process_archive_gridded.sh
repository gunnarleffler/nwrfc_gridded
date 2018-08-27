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

cnt=9; 
for DATE in $DATELIST; do
  echo $DATE
  let cnt=cnt+1;
  #Each netCDF file from the RFC has 10 days worth of data
  #So we only need to process every 10th file
  if [ $cnt -eq 10 ]; then
    gunzip -v ../archive/*${DATE}.nc.gz

    ./resample_tempair.py ../archive/QTE.${DATE}.nc ../archive/QTF.${DATE}.nc
    ./resample.py ../archive/QPE.${DATE}.nc ../archive/QPF.${DATE}.nc

    gzip -v ../archive/*${DATE}.nc

    rm ../temp/*.asc

    cnt=0;
  fi;

done

rsync -va ../temp/*.dss ../data
