"""
Purpose: Replace explicit Python loops with vectorized operations using NumPy or Pandas.
How It Works: NumPy and Pandas provide high-performance functions that operate on entire arrays or DataFrames, making your code faster by eliminating slow Python loops.
Best For: Numerical computing and data manipulation tasks.
Advantages: Massive speedup for array-based operations using highly optimized C and Fortran code underneath.
"""

import numpy as np

# Vectorized operation
arr = np.arange(1_000_000)
result = np.sum(arr**2)
print(result)
