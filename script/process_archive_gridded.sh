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
echo $DATELIST
#DATELIST="2019022712"
cnt=6; 
for DATE in $DATELIST; do
  if [[ $DATE == *"201904"* ]]; then
    echo $DATE
    let cnt=cnt+1;
    #Each netCDF file from the RFC has minimum 7 days worth of data
    #So we only need to process every 7th file
    if [ $cnt -eq 7 ]; then
    gunzip -v ../archive/*${DATE}.nc.gz

    ./resample_tempair.py ../archive/QTE.${DATE}.nc ../archive/QTF.${DATE}.nc
    ./resample_tempair_v2.py ../archive/QTE.${DATE}.nc ../archive/QTF.${DATE}.nc
    ./resample.py ../archive/QPE.${DATE}.nc ../archive/QPF.${DATE}.nc

    gzip -v ../archive/*${DATE}.nc

    rm ../temp/*.asc

    cnt=6; 
    fi;
  fi;
done

rsync -va ../temp/*.dss ../data
