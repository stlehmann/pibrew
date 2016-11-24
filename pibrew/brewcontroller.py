from datetime import datetime
from hardware import HdwRaspberry, HdwSimulator


class PWM_DC:

    def __init__(self):
        self._t0 = None
        self.enable = False
        self.in_pct = 0.0
        self.duty_cycle_s = 60.0
        self.out_pct = False

    def process(self, now=datetime.now(), enable=None,
                in_pct=None, duty_cycle_s=None):

        # set values of optional parameters
        if enable is not None:
            self.enable = enable

        if in_pct is not None:
            self.in_pct = in_pct

        if duty_cycle_s is not None:
            self.duty_cycle_s = duty_cycle_s

        # disable output if enable is false, if enable is set to true start
        # the duty cycle by setting _t0 to now.
        if not self.enable:
            self._t0 = None
            self.out_pct = False
        else:
            if self._t0 is None:
                self._t0 = now

            # calculated delta to last process call
            t = now
            dt = (t - self._t0).total_seconds()

            # if delta bigger then duty set starttime t0 to current time
            if dt > self.duty_cycle_s:
                self._t0 = t
                dt = 0

            # calculate the on time during the cycle according to the input
            # value
            on_time = self.in_pct / 100.0 * self.duty_cycle_s
            self.out_pct = False if in_pct == 0 else dt <= on_time

        return self.out_pct


class TempController:
    """ Controller class for temperature """

    POWER_MIN = 0.0
    POWER_MAX = 100.0

    def __init__(self):
        self._prev_time = None
        self._d_temp = 0
        self._dt = 0
        self._y_p = 0
        self._y_i = 0

        self.enable = False
        self.temp_current = 20
        self.temp_setpoint = 50
        self.kp = 10.0
        self.tn = 180.0
        self.manual = False
        self.manual_power = 0.0
        self.reset = False

        self.output = False
        self.power = 0.0

    def process(self, enable=None, now=None, temp_current=None,
                temp_setpoint=None, kp=None, tn=None, manual=None,
                manual_power=None, reset=None):

        self.enable = enable or self.enable
        self.now = now or datetime.now()
        self.temp_current = temp_current or self.temp_current
        self.temp_setpoint = temp_setpoint or self.temp_setpoint
        self.kp = kp or self.kp
        self.tn = tn or self.tn
        self.manual = manual or self.manual
        self.manual_power = manual_power or self.manual_power
        self.reset = reset or self.reset

        if self._prev_time is not None:
            self._dt = (self.now - self._prev_time).total_seconds()
        else:
            self._dt = 0

        if self.enable:
            if not self.manual:
                self._d_temp = self.temp_setpoint - self.temp_current

                # proportional part
                self._y_p = self.kp * self._d_temp

                # integral part
                if self.reset:
                    self._y_i = 0
                    self.reset = False
                else:
                    if not self.tn == 0:
                        delta_i = self._dt * self._d_temp / self.tn
                        if (not (self.power >= TempController.POWER_MAX and
                                 delta_i > 0) and
                                not(self.power <= TempController.POWER_MIN and
                                    delta_i < 0)):
                            self._y_i += delta_i

                        self._y_i = max(
                            min(self._y_i, TempController.POWER_MAX),
                            TempController.POWER_MIN
                        )
                # output
                self.power = self._y_p + self._y_i

            else:
                # in manual mode just use the manual power
                self.power = self.manual_power

            # limit power to maximum and minimum
            self.power = max(
                min(self.power, TempController.POWER_MAX),
                TempController.POWER_MIN
            )

            # pwm duty duty_cycle_s
            self.output = self.pwm.process(self.power)

        else:
            # if not enabled switch output off
            self.power = 0.0
            self.output = False

        self._prev_time = now


class BrewController():

    def __init__(self):
        pass

    def init_app(self, testing=False):
        self.temp_controller = TempController()
        self.temp_pwm = PWM_DC()

        self.heater_enabled = False
        self.mixer_enabled = False
        self.temp_current = 0.0
        self.temp_ctrl_reset = False
        self.manual = False

        self.settings = {
            'tempctrl': {
                'setpoint': 50.0,
                'kp': 10.0,
                'tn': 180.0,
                'manual_power_pct': 0.0,
                'duty_cycle_s': 60.0
            }
        }

        if self.testing:
            self.hdw_interface = HdwSimulator()
        else:
            self.hdw_interface = HdwRaspberry()

    def process(self):
        # get current time to pass to the controllers
        self.now = datetime.now()

        # read the current temperature
        self.temp_current = self.hdw_interface.read_temp()

        # process temperature controller
        s = self.settings['tempctrl']
        heater_power_pct = self.temp_contoller.process(
            enable=self.heater_enabled,
            now=self.now,
            temp_current=self.temp_current,
            temp_setpoint=s['setpoint'],
            kp=s['kp'],
            tn=s['tn'],
            manual=self.manual,
            manual_power_pct=['manual_power_pct'],
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
