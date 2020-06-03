import unittest
from unittest import mock, TestCase
from VK import VK as app
from Tests.load_fixtures import get_info
import requests
from system_settings import VK_API_VERSION
from settings import VK_TOKEN

api_ver = VK_API_VERSION
vk_token = VK_TOKEN


class TestVKRequest(TestCase):

    @classmethod
    def setUpClass(cls):
        if app.VKBase.test_vk_connection() != 0:
            print("Probably token not valid. Get new token and rerun the test.")
            exit(1)
        cls.fixt_info = get_info()

    @mock.patch("VK.VK.vk_token", "wrongtoken")
    def test_vk_wrong_key_exception(self):
        self.assertRaises(app.ExceptionVK, app.VKBase().vk_request, "users.get", {})

    def test_vk_vk_request_info_valid(self):
        # app_vk = app.VKBase()

        fixt_info_el = self.fixt_info.pop()
        params = {
            'access_token': vk_token,
            'v': api_ver,
            'user_ids': fixt_info_el.get('id'),
            #            'fields': cls.fields_to_get
        }

        # resp = app_vk.vk_request("users.get", params)
        # print("sdf", resp)
        # # self.assertEqual(r, 2)

        response = requests.get(
            f'https://api.vk.com/method/users.get',
            params=params
        )
        self.assertEqual(response.json().get("response").pop().get("first_name"), fixt_info_el.get("first_name"),
                         "First name not valid")

    def test_vk_vk_request_ok(self):
        fixt_info_el = self.fixt_info.pop()
        params = {
            'access_token': vk_token,
            'v': api_ver,
            'user_ids': fixt_info_el.get('id'),
        }

        response = requests.get(
            f'https://api.vk.com/method/users.get',
            params=params
        )
        self.assertEqual(response.status_code, 200, "Request to VK API status code is not OK")


if __name__ == '__main__':
    unittest.main()
