import unittest
import os

if __name__ == '__main__':
    suite = unittest.TestLoader().discover(os.path.dirname(__file__))
    unittest.TextTestRunner(verbosity=5).run(suite)
