# capture stdout & stderr
> pytest -s

# code coverage + missing item
> coverage run --source=src -m pytest -v tests && coverage report -m
# ```````````````````````````````````````````````````````````````````

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

# prevent import error
sys.path.append(str(Path(__file__).parent.parent.parent) + "/src")

# mocker param available after pip install pytest-mock 

@pytest.fixture(autouse=True)
def mock_http_req(mocker):
    uid = subprocess.Popen(["whoami"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    uid = uid.stdout.read().decode().strip()
    mocker.patch.dict(os.environ, {"TIME": "999"})
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response.return_value = {}
    mocker.patch("requests.get", return_value=mock_response)
    # takes precedence before return_value\json
    mock_response.side_effect = Exception("Network error")
    # forwarded exception must be raised
    with pytest.raises(ConnectionError) as rx:
        result = mocked_method("http://mock-url")
        assert "Network error" in result["message"]
        logging.getLogger().info("result %s", result["message"])
