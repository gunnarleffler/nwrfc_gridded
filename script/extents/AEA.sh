#This script converts Lat-Longs to AEA Northings and Eastings using proj4
proj +proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs -r <<EOF
41d30'0"N   125.0W
45d15.551666667N   -111d30
+45.25919444444    111d30'000w
EOF
