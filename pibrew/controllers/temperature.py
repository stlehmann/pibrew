from datetime import datetime
from utils import default_if_none


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
        self.manual_power_pct = 0.0
        self.reset = False

        self.power = 0.0

    def process(self, enable=None, now=None, temp_current=None,
                temp_setpoint=None, kp=None, tn=None, manual=None,
                manual_power_pct=None, reset=None):

        self.enable = default_if_none(enable, self.enable)
        self.now = default_if_none(now, datetime.now())
        self.temp_current = default_if_none(temp_current, self.temp_current)
        self.temp_setpoint = default_if_none(temp_setpoint, self.temp_setpoint)
        self.kp = default_if_none(kp, self.kp)
        self.tn = default_if_none(tn, self.tn)
        self.manual = default_if_none(manual, self.manual)
        self.manual_power_pct = default_if_none(
            manual_power_pct, self.manual_power_pct)
        self.reset = default_if_none(reset, self.reset)

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
                self.power = self.manual_power_pct

            # limit power to maximum and minimum
            self.power = max(
                min(self.power, TempController.POWER_MAX),
                TempController.POWER_MIN
            )

        else:
            # if not enabled set output to 0.0
            self.power = 0.0

        self._prev_time = now
