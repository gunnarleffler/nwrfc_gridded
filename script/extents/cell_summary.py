#!/usr/bin/python
# program initialization
import os, sys

if (len(sys.argv) < 2 or sys.argv[1] == '-h'):
    print sys.argv[0], ' gricell_file\n'
    print 'Searches gridcell_file_in for subbasins and prints '
    print 'the area of each subbasin to the standard output'
    exit(1)

sys.stdout.write("Reading from input file: %s\n" % sys.argv[1])
    
lineNumber = 0
isSubbasin = False
sbName = ""
sbArea = 0.0
xPos = 0  # position of column index
yPos = 1  # position of row index
tPos = 2  # position of travel-length value
aPos = 3  # position of area value
thisIsFirstCell = True
xWidth = 3
yWidth = 3

cellfile =open(sys.argv[1], 'r')
for line in cellfile:
    parts = line.split(':')
    key = (parts[0].strip().replace(' ', '').upper())
    if key == 'PARAMETERORDER':
      position = 0
      paramList = (parts[1].lower()).split()
      for item in paramList:
        if (item.strip(',') == 'xcoord'): xPos = position
        if (item.strip(',') == 'ycoord'): yPos = position
        if (item.strip(',') == 'area'): aPos = position
        if (item.strip(',') == 'travellength'): tPos = position
        position += 1
    elif key == 'GRIDCELL':
      values = parts[1].lower().split()
      xValue = int(values[xPos])
      yValue = int(values[yPos])
      aValue = float(values[aPos])
      tValue = float(values[tPos])
      sbArea += aValue
    elif key == 'SUBBASIN':
      isSubbasin = True
      sbName = parts[1].strip()
      sbArea = 0.
    elif key == 'END':
      if isSubbasin:
          sys.stdout.write("%s: %f\n" % (sbName, sbArea))

cellfile.close()
exit(0)
