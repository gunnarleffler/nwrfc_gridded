#This script converts Lat-Longs to AEA Northings and Eastings using proj4
#proj +proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs -r <<EOF
proj +proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +towgs84=1,1,-1,0,0,0,0 +units=m -r <<EOF
#Clearwater:
45.47126N  -117.68166W
47.12405N  -114.32161W
#Willowcreek NWP:
45.16407N  -119.71212W
45.45635N  -119.24816W
EOF

#Coordinates example
#41d30'0"N   125.0W
#45d15.551666667N   -111d30
#+45.25919444444    111d30'000w
