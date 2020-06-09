import unittest
from vk import vk_utils as app


class TestFindCommon(unittest.TestCase):
    def test_lists(self):
        v1 = ['1','2']
        v2 = ['1','2','3']
        r = app.find_common(v1, v2)
        self.assertEqual(r, 2)

    def test_list_set(self):
        v1 = ['1','2']
        v2 = set(['1','2','3'])
        r = app.find_common(v1, v2)
        self.assertEqual(r, 2)

    def test_str_int(self):
        v1 = 1
        v2 = '1'
        r = app.find_common(v1, v2)
        self.assertEqual(r, 1)

    def test_str_comma_list(self):
        v1 = [1,4,6]
        v2 = '1,2,3,4,5'
        r = app.find_common(v1, v2)
        self.assertEqual(r, 2)

    def test_str_comma_upper_list(self):
        v1 = ["f1",4,5]
        v2 = 'F1,2,3,4,5'
        r = app.find_common(v1, v2)
        self.assertEqual(r, 3)

    def test_lists_no_common(self):
        v1 = [6,4,5]
        v2 = ["sdfsdf", 9, 0, "dfgdd"]
        r = app.find_common(v1, v2)
        self.assertEqual(r, 0)


if __name__ == '__main__':
    unittest.main()
