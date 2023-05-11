import unittest
from package.module import ClassName


class TestClass(unittest.TestCase):
    
    def test_fun(self):
        new_obj = ClassName(arg1, arg2)
        self.assertEqual(new_cls.fun(argz), expected_rezult, 'Failure msg')
    
    # OR  
    
    def setUp(self):
        # this method runs every time before each test function
        self.new_obj = ClassName(arg1, arg2)
    
    # OR  
    
    @classmethod
    def setUpClass(self):
        # this method runs once and not before each test function
        self.new_obj = ClassName(arg1, arg2)
    
    # all test methods go from here
    def test_funX(self):
        pass
    
        
        
if __name__ == '__main__':
    unittest.main()
    
# OR run from CLI for specific test script under tests directory
# >>> python -m unittest -v tests.test
    
# OR run discovery mode from CLI for all test scripts
# >>> python -m unittest -v

# OR run from CLI a specific function from certain test script
# >>> python -m unittest -v tests.test
    
