import random
from helper import getSmallestPossibleBitpack

def generateTables(numJoinValues, numberOfLeftRows, numberOfRightRows):
  assert(numberOfLeftRows <= numberOfRightRows)
  joinValues = range(numJoinValues)
  leftTable = [[rowId, random.choice(joinValues)] for rowId in range(numberOfLeftRows)]
  rightTable = [[rowId, random.choice(joinValues)] for rowId in range(numberOfRightRows)]
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
def buildLineageIndexesInThetaJoin(leftTable, rightTable, idColInLeftTable = 0, joinColInLeftTable = 1, idColInRightTable = 0, joinColInRightTable = 1):
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
  outputColCount = getOutputColCount(leftTable, rightTable)
  lineageDiagonalArray = []
  lineageMatrix = [0 for _ in range(len(leftTable) * outputColCount)]
  smokeLeftForwardLineage = [[] for _ in leftTable]
  smokeRightForwardLineage = [[] for _ in rightTable]
  smokeLeftBackwardLineage = []
  smokeRightBackwardLineage = []
  outputId = 0
  for (rightRowId, rightRow) in enumerate(rightTable):
    rightCntr = 0
    for (leftRowId, leftRow) in enumerate(leftTable):
      if leftRow[joinColInLeftTable] == rightRow[joinColInRightTable]:
        lineageMatrix[leftRowId * outputColCount + outputId] = 1
        smokeLeftForwardLineage[leftRowId].append(outputId)
        smokeRightForwardLineage[rightRowId].append(outputId)
        smokeLeftBackwardLineage.append(leftRowId)
        smokeRightBackwardLineage.append(rightRowId)
        outputId += 1
        rightCntr += 1
    lineageDiagonalArray.append(rightCntr)
  return lineageDiagonalArray, lineageMatrix, smokeLeftForwardLineage, smokeRightForwardLineage, smokeLeftBackwardLineage, smokeRightBackwardLineage

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

if __name__ == "__main__":
  #random.seed(123)
  leftTable, rightTable = generateTables(1, 30, 1000)
  #print(leftTable)
  #print(rightTable)
  lineageDiagonalArray, lineageMatrix, smokeLeftForwardLineage, smokeRightForwardLineage, smokeLeftBackwardLineage, smokeRightBackwardLineage = buildLineageIndexesInThetaJoin(leftTable, rightTable)
  # Print out matrices - messy for large index values
  print(lineageDiagonalArray)
  print(lineageMatrix)
  #print(smokeLeftForwardLineage)
  #print(smokeRightForwardLineage)
  #print(smokeLeftBackwardLineage)
  #print(smokeRightBackwardLineage)
  lineageDiagonalArraySize = len(lineageDiagonalArray)
  lineageMatrixSize = len(lineageMatrix)
  smokeLeftIndexSize = sum([len(l) for l in smokeLeftForwardLineage]) + len(smokeLeftBackwardLineage)
  smokeRightIndexSize = sum([len(l) for l in smokeRightForwardLineage]) + len(smokeRightBackwardLineage)
  # Lineage Matrix + Diagonal Array
  print("Lineage matrix and diagonal array size:", lineageMatrixSize + (lineageDiagonalArraySize * 64))
  # Smallest possible bitpack is actually max(lineageDiagonalArray), but we won't know this beforehand
  # so we use the size of rightTable because, worst case, a single input record matches with all output records
  #smallestDiagArrBitpack = getSmallestPossibleBitpack(len(rightTable))
  smallestDiagArrBitpack = getSmallestPossibleBitpack(max(lineageDiagonalArray))
  print("Smallest diagonal array bitpack:", smallestDiagArrBitpack)
  print("Lineage matrix and bitpacked diagonal array size:", lineageMatrixSize + (lineageDiagonalArraySize * smallestDiagArrBitpack))
  # Smoke sizes with 64 bit ints
  smokeIndexSize = (smokeLeftIndexSize + smokeRightIndexSize) * 64
  print("Smoke index size:", smokeIndexSize)
  # Smoke sizes with smallest possible bitpack - highest value will be max row of either pk or fk table
  smallestSmokeBitpack = getSmallestPossibleBitpack(max(len(leftTable), len(rightTable)))
  print("Smallest smoke bitpack:", smallestSmokeBitpack)
  smallestBitpackSmokeIndexSize = (smokeLeftIndexSize + smokeRightIndexSize) * smallestSmokeBitpack
  print("Smallest bitpack Smoke matrix size:", smallestBitpackSmokeIndexSize)
