from unittest.mock import patch
import unittest
from Tests.load_fixtures import get_id_screen_name

from VK.User import User
from Tests.mocks import get_free_port, start_mock_server


class TestMockServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock_server_port = get_free_port()
        start_mock_server(cls.mock_server_port)
        cls.fixtures_name_id = get_id_screen_name()

    def test_screen_name_to_id_3_valid_screen_names(self):
        mock_api_url = 'http://localhost:{port}'.format(port=self.mock_server_port)
        with patch.dict('VK.VK.__dict__', {'base_url': mock_api_url}):
            names_for_test = list(self.fixtures_name_id.keys())[:3]
            for fixt_scr_name in names_for_test:
                user_id = User.screen_name_to_id(fixt_scr_name)
                self.assertEqual(user_id, self.fixtures_name_id.get(fixt_scr_name))

        # assert_dict_contains_subset({'Content-Type': 'application/json; charset=utf-8'}, response.headers)
        # assert_true(response.ok)
        # assert_list_equal(response.json(), [])

    def test_screen_name_to_id_one_invalid_scneen_name(self):
        mock_api_url = 'http://localhost:{port}'.format(port=self.mock_server_port)
        # / utils.resolveScreenName
        with patch.dict('VK.VK.__dict__', {'base_url': mock_api_url}):
            user_id = User.screen_name_to_id('fake_name234234242423424')
            self.assertIsNone(user_id)


if __name__ == '__main__':
    unittest.main()
