import unittest
from utils import default_if_none


class UtilsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_default_if_none(self):
        # test if default value is returned if value is None
        self.assertEqual(1, default_if_none(None, 1))

        # test if value is returned if value is not None
        self.assertEqual(0, default_if_none(0, 1))
