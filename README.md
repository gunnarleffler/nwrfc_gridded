GRIDDED DATA CONVERSION
=======================
This product downloads gridded data in netCDF format from the Northwest River Forecast Center and converts to a .DSS file.


Adding Basins
----
The basins2clip.csv file contains subbasin information this program uses to create gridded data in DSS files. To add
basins to this file add a line to the file. The coordinates are in AEA. Utilites in the script/extents directory can be
used to get basin extents from the models .mod file.


Example NetCDF Data
----

Obs Prec for the 24 hour period ending at 12Z on Dec 12, 2016.  The nc file contains 5 layers: 24hr and four 6hr files.
https://www.nwrfc.noaa.gov/weather/netcdf/precip_ptr_grid_20161216.nc.gz

Obs Temp for the previous 24 period ending at 12Z on Dec 12, 2016.  The nc file contains 6 layers: four 6hr files of instantaneous temp at 18,00,06,12Z and max and min temp.
https://www.nwrfc.noaa.gov/weather/netcdf/temperature_ptr_grid_20161216.nc.gz

Forecast Prec with layers representing 6hr precip totals extending 10 days into the future.
https://www.nwrfc.noaa.gov/weather/netcdf/qpf06f_has_2016121612f240_stegemil_201612161343.nc.gz

Forecast Max Temp with layers representing maximum daily temperature extending 10 days into the future
https://www.nwrfc.noaa.gov/weather/netcdf/tx24f_has_2016121612f240_stegemil_201612161342.nc.gz

Forecast Min Temp with layers representing minimum daily temperature extending 10 days into the future
https://www.nwrfc.noaa.gov/weather/netcdf/tn24f_has_2016121612f240_stegemil_201612161342.nc.gz

Rebuilding Virtual Environment
------------------------------
Currently this program uses Python 2.7. The dependency requirements are stored in docs/requirements.txt. You can use the following line rebuild the virtual environment.

`pip install -r requirements.txt`

