import time
import unittest
from pibrew.brewcontroller import BrewController
from pibrew import create_app, db, brew_controller


class BrewControllerTestCase(unittest.TestCase):

    def setUp(self):
        brew_controller.initialized = False
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        self.client = self.app.test_client()
        self.client.get('/')

    def tearDown(self):
        brew_controller.stop()
        while brew_controller.running:
            pass

        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    # def test_singleton(self):
    #     bc1 = BrewController.get_instance()
    #     bc2 = BrewController.get_instance()
    #     self.assertIs(bc1, bc2)

    #     # Allow initializing only once
    #     bc1.init_app(self.app)
    #     with self.assertRaises(RuntimeError):
    #         bc2.init_app(self.app)

    # def test_os_simulation(self):
    #     self.app.config['SIMULATE'] = False
    #     bc = BrewController(self.app)
    #     self.assertEqual('HdwSimulator', bc.hdw_interface.__class__.__name__)

    def test_enable_heater(self):
        brew_controller.heater_enabled = True
        self.assertFalse(brew_controller.temp_controller.enable)
        brew_controller.process()
        self.assertTrue(brew_controller.temp_controller.enable)

    def test_manual_mode(self):
        brew_controller.heater_enabled = True
        brew_controller.manual = True
        brew_controller.manual_power_pct = 50.0
        brew_controller.process()
        self.assertEqual(50.0, brew_controller.manual_power_pct)
        self.assertEqual(50.0, brew_controller.temp_controller.power)

    def test_automatic_mode(self):
        brew_controller.temp_setpoint = 20.0
        brew_controller.hdw_interface.temperature = 20.0

        brew_controller.kp = 0.5
        self.assertEqual(0.5, brew_controller.kp)

        brew_controller.tn = 0.0
        self.assertEqual(0.0, brew_controller.tn)

        brew_controller.heater_enabled = True
        brew_controller.process()

        # difference is 0 -> power should be 0
        self.assertAlmostEqual(
            0.0, brew_controller.temp_controller.power, 2)

        # difference is 100 -> power should be 50%
        brew_controller.temp_setpoint = 120.0
        brew_controller.process()
        self.assertAlmostEqual(
            50.0, brew_controller.temp_controller.power, 2)

    def test_integral_part(self):
        brew_controller.heater_enabled = True
        brew_controller.temp_setpoint = 120.0
        brew_controller.duty_cycle_s = 0.5
        brew_controller.kp = 0.0
        brew_controller.tn = 1.0
        tc = brew_controller.temp_controller

        # integral part at first cycle is 0
        brew_controller.process()
        self.assertEqual(0.0, tc.power)

        # wait 0.1 s before next cycle
        time.sleep(1.0)
        brew_controller.process()

        # integral part should be 10
        self.assertAlmostEqual(100.0, tc.power, 2)

        # test overload
        brew_controller.process()
        time.sleep(0.1)
        self.assertAlmostEqual(100.0, tc.power, 2)

        # reset
        brew_controller.reset = True
        brew_controller.process()

        # integral part should be 0
        self.assertEqual(0.0, tc.power)


if __name__ == '__main__':
    unittest.main()
