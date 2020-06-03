import unittest
from unittest import mock, TestCase
import db.db_orm as db_module


class TestDatabase(TestCase):
    def test_credentials_and_hostname(self):
        db = db_module.DBVK()
        is_conected = db.check_connection()
        self.assertTrue(is_conected, "Wrong credentials in settings.py or postgres server not available")

    def test_credentials_are_wrong_in_settings(self):
        with mock.patch("db.db_orm.DBVK.conn_string_db", 'postgresql://postgres:2@localhost/'):
            db = db_module.DBVK()
            is_conected = db.check_connection()
            self.assertFalse(is_conected, "Wrong credentials in settings.py or postgres server not available")


if __name__ == '__main__':
    unittest.main()
