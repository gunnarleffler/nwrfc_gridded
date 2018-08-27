#This script converts Lat-Longs to AEA Northings and Eastings using proj4
proj +proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs  -I <<EOF
-7531598        7915162
-1139199.86     714668.05
EOF