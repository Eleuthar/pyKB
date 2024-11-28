"""
Purpose: Just-In-Time (JIT) compiler that translates Python functions to machine code at runtime.
How It Works: Numba uses the LLVM compiler infrastructure to optimize Python code, specifically for numerical computations and array-based operations.
Best For: Numerical and scientific computing, operations with NumPy arrays, and loop-heavy code.
"""

from numba import jit
import numpy as np

@jit(nopython=True)
def sum_of_squares(arr):
    total = 0
    for num in arr:
        total += num * num
    return total

arr = np.arange(1_000_000)
print(sum_of_squares(arr))
