set a2gexec=J:\hecexe\asc2dssGrid.exe
set dss=%1

%a2gexec% input=A754.asc dssfile=%dss% PATH=/SHG/RRN-MNR/TEMP/05APR2001:0900//INTERPOLATED/ gridtype=SHG  dunits="DEG F" dtype=INST-VAL

%a2gexec% input=A755.asc dssfile=%dss% PATH=/SHG/RRN-MNR/TEMP/05APR2001:1000//INTERPOLATED/ gridtype=SHG  dunits="DEG F" dtype=INST-VAL

%a2gexec% input=A756.asc dssfile=%dss% PATH=/SHG/RRN-MNR/TEMP/05APR2001:1100//INTERPOLATED/ gridtype=SHG  dunits="DEG F" dtype=INST-VAL

%a2gexec% input=A757.asc dssfile=%dss% PATH=/SHG/RRN-MNR/TEMP/05APR2001:1200//INTERPOLATED/ gridtype=SHG  dunits="DEG F" dtype=INST-VAL

%a2gexec% input=testel.txt dssfile=%dss% PATH=/SHG/PLACE/ELEV/25MAR2008:1200//ASCII/ dunits=M dtype=INST-VAL

%a2gexec% input=try.asc dssfile=%dss% PATH=/SHG/LC/precip/25MAR2008:1200/25MAR2008:1300/ASCII/ gridtype=SHG  zlib=true

%a2gexec% input="C:\Documents and Settings\q0hectae\My Documents\code\HEC_depot\depot\usr\hec\code\asciiGrid\asc2dssGrid\test\try.asc" dssfile=%dss% PATH=/SHG/LC/precip/25MAR2008:1200/25MAR2008:1300/long-path/ gridtype=SHG  zlib=true

%a2gexec% input=austin_impervious_area.asc dssfile=%dss% PATH="/SHG100/AUSTIN/IMPERVIOUS AREA/25MAR2008:1200//ASCII/" dunits=%% dtype=2

%a2gexec% input=IDeficitGrid.asc dssfile=%dss% PATH="/SHG/RRB/Storage Capacity///Computed/" dunits=IN dtype=INST-VAL
