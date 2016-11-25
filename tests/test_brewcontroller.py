import unittest
from pibrew.brewcontroller import BrewController


class BrewControllerTestCase(unittest.TestCase):

    def setUp(self):
        self.brew_controller = BrewController(simulate=True)

    def teardown(self):
        pass

    def test_singleton(self):
        bc1 = BrewController.get_instance()
        bc2 = BrewController.get_instance()
        self.assertIs(bc1, bc2)

if __name__ == '__main__':
    unittest.main()
