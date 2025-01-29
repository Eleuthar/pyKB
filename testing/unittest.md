
# specific test script under tests directory
> python -m unittest -v tests.test
    
#  discovery mode for all test scripts
> python -m unittest -v

# specific function from certain script
> python -m unittest -v tests.test


import unittest


class TestClass(unittest.TestCase):


# run first, once, to share data for all methods
# good for DB connection \ server instance
    @classmethod
    def setUpClass(self):        
        self.data = [1, 2, 3]  

    @classmethod
    def tearDownClass(cls):
        del cls.shared_resource


# Run before each individual test
    def setUp(self):   
        print("Setting up for an individual test")

# Run after each individual test
    def tearDown(self):
        print("Tearing down after an individual test")



# all functions must start with `test_`
    def test_fun(self):
        new_obj = ClassName(arg1, arg2)
        self.assertEqual(new_cls.fun(argz), expected_rezult, 'Failure msg')

        
if __name__ == '__main__':
    unittest.main()
