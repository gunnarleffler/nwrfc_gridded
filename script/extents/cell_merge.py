#!/usr/bin/python
# program initialization
import os, sys

if (len(sys.argv) < 3 or sys.argv[1] == '-h'):
    print sys.argv[0], ' gricell_file_in gridcell_file_out\n'
    print 'Searches gridcell_file_in for duplicate grid cell indices in '
    print 'subbasins and merges their parameter values.\n'
    print 'Also eliminates cells with routing distance under 1m or'
    print 'area under 100 sq meters.\n'
    print 'Writes result to gridcell_file_ out'
    exit(1)

sys.stdout.write("Reading from input file: %s\n" % sys.argv[1])
sys.stdout.write("Writing to output file: %s\n\n" % sys.argv[2])
    
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

# Create a dictionary and a list to hold the cells for a subbasin
cellIndex = {}
cellList = []
cellCnt = 0

try:
    outfile = open(sys.argv[2], 'w')
except:
    sys.stderr.write("Error opening %s for output." % sys.argv[2])
    exit(-1)
    
for line in open(sys.argv[1], 'r'):
  parts = line.split(':')
  if len(parts) < 2:
      # duplicate lines that don't contain keywords
      outfile.write(line)
  else:
    key = (parts[0].strip().replace(' ', '').upper())
    if key == 'PARAMETERORDER':
      outfile.write(line) 
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

      sbArea += aValue
      kIndices = (xValue, yValue)
      if kIndices in cellIndex and tValue > 0.0:
          sys.stdout.write("Found duplicate cell %d, %d in subbasin %s\n"
                         % (xValue, yValue, sbName))
          storedValues = cellList[cellIndex[kIndices]].split(':')[1].split()
          readArea = float(values[aPos])
          storedArea = float(storedValues[aPos])
          newArea = readArea + storedArea
          valCnt = 0
          newLine = parts[0] + ': '
          for value in values:
              if valCnt == xPos:
                  newLine += '%d  ' % xValue
              elif valCnt == yPos:
                  newLine += '%d  ' % yValue
              elif valCnt == aPos:
                  newLine += '%.8f  ' % newArea
              else:
                  newFloat = (readArea * float(values[valCnt]) + 
                         storedArea * float(storedValues[valCnt]))/newArea
                  newLine += '%.8f  ' % newFloat
              valCnt += 1
          cellList[cellIndex[kIndices]] = newLine.rstrip() + '\n' 
          sys.stdout.write("%s\n\n" % cellList[cellIndex[kIndices]])
      elif aValue > 0.0 and tValue > 0.0:
          cellIndex[kIndices] = cellCnt
          cellList.append(line)
          cellCnt += 1
    elif key == 'SUBBASIN':
      isSubbasin = True
      sbName = parts[1].strip()
      outfile.write(line)
    elif key == 'END':
      if isSubbasin:
          if len(str(xMax)) >= xWidth:
              xWidth = len(str(xMax)) + 1
          if len(str(xMin)) >= xWidth:
              xWidth = len(str(xMin)) + 1
          if len(str(yMax)) >= yWidth:
              yWidth = len(str(yMax)) + 1
          if len(str(yMin)) >= yWidth:
              yWidth = len(str(yMin)) + 1
          for cell in cellList:
              parts = cell.split(':')
              values = parts[1].split()
              cellIsValid = True
              area = float(values[aPos])
              tlen = float(values[tPos])
              if tlen < 0.0001 or area < 0.0001:
                  cellIsValid = False
              if cellIsValid:
                  outLine = parts[0] + ':'
                  valCnt = 0
                  for value in values:
                      if valCnt == xPos:
                          outLine += '%*s ' % (xWidth, value) 
                      elif valCnt == yPos:
                          outLine += '%*s ' % (yWidth, value)
                      else:
                          outLine += '%.4f ' % float(value)
                      valCnt += 1
                  outfile.write(outLine + '\n')
      isSubbasin = False
      cellIndex = {}
      cellList = []
      cellCnt = 0
      sbArea = 0.0
      outfile.write(line)
outfile.close()

print "Grid Origin: %d, %d" % (xMin, yMin)
print "Grid Extents: %d, %d" % (xMax - xMin +1, yMax - yMin +1)

exit(0)
