'''
Mark directories on disk as Python package directories

codename/
    __init__.py
    package1.py (has class1 and is a script)
    package2.py (has class2)
    package3.py (has function1 and is a script)
    
test/
    __init__.py
    test_package1.py (has unit tests for package1)
    test_package3.py (has unit tests for package3)
'''


# Add parent dir of 'codename' to PYTHONPATH env or modify sys.path at runtime >> sys.path.append('path/to/custom/module')
# Import all names that need to be exported into 'codename/__init__.py'
import codename
    # OR
from .package3 import function1

obj = codename.class1()
codename.function1(obj)
