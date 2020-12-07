def join(leftJoinColVals, rightJoinColVals):
  oSize = 0
  for lVal in leftJoinColVals:
    for rVal in rightJoinColVals:
      if lVal == rVal:
        oSize += 1

  res = [[0 for _ in range(oSize)] for _ in range(len(leftJoinColVals) + len(rightJoinColVals))]
  oCtr = 0
  oJoinColVals = []
  for lCtr, lVal in enumerate(leftJoinColVals):
    for rCtr, rVal in enumerate(rightJoinColVals):
      if lVal == rVal:
        res[lCtr][oCtr] = 1
        res[len(leftJoinColVals) + rCtr][oCtr] = 1
        oCtr += 1
        oJoinColVals.append(lVal)

  return res, oJoinColVals

def mat_printer(arr, name):
  print(name)
  for row in arr:
    print("( ", end="")
    for elem in row:
       print(elem, " ", end="")
    print(")")

def mat_append_identity(mat, identitySize):
  origMatRows = len(mat)
  origMatCols = len(mat[0])

  for _ in range(identitySize):
    mat.append([0 for _ in range(origMatCols)])
  for row in mat:
    row.extend([0 for _ in range(identitySize)])
  for i in range(identitySize):
    mat[origMatRows + i][origMatCols + i] = 1
  return mat

def mat_mul(lMat, rMat):
  lMatRowCount = len(lMat)
  lMatColCount = len(lMat[0])
  rMatRowCount = len(rMat)
  rMatColCount = len(rMat[0])

  # Confirm col len of left matrix == row len of right matrix
  assert(lMatColCount == rMatRowCount)

  res = [[0 for _ in range(rMatColCount)] for _ in range(lMatRowCount)]

  for lIdx in range(lMatRowCount):
    for rIdx in range(rMatColCount):
      for i in range(lMatColCount):
        res[lIdx][rIdx] += lMat[lIdx][i] * rMat[i][rIdx]
  return res

if __name__ == "__main__":
  T2 = [1, 1, 2]
  T1 = [1, 2, 1, 2, 3, 1]
  T3 = [1, 2, 1, 2, 3]
  T4 = [1, 1, 2, 2, 2]

  res1, oJoinColValsT1T2 = join(T1, T2)
  mat_printer(res1, "res1")

  #res1 = mat_append_identity(res1, len(T3))
  #mat_printer(res1, "res1 updated")

  #res2, oJoinColValsT1T2T3 = join(oJoinColValsT1T2, T3)
  #mat_printer(res2, "res2")

  #res3 = mat_mul(res1, res2)
  #mat_printer(res3, "res3")

  #res3 = mat_append_identity(res3, len(T4))
  #mat_printer(res3, "res3 updated")

  #res4, _ = join(oJoinColValsT1T2T3, T4)
  #mat_printer(res4, "res4")

  #res5 = mat_mul(res3, res4)
  #mat_printer(res5, "res5")
