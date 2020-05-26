from unittest.mock import patch
import unittest
from nose.tools import assert_dict_contains_subset, assert_list_equal, assert_true

from VK.User import User
from Tests.mocks import get_free_port, start_mock_server


class TestMockServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock_server_port = get_free_port()
        start_mock_server(cls.mock_server_port)

    # @classmethod
    # def setup_class(cls):


    def test_request_response(self):
        mock_api_url = 'http://localhost:{port}'.format(port=self.mock_server_port)
        # / utils.resolveScreenName
        with patch.dict('VK.VK.__dict__', {'BASE_API_URL': mock_api_url}):
            response = User.screen_name_to_id('svetlana_belyaeva_photographer')

        self.assertEqual(response, 28711291)
        # assert_dict_contains_subset({'Content-Type': 'application/json; charset=utf-8'}, response.headers)
        # assert_true(response.ok)
        # assert_list_equal(response.json(), [])
