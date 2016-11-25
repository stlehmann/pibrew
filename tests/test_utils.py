import unittest
from utils import default_if_none


class UtilsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_default_if_none(self):
        default = 1
        value = None

        # test if default value is returned if value is None
        self.assertEqual(default, default_if_none(value, default))

        # test if value is returned if value is not None
        self.assertEqual(value, default_if_none(value, default))
        self.assertEqual(0, default_if_none(0, default))
