import unittest
from unittest import mock, TestCase
from VK import VK as app

print("sdf")
class TestVKRequest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app_vk = app.VK()
        # print(cls.app_vk.get_token())

        # cls.app_trans = app.Trans()

    @mock.patch("vk.vk.requests.get", return_value='mocked')
    def test_vk_vk_request(self, mock_requests_get):
        resp = self.app_vk.vk_request("users.get", {})
        print(resp)
        # self.assertEqual(r, 2)


if __name__ == '__main__':
    unittest.main()
