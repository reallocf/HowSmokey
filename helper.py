import math

def getSmallestPossibleBitpack(maxIndexVal):
  if maxIndexVal == 0:
    return 1
  res = 0
  while maxIndexVal > 0:
    maxIndexVal = math.floor(maxIndexVal / 2)
    res += 1
  return res

