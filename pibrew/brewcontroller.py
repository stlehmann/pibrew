import logging
from datetime import datetime
from .hardware import HdwRaspberry, HdwSimulator
from .controllers import TempController, PWM_DC


logger = logging.getLogger(__file__)


class BrewController():
    """
    BrewController is a singleton class controlling I/O of the Raspberry Pi or
    if no I/Os can be found it will simulate the signals. The singleton pattern
    is chosen because on a system there should always only be one
    BrewController to address hardware independent of the number of Flask
    clients.

    """

    class __BrewController:

        def __init__(self, simulate=False):
            self.simulate = simulate

            self.temp_controller = TempController()
            self.temp_pwm = PWM_DC()

            self.heater_enabled = False
            self.mixer_enabled = False
            self.temp_current = 0.0
            self.temp_ctrl_reset = False
            self.manual = False
            self.reset = False

            self.settings = {
                'tempctrl': {
                    'setpoint': 50.0,
                    'kp': 10.0,
                    'tn': 180.0,
                    'manual_power_pct': 0.0,
                    'duty_cycle_s': 60.0
                }
            }

            if self.simulate:
                self.hdw_interface = HdwSimulator()
            else:
                try:
                    self.hdw_interface = HdwRaspberry()
                except IOError:
                    logger.error('No temperature sensor found.'
                                 'Continuing in simulation mode.')
                    self.hdw_interface = HdwSimulator()

        def process(self):
            # get current time to pass to the controllers
            self.now = datetime.now()

            # read the current temperature
            self.temp_current = self.hdw_interface.read_temp()

            # process temperature controller
            s = self.settings['tempctrl']
            heater_power_pct = self.temp_controller.process(
                enable=self.heater_enabled,
                now=self.now,
                temp_current=self.temp_current,
                temp_setpoint=s['setpoint'],
                kp=s['kp'],
                tn=s['tn'],
                manual=self.manual,
                manual_power_pct=s['manual_power_pct'],
                reset=self.reset
            )

            # process duty cycle controller
            heater_output = self.temp_pwm.process(
                now=self.now,
                enable=self.heater_enabled,
                in_pct=heater_power_pct,
                duty_cycle_s=s['duty_cycle_s'],
            )

            # set output of the heater according to the temperature controller
            self.hdw_interface.set_heater_output(heater_output)

        @property
        def temp_setpoint(self):
            return self.settings['tempctrl']['setpoint']

        @temp_setpoint.setter
        def temp_setpoint(self, value):
            self.settings['tempctrl']['setpoint'] = value

    instance = None

    def __init__(self, simulate=False):
        if not BrewController.instance:
            BrewController.instance = BrewController.__BrewController(simulate)

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name, value):
        setattr(self.instance, name, value)
