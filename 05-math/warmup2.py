import numpy as np
from numpy.linalg import linalg

# y1 = x0 * 6  + x1 * 12 
# y2 = x0 * 6  + x1 * 10

# y1 = 10
# y2 = 5

coefficients = np.array([
  [ 6, 12 ],
  [ 6, 10 ]
])

results = np.array([
  10,
  5
])

result = linalg.solve(coefficients, results)

print(result)
(x0, x1) = result

print(f'{x0 * 6 + x1 * 12} = 10')
print(f'{x0 * 6 + x1 * 10} = 5')
