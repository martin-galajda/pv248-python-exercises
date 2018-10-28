import numpy as np
import numpy.linalg as linalg
import os
from os import linesep

list_of_lists = [
  [1,2,2,42,124],
  [2,1,8,21,214],
  [3,3,2,521,124],
  [4,6,4,42,5],
  [5,8,2,211,21],
]

matrix = np.array(list_of_lists)

rank = linalg.matrix_rank(matrix)
determinant = linalg.det(matrix)
inverse = linalg.inv(list_of_lists)

print(f'Rank: {rank},{linesep}determinant:{determinant},{linesep}inverse: {inverse}')
