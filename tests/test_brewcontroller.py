import time
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

    def test_enable_heater(self):
        self.brew_controller.heater_enabled = True
        self.assertFalse(self.brew_controller.temp_controller.enable)
        self.brew_controller.process()
        self.assertTrue(self.brew_controller.temp_controller.enable)

    def test_manual_mode(self):
        self.brew_controller.heater_enabled = True
        self.brew_controller.manual = True
        self.brew_controller.manual_power_pct = 50.0
        self.brew_controller.process()
        self.assertEqual(50.0, self.brew_controller.manual_power_pct)
        self.assertEqual(50.0, self.brew_controller.temp_controller.power)

    def test_automatic_mode(self):
        self.brew_controller.temp_setpoint = 20.0
        self.brew_controller.hdw_interface.temperature = 20.0

        self.brew_controller.kp = 0.5
        self.assertEqual(0.5, self.brew_controller.kp)

        self.brew_controller.tn = 0.0
        self.assertEqual(0.0, self.brew_controller.tn)

        self.brew_controller.heater_enabled = True
        self.brew_controller.process()

        # difference is 0 -> power should be 0
        self.assertAlmostEqual(
            0.0, self.brew_controller.temp_controller.power, 2)

        # difference is 100 -> power should be 50%
        self.brew_controller.temp_setpoint = 120.0
        self.brew_controller.process()
        self.assertAlmostEqual(
            50.0, self.brew_controller.temp_controller.power, 2)

    def test_integral_part(self):
        self.brew_controller.heater_enabled = True
        self.brew_controller.temp_setpoint = 120.0
        self.brew_controller.duty_cycle_s = 0.5
        self.brew_controller.kp = 0.0
        self.brew_controller.tn = 1.0
        tc = self.brew_controller.temp_controller

        # integral part at first cycle is 0
        self.brew_controller.process()
        self.assertEqual(0.0, tc.power)

        # wait 0.1 s before next cycle
        time.sleep(1.0)
        self.brew_controller.process()

        # integral part should be 10
        self.assertAlmostEqual(100.0, tc.power, 2)

        # test overload
        self.brew_controller.process()
        time.sleep(0.1)
        self.assertAlmostEqual(100.0, tc.power, 2)

        # reset
        self.brew_controller.reset = True
        self.brew_controller.process()

        # integral part should be 0
        self.assertEqual(0.0, tc.power)

    def test_duty_cycle(self):
        self.brew_controller.heater_enabled = True
        self.brew_controller.duty_cycle_s = 0.5
        self.assertEqual(0.5, self.brew_controller.duty_cycle_s)
        self.brew_controller.manual = True
        self.brew_controller.manual_power_pct = 50.0

        # output should be true at beginning of duty cycle
        self.brew_controller.process()
        self.assertTrue(self.brew_controller.temp_pwm.output)

        # after half duty cycle output should be set to false
        time.sleep(0.25)
        self.brew_controller.process()
        self.assertFalse(self.brew_controller.temp_pwm.output)


if __name__ == '__main__':
    unittest.main()
