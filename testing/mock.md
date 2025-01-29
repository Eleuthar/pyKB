# ~~~~~~~~~~~~~~~~ main.py
import requests

def len_joke():
    joke = get_joke()
    return len(joke)


def get_joke():
    uri = 'http://api.icndb.com/jokes/random'

    try:
        q = requests.get(uri)
        q.raise_for_status()

    except requests.exceptions.Timeout:
        return 'No joke'
    
    except requests.exceptions.ConnectionError:
        return 'ConnErr'

    except requests.exceptions.HTTPError as xx:
        status_code = xx.response.status_code
        if status_code in [503, 504]:
            pass
        else:
            pass
        return 'HTTPError triggered'

    else:
        if q.status_code == 200:
            joke = q.json()['value']['joke']
        else:
            joke = 'no joke'

    return joke

print(get_joke())




#  ~~~~~~~~~~~~~~~~ tests.py
import unittest
import responses

from main import get_joke


class TestGetJoke(unittest.TestCase):

    @responses.activate
    def test_get_joke_returns_joke(self):
        responses.get(
            uri='http://api.icnddb.com/jokes/random',
            json={'value': {'joke': 'funny joke'}},
            status=200
        )
        self.assertEqual(get_joke(), len('funny joke'))

    
    @responses.activate
    def test_get_joke_raise_for_status(self):
        responses.get(
            uri='http://api.icnddb.com/jokes/random',
            json={'value': {'joke': 'funny joke'}},
            status=403
        )
        self.assertEqual(get_joke(), len('HTTPError triggered'))


    @responses.activate
    def test_get_joke_connection_err(self):
        responses.get(
            uri='http://api.icnddb.com/jokes/random',
            body=requests.ConnectionError('ConnErr')
        )
        self.assertEqual(get_joke(), len(''))




#  ~~~~~~~~~~~~~~~~ tests.py

import unittest
from unittest.mock import patch

from requests.exceptions import Timeout, HTTPError
import requests.exceptions

from main import len_joke


class TestJoke(unittest.TestCase):

# make fake <joke> object
    @patch('main.get_joke')
    def test_len_joke(self, mock_get_joke):
        mock_get_joke.return_value = 'funny joke'
        self.assertEqual(len_joke(), len('funny joke'))

# mock the response, 200 status code, json return value
    @patch('main.requests')
    def test_get_joke(self, mock_requests):
        mock_reply = MagicMock()
        mock_reply.status_code = 200
        mock_reply.json.return_value = {'value': {'joke':'funny joke'}}
        mock_requests.get.return_value = mock_response
        self.assertEqual(get_joke(), 'funny joke')

# mock the response, 403 status code, json return value
    @patch('main.requests')
    def test_fail_get_joke(self, mock_requests):
        mock_reply = MagicMock(status_code=403)
        mock_reply.json.return_value = {'value': {'joke':'funny joke'}}
        mock_requests.get.return_value = mock_response
        self.assertEqual(get_joke(), 'no joke')

# requests.exceptions.Timeout from main.py will be replaced by 
# unittest.mock.MagicMock
# mock_requests.get.side_effect = Timeout('Server down') does not inherit from BaseException
# monkey patch inheritance \\ mock_requests.exceptions = requests.exceptions
    @patch('main.requests')
    def test_get_joke_raise_for_status(self, mock_requests):

        mock_requests.exceptions = requests.exceptions
        
        mock_reply = MagicMock(status_code=403)
        mock_reply.raise_for_status.side_effect = HTTPError('5xx error')
        mock_requests.get.return_value = mock_reply

# HTTPError from main.py
        self.assertEqual(get_joke(), 'HTTPError triggered')

unittest.main()