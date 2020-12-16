import csv
import math
import random
from helper import getSmallestPossibleBitpack

# Table generation scheme:
def generateTables(numberOfLeftRows, numberOfRightRows, numberOfOutputTuples):
  assert(numberOfLeftRows <= numberOfRightRows) # We decide left is smaller
  assert(numberOfOutputTuples <= (numberOfLeftRows - 1) * numberOfRightRows) # Construction choices get awkward at the edge, so limit
  if numberOfOutputTuples < numberOfLeftRows:
    # Pick numberOfOutputTuples individual rows in leftTable and rightTable to have join
    # so there will never be a double join. This is fine since we aren't using the max
    # id for the diagonal lineage array
    leftTable = [[rowId, rowId] for rowId in range(numberOfLeftRows)]
    rightTable = [[rowId, rowId] for rowId in range(numberOfOutputTuples)]
    rightTable.extend([[numberOfOutputTuples + rowId, numberOfLeftRows + rowId] for rowId in range(numberOfRightRows - numberOfOutputTuples)])
  elif numberOfOutputTuples < numberOfRightRows:
    # Loop through left table ids uniformly in trying to achieve numberOfOutputTuples.
    # Once again, the max id for the diagonal lineage array doesn't matter.
    leftTable = [[rowId, rowId] for rowId in range(numberOfLeftRows)]
    rightTable = [[rowId, rowId] for rowId in range(numberOfLeftRows)]
    rightTableSoFar = numberOfLeftRows
    while rightTableSoFar < numberOfOutputTuples:
      if rightTableSoFar + numberOfLeftRows <= numberOfOutputTuples:
        # Just put all of them in
        rightTable.extend([[rightTableSoFar + rowId, rowId] for rowId in range(numberOfLeftRows)])
        rightTableSoFar += numberOfLeftRows
      else:
        # Put in just enough
        rightTable.extend([[rightTableSoFar + rowId, rowId] for rowId in range(numberOfOutputTuples - rightTableSoFar)])
        rightTableSoFar += (numberOfOutputTuples - rightTableSoFar)
    # Fill in the rest of the right table with rows that don't match any
    rightTable.extend([[rightTableSoFar + rowId, numberOfLeftRows + rowId] for rowId in range(numberOfRightRows - rightTableSoFar)])
  else:
    # Now, we build a different kind of boring join
    # All the values on the left side will have the same join column except for 1 value that is used for cleanup
    # So, L - 1 join values will be the same, and 1 join value will be different
    # Then, we set X = floor(numberOfOutputTuples / (L - 1)) and Y = numberOfOutputTuple % (L - 1)
    # We then set X values in the right table to be the many valued join in the left
    # and Y values in the right table to be the few valued join
    # any leftover right table rows will be assigned to a value that will not join
    leftTable = [[rowId, 1] for rowId in range(numberOfLeftRows - 1)]
    leftTable.append([len(leftTable), 2])
    rightTable = [[rowId, 1] for rowId in range(math.floor(numberOfOutputTuples / (numberOfLeftRows - 1)))]
    rightTableLen = len(rightTable)
    rightTable.extend([[rightTableLen + rowId, 2] for rowId in range(numberOfOutputTuples % (numberOfLeftRows - 1))])
    rightTableLen = len(rightTable)
    rightTable.extend([[rightTableLen + rowId, 3] for rowId in range(numberOfRightRows - rightTableLen)])
  random.shuffle(leftTable)
  random.shuffle(rightTable)
  return leftTable, rightTable

def getOutputColCount(leftTable, rightTable, joinColIdLeft = 1, joinColIdRight = 1):
  res = 0
  for rightRow in rightTable:
    for leftRow in leftTable:
      if rightRow[joinColIdRight] == leftRow[joinColIdLeft]:
        res += 1
  return res

# pk = left
# fk = right
def buildLineageIndexesInThetaJoin(leftTable, rightTable, outputColCount, idColInLeftTable = 0, joinColInLeftTable = 1, idColInRightTable = 0, joinColInRightTable = 1):
  # Capture left portion as a lineage matrix because data doesn't follow any pattern
  # Capture right portion as a lineage diagonal array because data follows a diagonal pattern where,
  # for each row, all 1s are clustered are in immediately adjacent columns, like below
  # -             1100000
  # |             0010000
  # |             0000000
  # right portion 0001000
  # |             0000100
  # |             0000011
  # -             1010000
  # left portion  0100100
  # -             0001011
  # A lineage diagonal array captures the number of 1s that are at the particular row
  # You can further encode this array through bitpacking and (less generally) using run-length encoding
  # lineageDiagonalArray  = [2,1,0,1,1,2]
  # lineageMatrix = [101000001001000001011]
  lineageDiagonalArray = []
  rightLineageMatrix = [0 for _ in range(len(rightTable) * outputColCount)] # capturing for comparison
  leftLineageMatrix = [0 for _ in range(len(leftTable) * outputColCount)]
  smokeLeftForwardLineage = [[] for _ in leftTable]
  smokeRightForwardLineage = [[] for _ in rightTable]
  smokeLeftBackwardLineage = []
  smokeRightBackwardLineage = []
  outputId = 0
  for (rightRowId, rightRow) in enumerate(rightTable):
    rightCntr = 0
    for (leftRowId, leftRow) in enumerate(leftTable):
      if leftRow[joinColInLeftTable] == rightRow[joinColInRightTable]:
        rightLineageMatrix[rightRowId * outputColCount + outputId] = 1
        leftLineageMatrix[leftRowId * outputColCount + outputId] = 1
        smokeLeftForwardLineage[leftRowId].append(outputId)
        smokeRightForwardLineage[rightRowId].append(outputId)
        smokeLeftBackwardLineage.append(leftRowId)
        smokeRightBackwardLineage.append(rightRowId)
        outputId += 1
        rightCntr += 1
    lineageDiagonalArray.append(rightCntr)
  return lineageDiagonalArray, rightLineageMatrix, leftLineageMatrix, smokeLeftForwardLineage, smokeRightForwardLineage, smokeLeftBackwardLineage, smokeRightBackwardLineage

# 111100000000
# 000011110000
# 000000001111
# 100010001000
# 010001000100
# 001000100010
# 000100010001
def knownExampleTables():
  # 100000000000
  # 010000000000
  # 001100000000
  # 000010000000
  # 000000000000
  # 000001100000
  # 000000010000
  # 000000000000
  # 000000001100
  # 000000000011
  # 001001001010
  # 110010010000
  # 000100100101
  # lineageDiagonalArray = 1121021022
  # lineageMatrix = bottom 3 lines
  leftTable = [[0, 0], [1, 1], [2, 0]]
  rightTable = [[0, 1], [1, 1], [2, 0], [3, 1], [4, 2], [5, 0], [6, 1], [7, 2], [8, 0], [9, 0]]
  return leftTable, rightTable

def runTests(leftTableLen, rightTableLen, outputTupleCount):
  leftTable, rightTable = generateTables(leftTableLen, rightTableLen, outputTupleCount)
  assert(len(leftTable) == leftTableLen)
  assert(len(rightTable) == rightTableLen)
  assert(getOutputColCount(leftTable, rightTable) == outputTupleCount)
  #print(leftTable)
  #print(rightTable)
  lineageDiagonalArray, rightLineageMatrix, leftLineageMatrix, smokeLeftForwardLineage, smokeRightForwardLineage, smokeLeftBackwardLineage, smokeRightBackwardLineage = buildLineageIndexesInThetaJoin(leftTable, rightTable, outputTupleCount)
  # Print out matrices - messy for large index values
  #print(lineageDiagonalArray)
  #print(lineageMatrix)
  #print(smokeLeftForwardLineage)
  #print(smokeRightForwardLineage)
  #print(smokeLeftBackwardLineage)
  #print(smokeRightBackwardLineage)
  fullLineageMatrixSize = len(rightLineageMatrix) + len(leftLineageMatrix)
  optimizedLineageMatrixSize = len(leftLineageMatrix) + len(lineageDiagonalArray) * 32
  smokeForwardIndexSize = sum([len(l) for l in smokeLeftForwardLineage]) + sum([len(l) for l in smokeRightForwardLineage])
  smokeBackwardIndexSize = len(smokeLeftBackwardLineage) + len(smokeRightBackwardLineage)
  #smokeLeftIndexSize = sum([len(l) for l in smokeLeftForwardLineage]) + len(smokeLeftBackwardLineage)
  #smokeRightIndexSize = sum([len(l) for l in smokeRightForwardLineage]) + len(smokeRightBackwardLineage)
  # Full Lineage Matrix
  print("Full lineage matrix size: ", fullLineageMatrixSize)
  # Lineage Matrix + Diagonal Array
  print("Lineage matrix and diagonal array size:", optimizedLineageMatrixSize)
  # Smallest possible bitpack is actually max(lineageDiagonalArray), but we won't know this beforehand
  # so we use the size of rightTable because, worst case, a single input record matches with all output records
  #smallestDiagArrBitpack = getSmallestPossibleBitpack(len(rightTable))
  smallestDiagArrBitpack = getSmallestPossibleBitpack(rightTableLen)
  bitpackedOptimizedLineageMatrixSize = len(leftLineageMatrix) + len(lineageDiagonalArray) * smallestDiagArrBitpack
  print("Smallest diagonal array bitpack:", smallestDiagArrBitpack)
  print("Lineage matrix and bitpacked diagonal array size:", bitpackedOptimizedLineageMatrixSize)
  # Smoke sizes with 32 bit ints
  smokeIndexSize = (smokeForwardIndexSize + smokeBackwardIndexSize) * 32
  print("Smoke index size:", smokeIndexSize)
  # Smoke sizes with smallest possible bitpack
  smallestBitpackSmokeIndexSize = smokeForwardIndexSize * getSmallestPossibleBitpack(outputTupleCount) + smokeBackwardIndexSize * getSmallestPossibleBitpack(rightTableLen)
  print("Smallest bitpack Smoke matrix size:", smallestBitpackSmokeIndexSize)
  return [fullLineageMatrixSize, optimizedLineageMatrixSize, bitpackedOptimizedLineageMatrixSize, smokeIndexSize, smallestBitpackSmokeIndexSize]

if __name__ == "__main__":
  #random.seed(123)
  resultCSV = []
  numberOfLeftRows = 4
  while numberOfLeftRows <= 512:
    print("Starting left ", numberOfLeftRows)
    res = [numberOfLeftRows]
    res.extend(runTests(numberOfLeftRows, 1000, 2000))
    resultCSV.append(res)
    numberOfLeftRows *= 2
  print(resultCSV)
  with open("join1.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(resultCSV)
  resultCSV = []
  numberOfRightRows = 100
  while numberOfRightRows <= 12800:
    print("Starting right ", numberOfRightRows)
    res = [numberOfRightRows]
    res.extend(runTests(25, numberOfRightRows, 2000))
    resultCSV.append(res)
    numberOfRightRows *= 2
  print(resultCSV)
  with open("join2.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(resultCSV)
  resultCSV = []
  numberOfOutputTuples = 25
  while numberOfOutputTuples <= 3200:
    print("Starting output ", numberOfOutputTuples)
    res = [numberOfOutputTuples]
    res.extend(runTests(25, 1000, numberOfOutputTuples))
    resultCSV.append(res)
    numberOfOutputTuples *= 2
  print(resultCSV)
  with open("join3.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(resultCSV)
