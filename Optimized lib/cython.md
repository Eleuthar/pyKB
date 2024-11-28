"""
Purpose: Compile Python code into C, yielding significant performance improvements.
How It Works: Write Python code with optional type annotations and compile it into a C extension.
Best For: Optimizing Python code that performs intensive numerical computations, handling large data sets, or interfacing with C libraries.
"""

def sum_of_squares(arr):
    cdef int total = 0
    for num in arr:
        total += num * num
    return total

# TODO SYNTAX