"""
$ sudo apt-get install build-essential
$ sudo apt install python3-dev
$ pip install --upgrade setuptools wheel
$ pip install mypy
$ pip install mypyc
"""

# example.py
from typing import List

def compute_sum_of_squares(nums: List[int]) -> int:
    total = 0
    for num in nums:
        total += num * num
    return total


# ~~~~~~~~~~~~~~~~~~ METHOD 1 ~~~~~~~~~~~~~~~~~
# compile and execute 
"""
$ mypyc example.py
$ python3 -c "import example"
"""


# ~~~~~~~~~~~~~~~~~~ METHOD 2 ~~~~~~~~~~~~~~~~~
# setup.py
from setuptools import setup
from mypyc.build import mypycify

setup(
    name="example",
    ext_modules=mypycify(["example.py"]),
    zip_safe=False,
)

"""
$ python setup.py build_ext --inplace
"""

# In a new script or REPL:
import example

nums = list(range(1_000_000))
result = example.compute_sum_of_squares(nums)
print(result)

