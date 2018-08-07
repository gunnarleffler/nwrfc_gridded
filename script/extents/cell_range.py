#!/usr/bin/python
# program initialization
import os, sys

if (len(sys.argv) < 2 or sys.argv[1] == '-h'):
    print sys.argv[0], ' gricell_file'
    print 'Finds min, max, and range of cell indices from an'
    print 'HEC-HMS gridcell parameter file'
    exit(0)

    
lineNumber = 0
xPos = 0
yPos = 1
thisIsFirstCell = True

cellfile =open(sys.argv[1], 'r')
for line in cellfile:
  lineNumber += 1
  parts = line.split(':')
  if (len(parts) > 1):
    if(parts[0].lower() == 'parameter order'):
      position = 0
      paramList = (parts[1].lower()).split()
      for item in paramList:
        if (item.strip(',') == 'xcoord'): xPos = position
        if (item.strip(',') == 'ycoord'): yPos = position
        position = position + 1
        
    key = (parts[0].strip()).lower()
    if(key == 'gridcell' or key == 'grid cell'):
      values = (parts[1].lower()).split()
      try:
        xValue = int(values[xPos])
        yValue = int(values[yPos])
      except:
        print "Problem witn line %d" % lineNumber
      if (thisIsFirstCell):
        xMin = xValue
        xMax = xValue
        yMin = yValue
        yMax = yValue
        thisIsFirstCell = False
      else:
        if(xValue < xMin): xMin = xValue
        if(yValue < yMin): yMin = yValue
        if(xValue > xMax): xMax = xValue
        if(yValue > yMax): yMax = yValue
      
print "SubGridOrigin: %d, %d" % (xMin, yMin)
print "SubGridExtents: %d, %d" % (xMax - xMin +1, yMax - yMin +1)

print "basins2clip line:"
print "%s,%d,%d,%d,%d" % (sys.argv[1].split(".")[0],yMax - yMin +1, xMax - xMin +1, xMin*2000, yMin*2000)

cellfile.close()
exit(0)
