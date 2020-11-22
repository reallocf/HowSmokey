import random
from helper import getSmallestPossibleBitpack

def generateTables(numberOfPkRows, numberOfFkRows):
  pkTable = [[rowId] for rowId in range(numberOfPkRows)]
  fkTable = [[rowId, random.choice(pkTable)[0]] for rowId in range(numberOfFkRows)]
  return pkTable, fkTable

def buildLineageIndexesInThetaJoin(pkTable, fkTable, pkIdColInPkTable = 0, pkIdColInFkTable = 1):
  # Only capture pk portion of lineage matrix because fk portion is an identity matrix like so
  # -          1000000
  # |          0100000
  # |          0010000
  # fk portion 0001000
  # |          0000100
  # |          0000010
  # -          0000001
  # -          1010000
  # pk portion 0100100
  # -          0001011
  lineageMatrix = [0 for _ in range(len(fkTable) * len(pkTable))]
  # An Rid Index for the pk table, an Rid Array for the fk table
  smokePkForwardLineage = [[] for _ in pkTable]
  smokeFkForwardLineage = []
  smokePkBackwardLineage = []
  smokeFkBackwardLineage = []
  outputId = 0
  for (fkRowId, fkRow) in enumerate(fkTable):
    for (pkRowId, pkRow) in enumerate(pkTable):
      if pkRow[pkIdColInPkTable] == fkRow[pkIdColInFkTable]:
        lineageMatrix[pkRowId * len(fkTable) + outputId] = 1
        smokePkForwardLineage[pkRowId].append(outputId)
        smokeFkForwardLineage.append(outputId)
        smokePkBackwardLineage.append(pkRowId)
        smokeFkBackwardLineage.append(fkRowId)
        outputId += 1
  return lineageMatrix, smokePkForwardLineage, smokeFkForwardLineage, smokePkBackwardLineage, smokeFkBackwardLineage

if __name__ == "__main__":
  random.seed(123)
  pkTable, fkTable = generateTables(3, 1000000)
  lineageMatrix, smokePkForwardLineage, smokeFkForwardLineage, smokePkBackwardLineage, smokeFkBackwardLineage = buildLineageIndexesInThetaJoin(pkTable, fkTable)
  # Print out matrices - messy for large index values
  print(lineageMatrix)
  print(smokePkForwardLineage)
  print(smokeFkForwardLineage)
  print(smokePkBackwardLineage)
  print(smokeFkBackwardLineage)
  lineageMatrixSize = len(lineageMatrix)
  smokePkIndexSize = sum([len(l) for l in smokePkForwardLineage]) + len(smokePkBackwardLineage)
  smokeFkIndexSize = len(smokeFkForwardLineage) + len(smokeFkBackwardLineage)
  # Lineage Matrix
  print("Lineage matrix size:", len(lineageMatrix))
  # Smoke sizes with 64 bit ints
  smokeIndexSize = (smokePkIndexSize + smokeFkIndexSize) * 64
  print("Smoke matrix size:", smokeIndexSize)
  smokeIndexMinusBoringStuff = smokePkIndexSize * 64
  print("Smoke matrix size only including PK indexes (the interesting ones):", smokeIndexMinusBoringStuff)
  # Smoke sizes with smallest possible bitpack - highest value will be max row of either pk or fk table
  smallestBitpack = getSmallestPossibleBitpack(max(len(pkTable), len(fkTable)))
  print("Smallest bitpack:", smallestBitpack)
  smallestBitpackSmokeIndexSize = (smokePkIndexSize + smokeFkIndexSize) * smallestBitpack
  print("Smallest bitpack Smoke matrix size:", smallestBitpackSmokeIndexSize)
  smallestBitpackSmokeIndexSizeMinusBoringStuff = smokePkIndexSize * smallestBitpack
  print("Smallest bitpack Smoke matrix size only including PK indexes (the interesting ones):", smallestBitpackSmokeIndexSizeMinusBoringStuff)
