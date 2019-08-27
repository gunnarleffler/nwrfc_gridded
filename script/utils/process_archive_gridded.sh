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
  if [[ $DATE == *"201812"* ]]; then
    echo $DATE
    let cnt=cnt+1;
    #Each netCDF file from the RFC has minimum 7 days worth of data
    #So we only need to process every 7th file
    if [ $cnt -eq 7 ]; then
    gunzip -v ../archive/*${DATE}.nc.gz

    #RFC changed format for temperature input in late 2018
    if [[ $DATE = *"2017"* ]] || [[ "$fname" = *"20180"* ]]; then
      cnt=1; 
      echo "ORIGINAL"
      ./resample_tempair.py ../archive/QTE.${DATE}.nc 
    else
      cnt=6; 
      echo "NEW"
      ./resample_tempair_v2.py ../archive/QTE.${DATE}.nc 
    fi

    ./resample.py ../archive/QPE.${DATE}.nc 

    gzip -v ../archive/*${DATE}.nc

    rm ../temp/*.asc

    fi;
  fi;
done

rsync -va ../temp/*.dss ../data
