# capture stdout & stderr
> pytest -s
# ```````````````````````````````````````````````````

import pytest


class TestClass:


# Run ONCE before any test in the class
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self):
        print("Setting up class-level resources")
        yield
        print("Tearing down class-level resources")
        

# alternative to fixture
# run every time before each test function
    def setup_method(self):
        self.data = [1, 2, 3]  
     
    def teardown_method(self):
        self.data = None


# all functions must start with `test_`
    def test_fun(self):
        self.data = 2
        assert self.data == 2


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ OR


# fixtures instead of setup_method and teardown_method
# define global fixtures under `conftest.py` if all test files need the same


@pytest.fixture
def sample_data():
    """A reusable fixture to provide test data."""
    print("Creating fresh test data")
    data = [1, 2, 3]
    yield data  # Provides the data to the test
    print("Cleaning up test data")


def test_length_with_fixture(sample_data):
    """Test the length of the list using a fixture."""
    assert len(sample_data) == 3


def test_append_with_fixture(sample_data):
    """Test appending an element using a fixture."""
    sample_data.append(4)
    assert sample_data == [1, 2, 3, 4]
